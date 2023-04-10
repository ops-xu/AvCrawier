import js2xml
import scrapy
from ..redisPool.redisPool import redisPool
from pathlib import Path


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        with open(Path(__file__).resolve().parent.parent / 'config/scrapy_urls.txt', 'r') as file:
            content = file.read()
        for line in content.split('\n'):
            yield scrapy.Request(url=line.rstrip(), callback=self.parse)

    def parse(self, response):
        cards = response.xpath('//*[@id="waterfall"]/div/a')
        for card in cards:
            high = card.xpath('.//div[2]/span/div/button[2]')
            av = card.xpath('.//div[2]/span/date[1]/text()').get()
            if high.get() is None:
                continue

            if redisPool.getConn().sadd('ids', av) == 0:
                continue
            link = card.xpath('@href')
            yield from response.follow_all(link, self.parse_pikpak)

        pagination_links = response.xpath('//*[@id="next"]')
        yield from response.follow_all(pagination_links, self.parse)

    def parse_pikpak(self, response):
        def extract_with_xpath(query):
            return response.xpath(query).get(default='').strip()

        add_params = {'name': extract_with_xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')}

        script = response.xpath('/html/body/script[3]/text()').get()
        src_text = js2xml.parse(script)
        gid = src_text.xpath("//program/var[@name='gid']/number/@value")[0]
        uc = src_text.xpath("//program/var[@name='uc']/number/@value")[0]

        yield scrapy.Request('https://www.buscdn.me/ajax/uncledatoolsbyajax.php?lang=zh&gid=' + gid + '&uc=' + uc,
                             headers={"referer": response.request.url}, callback=self.parse_magnet,
                             cb_kwargs=add_params)

    def parse_magnet(self, response, name):
        for magnet in response.xpath('//tr'):
            if magnet.xpath('.//td[1]/a[2]').get() is not None and magnet.xpath('.//td[1]/a[3]').get() is not None:
                href = magnet.xpath('.//td[1]/a[1]/@href').get()
                yield {
                    'name': name,
                    'magnet': href,
                }
                break
