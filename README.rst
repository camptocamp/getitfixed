GetItFixed!
===========

Documentation
-------------
Build the docs

.. code-block:: bash

    cd getitfixed/docs
    make html

Demo :
https://geomapfish-demo.camptocamp.com/getitfixed/getitfixed/issues

Demo admin :
https://geomapfish-demo.camptocamp.com/getitfixed/getitfixed_admin/issues

Create a development instance
-----------------------------

.. code-block:: bash

    git clone git@github.com:camptocamp/getitfixed.git
    cd getitfixed
    make meacoffee

Public interface should be available at:
http://localhost:8080/getitfixed/issues

Admin interface should be available at:
http://localhost:8080/getitfixed_admin/issues

Generate a new alembic revision
-------------------------------

Before the first release we will overwrite the first migration:

.. code-block:: bash

    rm -rf getitfixed/alembic/versions/*.py
    cat <<<EOF | docker-compose exec --user postgres db psql -d getitfixed
    DROP SCHEMA getitfixed CASCADE;
    CREATE SCHEMA getitfixed;
    GRANT ALL ON SCHEMA getitfixed TO getitfixed;
    EOF

.. code-block:: bash

    docker-compose run --rm --user `id -u ` getitfixed \
        alembic -c /app/alembic.ini -n getitfixed revision --autogenerate -m 'First revision'

Now try it:

.. code-block:: bash

    docker-compose run --rm --user `id -u ` getitfixed \
        alembic -c /app/alembic.ini -n getitfixed upgrade head

Email
-----

In development we use a custom SMTP server. All emails will be available
at the following address:

http://localhost:8082/webmail/?_task=mail&_mbox=INBOX
