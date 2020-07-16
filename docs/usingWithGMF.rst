How to Integrate in GMF
=======================

Add GetItFixed! in a GeoMapFish project
---------------------------------------

In your GeoMapFish project, add configuration for GetItFixed! in file vars.yaml.
See `vars.yaml <https://github.com/camptocamp/getitfixed/blob/master/vars.yaml>`_.

Create the getitfixed db schema:

.. code-block:: bash

    # You can drop the schema if it already exists
    # docker-compose exec geoportal psql -c 'DROP SCHEMA IF EXISTS getitfixed CASCADE;'

    docker-compose exec geoportal alembic -n getitfixed upgrade head

    # You can fill schema with example dataset (for development or demo)
    # docker-compose exec geoportal getitfixed_setup_test_data c2cgeoportal://production.ini#app

Grant permission "getitfixed_admin" to some GMF role in geoportal/<project>_geoportal/resources.py:

.. code-block:: python

    class Root:
        __acl__ = [
            (Allow, 'role_admin', ALL_PERMISSIONS),
            (Allow, 'role_getitfixed', 'getitfixed_admin'),
            ]

Now the GetItFixed! module should be accessible:

- Public interface: <your_geomapfish_root_url>/getitfixed
- Admin interface: <your_geomapfish_root_url>/getitfixed_admin


Further upgrades
================

When upgrading GetItFixed! you may need to apply alembic migrations on your database.

For example when running GetItFixed! inside a GeoMapFish 2.5 container run the following command:

.. code-block:: bash

   docker-compose run --rm geoportal alembic -n getitfixed upgrade head
