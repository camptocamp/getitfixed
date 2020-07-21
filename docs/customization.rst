Customization
=============

Customization is done in the vars.yaml file

Change main layout file
-----------------------

In section ``getitfixed`` add new key ``layout`` with as value the path to your layout file.

.. code-block:: yaml

   layout: geomapfish_geoportal:templates/getitfixed/layout.jinja2

Custom layout file might extends the default GetItFixed! layout and override some blocks:

.. code-block:: html+jinja

   {% extends "getitfixed:templates/layout.jinja2" %}

   {% block title %}
   <title>{{_('GeoMapFish / GetItFixed!')}}</title>
   <link rel="shortcut icon" href="{{request.static_url('/etc/geomapfish/static/images/favicon.ico')}}">
   {% endblock title %}

   {% block style %}
   <link href="{{request.static_url('/etc/geomapfish/static/css/getitfixed.css')}}" rel="stylesheet">
   <style>
     body {
       background-color: #F0F0F0;
     }
   </style>
   {% endblock style %}

   {% block header %}
   <header class="container">
     <h3 class="title">{{_('GeoMapFish / GetItFixed!')}}</h3>
   </header>
   {% endblock header %}

   {% block footer %}
   <footer class="footer text-muted">
    <div class="container">
      <p>Contact: <a href="...">Contact form</a></p>
    </div>
   </footer>
   {% endblock footer %}

Change Email content
--------------------

4 email templates exist

* *admin_new_issue_email*: received by the administrator of the category when a new issue is created

* *new_issue_email*: received by the reporter once the issue has been submitted

* *update_issue_email*: received by either reporter/administrator when an issue has been updated

* *resolved_issue_email*: received by the reporter once the issue has been resolved


Configure SMTP
--------------

.. code-block:: yaml

   smtp:
     host: str (the SMTP hostname, required)
     ssl: boolean (default to false)
     starttls: boolean (default to false)
     user: str (username to authenticate with, no authentication if not set)
     password: str (required when username is set)


Configure maps
--------------

By default, application will use OSM standard tiles and projection ``EPSG:3857``.

Here is some maps configuration examples.

- Mapbox XYZ layer:

.. code-block:: yaml

   baseLayers:
     - type_: "XYZ"
       url: "https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/256/{{{{z}}}}/{{{{x}}}}/{{{{y}}}}?access_token=pk.eyJ1IjoianVsc2JyZWFrZG93biIsImEiOiJjanB3Y216bWowYXJlNDNqbmhwY3Fia3VrIn0.Yo9vCvuv-0sXSIbZag6QYg"

- GeoMapfish 2.5 WMTS layer:

.. code-block:: yaml

   map:
     # Projection code for the map widget serialization/deserialization
     srid: 2056

     # Projection definition (only EPSG:3857 is supported by default)
     projections:
       - code: "EPSG:2056"
         definition: "+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=2600000 \
                      +y_0=1200000 +ellps=bessel +towgs84=674.374,15.056,405.346,0,0,0,0 +units=m +no_defs"

      # Background layer definition
     baseLayers:
       - type_: "WMTS"
         url: "{VISIBLE_WEB_PROTOCOL}://{VISIBLE_WEB_HOST}{VISIBLE_ENTRY_POINT}tiles/1.0.0/\
               {{{{{{{{{{{{{{{{Layer}}}}}}}}}}}}}}}}/default/{{{{{{{{{{{{{{{{TileMatrixSet}}}}}}}}}}}}}}}}\
               /{{{{{{{{{{{{{{{{TileMatrix}}}}}}}}}}}}}}}}/{{{{{{{{{{{{{{{{TileRow}}}}}}}}}}}}}}}}/\
               {{{{{{{{{{{{{{{{TileCol}}}}}}}}}}}}}}}}.png"
         requestEncoding: "REST"
         layer: "map"
         matrixSet: "epsg2056_005"
         dimensions: {}
         style: "default"
         projection: "EPSG:2056"
         tileGrid:
           origin: [2420000, 1350000]
           resolutions: [4000, 2000, 1000, 500, 250, 100, 50, 20, 10, 5, 2.5, 1, 0.5, 0.25, 0.1, 0.05]
           matrixIds: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
         attributions: []

      # Openlayers view parameters
      view:
        projection: "EPSG:2056"
        initialExtent: [2495822, 1091449, 2780525, 1270656]

      # Max zoom when fitting on features
      fitMaxZoom: 12
