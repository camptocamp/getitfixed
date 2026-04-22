# GetItFixed!

Collaborative issue/incident reporting system for public services.
Citizens report geolocated problems (potholes, broken streetlights, illegal dumping, etc.) on a map;
administrators validate, update, and resolve them through a structured workflow.

Live demo:

- Public: <https://geomapfish-demo.camptocamp.com/getitfixed/getitfixed/issues>
- Admin: <https://geomapfish-demo.camptocamp.com/getitfixed/getitfixed_admin/issues>

## Overview

Three interfaces share a status workflow
(`new → validated → in_progress → waiting_for_reporter → resolved`):

- **Public** (`/getitfixed/`) — citizens submit geolocated issues with photos
- **Private** (`/getitfixed_private/`) — reporters track their own submissions
- **Admin** (`/getitfixed_admin/`) — moderators validate, update, and resolve

Each status transition can trigger an email to the reporter and/or the admin.

## Tech stack

- **Backend**: Python, Pyramid, SQLAlchemy + GeoAlchemy2, Alembic,
  Colander / Deform, c2cgeoform (Camptocamp's geospatial form library)
- **DB**: PostgreSQL 12 + PostGIS
- **Sessions**: Redis
- **Frontend**: Jinja2, jQuery, Bootstrap 3, bootstrap-table
- **i18n**: Lingua + Babel (EN / FR / DE)
- **Tests**: pytest (acceptance tests in `acceptance_tests/`)
- **Deploy**: Docker + `docker compose`, Waitress WSGI in prod
- **Dev tools**: black, flake8, ipython, ipdb, sphinx

All direct runtime and dev dependencies are exact-pinned
in `requirements.txt` and `requirements-dev.txt`.

## Architecture

MVC Pyramid app. The core package is `getitfixed/`:

- `models/getitfixed.py` — `Photo`, `Category`, `Type`, `Issue` (PostGIS point), `Event`
- `views/{public,private,admin}/` — one view module per interface,
  all subclassing c2cgeoform's `AbstractViews`
- `routes.py` — wires the three app prefixes to c2cgeoform CRUD
- `templates/`, `static/`, `locale/`, `emails/` — standard assets
- `alembic/versions/` — DB migrations
- `scripts/setup_test_data.py` — demo-data loader

Config files: `development.ini` / `production.ini`, plus YAML customization
(`vars.yaml` → `config.yaml`) through `c2c.template`.

## Running it locally

Prerequisites: Docker, Docker Compose, Make.

```bash
git clone git@github.com:camptocamp/getitfixed.git
cd getitfixed
make meacoffee
```

Then open:

- Public: <http://localhost:8080/getitfixed/issues>
- Admin: <http://localhost:8080/getitfixed_admin/issues>
- Webmail (captured outgoing emails): <http://localhost:8082/webmail/?_task=mail&_mbox=INBOX>

### Useful Make targets

| Target             | Purpose                                                            |
| ------------------ | ------------------------------------------------------------------ |
| `make meacoffee`   | Build, run, load test data, tail logs                              |
| `make meadeca`     | Same, but with an empty database                                   |
| `make test`        | Run the pytest acceptance suite                                    |
| `make check`       | Run black + flake8                                                 |
| `make black`       | Reformat Python code with black                                    |
| `make venv`        | Build a local `.venv` with all deps (for IDE / pyright resolution) |
| `make docs`        | Build Sphinx documentation                                         |
| `make psql`        | Open psql in the Postgres container                                |
| `make pshell`      | Open a Pyramid interactive shell                                   |
| `make bash`        | Open bash in the build container                                   |
| `make cleanall`    | Remove containers, images, `.env`                                  |
| `make clean-venv`  | Remove the local `.venv`                                           |
| `make help`        | List all targets                                                   |

Local dev overrides go in `docker-compose.override.yaml`
(gitignored; start from `docker-compose.override.sample.yaml`).

## Database migrations

Generate a new alembic revision:

```bash
docker compose run --rm --user `id -u` getitfixed \
    alembic -c /app/alembic.ini -n getitfixed revision --autogenerate -m 'Revision name'
```

Upgrade the database:

```bash
docker compose run --rm --user `id -u` getitfixed \
    alembic -c /app/alembic.ini -n getitfixed upgrade head
```

## Documentation

```bash
cd docs
make html
```

## CI

`.github/workflows/ci.yaml` runs on `ubuntu-24.04` with `actions/checkout@v4`
and executes `make build`, `make check`, `make test`.
Tagged pushes to `camptocamp/getitfixed` additionally run `scripts/deploy-pypi`.
