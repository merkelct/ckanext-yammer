import yampy
import db as db
import json
import ckan.model.package as package
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.yammer.model.yammer_user as yammer_user
from pylons import app_globals
from routes.mapper import SubMapper
from ckan.common import c
from copy import deepcopy
from sqlalchemy import exc

def yammer_config(id):

    try:
        context = {'for_view': True}
        yammer_config_options = yammer_user.Yammer_user().get(id)
        form = db.table_dictize(yammer_config_options, context)
        jsonform = json.dumps(form)
        print yammer_config_options
        return str(jsonform)
    except exc.SQLAlchemyError:
        return 'failure'

group_type = u'grup'
group_type_utf8 = group_type.encode('utf8')

class YammerPlugin(plugins.SingletonPlugin, toolkit.DefaultGroupForm):
    plugins.implements(plugins.IGroupForm, inherit=False)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IMapper)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    # Tell CKAN what custom template helper functions this plugin provides,
    def get_helpers(self):
        return {'yammer_config': yammer_config}

    def get_edit_type(self, p):
        yammer_poster = yammer_user.Yammer_user().get(c.userobj.id + "." + p.owner_org)
        types = []
        if yammer_poster.create_dataset == True:
            types.append('create')
        else:
            types.append('false')
        if yammer_poster.update_dataset == True:
            types.append('update')
        else:
            types.append('false')
        if yammer_poster.delete_dataset == True:
            types.append('delete')
        else:
            types.append('false')
        return types


    def yammer_post(self, edit_type, p):
        yammer_poster = yammer_user.Yammer_user().get(c.userobj.id + "." + p.owner_org)
        access_token = yammer_poster.token
        groups = yammer_poster.groups
        url_base = app_globals.site_url[:len(app_globals.site_url)-10]
        url = url_base + toolkit.url_for(controller='package', action='read', id=p.name)
        yammer = yampy.Yammer(access_token=access_token)
        for group_id in groups:
            if edit_type == 'deleted':
                message = 'The {} dataset has been {}'.format(p.name, edit_type)
            else:
                message = 'The {} dataset has been {}, you can see the changes here: {}'.format(p.name, edit_type, url)

            yammer.messages.create(message, group_id=group_id, topics=['Dataset', edit_type])

    # IConfigurer
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('fanstatic', 'yammer')

    # IMapper
    def before_update(self, mapper, connection, instance):
        pass

    def after_update(self, mapper, connection, instance):
        #get the package details from the mapper
        p = package.Package().get(instance.id)
        if p != None:
            edits = self.get_edit_type(p)
            if 'update' in edits and p.state != 'deleted' and p.state != 'draft':
                self.yammer_post('updated', p)
            elif 'delete' in edits and p.state == 'deleted':
                self.yammer_post('deleted', p)
            else:
                pass

    def before_insert(self, mapper, connection, instance):
        pass

    def after_insert(self, mapper, connection, instance):
        p = package.Package().get(instance.id)
        if p != None:
            edits = self.get_edit_type(p)
            if 'create' in edits:
                self.yammer_post('created', p)
            else:
                pass

    def before_delete(self, mapper, connection, instance):
        pass

    def after_delete(self, mapper, connection, instance):
        pass


    # IGroupForm

    def group_types(self):
        return (group_type,)

    def is_fallback(self):
        False

    def group_controller(self):
        return 'organization'

    # IRoutes

    def before_map(self, map):
        controller = 'ckanext.yammer.controller:YammerController'
        with SubMapper(map, controller=controller) as m:
            m.connect('ckanext_yammer_config',
                      '/organization/yammer_config/{id}',
                      action='yammer_config', ckan_icon='bullhorn', id='{id}')
        return map

    def yammer_user_create(self, something):
        print("this is called")