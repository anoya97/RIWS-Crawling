import os
import json
from elasticsearch import Elasticsearch, exceptions
import Levenshtein

# Conexión con Elasticsearch en localhost
es = Elasticsearch(hosts=["http://localhost:9200"])

# Crear el índice 'restaurants' si no existe
index_name = "restaurants"
if not es.indices.exists(index=index_name):
    try:
        es.indices.create(index=index_name)
        print(f"Índice '{index_name}' creado.")
    except exceptions.ElasticsearchException as e:
        print(f"Error al crear el índice '{index_name}': {e}")

# Función para fusionar documentos
def merge_documents(doc1, doc2):
    merged_doc = doc1.copy()
    for key, value in doc2.items():
        if key not in merged_doc or not merged_doc[key]:
            merged_doc[key] = value
        elif isinstance(merged_doc[key], list) and isinstance(value, list):
            if all(isinstance(item, dict) for item in merged_doc[key]) and all(isinstance(item, dict) for item in value):
                merged_doc[key].extend(item for item in value if item not in merged_doc[key])
            else:
                merged_doc[key] = list(set(merged_doc[key] + value))
        elif isinstance(merged_doc[key], dict) and isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if sub_key not in merged_doc[key]:
                    merged_doc[key][sub_key] = sub_value
    return merged_doc

# Sanear documentos eliminando campos con nombres vacíos
def sanitize_document(doc):
    sanitized_doc = {}
    for key, value in doc.items():
        if key.strip():
            sanitized_doc[key] = value
        else:
            print(f"Advertencia: Campo con nombre vacío detectado en el documento {doc.get('name', 'sin nombre')} y será omitido.")
    return sanitized_doc

# Función para comprobar si hay otro restaurante con estrellas y sin soles
def check_similar_restaurant_with_stars(restaurant_name):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "name": {
                                "query": restaurant_name,
                                "fuzziness": "AUTO"  # Fuzziness automático para mayor flexibilidad
                            }
                        }
                    },
                    {
                        "exists": {
                            "field": "star_number"
                        }
                    },
                    {
                        "bool": {
                            "must_not": [
                                {
                                    "exists": {
                                        "field": "soles_number"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }

    result = es.search(index=index_name, body=query)
    return result["hits"]["hits"]

# Función para comprobar si la URL y dirección coinciden
def check_url_and_contact_equal(doc1, doc2):
    url1 = doc1.get("web_url")
    url2 = doc2.get("web_url")
    contact1 = doc1.get("contact_number")
    contact2 = doc2.get("contact_number")
    return url1 == url2 or contact1 == contact2

# Función para calcular la distancia de Levenshtein entre dos cadenas
def levenshtein_distance(str1, str2):
    return Levenshtein.distance(str1, str2)

# Umbrales de similitud para las distancias de Levenshtein
LEVENSHTEIN_THRESHOLD_NAME = 3
LEVENSHTEIN_THRESHOLD_DIRECTION = 3

# Directorio donde están los archivos JSON
json_directory = "."

# Recorre cada archivo en el directorio
for filename in os.listdir(json_directory):
    if filename.endswith(".json"):
        filepath = os.path.join(json_directory, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    for doc in data:
                        doc = sanitize_document(doc)
                        restaurant_name = doc.get("name")
                        if not restaurant_name:
                            continue

                        # Comprobar si hay otro restaurante con estrellas y sin soles
                        similar_restaurants = check_similar_restaurant_with_stars(restaurant_name)
                        merged = False  # Indicador de si se realizó una fusión
                        if similar_restaurants:
                            for existing_doc_hit in similar_restaurants:
                                existing_doc = existing_doc_hit["_source"]
                                existing_doc_id = existing_doc_hit["_id"]

                                # Comprobar si la URL y número de contacto coinciden
                                if check_url_and_contact_equal(doc, existing_doc):
                                    merged_doc = merge_documents(existing_doc, doc)
                                    es.index(index=index_name, id=existing_doc_id, body=merged_doc)
                                    merged = True
                                    break
                                else:
                                    # Comparar usando Levenshtein
                                    name_distance = levenshtein_distance(doc.get("name", ""), existing_doc.get("name", ""))
                                    direction_distance = levenshtein_distance(doc.get("direction", ""), existing_doc.get("direction", ""))
                                    if name_distance <= LEVENSHTEIN_THRESHOLD_NAME or direction_distance <= LEVENSHTEIN_THRESHOLD_DIRECTION:
                                        merged_doc = merge_documents(existing_doc, doc)
                                        es.index(index=index_name, id=existing_doc_id, body=merged_doc)
                                        merged = True
                                        break

                        if not merged:
                            es.index(index=index_name, body=doc)
                elif isinstance(data, dict):
                    data = sanitize_document(data)
                    restaurant_name = data.get("name")
                    if not restaurant_name:
                        continue

                    # Repetir el mismo flujo que para la lista
                    similar_restaurants = check_similar_restaurant_with_stars(restaurant_name)
                    merged = False
                    if similar_restaurants:
                        for existing_doc_hit in similar_restaurants:
                            existing_doc = existing_doc_hit["_source"]
                            existing_doc_id = existing_doc_hit["_id"]
                            if check_url_and_contact_equal(data, existing_doc):
                                merged_doc = merge_documents(existing_doc, data)
                                es.index(index=index_name, id=existing_doc_id, body=merged_doc)
                                merged = True
                                break
                            else:
                                name_distance = levenshtein_distance(data.get("name", ""), existing_doc.get("name", ""))
                                direction_distance = levenshtein_distance(data.get("direction", ""), existing_doc.get("direction", ""))
                                if name_distance <= LEVENSHTEIN_THRESHOLD_NAME or direction_distance <= LEVENSHTEIN_THRESHOLD_DIRECTION:
                                    merged_doc = merge_documents(existing_doc, data)
                                    es.index(index=index_name, id=existing_doc_id, body=merged_doc)
                                    merged = True
                                    break

                    if not merged:
                        es.index(index=index_name, body=data)
        except json.JSONDecodeError:
            print(f"Error: El archivo {filename} no tiene formato JSON válido y será omitido.")
        except Exception as e:
            print(f"Error inesperado al indexar {filename}: {e}")

print("Proceso de indexación completado.")
