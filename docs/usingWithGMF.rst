How to Integrate in GMF
=======================

Add GetItFixed! in a GeoMapFish project
---------------------------------------

In your GeoMapFish project, add configuration for GetItFixed! in file vars.yaml.
See `vars.yaml <https://github.com/camptocamp/getitfixed/blob/master/vars.yaml>`_.

Create the getitfixed db schema:

.. code-block:: bash

    docker-compose exec geoportal \
        psql -c 'DROP SCHEMA IF EXISTS getitfixed CASCADE;'
    docker-compose exec geoportal \
        initialize_getitfixed_db "c2cgeoportal://development.ini#app"

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
