from elasticsearch import Elasticsearch

# 1. Conectar a Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

# 2. Crear un índice (opcional, se crea automáticamente al insertar documentos)
index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "nombre": {"type": "text"},
            "precio": {"type": "float"},
            "categoria": {"type": "keyword"}
        }
    }
}

# Crear el índice
es.indices.create(index='productos_python', body=index_settings)

# 3. Insertar documentos
documentos = [
    {
        "nombre": "Libro de Elasticsearch de Python",
        "precio": 25.99,
        "categoria": "libros"
    },
    {
        "nombre": "Portátil",
        "precio": 999.99,
        "categoria": "tecnología"
    },
    {
        "nombre": "Auriculares",
        "precio": 49.99,
        "categoria": "tecnología"
    }
]

# Insertar documentos uno a uno
for i, doc in enumerate(documentos, 1):
    es.index(index='productos', id=i, document=doc)

# 4. Búsquedas básicas
# Buscar todos los documentos
def buscar_todos():
    resultado = es.search(index="productos", 
                         body={"query": {"match_all": {}}})
    return resultado['hits']['hits']

# Buscar por categoría
def buscar_por_categoria(categoria):
    query = {
        "query": {
            "match": {
                "categoria": categoria
            }
        }
    }
    resultado = es.search(index="productos", body=query)
    return resultado['hits']['hits']

# Buscar por rango de precios
def buscar_por_rango_precio(min_precio, max_precio):
    query = {
        "query": {
            "range": {
                "precio": {
                    "gte": min_precio,
                    "lte": max_precio
                }
            }
        }
    }
    resultado = es.search(index="productos", body=query)
    return resultado['hits']['hits']

# 5. Búsquedas avanzadas
def busqueda_compleja(categoria, min_precio, max_precio):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"categoria": categoria}},
                    {"range": {
                        "precio": {
                            "gte": min_precio,
                            "lte": max_precio
                        }
                    }}
                ]
            }
        },
        "sort": [
            {"precio": "asc"}
        ]
    }
    resultado = es.search(index="productos", body=query)
    return resultado['hits']['hits']

# 6. Ejemplos de uso
if __name__ == "__main__":
    # Buscar todos los productos
    print("\nTodos los productos:")
    for hit in buscar_todos():
        print(f"ID: {hit['_id']}, Producto: {hit['_source']}")

    # Buscar productos de tecnología
    print("\nProductos de tecnología:")
    for hit in buscar_por_categoria("tecnología"):
        print(f"ID: {hit['_id']}, Producto: {hit['_source']}")

    # Buscar productos entre 20 y 100 euros
    print("\nProductos entre 20 y 100 euros:")
    for hit in buscar_por_rango_precio(20, 100):
        print(f"ID: {hit['_id']}, Producto: {hit['_source']}")

    # Búsqueda compleja: tecnología entre 0 y 500 euros
    print("\nTecnología entre 0 y 500 euros:")
    for hit in busqueda_compleja("tecnología", 0, 500):
        print(f"ID: {hit['_id']}, Producto: {hit['_source']}")

# 7. Funciones de mantenimiento
def eliminar_indice():
    es.indices.delete(index='productos_python', ignore=[400, 404])

def obtener_estado_cluster():
    return es.cluster.health()

def obtener_estadisticas_indice():
    return es.indices.stats(index='productos_python')