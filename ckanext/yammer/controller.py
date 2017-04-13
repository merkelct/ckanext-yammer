# encoding: utf-8
import ckan.lib.base as base
import ckan.model as model
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

        print context

        data_dict = {'id': id, 'include_datasets': False}
        print data_dict
        c.group_dict = get_action('organization_show')(context, data_dict)

        return render('organization/yammer_config.html',
                      extra_vars={'title': 'Yammer Configurations'})



