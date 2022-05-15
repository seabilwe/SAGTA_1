# Introduction

The implementation of the profile tool is based on [Altprofile](https://github.com/arno974/lizmap-altiProfil)
The repository documentation is written in French and below is a summary of how to
get it running in a docker-compose workflow and incorporate it with lizmap docker-compose.

**Note:** This assumes you already have a working version of lizmap webclient using
[docker-compose](https://github.com/3liz/lizmap-docker-compose)

* Download a DEM and load it into a PostgreSQL database example
    ``` 
    export PGPASSWORD="docker"
    raster2pgsql -C -I -M -F -Y -s 3857 -t 100x100 south_africa_cog_3857.tif south_africa | psql -d gis -p 5432 -U docker -h localhost
    ```
* Download the official [releases](https://github.com/arno974/lizmap-altiProfil/releases)
* Unzip the release and place the folders and files
    ```
    altiProfil  altiProfilAdmin  altiProfilAdmin.png  altiProfil.jpeg
    ```
    into `lizmap/var/lizmap-modules`
* Replace the file `https://github.com/kartoza/SAGTA/blob/main/plugins/profile_tool/altiServicesFromDB.class.php` to the folder `lizmap/var/lizmap-modules/altiProfil/classes`
* Copy `altiProfil.ini.php` into `lizmap/var/lizmap-config`
* Update `lizmap/var/lizmap-config/localconfig.ini.php` to add the following
    ```
    [modules]
    altiProfil.access=2
    altiProfilAdmin.access=2
    ```
* Add a database connection string to `lizmap/var/lizmap-config/profiles.ini.php`

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
    
* Execute into the running lizmap container and execute the following
    ``` 
    docker-compose exec lizmap ash
    apk add php7-pdo_pgsql
    exit
    ```

* Restart the lizmap container `docker-compose lizmap restart`.

