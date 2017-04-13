# encoding: utf-8
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
import ckan.lib.helpers as h

from ckan.common import c, request
from ckan.logic import get_action

import db

render = base.render


class YammerController(base.BaseController):

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
            print data
            h.flash_success(data, allow_html=True)



        data_dict = {'id': id, 'include_datasets': False}
        print data_dict
        c.group_dict = get_action('organization_show')(context, data_dict)

        return render('organization/yammer_config.html',
                      extra_vars={'title': 'Yammer Configurations'})



