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
            name = menu_option.css('span.title__item::text').get().strip()
            price = menu_option.css('div.header__item span::text').re_first(r'\d+,\d{2}€')

            description = menu_option.css('p.description__item::text').get()
            description = description.strip() if description else ''

            menu_options.append({
                'name': name,
                'price': price,
                'description': description
            })

        item['menu_options'] = menu_options

        services_list = response.css('li.service__list__item').getall()
        services_totals = []
        for service in services_list:
            services_totals = services_totals.append(service.css('span.rp-body-1.info::text').get())
        item['restaurant_services'] = services_totals

        yield item
#     name
#     soles_number
#     description
#     short_menu_description
#     menu_options
#     restaurant_services
#     owners_name
#     web_url
#     instagram_user