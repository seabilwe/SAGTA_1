import json
from datetime import datetime
from os import environ
from urllib import parse, request
from urllib.error import HTTPError
from math import floor
import ssl
from qgis.core import QgsMessageLog, Qgis, QgsExpression, QgsGeometry, QgsRectangle
from qgis.utils import qgsfunction



def json_response(url):
    try:
        data = request.urlopen(url)
        error_code = data.getcode()
    except HTTPError as error:
        error_code = error.code
    if error_code == 200:
        response = data.read()
        response_text = response.decode('utf-8')
    else:
        response_text = None
    return response_text


def dd2dms(decimal_degree):
    if type(decimal_degree) != 'float':
        try:
            decimal_degree = float(decimal_degree)
        except:
            print('\nERROR: Could not convert %s to float.' % (type(decimal_degree)))
            return 0
    if decimal_degree < 0:
        decimal_degree = -decimal_degree
        appendix = 'W'
    else:
        appendix = 'E'
    minutes = decimal_degree % 1.0 * 60
    seconds = minutes % 1.0 * 60
    format_degree = int(floor(decimal_degree))
    format_minutes = int(floor(minutes))
    format_seconds = round(seconds, 2)
    return format_degree, format_minutes, format_seconds, appendix


@qgsfunction(args='auto', group='Kartoza')
def map_decl(center_lat, center_long, feature, parent):
    """
    Calculates the magnetic declination of the map centroid.
    <h2>Example usage:</h2>
    <ul>
      <li>map_decl(x(map_get( item_variables('Ortho'), 'map_extent_center')),y(map_get( item_variables('Ortho'), 'map_extent_center'))) </li>
      <li>map_decl('lat_centroid_function','long_centroid_function') </li>
    </ul>
    """
    ssl._create_default_https_context = ssl._create_unverified_context
    now = datetime.now()
    month = now.month
    month_day = now.day
    lat_hemisphere = 'S'
    long_hemisphere = 'E'
    mag_model = 'IGRF'
    mag_component = 'd'
    params = parse.urlencode({'lat1': abs(center_lat), 'lon1': abs(center_long), 'lat1Hemisphere': lat_hemisphere, 'lon1Hemisphere': long_hemisphere, 'startDay': month_day, 'model': mag_model, 'magneticComponent': mag_component, 'resultFormat': 'json', 'startMonth': month})
    mag_url = "http://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination?%s" % params
    mag_response_text = json_response(mag_url)
    if mag_response_text is not None:
        try:
            mag_response_json = json.loads(mag_response_text)["result"][0]
        except json.decoder.JSONDecodeError:
            print("There was a problem accessing NOAA Magnetic Declination calculators.")
            formatted_label = 'NOAA Magnetic Declination unavailable'
        else:
            magnetic_declination = mag_response_json["declination"]
            annual_change = mag_response_json["declnation_sv"]
            dms_magnetic_decl = dd2dms(round(magnetic_declination, 4))
            dms_annual_change = dd2dms(round(annual_change, 4))
            mag_declination_value = ''' %s° %s' %s ''' % (
                dms_magnetic_decl[0], dms_magnetic_decl[1], dms_magnetic_decl[3])
            mean_annual_change_value = ''' %s° %s' %s ''' % (
                dms_annual_change[0], dms_annual_change[1], dms_annual_change[3])
            formatted_label = '%s%s \n%s%s %s' % (
                'Mean magnetic declination ', mag_declination_value, 'Mean annual change', mean_annual_change_value,
                'per year')
    else:
        formatted_label = None
        magnetic_declination = None
    return formatted_label