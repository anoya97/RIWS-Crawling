from elasticsearch import Elasticsearch

es = Elasticsearch(hosts=["http://localhost:9200"])

# Comprueba si el clúster está activo
if es.ping():
    print("Conexión exitosa a Elasticsearch")
else:
    print("No se pudo conectar a Elasticsearch")