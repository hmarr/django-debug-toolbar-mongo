==================================
Django Debug Toolbar MongoDB Panel
==================================
:Info: An extension panel for Rob Hudson's Django Debug Toolbar that adds
       MongoDB debugging information
:Author: Harry Marr (http://github.com/hmarr, http://twitter.com/harrymarr)

Setup
=====
Add the following lines to your ``settings.py``::

   INSTALLED_APPS = (
       ...
       'debug_toolbar_mongo',
       ...
   )

   DEBUG_TOOLBAR_PANELS = (
       ...
       'debug_toolbar_mongo.panel.MongoDebugPanel',
       ...
   )

An extra panel titled "MongoDB" should appear in your debug toolbar.

Note that this should work with any Django application that uses PyMongo.

Disclaimer: only tested in latest Chrome, may fall to pieces in other browers.
If you feel like fixing it, contributions are welcome!
