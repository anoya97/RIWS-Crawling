import re

import scrapy
from ..items import DineologyItemMichelin


class RestaurantMichelinSpider(scrapy.Spider):
    name = "RestaurantMichelinSpider"

    # Esta URL mejor que la que está puesta: https://guide.michelin.com/es/es/restaurantes/restaurantes-con-estrellas
    # Dejo esta porque así lo podemos ver nosotros mejor porque se ordena por ubicación
    start_urls = ['https://guide.michelin.com/es/es/comunidad-de-madrid/restaurantes']

    def parse(self, response):
        for restaurant in response.css('div.card__menu'):  # Selecciona cada bloque de restaurante
            item = DineologyItemMichelin()

            # Limpia el nombre del restaurante
            item['name'] = restaurant.css('h3.card__menu-content--title a::text').get().strip()

            # Limpia la dirección (si contiene varios fragmentos, puedes concatenarlos)
            item['direction'] = restaurant.css('div.card__menu-footer--score.pl-text::text').get().strip()

            # Extrae solo el precio, limpiando los saltos de línea y espacios adicionales
            price_parts = restaurant.css('div.card__menu-footer--score.pl-text::text').getall()
            item['price'] = price_parts[1].strip().split('·')[0].strip()
            item['meal_type'] = price_parts[1].strip().split('·')[1].strip()

            detail_page = restaurant.css('div.card__menu-image a::attr(href)').get()
            detail_page_url = response.urljoin(detail_page)
            yield scrapy.Request(detail_page_url, callback=self.parse_detail_page, meta={'item': item})



        #Follow the next page
        # Obtener todos los enlaces a páginas siguientes
        # HAY QUE CAMBIAR NEXT POR ARROW, ESTÁ ASÍ PARA QUE NO COJA TANTAS PÁGINAS DE GOLPE Y PODAMOS PROBAR CON UNAS POCAS SOLO
        next_pages = response.css('li.next a::attr(href)').getall()

        # Extraer el número actual de la página de la URL
        current_page_number = self.extract_current_page_number(response.url)

        # Calcular el número de la siguiente página
        next_page_number = current_page_number + 1

        # Filtrar y seguir el enlace correcto
        for link in next_pages:
            if f'page/{next_page_number}' in link:
                next_page_url = response.urljoin(link)  # Construir la URL completa
                yield scrapy.Request(next_page_url, callback=self.parse)


    def extract_current_page_number(self, url):
        # Extraer el número de página actual de la URL
        match = re.search(r'page/(\d+)', url)
        return int(match.group(1)) if match else 1  # Devuelve 1 si no se encuentra el número de página


    def parse_detail_page(self, response):

        item = response.meta['item']

        item['restaurant_photo_url'] = response.css('div.masthead__gallery-image::attr(data-bg)').get()
        # item['restaurant_photo_url'] = response.css('img.ci-image .lazyload .entered .ci-image-loaded .loaded::attr(ci-src)').get()

        item['star_number'] = response.css('div.restaurant-details__classification img.michelin-award').getall()
        print(item['star_number'])


        item['description'] = ''
        item['contact_number'] = ''
        item['working_hours'] = ''

        yield item