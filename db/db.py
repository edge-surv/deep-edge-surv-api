from tinydb import Query, TinyDB

db = TinyDB('db.json')
# tables
camera_table = db.table('cameras')
camera_settings_table = db.table('camera_settings')
camera_config_table = db.table('camera_config')
camera_zones_table = db.table('camera_zones')
logs_table = db.table('logs')
agents_table = db.table('agents')

# query
DBQuery = Query()
