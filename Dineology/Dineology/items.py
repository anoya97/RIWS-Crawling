# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class DineologyItemMichelin(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    direction = scrapy.Field()
    price = scrapy.Field()
    meal_type = scrapy.Field()
    star_number = scrapy.Field()
    description = scrapy.Field()
    contact_number = scrapy.Field()
    working_schedule = scrapy.Field()
    restaurant_photo_url = scrapy.Field()
    web_url = scrapy.Field()

    pass

class DineologyItemRepsol(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    soles_number = scrapy.Field()
    description = scrapy.Field()
    short_menu_description = scrapy.Field()
    menu_options = scrapy.Field()
    restaurant_services =  scrapy.Field()
    owners_name = scrapy.Field()
    web_url = scrapy.Field()
    instagram_user = scrapy.Field()
    contact_number = scrapy.Field()
    restaurant_photo_url = scrapy.Field()
    direction = scrapy.Field()
    meal_type = scrapy.Field()

    pass
