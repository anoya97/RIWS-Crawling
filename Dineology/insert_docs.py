import requests
import os
import json
from elasticsearch import Elasticsearch, exceptions
from geopy.distance import geodesic

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


# Función para obtener coordenadas usando Nominatim (con nombre o dirección)
def get_coordinates_nominatim(address_or_name):
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        "q": address_or_name,
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    headers = {
        "User-Agent": "Dineology r.delblanco@udc.es"
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        results = response.json()
        if results:
            lat = results[0]['lat']
            lon = results[0]['lon']
            return float(lat), float(lon)
    return None, None  # Si no se encuentran coordenadas


# Función para fusionar documentos
def merge_documents(doc1, doc2):
    merged_doc = doc1.copy()
    for key, value in doc2.items():
        if key not in merged_doc or not merged_doc[key]:
            merged_doc[key] = value
        elif isinstance(merged_doc[key], list) and isinstance(value, list):
            if all(isinstance(item, dict) for item in merged_doc[key]) and all(
                    isinstance(item, dict) for item in value):
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
            print(
                f"Advertencia: Campo con nombre vacío detectado en el documento {doc.get('name', 'sin nombre')} y será omitido.")
    return sanitized_doc

# Función para obtener un fragmento del nombre (1/3 de longitud)
def get_name_fragment(name):
    if name:
        fragment_length = max(1, len(name) // 3)  # Asegurarse de que el fragmento tenga al menos 1 carácter
        return name[:fragment_length].strip()
    return name

# Función para comparar la distancia entre dos ubicaciones
def are_locations_similar(lat1, lon1, lat2, lon2, max_distance_km=1.0):
    if None in [lat1, lon1, lat2, lon2]:
        return False
    location1 = (lat1, lon1)
    location2 = (lat2, lon2)
    distance = geodesic(location1, location2).km
    return distance <= max_distance_km

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

                        # Obtener fragmento del nombre para la búsqueda
                        name_fragment = get_name_fragment(restaurant_name)

                        # Obtener las coordenadas para la dirección del restaurante
                        address = doc.get("direction")
                        lat, lon = None, None
                        if address:
                            # Primero intentamos obtener las coordenadas usando la dirección
                            lat, lon = get_coordinates_nominatim(address)
                            if lat and lon:
                                doc['location'] = {'lat': lat, 'lon': lon}
                                print(f"Coordenadas encontradas usando la dirección: {address}")
                            else:
                                print(f"No se encontraron coordenadas para {restaurant_name}, dirección: {address}")
                                # Si no se encuentran, intentamos con el nombre del restaurante
                                lat, lon = get_coordinates_nominatim(restaurant_name)
                                if lat and lon:
                                    doc['location'] = {'lat': lat, 'lon': lon}
                                    print(f"Coordenadas encontradas usando el nombre: {restaurant_name}")
                                else:
                                    print(
                                        f"No se encontraron coordenadas ni con la dirección ni con el nombre para {restaurant_name}")

                        # Búsqueda con coincidencias flexibles usando un fragmento del nombre
                        query = {
                            "query": {
                                "match_phrase_prefix": {
                                    "name": {
                                        "query": name_fragment
                                    }
                                }
                            },
                            "min_score": 2.0  # Ajuste del umbral de similitud
                        }
                        result = es.search(index=index_name, body=query)

                        if result["hits"]["total"]["value"] > 0:
                            # Obtener el primer documento existente coincidente
                            existing_doc = result["hits"]["hits"][0]["_source"]
                            existing_doc_id = result["hits"]["hits"][0]["_id"]

                            # Verificar si tienen coordenadas y si las ubicaciones son similares
                            existing_location = existing_doc.get("location", {})
                            existing_lat = existing_location.get("lat")
                            existing_lon = existing_location.get("lon")

                            if lat and lon and are_locations_similar(lat, lon, existing_lat, existing_lon):
                                merged_doc = merge_documents(existing_doc, doc)
                                es.index(index=index_name, id=existing_doc_id, body=merged_doc)
                                print(
                                    f"Documento de {restaurant_name} fusionado y actualizado con ID {existing_doc_id}")
                            else:
                                es.index(index=index_name, body=doc)
                                print(
                                    f"Documento de {restaurant_name} indexado como nuevo porque las ubicaciones no son similares")
                        else:
                            es.index(index=index_name, body=doc)
                            print(f"Documento de {restaurant_name} indexado")
                elif isinstance(data, dict):
                    data = sanitize_document(data)
                    restaurant_name = data.get("name")
                    if not restaurant_name:
                        continue

                    # Obtener fragmento del nombre para la búsqueda
                    name_fragment = get_name_fragment(restaurant_name)

                    # Obtener las coordenadas para la dirección del restaurante
                    address = data.get("direction")
                    lat, lon = None, None
                    if address:
                        # Primero intentamos obtener las coordenadas usando la dirección
                        lat, lon = get_coordinates_nominatim(address)
                        if lat and lon:
                            data['location'] = {'lat': lat, 'lon': lon}
                            print(f"Coordenadas encontradas usando la dirección: {address}")
                        else:
                            print(f"No se encontraron coordenadas para {restaurant_name}, dirección: {address}")
                            # Si no se encuentran, intentamos con el nombre del restaurante
                            lat, lon = get_coordinates_nominatim(restaurant_name)
                            if lat and lon:
                                data['location'] = {'lat': lat, 'lon': lon}
                                print(f"Coordenadas encontradas usando el nombre: {restaurant_name}")
                            else:
                                print(
                                    f"No se encontraron coordenadas ni con la dirección ni con el nombre para {restaurant_name}")

                    query = {
                        "query": {
                            "match_phrase_prefix": {
                                "name": {
                                    "query": name_fragment
                                }
                            },
                            "min_score": 2.0
                        }
                    }
                    result = es.search(index=index_name, body=query)

                    if result["hits"]["total"]["value"] > 0:
                        existing_doc = result["hits"]["hits"][0]["_source"]
                        existing_doc_id = result["hits"]["hits"][0]["_id"]

                        existing_location = existing_doc.get("location", {})
                        existing_lat = existing_location.get("lat")
                        existing_lon = existing_location.get("lon")

                        if lat and lon and are_locations_similar(lat, lon, existing_lat, existing_lon):
                            merged_doc = merge_documents(existing_doc, data)
                            es.index(index=index_name, id=existing_doc_id, body=merged_doc)
                            print(f"Documento de {restaurant_name} fusionado y actualizado con ID {existing_doc_id}")
                        else:
                            es.index(index=index_name, body=data)
                            print(
                                f"Documento de {restaurant_name} indexado como nuevo porque las ubicaciones no son similares")
        except json.JSONDecodeError:
            print(f"Error: El archivo {filename} no tiene formato JSON válido y será omitido.")
        except Exception as e:
            print(f"Error inesperado al indexar {filename}: {e}")
print("Proceso de indexación completado.")
