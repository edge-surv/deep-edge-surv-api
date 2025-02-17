from tinydb import Query, TinyDB

db = TinyDB('db.json')
# tables
camera_table = db.table('cameras')
settings_table = db.table('settings')
camera_config_table = db.table('camera_config')
logs_table = db.table('logs')

# query
DBQuery = Query()
