# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import datetime

# useful for handling different item types with a single interface
from .redisPool.redisPool import redisPool


class TutorialPipeline:
    file = None

    def open_spider(self, spider):
        self.file = open(str(datetime.date.today()) + '.txt', 'a', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        redisPool.getConn().sadd('ids', item['name'])
        self.file.write(item['magnet'])
        self.file.write('\n')
        return item
