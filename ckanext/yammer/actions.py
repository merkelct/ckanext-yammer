#create an action that called the model update
import ckan.model.meta as meta
import ckanext.yammer.model.yammer_user as yammer_user
from sqlalchemy import exc




def yammer_user_update(yammer_poster):
    session = meta.Session
    if yammer_user.Yammer_user().get(yammer_poster['id']) == None:
        y = yammer_user.Yammer_user()
        y.id = yammer_poster['id']
        y.name = yammer_poster['name']
        y.token = yammer_poster['token']
        groups = [yammer_poster['groups']]
        groups = map(int, groups)
        y.groups = groups
        y.org = yammer_poster['org']
        y.create_dataset = yammer_poster['create_dataset']
        y.update_dataset = yammer_poster['update_dataset']
        y.delete_dataset = yammer_poster['delete_dataset']
        session.add(y)
    else:
        y = yammer_user.Yammer_user().get(yammer_poster['id'])
        y.id = yammer_poster['id']
        y.name = yammer_poster['name']
        y.token = yammer_poster['token']
        groups = [yammer_poster['groups']]
        groups = map(int, groups)
        y.groups = groups
        y.org = yammer_poster['org']
        y.create_dataset = yammer_poster['create_dataset']
        y.update_dataset = yammer_poster['update_dataset']
        y.delete_dataset = yammer_poster['delete_dataset']
        session.add(y)
    try:
        session.commit()
        return 'success'
    except exc.SQLAlchemyError:
        return 'failure'
