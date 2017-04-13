import yampy
import ckan.model.package as package
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import db
import ckan.lib.base as base
from pylons import app_globals
from routes.mapper import SubMapper


group_type = u'grup'
group_type_utf8 = group_type.encode('utf8')


class YammerPlugin(plugins.SingletonPlugin, toolkit.DefaultGroupForm):
    plugins.implements(plugins.IGroupForm, inherit=False)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMapper)
    plugins.implements(plugins.IRoutes, inherit=True)


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
        yammer_man  = db.Yammer_user.get()

        if p != None:
            access_token = ''
            group_id = 0
            url = app_globals.site_url + toolkit.url_for(controller = 'package', action = 'read', id = p.name)
            yammer = yampy.Yammer(access_token = access_token)
            yammer.messages.create('The {} Dataset has been updated, check it out here: {}'.format(p.name, url),
                                   group_id=group_id,
                                   topics=['Dataset', 'Update'])

    def before_insert(self, mapper, connection, instance):
        pass

    def after_insert(self, mapper, connection, instance):
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