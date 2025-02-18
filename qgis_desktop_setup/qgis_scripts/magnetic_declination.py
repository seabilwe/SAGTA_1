# Import necessary libraries
import json
from datetime import datetime
from urllib import parse, request
from urllib.error import HTTPError
from math import floor
import ssl
from qgis.core import QgsMessageLog, Qgis
from qgis.utils import qgsfunction

def json_response(url):
    """
    Makes an HTTP request to the provided URL and returns the response text.
    
    Args:
        url (str): The URL to request.
        
    Returns:
        str: The response text if the request is successful, otherwise None.
    """
    try:
        # Open the URL and retrieve the response
        data = request.urlopen(url)
        error_code = data.getcode()
    except HTTPError as error:
        # In case of an HTTP error, capture the error code
        error_code = error.code
    
    # If the response code is 200 (OK), read and decode the response
    if error_code == 200:
        response = data.read()
        return response.decode('utf-8')
    else:
        # Return None if the response was not successful
        return None

def dd2dms(decimal_degree, is_annual_change=False):
    """
    Converts a decimal degree value to degrees, minutes, and a direction (E or W).
    
    Args:
        decimal_degree (float): The decimal degree value to convert.
        is_annual_change (bool): Flag indicating if this value is for annual change 
                                 (affects any custom logic if needed).
    
    Returns:
        tuple: A tuple containing degrees, minutes, None (placeholder), and 
               a single-letter direction ('E' or 'W').
    """
    # Ensure the input is a float; if not, attempt conversion
    if not isinstance(decimal_degree, float):
        try:
            decimal_degree = float(decimal_degree)
        except:
            # Log an error if conversion fails and return a default tuple
            QgsMessageLog.logMessage(
                f'ERROR: Could not convert {type(decimal_degree)} to float.',
                'MagDecl', Qgis.Warning
            )
            return 0, 0, 0, ''
    
    # Determine the direction letter based on the sign of the value:
    # Positive values indicate 'E' (east), negative values indicate 'W' (west)
    direction = 'E' if decimal_degree >= 0 else 'W'
    
    # Use the absolute value for conversion to degrees and minutes
    decimal_degree = abs(decimal_degree)
    
    # Calculate whole degrees by flooring the decimal degree
    degrees = int(floor(decimal_degree))
    # Calculate minutes by taking the fractional part and multiplying by 60
    minutes = (decimal_degree % 1.0) * 60
    
    # Return the calculated degrees, minutes (floored), a placeholder (None), and the direction letter
    return degrees, int(floor(minutes)), None, direction

@qgsfunction(args='auto', group='Kartoza')
def map_decl(center_lat, center_long, feature, parent):
    """
    Calculates the magnetic declination and annual change for the map's centroid.
    Forces the output to be westerly (W) for the Southern Hemisphere as per 
    South African convention.
    
    Args:
        center_lat (float): Latitude of the map center.
        center_long (float): Longitude of the map center.
        feature: The feature being processed (provided by QGIS).
        parent: Parent function for the QGIS expression context.
    
    Returns:
        str: A formatted string displaying the magnetic declination and annual change.
    """
    # Bypass SSL certificate verification by using an unverified SSL context
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Get the current date and time to use the current month for the API call
    now = datetime.now()
    
    # Prepare the parameters for the NOAA API request:
    # - 'lat1' and 'lon1': center latitude and longitude.
    # - 'key': API key for NOAA.
    # - 'resultFormat': output format requested as JSON.
    # - 'startMonth': current month.
    params = parse.urlencode({
        'lat1': center_lat,
        'lon1': center_long,
        'key': 'zNEw7',  # NOAA API key
        'resultFormat': 'json',
        'startMonth': now.month
    })
    
    # Construct the NOAA Geomagnetic Field Calculator URL with the query parameters
    mag_url = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination?%s" % params
    
    # Make the HTTP request and fetch the API response
    mag_response_text = json_response(mag_url)
    if not mag_response_text:
        # Log and return a message if no response was received
        QgsMessageLog.logMessage(
            "Magnetic declination data unavailable.", 'MagDecl', Qgis.Warning
        )
        return "Magnetic declination data unavailable"
    
    # Try to parse the JSON response from NOAA
    try:
        mag_response_json = json.loads(mag_response_text)["result"][0]
    except json.decoder.JSONDecodeError:
        # Log an error if JSON parsing fails
        QgsMessageLog.logMessage(
            "Error accessing NOAA Magnetic Declination calculator.", 'MagDecl', Qgis.Warning
        )
        return "NOAA Magnetic Declination unavailable"
    
    # Extract the magnetic declination and the mean annual change from the response
    magnetic_declination = mag_response_json.get("declination", 0.0)
    annual_change = mag_response_json.get("declination_sv", 0.0)
    
    # For the Southern Hemisphere (e.g., South Africa):
    # If the center latitude is negative, force both values to be westerly (W)
    if float(center_lat) < 0:
        magnetic_declination = -abs(magnetic_declination)
        annual_change       = -abs(annual_change)
    
    # Convert the decimal values to degrees, minutes, and a direction letter (E or W)
    dms_magnetic_decl = dd2dms(round(magnetic_declination, 4))
    dms_annual_change = dd2dms(round(annual_change, 4), is_annual_change=True)
    
    # Format the final output string for display
    formatted_label = (
        f"Mean magnetic declination {dms_magnetic_decl[0]}°{dms_magnetic_decl[1]}' {dms_magnetic_decl[3]}\n"
        f"Mean annual change {dms_annual_change[0]}°{dms_annual_change[1]}' {dms_annual_change[3]}"
    )
    
    # Return the formatted magnetic declination information
    return formatted_label
