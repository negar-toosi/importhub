# ImportHub

ImportHub is a backend service for bulk-importing shipment data from Excel
files. Users upload a spreadsheet, the service validates each row, processes the
records in the background, and exposes the import results and the stored
shipments through a REST API.

---

## Table of contents

- [Project overview](#project-overview)
- [Architecture](#architecture)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [How to run the project (locally)](#how-to-run-the-project-locally)
- [How to run with Docker](#how-to-run-with-docker)
- [How to run migrations](#how-to-run-migrations)
- [API examples](#api-examples)
- [Main technical decisions](#main-technical-decisions)
  - [Why Clean Architecture](#why-clean-architecture)
  - [Why PostgreSQL](#why-postgresql)
  - [Why Redis](#why-redis)
  - [Why Celery](#why-celery)
- [Sync vs async explanation](#sync-vs-async-explanation)
- [Known limitations](#known-limitations)

---

## Project overview

ImportHub solves a common back-office problem: someone has a spreadsheet full of
shipment records and needs to load it into a system in bulk — with each row
validated and a clear report of what went in and what was rejected.

The flow has three steps:

1. **Upload** — the client posts an `.xlsx`/`.xls` file. The API saves it to
   disk, creates an `Import` record with status `pending`, and immediately hands
   the work off to a background worker. The request returns right away with an
   `import_id`.
2. **Process (in the background)** — a Celery worker reads the Excel file,
   validates each row, inserts the valid ones as `ShipmentRecord`s, and writes an
   `ImportError` for every row that fails. The `Import` status advances from
   `pending → processing → completed` (or `failed`).
3. **Read back** — the client polls the import status, lists the per-row errors,
   and queries the imported shipments with filtering and pagination.

### Core domain objects

| Object | Meaning |
| --- | --- |
| `Import` | A single uploaded file together with its processing summary (totals, success/failure counts, timestamps, and status). |
| `ShipmentRecord` | A single valid shipment row written to the database. |
| `ImportError` | A single validation failure, linked to an import and a row number. |

### Statuses

- **Import status:** `pending`, `processing`, `completed`, `failed`
- **Shipment status:** `pending`, `in_transit`, `delivered`, `canceled`

---

## Architecture

The project follows **Clean Architecture**. The code is divided into independent
layers, and dependencies point **inward only** — outer layers depend on inner
layers, never the other way around.

```
┌───────────────────────────────────────────────────────────┐
│  apis  (HTTP layer: FastAPI routers + request/response DTOs)│
├───────────────────────────────────────────────────────────┤
│  presentation  (composition root: DI container + wiring)    │
├───────────────────────────────────────────────────────────┤
│  aplication  (use cases / services: orchestration logic)    │
├───────────────────────────────────────────────────────────┤
│  domain  (entities + interfaces; pure, no framework deps)   │
├───────────────────────────────────────────────────────────┤
│  infrastructure  (DB, Celery, Redis, file storage, tables)  │
└───────────────────────────────────────────────────────────┘
```

The whole design turns on **dependency inversion** around the `domain` layer:

- `domain/repositories/` and `domain/interfaces/` define the **abstract
  interfaces** (`IImportRepository`, `IShipmentRepository`,
  `IImportErrorRepository`, `IFileStorage`, `IImportDispatcher`).
- The `aplication` services depend only on those interfaces — they never import
  SQLAlchemy, Celery, or the filesystem directly.
- The `infrastructure` layer supplies the **concrete implementations**
  (`ImportRepository`, `LocalFileStorage`, `CeleryImportDispatcher`, and so on).
- The `presentation` layer (`Container` + `dependencies.py`) plugs those
  concrete implementations into the abstract slots at runtime through FastAPI's
  `Depends`.

Because every layer knows the one beneath it **only through interfaces**, you
can swap PostgreSQL for another store, local disk for S3, or Celery for another
queue **without touching the use-case logic**.

### Why this design fits the problem

The heart of this service isn't the HTTP plumbing or the database — it's the
**import workflow**: validate a file row by row, record what succeeded and what
failed, and let a client read the result back. This design keeps that workflow at
the center.

- **The problem has volatile edges and a stable core.** *How* a file arrives
  (HTTP today), *where* it is stored (local disk today), and *how* work is queued
  (Celery/Redis today) are all implementation details that are likely to change.
  *What* an import does — parse, validate, persist, summarize — is the stable
  business logic. Clean Architecture keeps that stable logic in
  `aplication`/`domain` and pushes the volatile edges out to
  `apis`/`infrastructure`, so churn at the edges never reaches the core.

- **Two processes share one core.** The work runs across two runtimes — the
  FastAPI web process (which enqueues) and the Celery worker (which processes).
  Both are built from the *same* domain interfaces and use cases (`web` via
  [src/presentation/container.py](src/presentation/container.py), the worker via
  [src/infrastructure/container.py](src/infrastructure/container.py)). The
  layered boundaries are what let a single set of business rules be wired into
  two different entrypoints with no duplication.

- **The async/sync split falls out of the layering.** Because all I/O (DB, file
  storage) sits behind infrastructure interfaces, it can be uniformly `async`,
  while the CPU-bound steps (Excel parsing and row validation) stay plain `sync`
  inside the worker — see
  [Sync vs async explanation](#sync-vs-async-explanation). The architecture turns
  that into a local decision rather than a cross-cutting one.

- **It is deliberately proportionate.** For a focused service like this, the
  layer count is the minimum needed to isolate the domain from frameworks —
  enough to gain testability and replaceability, without the ceremony of a larger
  system.

In short, the design optimizes for the **changeability and testability** of the
one thing that matters — the import use cases — and treats everything else
(framework, database, queue, storage) as a swappable detail. See
[Main technical decisions](#main-technical-decisions) for the per-component
rationale (PostgreSQL, Redis, Celery).

---

## Tech stack

| Concern | Choice |
| --- | --- |
| Language / runtime | Python 3.14 |
| Web framework | FastAPI + Uvicorn |
| Background jobs | Celery |
| Message broker / result backend | Redis |
| Database | PostgreSQL 18 |
| ORM / DB access | SQLAlchemy 2.0 (async, `asyncpg` driver) |
| Validation / DTOs | Pydantic v2 + `pydantic-settings` |
| Excel parsing | pandas + openpyxl |
| Containerization | Docker + Docker Compose |

---

## Project structure

```
src/
├── main.py                       # FastAPI app entrypoint + lifespan (schema creation)
│
├── apis/                         # HTTP layer
│   ├── routers/
│   │   ├── imports.py            # POST /imports, GET /imports/{id}, GET /imports/{id}/errors
│   │   └── shipments.py          # GET /shipments (filter + paginate)
│   └── dto/                      # request/response Pydantic models
│
├── presentation/                 # composition root
│   ├── container.py              # Container: builds concrete implementations
│   └── dependencies.py           # FastAPI Depends providers
│
├── aplication/                   # use cases / services
│   ├── upload_import_service.py  # save file + create Import record
│   ├── get_import_service.py     # fetch an import by id
│   ├── process_import.py         # the background processing use case
│   ├── validator.py              # per-field shipment row validation (sync, CPU-bound)
│   └── map_celery_state.py       # Celery state -> ImportStatus mapping
│
├── domain/                       # pure domain, no framework deps
│   ├── entities/                 # Import, ShipmentRecord, ImportError, ShipmentFilter
│   ├── interfaces/               # IFileStorage, IImportDispatcher
│   └── repositories/             # IImportRepository, IShipmentRepository, IImportErrorRepository
│
├── infrastructure/               # concrete implementations
│   ├── config.py                 # Settings (env-driven) + DATABASE_URL
│   ├── database.py               # async engine + session factory + Base
│   ├── file_storage.py           # LocalFileStorage
│   ├── container.py              # builder for the worker-side service
│   ├── celery/
│   │   ├── setup.py              # Celery app (broker/backend = Redis)
│   │   ├── task.py               # process_import_task
│   │   └── import_dispatcher.py  # CeleryImportDispatcher
│   ├── repository/               # SQLAlchemy repository implementations
│   └── tables/                   # SQLAlchemy ORM table models
│
└── utils/
    └── enums.py                  # ShipmentStatus, ImportStatus
```

---

## How to run the project (locally)

### Prerequisites

- Python 3.14
- A running PostgreSQL instance
- A running Redis instance

### 1. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root. When you run everything on your host
(rather than through Compose), point the hosts at `localhost`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=importhub
POSTGRES_PORT=5432
POSTGRES_HOST=localhost

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_BACKEND_URL=redis://localhost:6379/1
```

### 3. Start the API server

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The app creates the database schema automatically on startup (see
[How to run migrations](#how-to-run-migrations)).

### 4. Start the Celery worker (in a separate terminal)

The API only enqueues jobs, so you need a worker running to actually process the
uploads:

```bash
celery -A src.infrastructure.celery.setup worker --loglevel=info
```

### 5. Open the interactive docs

FastAPI serves auto-generated documentation at:

- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc

---

## How to run with Docker

Docker Compose is the recommended way to run the full stack (Postgres + Redis +
API + worker) with a single command.

### 1. Make sure your `.env` uses the Compose service names

Inside the Compose network, the database host is `db` and Redis is `redis`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=importhub
POSTGRES_PORT=5432
POSTGRES_HOST=db

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_BACKEND_URL=redis://redis:6379/1
```

### 2. Build and start everything

```bash
docker compose up --build
```

This starts four containers:

| Service | Container | Host port |
| --- | --- | --- |
| `web` (FastAPI/Uvicorn) | `importhub_web` | `8001 → 8000` |
| `worker` (Celery) | `importhub_worker` | — |
| `db` (PostgreSQL 18) | `importhub_postgres` | `5430 → 5432` |
| `redis` (Redis 7) | `importhub_redis` | `6381 → 6379` |

The API is then available at **http://localhost:8001** and the docs at
**http://localhost:8001/docs**.

Uploaded files are persisted in the shared `uploads` Docker volume, which is
mounted into both `web` and `worker` so the worker can read the files the API
wrote.

### 3. Stop

```bash
docker compose down          # stop the containers
docker compose down -v       # also remove the db + uploads volumes
```

---

## How to run migrations

This project does **not** use a standalone migration tool such as Alembic.
Instead, the database schema is created automatically from the SQLAlchemy ORM
models **when the application starts**, inside the FastAPI lifespan in
[src/main.py](src/main.py):

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.infrastructure.tables import Import, ImportError, ShipmentRecord
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
```

In practice, this means:

- **You don't run a migration command.** Simply starting the API (locally with
  `uvicorn`, or via `docker compose up`) creates any missing tables defined in
  [src/infrastructure/tables/](src/infrastructure/tables/).
- `create_all` only **creates tables that don't exist yet**. It does **not**
  alter or drop existing tables, so changing a column on a model will not be
  reflected in an already-created table.
- To pick up a schema change during development, drop the database/volume and let
  it be recreated:

  ```bash
  docker compose down -v && docker compose up --build
  ```
---

## API examples

Base URL (Docker): `http://localhost:8001` — (local: `http://localhost:8000`).

The expected Excel columns are:
`shipment_code`, `customer_name`, `origin_city`, `destination_city`,
`weight_kg`, `price`, `status`, `delivery_date`.

### 1. Upload an import

```bash
curl -X POST "http://localhost:8001/api/v1/imports/" \
  -H "accept: application/json" \
  -F "file=@shipments.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
```

**201 Created**

```json
{
  "import_id": "0f3b2c5a-9b6e-4f8a-9b1d-2f6a1c4e7d90",
  "status": "pending",
  "created_at": "2026-06-20T10:15:00.000000"
}
```

Only `.xlsx` / `.xls` content types are accepted; anything else returns
`422 Unprocessable Entity`.

### 2. Get an import's status / summary

```bash
curl "http://localhost:8001/api/v1/imports/0f3b2c5a-9b6e-4f8a-9b1d-2f6a1c4e7d90"
```

**200 OK**

```json
{
  "import_id": "0f3b2c5a-9b6e-4f8a-9b1d-2f6a1c4e7d90",
  "status": "completed",
  "total_row": 100,
  "success_count": 97,
  "failed_count": 3,
  "created_at": "2026-06-20T10:15:00.000000",
  "finished_at": "2026-06-20T10:15:04.000000"
}
```

### 3. List an import's per-row errors (paginated)

```bash
curl "http://localhost:8001/api/v1/imports/0f3b2c5a-9b6e-4f8a-9b1d-2f6a1c4e7d90/errors?page=1&page_size=20"
```

**200 OK**

```json
{
  "items": [
    { "row_number": 5,  "error": "weight_kg must be greater than 0" },
    { "row_number": 12, "error": "status must be one of: pending, in_transit, delivered, canceled" },
    { "row_number": 31, "error": "duplicate shipment_code: SHP-0031" }
  ],
  "page": 1,
  "page_size": 20,
  "total": 3
}
```

### 4. List imported shipments (filter + paginate)

```bash
curl "http://localhost:8001/api/v1/shipments/?status=in_transit&origin_city=Tehran&page=1&page_size=20"
```

Supported query parameters: `status`, `origin_city`, `destination_city`,
`customer_name`, `created_from`, `created_to` (date), `page`, and `page_size`
(1–100).

**200 OK**

```json
{
  "items": [
    {
      "id": 1,
      "shipment_code": "SHP-0001",
      "customer_name": "Acme Co",
      "origin_city": "Tehran",
      "destination_city": "Shiraz",
      "weight_kg": "12.500",
      "price": "450.000",
      "status": "in_transit",
      "delivery_date": "2026-06-25"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

---

## Main technical decisions

### Why Clean Architecture

The project is split into **api, application (`aplication`), domain,
infrastructure, and presentation** layers. Every file in a layer is independent
of the layers above it and depends only on abstractions, never on concrete
details.

This buys us several things:

- **Testability** — the use cases in `aplication` depend on
  repository/dispatcher *interfaces* defined in `domain`, so they can be
  unit-tested with fakes, with no database, Redis, or filesystem involved.
- **Replaceability** — storage, the queue, and the database are all details
  hidden behind interfaces. `LocalFileStorage` could become an `S3FileStorage`,
  or `CeleryImportDispatcher` an SQS dispatcher, without changing a single use
  case.
- **Clear boundaries** — the domain layer is pure Python/Pydantic with no
  framework imports, so business rules never leak into HTTP handlers or SQL.
- **A single composition root** — all the concrete wiring lives in
  [src/presentation/container.py](src/presentation/container.py), so dependency
  wiring sits in one place instead of being scattered across the codebase.

### Why PostgreSQL

- It is a mature relational database, which suits this data well: shipments,
  imports, and import errors are **structured and related** (an import has many
  errors through a foreign key).
- We rely on relational features directly: a **unique constraint** on
  `shipment_code` (used to detect duplicates), **check constraints**
  (`weight_kg > 0`, `price >= 0`, non-negative counts), and precise
  `Numeric(13, 3)` decimal columns for weight and price.
- It handles concurrent reads and writes well, which matters here because the API
  and the Celery worker write to the same database at the same time.

### Why Redis

- Celery needs a **message broker** to pass jobs from the API to the worker and a
  **result backend** to track task state. Redis fills both roles here
  (`CELERY_BROKER_URL` → db `0`, `CELERY_BACKEND_URL` → db `1`).
- It is lightweight, fast, and trivial to run (a single small container), which
  makes it ideal for a job queue whose messages are short-lived.

### Why Celery

- File processing is **slow and unbounded** — a large Excel file can take many
  seconds to parse, validate, and insert. Doing that inside the HTTP request
  would block the client and risk timeouts.
- With Celery, the upload endpoint simply **enqueues a job and returns
  immediately** with an `import_id`; the heavy lifting happens out of band in a
  worker process, and the client polls `GET /imports/{id}` for progress.
- It scales horizontally: you increase processing throughput just by running
  **more workers**, independently of the API.

---

## Sync vs async explanation

This project deliberately mixes **async** and **sync** code, choosing between
them based on whether an operation is **I/O-bound** or **CPU-bound**.

### Async — for all I/O operations

Almost everything is `async`:

- All **database access** uses SQLAlchemy's async engine with the `asyncpg`
  driver (`create_async_engine`, `async_sessionmaker`).
- All **repositories**, **use-case services**, **file storage**, and **API
  handlers** are `async`.

The reason is that these are **I/O-bound** operations (network round-trips to
Postgres, reading and writing files). While one request waits on the database,
the event loop is free to make progress on other work. The operations here are
**not inherently sequential** — each row insert, each query, and each upload is
independent of the others — so async concurrency is a natural fit and keeps the
service responsive under load.

### Sync — for CPU-bound steps

Two specific steps are intentionally **synchronous**:

1. **Reading the Excel file** — `pd.read_excel(...)` in
   [ProcessImportService._read_excel](src/aplication/process_import.py). Parsing
   a spreadsheet is pure computation (decompress, parse XML, build a DataFrame),
   not waiting on I/O.
2. **Validating each shipment row** — the methods of
   [ShipmentRecordValidator](src/aplication/validator.py) are plain synchronous
   functions that perform type, range, and format checks in memory.

These are **CPU-bound**: making them `async` would add no benefit, because there
is nothing to await — they don't release the event loop while computing, they
just use CPU. Marking them `async` would only add overhead and falsely imply that
they yield control. Keeping them as straightforward synchronous functions is both
clearer and more honest about what they do.

Because these CPU-bound steps run **inside the Celery worker** (a separate
process from the API), they never block the web server's event loop in the first
place — which is exactly why the file processing was pushed into a background task.

---

## Known limitations

- **No real database migrations.** The schema is created with
  `Base.metadata.create_all` at startup, which only creates missing tables and
  never alters existing ones. A production setup should adopt **Alembic** for
  versioned, reversible migrations.
- **Import status is set by the processing code, not derived from Celery.** The
  upload response returns `pending`, and the worker updates the row to
  `processing`/`completed`/`failed`. There is a `map_celery_state` helper and a
  `# TODO` in the upload handler noting that the status could instead come from
  Celery's task state — this is not yet wired up.
- **Local-disk file storage only.** `LocalFileStorage` writes to a local
  directory shared between the API and worker via a Docker volume. This does not
  scale across multiple hosts; object storage (e.g. S3) would be needed for that.
- **Coarse error handling.** Some failures raise generic `HTTPException`s with
  `# TODO: error handling` notes (for example, fetching an unknown import returns
  `400` rather than `404`). Error responses are not yet standardized.
- **No automated tests yet.** The `tests/` package exists but is empty; the
  architecture is structured to make the use cases easy to test with fakes.
- **The whole file is read into memory.** The upload endpoint calls
  `await request.file.read()` and pandas loads the entire sheet into a DataFrame,
  so very large files are limited by available memory.
```