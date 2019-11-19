# GetItFixed! README

Demo : https://geomapfish-demo.camptocamp.com/getitfixed/getitfixed/issues

## Create a development instance

```
git clone git@github.com:camptocamp/getitfixed.git
cd getitfixed
make meacoffee
```

Public interface should be available at: http://localhost:8080/getitfixed/issues

Admin interface should be available at: http://localhost:8080/admin/issues

## Upgrade GetItFixed! demo

Build docker images locally and push them on docker hub:

```
make -f demo.mk build docker-push
```

Now connect to server and update docker composition:

```
ssh geomapfish-demo.camptocamp.com
cd /var/www/vhosts/geomapfish-demo/private/getitfixed_demo/getitfixed
git pull origin/master
docker-compose down
docker login  # Because images are private for now
make -f demo.mk demo
```

Test the application:

- https://geomapfish-demo.camptocamp.com/getitfixed/getitfixed/issues
- https://geomapfish-demo.camptocamp.com/getitfixed/admin/issues
- https://geomapfish-demo.camptocamp.com/webmail/

If everything went well you can now exit from logs, close ssh connection, and go take your coffee.

## Add GetItFixed! in demo_geomapfish

Copy the `gmf_demo` database locally:

```
export SRC_PGHOST=pg-cluster-master.exo.camptocamp.com
export SRC_PGDATABASE=gmf_demo
export SRC_PGUSER=gmf_demo
export PGPASSWORD=...

sudo service postgresql restart
sudo -u postgres dropdb demo_geomapfish
sudo -u postgres createdb demo_geomapfish
sudo -u postgres psql -c 'GRANT ALL ON DATABASE demo_geomapfish TO "www-data";'
sudo -u postgres psql -d demo_geomapfish -c 'CREATE EXTENSION postgis;'

pg_dump -Fc --no-owner -n edit -n geodata -n main -n main_static -h $SRC_PGHOST -d $SRC_PGDATABASE -U $SRC_PGUSER | \
sudo -u www-data pg_restore --no-owner --exit-on-error -d demo_geomapfish
```

Clone the demo_geomapfish project:

```
git clone --branch getitfixed git@github.com:camptocamp/demo_geomapfish.git
cd demo_geomapfish
```

Create a user makefile:

```
export DOCKER_PGHOST ?= 172.17.0.1
export DOCKER_PGHOST_SLAVE ?= 172.17.0.1
export DOCKER_PGDATABASE ?= demo_geomapfish
export DOCKER_PGSCHEMA ?= main
export DOCKER_PGSCHEMA_STATIC ?= main_static

include Makefile
```

Create the getitfixed db schema:

```
docker-compose exec geoportal \
    psql -c 'DROP SCHEMA IF EXISTS getitfixed CASCADE;'
docker-compose exec geoportal \
    initialize_getitfixed_db "c2cgeoportal://development.ini#app" --with-data=1
```

Clone and build GetItFixed! plugin and others:

```
git clone git@github.com:camptocamp/getitfixed.git geoportal/getitfixed
make -C geoportal/getitfixed build

git clone --branch getitfixed git@github.com:camptocamp/c2cgeoportal.git ../c2cgeoportal
make -C ../c2cgeoportal docker-build

git clone --branch getitfixed git@github.com:camptocamp/c2cgeoform.git ../c2cgeoform
make -C ../c2cgeoform build
```

Create a docker-compose.override.yaml file:

```
cp docker-compose.override.sample.yaml docker-compose.override.yaml
```

Add volumes for source files:

```
services:
  geoportal:
    volumes:- ${PWD}/geoportal/demo_geoportal:/app/demo_geoportal
      - ${PWD}/../c2cgeoportal/admin/c2cgeoportal_admin:/opt/c2cgeoportal_admin/c2cgeoportal_admin
      - ${PWD}/../c2cgeoportal/commons/c2cgeoportal_commons:/opt/c2cgeoportal_commons/c2cgeoportal_commons
      - ${PWD}/../c2cgeoportal/geoportal/c2cgeoportal_geoportal:/opt/c2cgeoportal_geoportal/c2cgeoportal_geoportal
      - ${PWD}/geoportal/getitfixed/getitfixed:/app/getitfixed/getitfixed
      - ${PWD}/../c2cgeoform/c2cgeoform:/usr/local/lib/python3.6/dist-packages/c2cgeoform
```

Build, run and watch the logs:

```
./docker-run make -f user.mk build && docker-compose up -d && docker-compose logs -f geoportal
```

Here is it: https://localhost:8484/getitfixed

Now you need to create the GetItFixed database schema and tables:

```
DATABASE=demo_geomapfish
sudo -u postgres psql -d $DATABASE -c 'DROP SCHEMA IF EXISTS getitfixed CASCADE;'
sudo -u postgres psql -d $DATABASE -c 'CREATE SCHEMA getitfixed AUTHORIZATION "www-data";'
docker-compose exec geoportal alembic -c alembic.ini -n getitfixed upgrade head
```

Add test data:

```
docker-compose exec geoportal initialize_getitfixed_db c2cgeoportal://development.ini#app
```

Now you should be able to create new issues in the form.

## Generate a new alembic revision

Before the first release we will overwrite the first migration:

```
rm -rf getitfixed/alembic/versions/*.py
cat <<<EOF | docker-compose exec --user postgres db psql -d getitfixed
DROP SCHEMA getitfixed CASCADE;
CREATE SCHEMA getitfixed;
GRANT ALL ON SCHEMA getitfixed TO getitfixed;
EOF
```

```
docker-compose run --rm --user `id -u ` getitfixed \
    alembic -c /app/alembic.ini -n getitfixed revision --autogenerate -m 'First revision'
```

Now try it:

```
docker-compose run --rm --user `id -u ` getitfixed \
    alembic -c /app/alembic.ini -n getitfixed upgrade head
```



## Email

In development we use a custom SMTP server. All emails will be available at the following address:

  http://localhost:8082/webmail/?_task=mail&_mbox=INBOX
