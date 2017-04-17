# encoding: utf-8
import actions
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
import ckan.lib.helpers as h
from ckan.common import c, request
from ckan.logic import get_action

import db

render = base.render
_ = p.toolkit._

class YammerController(base.BaseController):
    controller = 'ckanext.yammer.controller:YammerController'

    def yammer_config(self, id):
        '''Render the config template with the first custom title.'''

        #if yammer_user table does not exit
        # create it
        if db.yammer_user_table is None:
            db.init_db(model)

        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'parent': request.params.get('parent', None)
                   }

        #print context
        if p.toolkit.request.method == 'POST':

            #do a try catch here for sending the data objec to the DB after save
            data = dict(p.toolkit.request.POST)
            #print data
            h.flash_success(data, allow_html=True)
            #call the action

            #the values for create, update, and delete values need to be passed into
            # the data variable, they are hard coded for now
            if 'Create' in data and data['Create'] == 'True':
                create_dataset = True
            else:
                create_dataset = False
            if 'Update' in data and data['Update'] == 'True':
                update_dataset = True
            else:
                update_dataset = False
            if 'Delete' in data and data['Delete'] == 'True':
                delete_dataset = True
            else:
                delete_dataset = False
            yammer_poster = {'id': data['user_id'],
                             'name': data['user_name'],
                             'token': data['ckanext.yammer.token'],
                             'groups': data['ygroups'],
                             'create_dataset': create_dataset,
                             'update_dataset': update_dataset,
                             'delete_dataset': delete_dataset,
                             'org': data['organization']}
            print(yammer_poster)
            actions.yammer_user_update(yammer_poster)




        data_dict = {'id': id, 'include_datasets': False}
        print data_dict
        c.group_dict = get_action('organization_show')(context, data_dict)

        return render('organization/yammer_config.html',
                      extra_vars={'title': 'Yammer Configurations'})



