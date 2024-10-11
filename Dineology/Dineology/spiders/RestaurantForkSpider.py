import scrapy
from ..items import DineologyItem

class RestaurantForkSpider(scrapy.Spider):
    name = "RestaurantForkSpider"

    start_urls = ['https://www.thefork.es/restaurantes/madrid-c328022/con-estrella-michelin-t4423']

    def parse(self, response):
        for restaurant in response.css(''):  # Selecciona cada bloque de restaurante

            item = DineologyItem()
            item['name'] = ""
            item['direction'] = ""
            item['price'] = ""

            yield item

        # Follow the next page
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)  # Construir la URL completa
            yield scrapy.Request(next_page, callback=self.parse)