# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime, timedelta
import pymongo
from pymongo import MongoClient, ASCENDING


class PBPipeline:

    collection_name = 'pull&bear'
    ttl_field = 'expiration_date'  # Field to set TTL

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod

    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )
    
    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[self.collection_name].create_index([(self.ttl_field, ASCENDING)], expireAfterSeconds=0)  # Creating TTL index
        self.db[self.collection_name].create_index([("url_producto", 1)], unique=True)

    
        # self.db[self.collection_name].delete_many({})


    def close_spider(self, spider):
        self.client.close()
    

    def process_item(self, item, spider):
        expiration_time = datetime.utcnow() + timedelta(minutes=2)  # Set expiration time (e.g., 4 hours from now)
        item['expiration_date'] = expiration_time  
        item.setdefault('_id', item['url_producto'])

        self.db[self.collection_name].replace_one({'url_producto': item['url_producto']}, dict(item), upsert=True)

        return item




 
