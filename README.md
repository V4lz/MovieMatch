# MovieMatch

Proyecto académico de bases de datos NoSQL implementado en Python.

## Estructura

- `src/mongodb/`: implementación de MongoDB.
- `src/dgraph/`: implementación de Dgraph.
- `src/cassandra/`: implementación de Cassandra.
- `src/chromadb/`: implementación de ChromaDB.
- `src/client/`: interfaz o cliente de MovieMatch.
- `data/`: datos compartidos para cargar en las bases.
- `tests/`: pruebas.
- `report/`: reporte final.
- `slides/`: presentación.

## Requisitos previos

- Python 3.10 o superior (ajustar según las dependencias elegidas).
- Docker y Docker Compose.
- Servicios de MongoDB, Dgraph y Cassandra; ChromaDB se ejecutará desde Python o según la configuración del equipo.

## Configuración inicial

1. Crear y activar un entorno virtual.
2. Instalar dependencias con `pip install -r requirements.txt`.
3. Copiar `.env.example` a `.env`.
4. Completar las variables de conexión en `.env`.
5. Configurar y levantar los servicios según `docker-compose.yml`.

## Trabajo en equipo

Antes de cargar datos, el equipo debe acordar y utilizar los mismos identificadores para las entidades compartidas en las cuatro bases de datos.

No subir archivos `.env`, credenciales, entornos virtuales ni datos privados al repositorio.
