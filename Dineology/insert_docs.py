import os
import json
from elasticsearch import Elasticsearch

# Conexión con Elasticsearch en localhost
es = Elasticsearch(hosts=["http://localhost:9200"])

# Directorio donde están los archivos JSON
json_directory = "."

doc1 = {
    "name": "Desde 1911",
    "price": "€€€€",
    "meal_type": "Pescados y mariscos"
}

doc2 = {
    "name": "Pito",
    "price": "Pito",
    "meal_type": "Pito"
}

doc3 = {
    "name": "PitoBrais",
    "price": "PitoBrais",
    "meal_type": "PitoBrais"
}

es.index(index="restaurants", id=1, body=doc1)
es.index(index="restaurants", id=2, body=doc2)
es.index(index="restaurants", id=3, body=doc3)


print("Datos indexados correctamente.")

