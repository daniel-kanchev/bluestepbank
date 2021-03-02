import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bluestepbank.items import Article


class BluestepbankSpider(scrapy.Spider):
    name = 'bluestepbank'
    start_urls = ['https://www.bluestepbank.com/press/press-releases/']

    def parse(self, response):
        articles = response.xpath('//a[@class="Link--wrapper Grid Grid--fit"]')
        for article in articles:
            link = article.xpath('./@href').get()
            date = article.xpath('.//i/text()').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="Pager-link Pager-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//article//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
