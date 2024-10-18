# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json


class DineologyJsonPipeline:
    def open_spider(self, spider):
        self.file = open('dineology.json', 'w', encoding='utf-8')
        self.file.write('[')
        self.first_item = True  # Check if is first

    def close_spider(self, spider):
        self.file.write(']\n')
        self.file.close()

    def process_item(self, item, spider):
        # Reemplazar la ñ por n y caracteres especiales en dirección
        # item['direction'] = item['direction'].replace('ñ', 'n').replace('Ñ', 'N')

        # Limpiar cada campo del item antes de escribirlo
        item = {key: value.strip() if isinstance(value, str) else value for key, value in item.items()}

        if not self.first_item:
            self.file.write(',\n')
        self.first_item = False

        # Escribir el item formateado
        line = json.dumps(dict(item), indent=4, ensure_ascii=False)  # UTF-8 friendly JSON output
        self.file.write(line)

        return item

