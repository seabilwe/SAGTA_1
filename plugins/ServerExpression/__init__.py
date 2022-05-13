import json
from datetime import datetime
from math import floor
from urllib import parse, request
from urllib.error import HTTPError

from qgis.core import QgsMessageLog, Qgis, QgsExpression
from qgis.utils import qgsfunction
from qgis.server import *


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


def decimal_degree_2dms(decimal_degree, direction='x'):
    if type(decimal_degree) != 'float':
        try:
            decimal_degree = float(decimal_degree)
        except Exception:
            print('\nERROR: Could not convert %s to float.' % (type(decimal_degree)))
            return 0
    if decimal_degree < 0:
        decimal_degree = -decimal_degree
        if direction == 'y':
            appendix = 'W'
        else:
            appendix = 'S'
    else:
        if direction == 'x':
            appendix = 'E'
        else:
            appendix = 'N'
    minutes = decimal_degree % 1.0 * 60
    seconds = minutes % 1.0 * 60
    dms_values = '{0}°{1}\'{2:2.3f}"{3}'.format(int(floor(decimal_degree)), int(floor(minutes)), seconds, appendix)

    return dms_values


@qgsfunction(
    args='auto', group='Your group', usesGeometry=False, referencedColumns=[], helpText='Define the help string here')
def map_decl(center_lat, center_long, feature, parent):
    dms_center_lat = decimal_degree_2dms(round(center_lat, 4))
    dms_center_long = decimal_degree_2dms(round(center_long, 4))
    elevation_url = "https://staging.geocontext.kartoza.com/api/v1/geocontext/value/group/%s/%s/elevation_group/?format=json" \
                    % (center_long, center_lat)
    elevation_response_text = json_response(elevation_url)
    if elevation_response_text is not None:
        elevation_response_json = json.loads(elevation_response_text)["service_registry_values"][0]
        elevation_value = elevation_response_json['value']
    else:
        elevation_value = 'None'
    current_date_time = datetime.now()
    month = current_date_time.month
    params = parse.urlencode({'lat1': center_lat, 'lon1': center_long, 'resultFormat': 'json', 'startMonth': month})
    mag_url = "http://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination?%s" % params
    mag_response_text = json_response(mag_url)
    if mag_response_text is not None:
        mag_response_json = json.loads(mag_response_text)["result"][0]
        magnetic_declination = mag_response_json["declination"]
        dms_magnetic_decl = decimal_degree_2dms(round(magnetic_declination, 4), direction='y')
        if elevation_value is None:
            formatted_label = '%s\n%s\n%s%s' % (
                dms_center_lat, dms_center_long, 'Mag Declination ', dms_magnetic_decl)
        else:
            formatted_label = '%s\n%s \n%s%s \n%s%s' % (
                dms_center_lat, dms_center_long, 'Elevation ', elevation_value, 'Mag Declination ',
                dms_magnetic_decl)
        QgsMessageLog.logMessage('Formatted label', formatted_label, Qgis.Info)
    else:
        formatted_label = None
        magnetic_declination = None

    return formatted_label


class ServerExpressionPlugin:
    def __init__(self):
        QgsMessageLog.logMessage('Loading expressions', 'ServerExpression', Qgis.Info)
        QgsExpression.registerFunction(map_decl)


def serverClassFactory(serverIface):
    _ = serverIface
    return ServerExpressionPlugin()
