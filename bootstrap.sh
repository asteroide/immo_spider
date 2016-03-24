#!/bin/sh

#export http_proxy=http://www-cache-nrs.si.fr.intraorange:3128
#export https_proxy=http://www-cache-nrs.si.fr.intraorange:3128

curl -sL https://deb.nodesource.com/setup_0.12 | sudo -E bash -

#sudo -E apt-get update 

sudo -E apt-get -y install nodejs apache2 python3-pip libxml2-dev libxslt1-dev python-dev openjdk-7-jre mongodb-server zlib1g-dev

#sudo update-alternatives --install /usr/bin/node nodejs /usr/bin/nodejs 100

cd /vagrant

#npm config set proxy http://www-cache-nrs.si.fr.intraorange:3128
#npm config set https-proxy http://www-cache-nrs.si.fr.intraorange:3128

mkdir openlayers 2>/dev/null
cd /vagrant/openlayers
echo Installing openlayers with npm

npm install openlayers

mkdir -p node_modules/openlayers/build 2>/dev/null

echo Configuring openlayers

cat > node_modules/openlayers/build/ol-custom.json <<EOF
{
  "exports": [
    "ol.Map",
    "ol.View",
    "ol.control.defaults",
    "ol.layer.Tile",
    "ol.source.OSM"
  ],
  "compile": {
    "externs": [
      "externs/bingmaps.js",
      "externs/closure-compiler.js",
      "externs/geojson.js",
      "externs/oli.js",
      "externs/olx.js",
      "externs/proj4js.js",
      "externs/tilejson.js",
      "externs/topojson.js"
    ],
    "define": [
      "goog.dom.ASSUME_STANDARDS_MODE=true",
      "goog.json.USE_NATIVE_JSON=true",
      "goog.DEBUG=false"
    ],
    "jscomp_off": [
      "unknownDefines"
    ],
    "extra_annotation_name": [
      "api", "observable"
    ],
    "compilation_level": "ADVANCED_OPTIMIZATIONS",
    "manage_closure_dependencies": true
  }
}
EOF

echo Building Custom Openlayers
cd node_modules/openlayers

node tasks/build.js build/ol-custom.json build/ol-custom.js

cd -

cat > index.html <<EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>OpenLayers 3 example</title>
    <link rel="stylesheet" href="node_modules/openlayers/css/ol.css" />
    <style>
      #map {
        width: 600px;
        height: 400px;
      }
    </style>
</head>
<body>
    <div id="map"></div>
    <script src="node_modules/openlayers/build/ol-custom.js"></script>
    <script>
    var map = new ol.Map({
      target: 'map',
      layers: [
        new ol.layer.Tile({
          source: new ol.source.OSM()
        })
      ],
      view: new ol.View({
        center: [0, 0],
        zoom: 4
      })
    });
    </script>
</body>
</html>
EOF

echo Configuring Apache

sudo mv /etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-enabled/000-default.conf.bak
sudo tee /etc/apache2/sites-enabled/000-default.conf <<EOF
Listen 0.0.0.0:80

<VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        #ServerName www.example.com

        ServerAdmin webmaster@localhost
        DocumentRoot /vagrant/openlayers
        <Directory /vagrant/openlayers>
            Options Indexes FollowSymLinks
            AllowOverride None
            Require all granted
        </Directory>

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        ErrorLog \${APACHE_LOG_DIR}/error.log
        CustomLog \${APACHE_LOG_DIR}/access.log combined

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
EOF

sudo service apache2 restart
