# magnetic_declination.py
from qgis.core import qgsfunction, QgsMessageLog, Qgis
import urllib.parse
import urllib.request
import json
from datetime import datetime
import ssl

@qgsfunction(args='auto', group='SAGTA')
def map_decl(center_lat, center_long, feature, parent):
    """
    Calculates the magnetic declination and annual change at the map center 
    (in South African topo map format), using NOAA’s API. 
    Returns a formatted string.
    """
    # Prepare date for NOAA request
    now = datetime.now()
    params = {
        'lat1': center_lat,
        'lon1': center_long,
        'model': 'WMM',
        'startYear': now.year,
        'startMonth': now.month,
        'startDay': now.day,
        'resultFormat': 'json',
        'key': 'zNEw7'
    }
    url = 'https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination?' + urllib.parse.urlencode(params)
    # Bypass any SSL issues
    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        response = urllib.request.urlopen(url, timeout=10)
        mag_data = json.loads(response.read().decode())
    except Exception as e:
        QgsMessageLog.logMessage(f"NOAA Magnetic Declination API error: {e}", 'MagDecl', Qgis.Warning)
        return "Magnetic declination data unavailable"
    
    # Extract declination and annual change from result
    try:
        result = mag_data['result'][0]
        decl = result.get('declination', 0.0)
        ann = result.get('declination_sv', 0.0)
    except Exception:
        QgsMessageLog.logMessage("Unexpected NOAA API response format", 'MagDecl', Qgis.Warning)
        return "Magnetic declination data unavailable"
    
    # Convert decimal degrees to D°M′ and E/W
    def dd2dms(val):
        hemi = 'W' if val < 0 else 'E'
        val = abs(val)
        deg = int(val)
        mins = int((val - deg) * 60)
        return deg, mins, hemi
    
    deg_decl, min_decl, hemi_decl = dd2dms(decl)
    deg_ann, min_ann, hemi_ann = dd2dms(ann)
    
    # Build formatted strings; omit "0°" for annual if zero
    decl_str = f"{deg_decl}°{min_decl}′ {hemi_decl} of True North"
    if deg_ann == 0:
        ann_str = f"{min_ann}′ {hemi_ann} per year"
    else:
        ann_str = f"{deg_ann}°{min_ann}′ {hemi_ann} per year"
    
    return f"Mean magnetic declination {decl_str}\nMean annual change {ann_str}"
