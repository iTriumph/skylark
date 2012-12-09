"""
test code so far:
---------------------------------- test code -------------------
from mysqlorm import *

Database.config(db = "mydb", user = 'root', passwd = "123456", charset = "utf8")

class User(Model):
    username = Field()
    email = Field()

user = User.find(1)

print user._data

----------------------------------------------------------------

implemented APIs and Attributes

model_instance Model.create(**field_value)

list Model.fields

str Model.table_name

model_instance Model.find(key)

model_instance.save()



"""


import MySQLdb
import MySQLdb.cursors 

class Database:
    """class to manage Database connection"""

    configs = { # default configs for connection
            'host' : 'localhost' , # mysql host
            'port' : 3306 , # mysql port
            'db' : "" , # database name
            'user' : "" ,  # mysql user
            'passwd' : "" , # mysql passwd for user
            'charset' : "utf8"   # mysql connection charset, default set as utf8
            }

    conn = None # connection object of MySQLdb

    @classmethod
    def config(cls, **configs):
        cls.configs.update(configs)

    @classmethod
    def connect(cls):
        if not cls.conn or not cls.conn.open: # if not connected, new one, else use the exist
            cls.conn = MySQLdb.connect(cursorclass=MySQLdb.cursors.DictCursor, **cls.configs) 
        return cls.conn

    @classmethod
    def close(cls):
        cls.conn.close()

    @classmethod
    def get_con(cls):
        return cls.connect()

    @classmethod
    def query(cls, sql):
        cursor = Database.get_con().cursor()
        cursor.execute(sql)
        return cursor



class Field(object):

    def __init__(self, primarykey = False):
        self.name = None
        primarykey = False

    def __get__(self, instance, type = None):
        if instance:
            return instance._data[self.name]
        return self
    def __set__(self, instance, value):
        instance._data[self.name] = value


class PrimaryKey(Field):

    def __init__(self):
        self.primarykey = True


class MetaModel(type):

    def __init__(cls, name, bases , attrs):

        cls.table_name = cls.__name__.lower() 
        cls.primarykey = 'id'
        cls._data = {'id':None}

        for name, attr in cls.__dict__.iteritems():
            if isinstance(attr, Field):
                attr.name = name
                cls._data[name] = None
            if isinstance(attr, PrimaryKey):
                cls.primarykey = name
                cls._data.pop('id')
        cls.fields = cls._data.keys()


class Model(object):

    __metaclass__ = MetaModel

    def __init__(self, **attrs):
        self._data.update(attrs)

    def save(self):
        a = dict((x, y) for x, y in self._data.iteritems() if y) 
        self.__class__.insert(**a)

    @classmethod
    def join_fields(cls, d):
        return ", ".join([x+"='"+MySQLdb.escape_string(str(y))+"'" for x, y in d.iteritems()])

    @classmethod
    def insert(cls, dct):
        return Database.query("insert into "+cls.table_name+" set "+cls.join_fields(dct))

    @classmethod
    def select(cls):pass

    @classmethod
    def create(cls, **dct):
        cls.insert(dct)
        return cls(**dct)
    @classmethod
    def find(cls, key):
        dct = Database.query("select * from "+cls.table_name+" where "+cls.join_fields({cls.primarykey:key})).fetchone()
        return cls(**dct)