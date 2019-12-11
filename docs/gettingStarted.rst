Getting Started
=======================

Start by cloning the repository

Containers
----------

GetItFixed is based on docker containers.

*The docker-compose.yaml* file defines the containers used.

The services are

 * **database** (hosts the postgresql database)

 * **web application** (hosts the wsgi python application)

 * webmail, courier-imap and smtp

Webmail, courier-imap and smtp are used for demo purpose, and can be removed in order
to use your own.


Build with data
---------------

You are able to start the application with some dummy data.


.. code-block:: bash

    make meacoffee

Visit
http://localhost:8080/getitfixed/issues
to get the public view

or
http://localhost:8080/getitfixed_admin/issues
to get the admin view



Build with empty data
---------------------

To build and start the application with empty content

.. code-block:: bash

    make meadeca


Creating categories & issues
----------------------------

Executing the following code will enable you to execute SQL commands, this is required
if you want to add Categories and Types.

.. code-block:: bash

    make psql


To create your own **Categories**

.. code-block:: sql

    INSERT into getitfixed.category VALUES (default, 'category_name_fr',
     'category_name_en', 'email@adress.com', default);

This will insert a new category with the default icon:

.. image:: images/cat-default.png
   :width: 20px
   :align: center


To add your custom icons, add them to the `.getitfixed/getitfixed/static/assets/icons/` directory
add change the default value with `/assets/icons/new_icon.png`


To create your own **Types**.

.. code-block:: sql

    INSERT into getitfixed.type VALUES (default, 'category_name_fr',
     'category_name_en', id_category);
