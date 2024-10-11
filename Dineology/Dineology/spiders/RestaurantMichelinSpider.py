import scrapy
from ..items import DineologyItem

class RestaurantMichelinSpider(scrapy.Spider):
    name = "RestaurantMichelinSpider"

    start_urls = ['https://guide.michelin.com/es/es/comunidad-de-madrid/restaurantes']

    def parse(self, response):
        for restaurant in response.css('div.card__menu-content'):  # Selecciona cada bloque de restaurante
            item = DineologyItem()

            # Limpia el nombre del restaurante
            item['name'] = restaurant.css('h3.card__menu-content--title a::text').get().strip()

            # Limpia la dirección (si contiene varios fragmentos, puedes concatenarlos)
            item['direction'] = restaurant.css('div.card__menu-footer--score.pl-text::text').get().strip()

            # Extrae solo el precio, limpiando los saltos de línea y espacios adicionales
            price_parts = restaurant.css('div.card__menu-footer--score.pl-text::text').getall()
            item['price'] = price_parts[0].strip() if price_parts else ''

            yield item


    #Follow the next page
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)  # Construir la URL completa
            yield scrapy.Request(next_page, callback=self.parse)