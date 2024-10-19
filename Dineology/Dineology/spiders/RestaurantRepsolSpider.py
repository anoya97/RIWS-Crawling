import scrapy
from ..items import DineologyItemRepsol

class RestaurantRepsolSpider(scrapy.Spider):
    name = "RestaurantRepsolSpider"

    start_urls = ['https://guiarepsol.com/es/soles-repsol/ediciones-de-soles-guia-repsol/']

    def parse(self, response):
        for restaurant in response.css('li.col-6.col-sm-4.col-md-3'):  # Selecciona cada bloque de restaurante

            detail_page = restaurant.css('a::attr(href)').get()
            detail_page_url = response.urljoin(detail_page)

            yield scrapy.Request(detail_page_url, callback=self.parse_detail_page)


    def parse_detail_page(self, response):
        item = DineologyItemRepsol()

        item['name'] = response.css('div.hero__ficha__main h1::text').get().strip()

        number_soles = response.css('div.badge__data span.badge__category::text').get()

        item['soles_number'] = int(number_soles.replace("soles","").replace("sol","").replace("Recomendado","0"))

        item['description'] = response.css('div.description-block p::text').get().strip()

        item['short_menu_description'] = response.css('section.list-info-component p::text').get()

        # Hay que seguir a partir de aquí.
        menu_option_list = response.css('li.list__info__item')

        menu_options = []
        # [Nombre, descripción, precio]
        for menu_option in menu_option_list:
            # Captura el nombre de la opción del menú (dentro de un span.title__item)
            name = menu_option.css('span.title__item *::text').getall()
            name = ' '.join([n.strip() for n in name if n.strip()])  # Limpiar y unir el texto

            # Captura el precio directamente del span que lo contiene
            price = menu_option.css('div.header__item span:nth-child(2)::text').get()  # Segundo span contiene el precio
            if price:
                price = price.strip()  # Asegúrate de que no haya espacios adicionales

            description = menu_option.css('p.description__item::text').get()
            description = description.strip() if description else ''

            menu_options.append({
                'name': name,
                'price': price,
                'description': description
            })

        item['menu_options'] = menu_options

        servicios = response.css('ul.service__list li.service__list__item span.rp-body-1.info::text').getall()
        item['restaurant_services'] = [servicio.strip() for servicio in servicios]

        owners = response.xpath('//span[contains(text(), "Propietario")]/following-sibling::span/span/text()').getall()
        item['owners_name'] = []
        for i, owner in enumerate(owners):
            cleaned_owner = owner.strip()  # Quitar espacios en blanco

            # Quitar la coma si es el primer elemento
            if i == 0 and cleaned_owner.endswith(','):
                cleaned_owner = cleaned_owner[:-1]  # Quitar la última coma

            item['owners_name'].append(cleaned_owner)

        item['web_url'] = response.xpath('//li[div/span[contains(text(), "Web")]]/a/@href').get()


        user = response.xpath('//span[contains(text(), "Instagram")]/following-sibling::p/text()').get()

        if user.startswith("@"):
             item['instagram_user'] = user
        else:
            item['instagram_user'] = '@' + user.rstrip('/').split('/')[-1]

        item['contact_number'] = response.xpath('//li[@class="basic__list__item"]//span[contains(text(), "Teléfono")]/following-sibling::p/text()').get()

        item['direction'] = response.xpath('//li[@class="basic__list__item"]//span[contains(text(), "Ubicación")]/following-sibling::p/text()').get()

        item['restaurant_photo_url'] = 'https:://guiarepsol.com' + response.css('div.listado-imagenes div::attr(data-path)').get()


        meals = response.xpath('//span[contains(text(), "Tipo de cocina")]/following-sibling::span/span/text()').getall()
        item['meal_type'] = []
        for i, meal in enumerate(meals):
            cleaned_meal = meal.strip()  # Quitar espacios en blanco

            # Quitar la coma si es el primer elemento
            if i == 0 and cleaned_meal.endswith(','):
                cleaned_meal = cleaned_meal[:-1]  # Quitar la última coma

            item['meal_type'].append(cleaned_meal)
            yield item

