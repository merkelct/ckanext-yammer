import yampy
import pprint
import ckan.model.package as package
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.yammer.model.yammer_user as yammer_user
import ckan.logic as logic
from pylons import app_globals
from routes.mapper import SubMapper
from ckan.common import c
from copy import deepcopy



def yammer_config(id):

    yammer_config_options = yammer_user.Yammer_user().get(id)
    return yammer_config_options

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
        print(p)
        yammer_poster = yammer_user.Yammer_user().get(c.userobj.id + "." + p.owner_org)
        types = []
        if yammer_poster.create_dataset == True:
            types.append('create')
        if yammer_poster.update_dataset == True:
            types.append('update')
        if yammer_poster.delete_dataset == True:
            types.append('delete')

        return types


    def yammer_post(self, edit_type, p):
        yammer_poster = yammer_user.Yammer_user().get(c.userobj.id + "." + p.owner_org)
        access_token = yammer_poster.token
        groups = yammer_poster.groups
        url = app_globals.site_url + toolkit.url_for(controller='package', action='read', id=p.name)
        yammer = yampy.Yammer(access_token=access_token)
        for group_id in groups:
            yammer.messages.create('The {} Dataset has been {}, check it out here: {}'.format(p.name, edit_type, url),
                                    group_id=group_id,
                                    topics=['Dataset', edit_type])

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
        p = deepcopy(package.Package().get(instance.id))
        if p != None:
            edits = self.get_edit_type(p)
            if 'update' in edits:
                self.yammer_post('updated', p)

    def before_insert(self, mapper, connection, instance):
        pass

    def after_insert(self, mapper, connection, instance):
        p = deepcopy(package.Package().get(instance.id))
        if p != None:
            edits = self.get_edit_type(p)
            if 'create' in edits:
                self.yammer_post('created', p)

    def before_delete(self, mapper, connection, instance):
        pass

    def after_delete(self, mapper, connection, instance):
        p = deepcopy(package.Package().get(instance.id))
        if p != None:
            edits = self.get_edit_type(p)
            if 'delete' in edits:
                self.yammer_post('deleted', p)


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