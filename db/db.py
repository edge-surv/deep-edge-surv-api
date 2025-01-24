from tinydb import Query, TinyDB

db = TinyDB('db.json')
# tables
camera_table = db.table('cameras')
settings_table = db.table('settings')
storage_table = db.table('storage')

# query
DBQuery = Query()
