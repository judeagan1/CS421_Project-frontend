import pymongo
import json
import pprint
import os

os.system('mongod --dbpath=./db &')

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
coll = db['events']

coll.insert_one(json.loads('{ "_id" : ObjectId("5f04915147caaad6aeab754c"), "id" : "1", "event" : { "timestamp" : "2020-7-7T15:14:24Z", "humdity" : 79, "temperature" : 26, "hostname" : "04:83:d0:00" } }'))
pprint.pprint(coll.find_one({"timestamp" : "2020-7-7T15:14:24Z"}))
