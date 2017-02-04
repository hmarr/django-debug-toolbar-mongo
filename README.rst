==================================
Flask Debug Toolbar MongoDB Panel
==================================
:Info: An extension panel for Rob Hudson's Django Debug Toolbar that adds
       MongoDB debugging information
:Author: Harry Marr (http://github.com/hmarr, http://twitter.com/harrymarr)

Setup
=====


Set this in your Flask config object.


    'DEBUG_TB_PANELS': {
        'flask_debug_toolbar_mongo.panel.MongoDebugPanel'
    }



An extra panel titled "MongoDB" should appear in your debug toolbar.
