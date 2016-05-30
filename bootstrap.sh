#!/bin/sh

sudo -E apt-get update

sudo -E apt-get -y install apache2 python3-pip libxml2-dev libxslt1-dev python-dev mongodb-server zlib1g-dev

cd /vagrant

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

# part for micro services and lxc

sudo apt-get install lxc

sudo -E lxc-create -t download -n rabbitmq -- --dist ubuntu --release xenial --arch amd64
sudo -E lxc-create -t download -n spider -- --dist ubuntu --release xenial --arch amd64
sudo -E lxc-create -t download -n apiviewer -- --dist ubuntu --release xenial --arch amd64
sudo -E lxc-create -t download -n logger -- --dist ubuntu --release xenial --arch amd64

sudo lxc-start -n rabbitmq
sudo lxc-start -n spider
sudo lxc-start -n apiviewer
sudo lxc-start -n logger

sudo lxc-execute  -n rabbitmq -- apt-get update
sudo lxc-execute  -n rabbitmq -- apt-get install rabbitmq-server