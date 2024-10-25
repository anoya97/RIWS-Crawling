import os
import json
from elasticsearch import Elasticsearch

# Conexión con Elasticsearch en localhost
es = Elasticsearch(hosts=["http://localhost:9200"])

# Directorio donde están los archivos JSON
json_directory = "."

# Recorre cada archivo en el directorio
doc_id = 1  # Contador global para IDs únicos
for filename in os.listdir(json_directory):
    # Solo procesa archivos JSON
    if filename.endswith(".json"):
        filepath = os.path.join(json_directory, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                # Carga el contenido del archivo JSON
                data = json.load(file)
                # Verifica si el archivo JSON contiene una lista de objetos
                if isinstance(data, list):
                    # Si es una lista, indexa cada objeto individualmente
                    for doc in data:
                        es.index(index="restaurants", id=doc_id, body=doc)
                        print(f"Documento en {filename} indexado con ID {doc_id}")
                        doc_id += 1
                elif isinstance(data, dict):
                    # Si es un solo objeto, lo indexa directamente
                    es.index(index="restaurants", id=doc_id, body=data)
                    print(f"Documento en {filename} indexado con ID {doc_id}")
                    doc_id += 1
                else:
                    print(f"Formato no soportado en {filename}. Se espera un objeto o una lista.")
        except json.JSONDecodeError:
            print(f"Error: El archivo {filename} no tiene formato JSON válido y será omitido.")
        except Exception as e:
            print(f"Error inesperado al indexar {filename}: {e}")

print("Proceso de indexación completado.")
