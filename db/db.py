from tinydb import Query, TinyDB

db = TinyDB('db.json')
# tables
camera_table = db.table('cameras')
settings_table = db.table('settings')

# query
DBQuery = Query()
