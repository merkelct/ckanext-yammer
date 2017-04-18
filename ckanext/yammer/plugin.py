import yampy
import db as db
import json
import ckan.model.package as package
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.yammer.model.yammer_user as yammer_user
from pylons import app_globals, config
from routes.mapper import SubMapper
from ckan.common import c
from sqlalchemy import exc, inspect
import ckan.lib.helpers as h


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


def get_yammer_clientid():
    id = config['ckan.yammer.id']
    return id


class YammerPlugin(plugins.SingletonPlugin, toolkit.DefaultGroupForm):
    plugins.implements(plugins.IGroupForm, inherit=False)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IMapper)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    # Tell CKAN what custom template helper functions this plugin provides,
    def get_helpers(self):
        return {'yammer_config': yammer_config,
                'get_yammer_clientid': get_yammer_clientid }

    def get_edit_type(self, p):
        yammer_poster = yammer_user.Yammer_user().get(c.userobj.id + "." + p.owner_org)
        types = []

        if p is not None:
            yammer_poster = yammer_user.Yammer_user().get(c.userobj.id + "." + p.owner_org)

            if yammer_poster is not None and yammer_poster.create_dataset is True:
                types.append('create')
            if yammer_poster is not None and yammer_poster.update_dataset is True:
                types.append('update')
            if yammer_poster is not None and yammer_poster.delete_dataset is True:
                types.append('delete')

        return types

    def yammer_post(self, edit_type, p, org_name):
        yammer_poster = yammer_user.Yammer_user().get(c.userobj.id + "." + p.owner_org)
        access_token = yammer_poster.token
        groups = yammer_poster.groups
        url_base = app_globals.site_url[:len(app_globals.site_url)-10]
        url = url_base + toolkit.url_for(controller='package', action='read', id=p.name)
        yammer = yampy.Yammer(access_token=access_token)
        for group_id in groups:
            if edit_type == 'deleted':
                message = 'The {} dataset has been {} from {}'.format(p.name, edit_type,  org_name)
                yammer.messages.create(message, group_id=group_id, topics=['Dataset', edit_type])
            elif edit_type == 'created':
                message = 'The {} dataset has been {} for {}, you can see it here: {}'.format(p.name, edit_type, org_name,  url)
                yammer.messages.create(message, group_id=group_id, topics=['Dataset', edit_type])
            elif edit_type == 'updated':
                message = 'The {} dataset has been {} for {}, you can see the updates here: {}'.format(p.name, edit_type, org_name,  url)
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
            org = h.get_organization(org=p.owner_org)
            for action in edits:
                if action == 'update' and p.state != 'deleted' and p.state != 'draft' and p.private is not True:
                    self.yammer_post('updated', p, org['display_name'])
                elif action == 'delete' and p.state == 'deleted':
                    self.yammer_post('deleted', p, org['display_name'])
                else:
                    pass


    def before_insert(self, mapper, connection, instance):
        pass

    def after_insert(self, mapper, connection, instance):
        p = package.Package().get(instance.id)
        if p is not None:
            edits = self.get_edit_type(p)
            org = h.get_organization(org=p.owner_org)
            for action in edits:
                if action == 'create' and p.state != 'deleted' and p.private is not True:
                    print('posting to yammer')
                    self.yammer_post('created', p, org['display_name'])
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