# SAGTA
SAGTA Map downloader

## Setup

This repo is based on the work provided from [lizmap](git@github.com:3liz/lizmap-docker-compose.git)
To get a running version of the repo use the following instructions

* Clone the sagta repository into a separate folder.

    ```bash
    git clone git@github.com:kartoza/SAGTA.git
    ```
* Clone the lizmap github repository

    ```bash
    git clone git@github.com:3liz/lizmap-docker-compose.git
    ```
* Navigate to the `lizmap-docker` folder
* Run `make configure` to generate the configs in the folder.
* Remove the test QGIS projects from the repo.
    ```bash
    rm -rf lizmap/instances/*
    ```
* Download the latest compose file from the SAGTA repo to overwrite the 
current one.

  ```bash
  wget https://raw.githubusercontent.com/kartoza/SAGTA/main/deployment/docker-compose.yml
  ```
* Download the `env.example` from the SAGTA repo and make sure to adjust the
env variable to match the path for the folders in the current directory

  ```bash
  wget https://raw.githubusercontent.com/kartoza/SAGTA/main/deployment/env.example -O .env
  ```
**Note:** Make sure you adjust the two variables to match the proper paths.

  ```bash
  LIZMAP_PROJECTS=/tmp/lizmap/docker-compose/lizmap/instances
  LIZMAP_DIR=/tmp/lizmap/docker-compose/lizmap 
  ```
* Copy the `plugins` folder from the [SAGTA plugin folder](https://github.com/kartoza/SAGTA/tree/main/plugins) 
you have cloned previously into the folder `lizmap/plugins/`
* Copy the QGIS projects from the [SAGTA QGIS projects](https://github.com/kartoza/SAGTA/tree/main/projects/map_downloader) 
you have previously cloned to `lizmap/instances/`
* Get the services up by running `docker-compose up -d`
* The default login credentials is `admin:admin`
* To activate the Profile tool follow the instructions specified in 


