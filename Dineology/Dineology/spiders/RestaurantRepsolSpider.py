import scrapy
from ..items import DineologyItemRepsol

class RestaurantRepsolSpider(scrapy.Spider):
    name = "RestaurantRepsolSpider"

    start_urls = ['https://guiarepsol.com/es/soles-repsol/ediciones-de-soles-guia-repsol/']

    def parse(self, response):
        for restaurant in response.css(''):  # Selecciona cada bloque de restaurante

            item = DineologyItemRepsol()
            item['name'] = ""
            item['direction'] = ""
            item['price'] = ""

            yield item

        # Follow the next page
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)  # Construir la URL completa
            yield scrapy.Request(next_page, callback=self.parse)