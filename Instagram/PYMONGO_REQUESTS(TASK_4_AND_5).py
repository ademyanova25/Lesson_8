from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['Library']
instagram = db.insta_spider.instagram

# 4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
for i in instagram.find({'$and': [{'username': 'y_practicum'}, {'type': 'followers'}]}):
    pprint(i)

# 5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
for i in instagram.find({'$and': [{'username': 'y_practicum'}, {'type': 'following'}]}):
    pprint(i)
