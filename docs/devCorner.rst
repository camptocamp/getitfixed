Dev corner
=======================

Upgrade GetItFixed! demo
------------------------

Build docker images locally and push them on docker hub:

.. code-block:: bash

    make -f demo.mk build docker-push

Now connect to server and update docker composition:

.. code-block:: bash

    ssh geomapfish-demo.camptocamp.com
    cd /var/www/vhosts/geomapfish-demo/private/getitfixed_demo/getitfixed
    git pull origin/master
    docker-compose down
    docker login  # Because images are private for now
    make -f demo.mk demo

If everything went well you can now exit from logs, close ssh
connection, and go take your coffee.


Useful links
------------

-  https://geomapfish-demo.camptocamp.com/getitfixed/getitfixed/issues
-  https://geomapfish-demo.camptocamp.com/getitfixed/admin/issues
-  https://geomapfish-demo.camptocamp.com/webmail/


Publish to pypi
---------------

Information can be found :travis/deploy-pypi

To publish to pypi:
 - Create a new tag in the GitHub repository
 - Increment the version in setup.py
 - Create a new commit and push it to master

NB: travis uses Amorvan's account to publish to pypi