# Introduction

The implementation of the profile tool is based on [Altprofile](https://github.com/arno974/lizmap-altiProfil)
The repository documentation is written in French and below is a summary of how to
get it running in a docker-compose workflow and incorporate it with `lizmap` docker-compose.

**Note:** This assumes you already have a working version of `lizmap` webclient using
[docker-compose](https://github.com/3liz/lizmap-docker-compose)

* Download a DEM and load it into a [PostgreSQL](https://www.postgresql.org/) database.
    ``` 
    export PGPASSWORD="docker"
    raster2pgsql -C -I -M -F -Y -s 3857 -t 100x100 south_africa_cog_3857.tif south_africa | psql -d gis -p 5432 -U docker -h localhost
    ```
* Download the official [releases](https://github.com/arno974/lizmap-altiProfil/releases) 
  ```bash
    wget https://github.com/arno974/lizmap-altiProfil/archive/refs/tags/0.3.0.zip
    unzip 0.3.0.zip
  ```
* cd into the unzipped folder i.e. `lizmap-altiProfil-0.3.0`.
    ```
    cp -r altiProfil  altiProfilAdmin  altiProfilAdmin.png  altiProfil.jpeg  /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/var/lizmap-modules/
    ```
* Copy the file `altiServicesFromDB.class.php` into the appropriate folder.

  ```bash
  cp -r /home/${user}/deployment/map_downloader/SAGTA/plugins/lizmap/profile_tool/altiServicesFromDB.class.php /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/var/lizmap-modules/altiProfil/classes/
  ```

* Copy the following file
  ```bash
  cp -r altiProfil.ini.php /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/var/lizmap-config/
  ```

* Update `/home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/var/lizmap-config/localconfig.ini.php` 
adding the following
    ```
    [modules]
    altiProfil.access=2
    altiProfilAdmin.access=2
    ```
* Add a database connection string to `/home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/var/lizmap-config/profiles.ini.php`

  ``` 
      [jdb:altiProfil]
      driver=pgsql
      database=gis
      host=db
      user=docker
      password=docker
      port=5432
      search_path=public
  ```
Use the example above
    
* Run the services again and exec into the `lizmap` container:
    ``` 
    cd /home/${user}/deployment/map_downloader/lizmap-docker-compose/
    docker-compose up -d 
    docker-compose exec lizmap ash
    apk add php7-pdo_pgsql
    exit
    ```

* Restart the `lizmap` container 
  ```bash
  docker-compose lizmap restart
  ```


