# MovieMatch — Cassandra y Dgraph

Usa PowerShell desde la carpeta que contiene `docker-compose.yml`. Requisitos locales:
Python 3.11 o 3.12, Docker Desktop abierto y Git para subir tu rama.

## 1. Instala y levanta los motores

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-andrea.txt
docker compose up -d cassandra dgraph-zero dgraph-alpha
docker compose ps
docker compose logs --tail 25 cassandra dgraph-alpha
```

Cambia `-3.12` por `-3.11` si tienes Python 3.11. Guarda la ruta del intérprete en esta
variable de PowerShell para los siguientes comandos.

```powershell
$python = ".\.venv\Scripts\python.exe"
```

Cassandra puede tardar un par de minutos en abrir el puerto 9042. En sus logs busca
`Starting listening for CQL clients`. Verifica que Alpha responda con
`Invoke-RestMethod http://localhost:8080/health`. Si ya tienes contenedores de prácticas
usando los mismos puertos, detenlos antes de levantar MovieMatch. Para usar otro
puerto, cambia el mapeo de Compose y la variable correspondiente de `.env.example`.

## 2. Cassandra

```powershell
& $python -m src.cassandra.client setup
& $python -m src.cassandra.client seed
& $python -m src.cassandra.client seed
& $python -m src.cassandra.client demo
```

La segunda carga verifica los reintentos con el mismo UUID y fecha. La demo comprueba
11 eventos mensuales de `user_001`, 2 búsquedas en su partición de búsqueda y 3
actualizaciones de Inception en su partición de administración. Son datos de
prueba. Usa estos comandos para ver resultados pequeños y tomar capturas.

```powershell
& $python -m src.cassandra.client monthly --user user_001 --month 2026-11
& $python -m src.cassandra.client category --category searches
& $python -m src.cassandra.client title --movie movie_001 --day 2026-11-07 --event rating_updated
```

| Requisito | Consulta | Partición |
| --- | --- | --- |
| 01 | `monthly` | Usuario y mes |
| 02–07 | `category` con `ratings`, `searches`, `views`, `watchlist`, `favorites` o `clicks` | Usuario, mes y tipo de evento |
| 08 | `title` | Película, día y tipo de evento |

Cada evento usa un batch CQL para escribir sus copias con el mismo UUID y timestamp.
El día y mes se calculan en UTC. Las búsquedas ocupan solo las dos tablas de
usuario porque carecen de película. La interfaz debe restringir la consulta
por título a administradores.

### Ejemplos de filas cargadas

| Tabla | Clave de partición | Hora UTC | Tipo y datos |
| --- | --- | --- | --- |
| `activity_by_user_month` | `user_001 / 2026-11` | 16:41 | `rating_deleted`, `movie_004`, 4 → sin calificación |
| `activity_by_user_month` | `user_001 / 2026-11` | 16:40 | `search_submitted`, science fiction |
| `activity_by_user_month_type` | `user_001 / 2026-11 / search_submitted` | 16:40 | science fiction |
| `activity_by_user_month_type` | `user_001 / 2026-11 / search_submitted` | 16:30 | space travel |
| `activity_by_title_day_type` | `movie_001 / 2026-11-07 / rating_updated` | 16:42 | `user_003`, 3 → 4 |
| `activity_by_title_day_type` | `movie_001 / 2026-11-07 / rating_updated` | 16:34 | `user_002`, 4 → 5 |
| `activity_by_title_day_type` | `movie_001 / 2026-11-07 / rating_updated` | 16:33 | `user_001`, 3 → 5 |

## 3. Dgraph

```powershell
& $python -m src.dgraph.client setup
& $python -m src.dgraph.client seed
& $python -m src.dgraph.client seed
& $python -m src.dgraph.client demo
```

La demo comprueba que `user_002` y `user_003` comparten dos títulos con `user_001`,
que The Matrix queda primero con dos votos y que `Drama` devuelve The Shawshank
Redemption con un voto. También valida las relaciones inversas y los títulos de
las cuentas seguidas. Usa estas salidas para tus capturas.

```powershell
& $python -m src.dgraph.client similar --user user_001
& $python -m src.dgraph.client recommend --user user_001
& $python -m src.dgraph.client recommend --user user_001 --genre Drama
& $python -m src.dgraph.client reverse --user user_002 --genre Sci-Fi
& $python -m src.dgraph.client related --movie movie_001
& $python -m src.dgraph.client following --user user_001
```

