##############################################################
### HELPERS FOR GLOBAL FUNCTIONS AND METHODS
##############################################################
from xmlrpc.client import _datetime
import frappe
from datetime import datetime,timedelta
import pytz

###-START=> FUNCTION TO GET UTC DATE TIME WRITTEN BY HASEEB
def get_current_date_iso(days_offset=0, time_str="00:00:00"):
    """*****Example usage*****
    current_date = get_current_date_iso()  # Today's date with default time (00:00:00)
    previous_date_with_time = get_current_date_iso(5, "15:30:45")  # 5 days ago with time 15:30:45
    print("Current Date:", current_date)
    print("Previous Date with Time:", previous_date_with_time)
    """

    # Parse the time_str into hours, minutes, and seconds
    try:
        hours, minutes, seconds = map(int, time_str.split(":"))
    except ValueError:
        raise ValueError("Invalid time format. Use HH:MM:SS format.")
    
    # Get the current date and time in UTC
    now_utc = datetime.now(pytz.utc)

    # Apply the offset in days
    adjusted_date = (now_utc - timedelta(days=days_offset)).replace(hour=hours, minute=minutes, second=seconds, microsecond=0)

    # Format the date in ISO 8601 format with milliseconds
    iso_date = adjusted_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    return iso_date

def get_current_date_time(days_offset=0, time_str="00:00:00"):
    """*****Example usage*****
    current_date = get_current_date_time()  # Today's date with default time (00:00:00)
    previous_date_with_time = get_current_date_time(5, "15:30:45")  # 5 days ago with time 15:30:45
    print("Current Date:", current_date)
    print("Previous Date with Time:", previous_date_with_time)
    """

    # Parse the time_str into hours, minutes, and seconds
    try:
        # hours, minutes, seconds = map(int, time_str.split(":"))
        hours, minutes, seconds = map(int, datetime.now().strftime("%H:%M:%S").split(":"))
        
    except ValueError:
        raise ValueError("Invalid time format. Use HH:MM:SS format.")
    
    # Get the current date and time in UTC
    now_utc = datetime.now(pytz.utc)

    # Apply the offset in days
    adjusted_date = (now_utc - timedelta(days=days_offset)).replace(hour=hours, minute=minutes, second=seconds, microsecond=0)

    # Format the date in desired format
    formatted_date = adjusted_date.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_date
