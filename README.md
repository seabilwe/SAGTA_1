# SAGTA Map downloader

## Map specifications

Maps are defined in QGIS projects that need to be synced to the correct path on the server. 

Maps must follow [these specifications](https://github.com/kartoza/SAGTA/wiki/SAGTA-Map-Downloader-Specifications)

## System Setup

This repo is based on the work provided by [lizmap](git@github.com:3liz/lizmap-docker-compose.git).

To get a running version of the repo you can use the following recipes:

### Docker-Compose Deployment
The instructions below assume you are running docker compose version 1. If you are running
version 2 you will need to replace all instances of `docker-compose` with `docker compose`.

* Make a deployment folder where all source code will be stored

  ```bash
  mkdir -p /home/${user}/deployment/map_downloader
  cd /home/${user}/deployment/map_downloader
  ```

* Clone the `SAGTA` and `lizmap` repository.

    ```bash
    git clone git@github.com:kartoza/SAGTA.git
    git clone git@github.com:3liz/lizmap-docker-compose.git
    ```
* Navigate to the `lizmap-docker-compose` folder
  ```bash
  cd lizmap-docker-compose
  ```
* Run `make configure` to generate the configs in the folder.
* Remove the test QGIS projects from the repo.
    ```bash
    rm -rf ./lizmap/instances/*
    ```
* Copy the `docker-compose.yml` from the `SAGTA` repository into this current one.

  ```bash
  cp -r  /home/${user}/deployment/map_downloader/SAGTA/docker-compose.yml .
  ```
* Copy the `env.example` from the `SAGTA` repository into this folder.

  ```bash
  cp -r /home/${user}/deployment/map_downloader/SAGTA/deployment/env.example .env
  ```
**Note:** Adjust the two paths specified below to reference the correct paths.

Original copied path:
  ```bash
  LIZMAP_PROJECTS=/tmp/lizmap/docker-compose/lizmap/instances
  LIZMAP_DIR=/tmp/lizmap/docker-compose/lizmap 
  ```
Change them to match the following:
  ```bash
  LIZMAP_PROJECTS=/home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/instances
  LIZMAP_DIR=/home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap 
  
  ```
* Copy the `plugins` folder from the `SAGTA` plugin folder into the plugin directory.
  ```bash
  cp -r /home/${user}/deployment/map_downloader/SAGTA/qgisserver_plugins/* ./lizmap/plugins/
  ```

* Copy the QGIS projects from the QGIS projects from the `SAGTA` repository. 
  ```bash
  cp -r /home/${user}/deployment/map_downloader/SAGTA/projects/* ./lizmap/instances/
  ```
* Get the services up by running 
  ```bash
  docker-compose up -d
  ```
* The default login credentials are `admin:admin`
* Stop the services running to enable the profile tool.
  ```bash
  docker-compose stop
  ```
* To activate the Profile tool follow the instructions specified in 
[profile-plugin](https://github.com/kartoza/SAGTA/tree/main/lizmap_plugins/profile_tool/README.md)
* Access the services from the URL http://localhost

#### SAGTA Oauth Deployment

The instance deployed above will have all the plugins available but will use the normal login
to the platform. In order to authenticate with the [SAGTA](https://sagta.org.za/) domain a few
changes are needed. These changes are based on https://github.com/kartoza/lizmap-web-client

* Make sure the services are not running: 
  ```bash
  docker-compose stop
  ```
* Open the `docker-compose.yml` file to make some changes
* Add the following environment variables to the `lizmap` service in the `docker-compose.yml`
  ```bash
    CLIENT_ID: add a value here 
    CLIENT_SECRET: add a value here
    SAGTA_URL: https://sagta.org.za
    REDIRECT_URI: https://maps.sagta.org.za/
    MEMBER_USERNAME: sagta_mapdownloader
    MEMBER_PASSWORD: add a password here
  ```
* Adjust the volumes section in `lizmap` service in the `docker-compose.yml`
```bash
    /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/modules/lizmap:/www/lizmap/modules/lizmap
    /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/modules/view/controllers:/www/lizmap/modules/view/controllers
```
* Update the repository adding changes from https://github.com/kartoza/lizmap-web-client
  ```bash
  cd /home/${user}/deployment/map_downloader/
  git clone git@github.com:kartoza/lizmap-web-client.git
  cd lizmap-web-client
  cp -r ./lizmap/modules/lizmap/module.xml /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/modules/lizmap/
  cp -r ./lizmap/modules/lizmap/classes/sagta.class.php /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/modules/lizmap/classes
  cp -r ./lizmap/modules/lizmap/templates/user_menu.tpl /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/modules/lizmap/templates/
  cp -r ./lizmap/modules/view/controllers/default.classic.php /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/modules/view/controllers/
  cp -r ./lizmap/modules/view/controllers/lizMap.classic.php /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/modules/view/controllers/
  cp -r ./lizmap/var/config/admin/auth.coord.ini.php /home/${user}/deployment/map_downloader/lizmap-docker-compose/lizmap/var/lizmap-config/admin/
  ```
* Start the services again
  ```bash
  cd /home/${user}/deployment/map_downloader/lizmap-docker-compose
  docker compose up -d
  
  ```


