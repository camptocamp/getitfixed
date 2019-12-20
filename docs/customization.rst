Customization
=======================

Customization is done in the vars.yaml file

Change Email content
--------------------

4 email templates exist

* *admin_new_issue_email*: received by the administrator of the category when a new issue is created

* *new_issue_email*: received by the reporter once the issue has been submitted

* *update_issue_email*: received by either reporter/administrator when an issue has been updated

* *resolved_issue_email*: received by the reporter once the issue has been resolved


Change SMTP
-----------

.. code-block:: bash

       smtp:
        host: smtp


to the host of your smtp


Change Map background
---------------------

The following will add a mapbox backgound XYZ layer.

.. code-block:: bash

        baseLayers:
            - type_: "XYZ"
             url: "https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/256/{{{{z}}}}/{{{{x}}}}/{{{{y}}}}?access_token=pk.eyJ1IjoianVsc2JyZWFrZG93biIsImEiOiJjanB3Y216bWowYXJlNDNqbmhwY3Fia3VrIn0.Yo9vCvuv-0sXSIbZag6QYg"
