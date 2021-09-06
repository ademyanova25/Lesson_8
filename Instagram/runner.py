from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from Instagram import settings
from Instagram.spiders.instagram import InstagramSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(crawler_settings)
    process.crawl(InstagramSpider)

    process.start()
