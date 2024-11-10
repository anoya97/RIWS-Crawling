import os
import json
from elasticsearch import Elasticsearch, exceptions

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

                        # Búsqueda con coincidencias flexibles usando match_phrase_prefix
                        query = {
                            "query": {
                                "match_phrase_prefix": {
                                    "name": {
                                        "query": restaurant_name
                                    }
                                }
                            },
                            "min_score": 0.2  # Ajuste del umbral de similitud
                        }
                        result = es.search(index=index_name, body=query)

                        if result["hits"]["total"]["value"] > 0:
                            existing_doc = result["hits"]["hits"][0]["_source"]
                            existing_doc_id = result["hits"]["hits"][0]["_id"]
                            merged_doc = merge_documents(existing_doc, doc)
                            es.index(index=index_name, id=existing_doc_id, body=merged_doc)
                            print(f"Documento de {restaurant_name} fusionado y actualizado con ID {existing_doc_id}")
                        else:
                            es.index(index=index_name, body=doc)
                            print(f"Documento de {restaurant_name} indexado")
                elif isinstance(data, dict):
                    data = sanitize_document(data)
                    restaurant_name = data.get("name")
                    if not restaurant_name:
                        continue

                    query = {
                        "query": {
                            "match_phrase_prefix": {
                                "name": {
                                    "query": restaurant_name
                                }
                            },
                            "min_score": 2.0
                        }
                    }
                    result = es.search(index=index_name, body=query)

                    if result["hits"]["total"]["value"] > 0:
                        existing_doc = result["hits"]["hits"][0]["_source"]
                        existing_doc_id = result["hits"]["hits"][0]["_id"]
                        merged_doc = merge_documents(existing_doc, data)
                        es.index(index=index_name, id=existing_doc_id, body=merged_doc)
                        print(f"Documento de {restaurant_name} fusionado y actualizado con ID {existing_doc_id}")
                    else:
                        es.index(index=index_name, body=data)
                        print(f"Documento de {restaurant_name} indexado")
        except json.JSONDecodeError:
            print(f"Error: El archivo {filename} no tiene formato JSON válido y será omitido.")
        except Exception as e:
            print(f"Error inesperado al indexar {filename}: {e}")
print("Proceso de indexación completado.")
