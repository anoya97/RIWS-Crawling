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
        if key not in merged_doc or not merged_doc[key]:  # Si el campo no existe o está vacío
            merged_doc[key] = value
        elif isinstance(merged_doc[key], list) and isinstance(value, list):
            # Fusionar listas sin duplicados, manejando dicts si es necesario
            if all(isinstance(item, dict) for item in merged_doc[key]) and all(isinstance(item, dict) for item in value):
                # Para listas de diccionarios, evitar duplicados según un campo clave
                merged_doc[key].extend(item for item in value if item not in merged_doc[key])
            else:
                # Para listas simples
                merged_doc[key] = list(set(merged_doc[key] + value))
        elif isinstance(merged_doc[key], dict) and isinstance(value, dict):
            # Fusionar diccionarios (como el horario), priorizando el primero
            for sub_key, sub_value in value.items():
                if sub_key not in merged_doc[key]:
                    merged_doc[key][sub_key] = sub_value
    return merged_doc

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
                        restaurant_name = doc.get("name")
                        if not restaurant_name:
                            continue  # Si no tiene nombre, omitimos el documento

                        # Búsqueda en Elasticsearch para ver si ya existe un documento con ese nombre
                        query = {
                            "query": {
                                "match": {
                                    "name.keyword": restaurant_name  # Búsqueda exacta por nombre
                                }
                            }
                        }
                        result = es.search(index=index_name, body=query)

                        if result["hits"]["total"]["value"] > 0:
                            # Si ya existe un documento con ese nombre, lo fusionamos con el nuevo
                            existing_doc = result["hits"]["hits"][0]["_source"]
                            merged_doc = merge_documents(existing_doc, doc)
                            existing_doc_id = result["hits"]["hits"][0]["_id"]
                            es.index(index=index_name, id=existing_doc_id, body=merged_doc)
                            print(f"Documento de {restaurant_name} fusionado y actualizado con ID {existing_doc_id}")
                        else:
                            # Si no existe, indexamos el documento directamente
                            es.index(index=index_name, body=doc)
                            print(f"Documento de {restaurant_name} indexado")
                elif isinstance(data, dict):
                    restaurant_name = data.get("name")
                    if not restaurant_name:
                        continue

                    query = {
                        "query": {
                            "match": {
                                "name.keyword": restaurant_name
                            }
                        }
                    }
                    result = es.search(index=index_name, body=query)

                    if result["hits"]["total"]["value"] > 0:
                        existing_doc = result["hits"]["hits"][0]["_source"]
                        merged_doc = merge_documents(existing_doc, data)
                        existing_doc_id = result["hits"]["hits"][0]["_id"]
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
