from sqlalchemy import Column, BigInteger
import sqlalchemy.dialects.postgresql
import sqlalchemy.ext.mutable

def JSONB():
    return sqlalchemy.ext.mutable.MutableDict.as_mutable(
        sqlalchemy.dialects.postgresql.JSONB)

reserved_names = '_sa_instance_state', 'ATTRS', 'id'
class Object:

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
    ATTRS = sqlalchemy.Column(JSONB())

    def __init__(self):
        self.ATTRS = {}

    def __getattr__(self, name):
        if name in reserved_names:
            raise AttributeError(name)

        return self.ATTRS[name]

    def __setattr__(self, name, v):
        if name in reserved_names:
            return super().__setattr__(name, v)

        self.ATTRS[name] = v

    def json_reduce(self):
        data = self.ATTRS.copy()
        data['id'] = self.id
        return data
