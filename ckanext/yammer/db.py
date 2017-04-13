import datetime
import uuid
import json

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import class_mapper
try:
    from sqlalchemy.engine.result import RowProxy
except:
    from sqlalchemy.engine.base import RowProxy

yammer_user_table = None
Yammer_user = None

def make_uuid():
    return unicode(uuid.uuid4())

def init_db(model):
    class _Yammer_user(model.DomainObject):

        @classmethod
        def get(cls, yammer_user_reference):
            query = query.filter(or_(cls.name == yammer_user_reference,
                                     cls.id == yammer_user_reference))
            return query.first()

    global Yammer_user
    Yammer_user = _Yammer_user
    # We will just try to create the table.  If it already exists we get an
    # error but we can just skip it and carry on.
    sql = '''
                CREATE TABLE ckanext_yammer_user (
                    id text NOT NULL PRIMARY KEY,
                    name text NOT NULL,
                    token text,
                    groups integer ARRAY,
                    create_dataset boolean,
                    update_dataset boolean,
                    delete_dataset boolean
                );
    '''
    conn = model.Session.connection()
    try:
        #print(sql)
        conn.execute(sql)
    except sa.exc.ProgrammingError as e:
        print(e)
    model.Session.commit()

    sql_upgrade_01 = (
        "ALTER TABLE ckanext_yammer_user add column publish_date timestamp;",
        "ALTER TABLE ckanext_yammer_user add column user_type Text;",
        "UPDATE ckanext_yammer_user set user_type = 'user';",
    )

    conn = model.Session.connection()
    try:
        for statement in sql_upgrade_01:
            conn.execute(statement)
    except sa.exc.ProgrammingError:
        pass
    model.Session.commit()

    sql_upgrade_02 = ('ALTER TABLE ckanext_yammer_user add column extras Text;',
                      "UPDATE ckanext_yammer_user set extras = '{}';")

    conn = model.Session.connection()
    try:
        for statement in sql_upgrade_02:
            conn.execute(statement)
    except sa.exc.ProgrammingError:
        pass
    model.Session.commit()

    types = sa.types
    global frontpage_table
    yammer_user_table = sa.Table('ckanext_yammer_user', model.meta.metadata,
        sa.Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
        sa.Column('name', types.UnicodeText, nullable=False),
        sa.Column('token', types.UnicodeText),
        sa.Column('groups', ARRAY(types.Integer)),
        sa.Column('create', types.Boolean),
        sa.Column('update', types.Boolean),
        sa.Column('delete', types.Boolean),
        extend_existing=True
    )

    model.meta.mapper(
        Yammer_user,
        yammer_user_table,
    )


def table_dictize(obj, context, **kw):
    '''Get any model object and represent it as a dict'''
    result_dict = {}

    if isinstance(obj, RowProxy):
        fields = obj.keys()
    else:
        ModelClass = obj.__class__
        table = class_mapper(ModelClass).mapped_table
        fields = [field.name for field in table.c]

    for field in fields:
        name = field
        if name in ('current', 'expired_timestamp', 'expired_id'):
            continue
        if name == 'continuity_id':
            continue
        value = getattr(obj, name)
        if name == 'extras' and value:
            result_dict.update(json.loads(value))
        elif value is None:
            result_dict[name] = value
        elif isinstance(value, dict):
            result_dict[name] = value
        elif isinstance(value, int):
            result_dict[name] = value
        elif isinstance(value, datetime.datetime):
            result_dict[name] = value.isoformat()
        elif isinstance(value, list):
            result_dict[name] = value
        else:
            result_dict[name] = unicode(value)

    result_dict.update(kw)

    ##HACK For optimisation to get metadata_modified created faster.

    context['metadata_modified'] = max(result_dict.get('revision_timestamp', ''),
                                       context.get('metadata_modified', ''))

    return result_dict