from elasticsearch import Elasticsearch
from pymongo import MongoClient
import time

# Conexiones
es = Elasticsearch(['http://localhost:9200'])
client = MongoClient('mongodb+srv://jesusdediossanchez:Y2vwkp89iFv8d7qk@clusterjdds.pbckg.mongodb.net/')
db = client['practica2']
productos_collection = db['productos']

# Datos de prueba
productos = [
    {"nombre": "Libro de Elasticsearch", "precio": 25.99, "categoria": "libros"},
    {"nombre": "Portátil", "precio": 999.99, "categoria": "tecnología"},
    {"nombre": "Auriculares", "precio": 49.99, "categoria": "tecnología"}
]

# Variables para almacenar los tiempos
es_times = []
mongo_times = []

def insertar_datos():
    print("\n=== Insertando datos ===")
    
    # Elasticsearch
    start_time = time.time()
    for i, doc in enumerate(productos, 1):
        es.index(index='productos', id=i, document=doc)
    es_time = time.time() - start_time
    es_times.append(es_time)
    print(f"Elasticsearch: {es_time:.4f} segundos")
    
    # PyMongo
    start_time = time.time()
    productos_collection.insert_many(productos)
    mongo_time = time.time() - start_time
    mongo_times.append(mongo_time)
    print(f"PyMongo: {mongo_time:.4f} segundos")

def busqueda_simple():
    print("\n=== Búsqueda simple (todos los productos) ===")
    
    # Elasticsearch
    start_time = time.time()
    es_result = es.search(index="productos", body={"query": {"match_all": {}}})
    es_time = time.time() - start_time
    es_times.append(es_time)
    print(f"Elasticsearch encontró {len(es_result['hits']['hits'])} documentos en {es_time:.4f} segundos")
    
    # PyMongo
    start_time = time.time()
    mongo_result = list(productos_collection.find())
    mongo_time = time.time() - start_time
    mongo_times.append(mongo_time)
    print(f"PyMongo encontró {len(mongo_result)} documentos en {mongo_time:.4f} segundos")

def busqueda_por_categoria():
    print("\n=== Búsqueda por categoría (tecnología) ===")
    
    # Elasticsearch
    start_time = time.time()
    es_result = es.search(index="productos", body={
        "query": {
            "match": {
                "categoria": "tecnología"
            }
        }
    })
    es_time = time.time() - start_time
    es_times.append(es_time)
    print(f"Elasticsearch encontró {len(es_result['hits']['hits'])} documentos en {es_time:.4f} segundos")
    
    # PyMongo
    start_time = time.time()
    mongo_result = list(productos_collection.find({"categoria": "tecnología"}))
    mongo_time = time.time() - start_time
    mongo_times.append(mongo_time)
    print(f"PyMongo encontró {len(mongo_result)} documentos en {mongo_time:.4f} segundos")

def busqueda_por_rango_precio():
    print("\n=== Búsqueda por rango de precio (20-100) ===")
    
    # Elasticsearch
    start_time = time.time()
    es_result = es.search(index="productos", body={
        "query": {
            "range": {
                "precio": {
                    "gte": 20,
                    "lte": 100
                }
            }
        }
    })
    es_time = time.time() - start_time
    es_times.append(es_time)
    print(f"Elasticsearch encontró {len(es_result['hits']['hits'])} documentos en {es_time:.4f} segundos")
    
    # PyMongo
    start_time = time.time()
    mongo_result = list(productos_collection.find({
        "precio": {
            "$gte": 20,
            "$lte": 100
        }
    }))
    mongo_time = time.time() - start_time
    mongo_times.append(mongo_time)
    print(f"PyMongo encontró {len(mongo_result)} documentos en {mongo_time:.4f} segundos")

def busqueda_compleja():
    print("\n=== Búsqueda compleja (tecnología entre 0-500€ ordenado por precio) ===")
    
    # Elasticsearch
    start_time = time.time()
    es_result = es.search(index="productos", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"categoria": "tecnología"}},
                    {"range": {
                        "precio": {
                            "gte": 0,
                            "lte": 500
                        }
                    }}
                ]
            }
        },
        "sort": [
            {"precio": "asc"}
        ]
    })
    es_time = time.time() - start_time
    es_times.append(es_time)
    print(f"Elasticsearch encontró {len(es_result['hits']['hits'])} documentos en {es_time:.4f} segundos")
    
    # PyMongo
    start_time = time.time()
    mongo_result = list(productos_collection.find({
        "categoria": "tecnología",
        "precio": {
            "$gte": 0,
            "$lte": 500
        }
    }).sort("precio", 1))
    mongo_time = time.time() - start_time
    mongo_times.append(mongo_time)
    print(f"PyMongo encontró {len(mongo_result)} documentos en {mongo_time:.4f} segundos")

def mostrar_resultados(titulo, resultados):
    print(f"\n=== {titulo} ===")
    for doc in resultados:
        print(doc)

if __name__ == "__main__":
    try:
        # Limpiar datos existentes
        es.indices.delete(index='productos', ignore=[400, 404])
        productos_collection.delete_many({})
        
        # Ejecutar pruebas
        insertar_datos()
        time.sleep(1)  # Dar tiempo a Elasticsearch para indexar
        
        print("\n=== Iniciando pruebas de rendimiento ===")
        busqueda_simple()
        busqueda_por_categoria()
        busqueda_por_rango_precio()
        busqueda_compleja()
        
        # Calcular medias
        es_avg_time = sum(es_times) / len(es_times)
        mongo_avg_time = sum(mongo_times) / len(mongo_times)
        
        print("\n=== Resultados de rendimiento ===")
        print(f"Tiempo medio de Elasticsearch: {es_avg_time:.4f} segundos")
        print(f"Tiempo medio de PyMongo: {mongo_avg_time:.4f} segundos")
        
        if es_avg_time < mongo_avg_time:
            print("Elasticsearch es más rápido en promedio.")
        else:
            print("PyMongo es más rápido en promedio.")
        
        # Mostrar algunos resultados de ejemplo
        print("\n=== Resultados de ejemplo ===")
        print("MongoDB - Productos de tecnología hasta 500€:")
        mongo_results = list(productos_collection.find({
            "categoria": "tecnología",
            "precio": {"$lte": 500}
        }))
        for doc in mongo_results:
            print(f"- {doc['nombre']}: {doc['precio']}€")
        
        print("\nElasticsearch - Productos de tecnología hasta 500€:")
        es_results = es.search(index="productos", body={
            "query": {
                "bool": {
                    "must": [
                        {"match": {"categoria": "tecnología"}},
                        {"range": {"precio": {"lte": 500}}}
                    ]
                }
            }
        })
        for hit in es_results['hits']['hits']:
            doc = hit['_source']
            print(f"- {doc['nombre']}: {doc['precio']}€")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Limpiar datos
        es.indices.delete(index='productos', ignore=[400, 404])
        productos_collection.delete_many({})