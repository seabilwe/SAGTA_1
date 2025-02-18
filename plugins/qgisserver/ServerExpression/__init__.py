# Import necessary libraries
import json
from datetime import datetime
from os import environ
from urllib import parse, request
from urllib.error import HTTPError
from math import floor
import ssl
from qgis.core import QgsMessageLog, Qgis, QgsExpression, QgsGeometry, QgsRectangle
from qgis.utils import qgsfunction
from qgis.server import *

def json_response(url):
    """
    Makes an HTTP request to the provided URL and returns the response text.
    
    Args:
        url (str): The URL to make the request to.
        
    Returns:
        str: The response text if the request is successful, None otherwise.
    """
    try:
        # Make the request and get the response
        data = request.urlopen(url)
        error_code = data.getcode()
    except HTTPError as error:
        error_code = error.code
    
    # If the request was successful, read and return the response
    if error_code == 200:
        response = data.read()
        response_text = response.decode('utf-8')
    else:
        response_text = None
    return response_text

def dd2dms(decimal_degree, is_annual_change=False):
    """
    Converts decimal degrees to degrees, minutes, and direction.
    
    Args:
        decimal_degree (float): The decimal degree value to convert.
        is_annual_change (bool): Flag to determine if it's for annual change (affects direction labeling).
        
    Returns:
        tuple: A tuple containing degrees, minutes, and direction (East/West or Eastwards/Westwards).
    """
    # Check if the input is a float, and try converting it if it's not
    if not isinstance(decimal_degree, float):
        try:
            decimal_degree = float(decimal_degree)
        except:
            QgsMessageLog.logMessage(f'ERROR: Could not convert {type(decimal_degree)} to float.', 'MagDecl', Qgis.Warning)
            return 0, 0, 0, ''
    
    # Determine the direction based on whether the value is positive (East) or negative (West)
    appendix = 'E' if decimal_degree >= 0 and not is_annual_change else 'W' if decimal_degree < 0 and not is_annual_change else 'E' if decimal_degree >= 0 else 'W'
    decimal_degree = abs(decimal_degree)  # Work with the absolute value for calculations
    
    # Calculate degrees and minutes
    degrees = int(floor(decimal_degree))
    minutes = (decimal_degree % 1.0) * 60

    # For West or East directions, return both degrees and minutes for declination
    if not is_annual_change and appendix in ['W', 'E']:
        return degrees, int(floor(minutes)), None, appendix
    else:
        # For annual change, return both degrees and minutes without seconds
        return degrees, int(floor(minutes)), None, appendix

@qgsfunction(args='auto', group='Kartoza')
def map_decl(center_lat, center_long, feature, parent):
    """
    Calculates the magnetic declination and annual change of the map centroid
    in the South African topo map format. It fetches data from NOAA's Geomagnetic
    Field Calculator API and formats it accordingly.
    
    Args:
        center_lat (float): Latitude of the map center.
        center_long (float): Longitude of the map center.
        feature: The feature being processed (for QGIS context).
        parent: Parent function for the QGIS expression context.
    
    Returns:
        str: A formatted string showing magnetic declination and annual change.
    """
    # Use an unverified SSL context to bypass certificate verification
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Get the current month to request accurate magnetic declination data
    now = datetime.now()
    
    # Prepare the parameters for the NOAA API request
    params = parse.urlencode({
        'lat1': center_lat, 
        'key': 'zNEw7', 
        'lon1': center_long, 
        'resultFormat': 'json', 
        'startMonth': now.month
    })
    
    # Build the URL for the NOAA magnetic declination calculator
    mag_url = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination?%s" % params
    
    # Call the function to fetch the response from the NOAA API
    mag_response_text = json_response(mag_url)
  
    # If we received a valid response
    if mag_response_text is not None:
        try:
            # Parse the response JSON and get the relevant data
            mag_response_json = json.loads(mag_response_text)["result"][0]
        except json.decoder.JSONDecodeError:
            # Handle JSON decoding error if the response is malformed
            QgsMessageLog.logMessage("Error accessing NOAA Magnetic Declination calculator.", 'MagDecl', Qgis.Warning)
            return "NOAA Magnetic Declination unavailable"
        
        # Extract the magnetic declination and annual change values
        magnetic_declination = mag_response_json.get("declination", 0)
        annual_change = mag_response_json.get("declination_sv", 0)

        # --- Southern Hemisphere Handling ---
        # If the map center is in the Southern Hemisphere, force both values to be westerly.
        if float(center_lat) < 0:
            magnetic_declination = -abs(magnetic_declination)
            annual_change = -abs(annual_change)
        
        # Convert both magnetic declination and annual change to degrees, minutes, and direction
        dms_magnetic_decl = dd2dms(round(magnetic_declination, 4))
        dms_annual_change = dd2dms(round(annual_change, 4), is_annual_change=True)
        
        # Format the output based on the direction (E/W for declination, E/W for annual change)
        formatted_label = (
            f"Mean magnetic declination {dms_magnetic_decl[0]}°{dms_magnetic_decl[1]}' {dms_magnetic_decl[3]}\n"
            f"Mean annual change {dms_annual_change[0]}°{dms_annual_change[1]}' {dms_annual_change[3]}"
        )
        
        return formatted_label
    else:
        # If no valid data is available, log the message and return a default message
        QgsMessageLog.logMessage("Magnetic declination data unavailable.", 'MagDecl', Qgis.Warning)
        return "Magnetic declination data unavailable"
        
class ServerExpressionPlugin:
    def __init__(self):
        QgsMessageLog.logMessage('Loading expressions', 'ServerExpression', Qgis.Info)
        QgsExpression.registerFunction(map_decl)

def serverClassFactory(serverIface):
    _ = serverIface
    return ServerExpressionPlugin()