| Requisito | Qué comprueba |
| --- | --- |
| 01 | Dgraph cuenta títulos compartidos calificados con 4 o 5 por ambos usuarios y exige al menos dos. |
| 02–05 | La variable `similar` alimenta las recomendaciones en la misma consulta. Dgraph excluye títulos ya calificados, cuenta votos, ordena por ese valor e incluye los usuarios y títulos compartidos de cada recomendación. |
| 06 | Dgraph encuentra los títulos del género por `~has_genre` y filtra las recomendaciones en el servidor. |
| 07–08 | Dgraph encuentra títulos relacionados por calificaciones altas y títulos de cuentas seguidas, respectivamente. `~follows` permite consultar seguidores. |

Las demos esperan los datos de prueba recién cargados. Ejecuta las demos antes de
mezclar sus usuarios y calificaciones con datos de la aplicación.

### Ejemplos de nodos y relaciones

| Origen | Relación | Destino |
| --- | --- | --- |
| Usuario `user_001` | `rated` con `score=5` | Inception (`movie_001`) |
| Usuario `user_001` | `rated` con `score=4` | Interstellar (`movie_002`) |
| Usuario `user_002` | `rated` con `score=5` | The Matrix (`movie_003`) |
| Usuario `user_003` | `rated` con `score=4` | The Matrix (`movie_003`) |
| Usuario `user_001` | `follows` | Usuario `user_002` |
| Usuario `user_003` | `follows` | Usuario `user_002` |
| Inception | `has_genre` | Género Sci-Fi |
| The Matrix | `has_genre` | Género Sci-Fi |
| The Shawshank Redemption | `has_genre` | Género Drama |

## 4. Conexión con el código del equipo

Desde la raíz del repositorio, el cliente común puede importar `MovieGraph`,
`ActivityStore`, `Event` y `connect` de los módulos indicados abajo. Usen los valores
de `_id` en `db.users` y `db.movies` y los nombres de género del arreglo `genres`.
En el catálogo del ZIP, `movie_001` es Inception y `movie_002` es Interstellar.

```python
from src.cassandra.client import ActivityStore, Event, connect
from src.dgraph.client import MovieGraph

graph = MovieGraph()
cluster = connect()
try:
    activity = ActivityStore(cluster.connect("moviematch"))

    # Project users and movies from MongoDB before saving graph edges.
    graph.save_user(user_doc["_id"])
    graph.save_title(movie_doc["_id"], movie_doc["title"], movie_doc["genres"])

    # The application prepares this event once when accepting a rating update.
    event = Event.create(
        user_doc["_id"], "rating_updated", movie_id=movie_doc["_id"],
        previous_rating=3, new_rating=5,
    )

    # After the MongoDB update succeeds, project the rating and save its history.
    graph.save_rating(event.user_id, event.movie_id, event.new_rating)
    activity.record(event)
finally:
    cluster.shutdown()
    graph.close()
```

Para eliminar una calificación, usa `graph.delete_rating(user_id, movie_id)` y registra
un `rating_deleted`. Para altas usa `rating_added`. La aplicación debe llamar a
`activity.record(event)` también para búsquedas, vistas de títulos, listas y clics.
Conserva el mismo objeto Event o el mismo UUID y timestamp si reintentas una escritura.
MongoDB, Dgraph y Cassandra son llamadas separadas. Si el cliente integra reintentos
después de fallos entre motores, debe conservar el evento pendiente hasta completar
ambas proyecciones. Los datos de ejemplo de Cassandra y Dgraph son independientes.

## 5. Sube tu parte a GitHub

En el repositorio del equipo, abre **Code → HTTPS** y copia la URL. Clónalo y crea
tu rama. Ejecuta los comandos desde el clon de Git.

```powershell
git clone URL_DEL_REPOSITORIO
cd MovieMatch
git switch -c andrea/cassandra-dgraph
```

Aplica `MovieMatch_Andrea.patch` desde la raíz del clon. La revisión previa te avisa
si el equipo cambió alguno de los mismos archivos desde el ZIP original.

```powershell
git apply --check "C:\ruta\MovieMatch_Andrea.patch"
git apply "C:\ruta\MovieMatch_Andrea.patch"
git status --short
git add docker-compose.yml requirements-andrea.txt README_Andrea.md src/cassandra src/dgraph
git diff --cached --stat
git commit -m "Implement Cassandra activity and Dgraph recommendations"
git push -u origin andrea/cassandra-dgraph
```

En GitHub, abre **Compare & pull request** y elige la rama de integración del equipo.
Si GitHub pide acceso al repositorio, la dueña debe agregarte como colaboradora.
