import scrapy
from hello.items import HelloItem


class HelloSpider(scrapy.Spider):
    name = "hello"
    allowed_domains = ["stackoverflow.com"]
    start_urls = [
        "http://stackoverflow.com/questions?pagesize=50&sort=newest",
    ]

    def parse(self, response):
        questions = response.xpath('//div[@class="summary"]/h3')

        for question in questions:
            item = HelloItem()
            item['title'] = question.xpath('a[@class="question-hyperlink"]/text()').extract()[0]
            item['url'] = question.xpath('a[@class="question-hyperlink"]/@href').extract()[0]
            yield item
