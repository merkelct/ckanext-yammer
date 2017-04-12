import yampy
import ckan.model.package as package
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from pylons import app_globals



class YammerPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMapper)

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





