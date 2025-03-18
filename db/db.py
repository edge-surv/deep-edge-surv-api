from tinydb import Query, TinyDB

db = TinyDB("db.json")
# tables
camera_table = db.table("cameras")
camera_settings_table = db.table("camera_settings")
camera_config_table = db.table("camera_config")
camera_zones_table = db.table("camera_zones")
logs_table = db.table("logs")
agents_table = db.table("agents")
users_table = db.table("users")
emails_details_table = db.table("email_details")
notifications_table = db.table("notifications")

# query
DBQuery = Query()
