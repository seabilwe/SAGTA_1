# Deployment Setup

This setup describes how to configure a working example of  QGIS projects
and manipulating them on the desktop.

The QGIS projects primarily use local data, remote data (from maps.kartoza and external providers).
Some projects also require custom scripts to render properly i.e labels in topographic layouts.

# Procedure

* Git clone the SAGTA repository.
* Copy the QGIS scripts and add them in QGIS as 
[custom functions](https://www.qgistutorials.com/en/docs/3/custom_python_functions.html)
* Open the QGIS projects and start interacting with them.

**Note:** We only commit the QGIS projects when significant changes have been made to them
and annotate the commit message explicitly so that we can revert to a last known working
version. All custom scripts in QGIS are converted to QGIS Server plugins to be used
