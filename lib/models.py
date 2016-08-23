from peewee import *
from pprint import pprint
from time import time

import os
import sys
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
import config
import simplejson
import binascii

env = os.environ.get('SENTINEL_ENV') or 'production'
db_cfg = config.db[env]
dbname = db_cfg.pop('database')

db = MySQLDatabase(dbname, **db_cfg)

# === models ===

class BaseModel(Model):
    def get_dict(self):
      dikt = {}
      for field_name in self._meta.columns.keys():

        # don't include DB id
        if "id" == field_name:
            continue

        dikt[ field_name ] = getattr( self, field_name )
      return dikt

    class Meta:
      database = db


class PeeWeeGovernanceObject(BaseModel):
    #id = IntegerField(primary_key = True)
    parent_id = IntegerField()
    object_creation_time = IntegerField()
    object_hash = CharField()
    object_parent_hash = CharField()
    object_name = CharField()
    object_type = IntegerField()
    object_revision = IntegerField()
    object_data = TextField(default = '')
    object_fee_tx = CharField()

    class Meta:
      db_table = 'governance_object'

    @classmethod
    def object_with_name_exists(self, name):
        count = self.select().where(self.object_name == name).count()
        return count > 0

    def serialize_subclasses(self):
        objects = []

        for obj_type in self._meta.reverse_rel.keys():
            res = getattr( self, obj_type )
            if res:
              # should only return one row, but for completeness...
              for row in res:
                objects.append((obj_type, row.get_dict()))

        the_json = simplejson.dumps(objects, sort_keys = True)
        # print "the_json = %s" % the_json

        the_hex = binascii.hexlify( the_json )
        # print "the_hex = %s" % the_hex

        return the_hex

class PeeWeeAction(BaseModel):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(PeeWeeGovernanceObject, related_name = 'action')
    absolute_yes_count = IntegerField()
    yes_count = IntegerField()
    no_count = IntegerField()
    abstain_count = IntegerField()
    class Meta:
      db_table = 'action'

class PeeWeeEvent(BaseModel):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(PeeWeeGovernanceObject, related_name = 'event')
    start_time = IntegerField(default=int(time()))
    prepare_time = IntegerField()
    submit_time = IntegerField()
    error_time = IntegerField()
    error_message = CharField()
    class Meta:
      db_table = 'event'

class User(BaseModel):
    username = CharField(primary_key = True)
    userkey  = CharField()
    email    = CharField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    class Meta:
      db_table = 'users'

class Setting(BaseModel):
    #id = IntegerField(primary_key = True)
    datetime = IntegerField()
    setting  = CharField()
    name     = CharField()
    value    = CharField()
    class Meta:
      db_table = 'setting'

class PeeWeeProposal(BaseModel):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(PeeWeeGovernanceObject, related_name = 'proposal')
    proposal_name = CharField(unique=True)
    start_epoch = IntegerField()
    end_epoch = IntegerField()
    payment_address = CharField()
    payment_amount = DecimalField(max_digits=16, decimal_places=8)
    class Meta:
      db_table = 'proposal'

class PeeWeeSuperblock(BaseModel):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(PeeWeeGovernanceObject, related_name = 'superblock')
    superblock_name      = CharField() # unique?
    event_block_height   = IntegerField()
    payment_addresses    = TextField()
    payment_amounts      = TextField()
    class Meta:
      db_table = 'superblock'

# === /models ===

db.connect()
