# Deployment Setup

This setup describes how to configure a working example of  QGIS projects
and manipulating them on the desktop.

The QGIS projects primarily use local data, remote data (from maps.kartoza and external providers).
Some projects also require custom scripts to render properly i.e labels in topographic layouts.

# Procedure

* Git clone the SAGTA repository.
    ```bash
    git clone git@github.com:kartoza/SAGTA.git
    cd SAGTA
    ```
* Copy the QGIS scripts from the repository and add them to the correct folder in your
profile folder.
    ```bash
    cp ./qgis_desktop_setup/qgis_scripts/* /home/${user}/.local/share/QGIS/QGIS3/profiles/default/python/expressions
    ```

* Open the QGIS projects `./projects/mapdownloader` or `./projects/mapdownloader_public` using QGIS
Desktop and start interacting with the projects.

**Note:** We only commit the QGIS projects when significant changes have been made to them
and annotate the commit message explicitly so that we can revert to a last known working
version. All custom scripts in QGIS are converted to QGIS Server plugins to be used
