.. gif documentation master file, created by
   sphinx-quickstart on Thu Dec  5 13:25:08 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to GIF's documentation!
===============================

.. toctree::
   :maxdepth: 2

   requirements
   gettingStarted
   database
   customization


GetItFixed is based on docker containers.

The docker-compose.yaml file defines the containers used.

The services are

 * database (hosts the postgresql database)

 * webapplication (hosts the wsgi python application)

 * webmail, courier-imap and smtp are used as démo purpose and can be removed in order to use your own.









Indices and tables
==================

* :ref:`search`
