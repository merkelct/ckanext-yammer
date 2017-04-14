#create an action that called the model update
import ckan.model.meta as meta
import ckanext.yammer.model.yammer_user as yammer_user

def yammer_user_update(yammer_poster):
    #insert
    if yammer_user.Yammer_user().get(yammer_poster['name']) == None:
        #yammer_user.Yammer_user().update(out)
        y = yammer_user.Yammer_user()
        y.name = yammer_poster['name']
        y.token = yammer_poster['token']
        groups = [yammer_poster['groups']]
        groups = map(int, groups)
        y.groups = groups
        y.create_dataset = yammer_poster['create_dataset']
        y.update_dataset = yammer_poster['update_dataset']
        y.delete_dataset = yammer_poster['delete_dataset']

        session = meta.Session
        session.add(y)
        print(session)
        session.commit()
    #update
    else:
        y = yammer_user.Yammer_user()
        y.name = yammer_poster['name']
        y.token = yammer_poster['token']
        groups = [yammer_poster['groups']]
        groups = map(int, groups)
        y.groups = groups
        y.create_dataset = yammer_poster['create_dataset']
        y.update_dataset = yammer_poster['update_dataset']
        y.delete_dataset = yammer_poster['delete_dataset']

        session = meta.Session
        session.add(y)
        print(session)
        session.commit()
        print("actions called")