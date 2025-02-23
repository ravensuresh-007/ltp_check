from datetime import datetime
import configparser
from functools import wraps
import time
import json


from Xts_MarketData import Connect


def Fetch_Specific_Time_Xts_Format(year, month, day, hour, minute, second):
    specific_time = datetime(year, month, day, hour, minute, second)
    return specific_time.strftime('%b %d %Y %H%M%S')


Index_Dict = {"NIFTY": {"Tok": 26000, "Points_Per_Step": 50, "Lot_Size": 75,"Base_Exch_Seg" : 1,"Derv_Exch_Seg":2,"Option_Series" : "OPTIDX"},
              "BANKNIFTY": {"Tok": 26001, "Points_Per_Step": 100, "Lot_Size": 30,"Base_Exch_Seg" : 1,"Derv_Exch_Seg":2,"Option_Series" : "OPTIDX"},
              "FINNIFTY": {"Tok": 26034, "Points_Per_Step": 50, "Lot_Size": 25,"Base_Exch_Seg" : 1,"Derv_Exch_Seg":2,"Option_Series" : "OPTIDX"},
              "SENSEX" : {"Tok": 26065, "Points_Per_Step": 100, "Lot_Size": 30,"Base_Exch_Seg" : 11,"Derv_Exch_Seg":12,"Option_Series" : "IO"}
              }


def Convert_Date_Format_For_Expiry(date_string):
    date_object = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
    formatted_date = date_object.strftime('%d%b%Y')

    return formatted_date


def Initial_Login():
    Config = configparser.ConfigParser()


    # Read the config file
    Config.read('config.ini')

    ClientID = Config.get('Miscellaneous', 'ClientID')

    API_KEY_MarketData = Config.get('Market_Data_API', 'API_KEY_MarketData')
    API_SECRET_MarketData = Config.get('Market_Data_API', 'API_SECRET_MarketData')
    source = "WEBAPI"

    # Interactive API Credentials
    API_KEY_Interactive = Config.get('Interactive_Data_API', 'API_KEY_Interactive')
    API_SECRET_Interactive = Config.get('Interactive_Data_API', 'API_SECRET_Interactive')

    # Market_Data_Object
    Market_Xt = Connect.XTSConnect(API_KEY_MarketData, API_SECRET_MarketData, source)

    print(Market_Xt)
    # Login for authorization token
    response = Market_Xt.marketdata_login()

    print(response)

    set_marketDataToken = response['result']['token']
    set_muserID = response['result']['userID']
    print("Market_Data Login: ", response)

    Interactive_Xt = Connect.XTSConnect(API_KEY_Interactive, API_SECRET_Interactive, source)
    response = Interactive_Xt.interactive_login()

    set_Interactive_DataToken = response['result']['token']
    set_Int_userID = response['result']['userID']
    print("Interactive Login: ", response)

    Connect_Dict = {"Market_Xt": Market_Xt, "Interactive_Xt": Interactive_Xt,
                    "set_marketDataToken": set_marketDataToken, "set_muserID": set_muserID,
                    "set_Interactive_DataToken": set_Interactive_DataToken, "set_Int_userID": set_Int_userID,
                    "ClientID": ClientID}

    return Connect_Dict

def Generate_Range(Mid_value, Count, Step):
    return list(range(Mid_value - (Count * Step), Mid_value + (Count * Step) + 1, Step))

def Fetch_Begin_End_Time():
    now = datetime.now()
    Begin_Year = now.year
    Begin_Day = now.day
    Begin_Month = now.month
    Begin_Hour = 9
    Begin_Minute = 15


    End_Year = now.year
    End_Month = now.month
    End_Day = now.day
    End_Hour = 15
    End_Minute = 30



    Begin_Time = Fetch_Specific_Time_Xts_Format(Begin_Year, Begin_Month, Begin_Day, Begin_Hour, Begin_Minute, 0)
    End_Time = Fetch_Specific_Time_Xts_Format(End_Year, End_Month, End_Day, End_Hour, End_Minute, 0)

    Time_Dict = {"Begin_Time": Begin_Time, "End_Time": End_Time}
    return Time_Dict




def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' took {execution_time:.4f} seconds to execute.")
        return result
    return wrapper

def Initial_Login_Modified(client_id):
    """
    Initialize login for both Market Data and Interactive APIs
    Args:
        client_id (str): The client ID to use for authentication
    Returns:
        dict: Connection details and tokens
    """
    try:
        Config = configparser.ConfigParser()
        Config.read('config.ini')

        # Get user configuration
        source = Config.get('user', 'source')

        # Get client credentials
        if not Config.has_section(client_id):
            raise ValueError(f"Client ID {client_id} not found in config")

        client_name = Config.get(client_id, 'client_name')

        # Extract API credentials
        API_KEY_MarketData = Config.get(client_id, 'market_data_api_key')
        API_SECRET_MarketData = Config.get(client_id, 'market_data_api_secret')
        API_KEY_Interactive = Config.get(client_id, 'interactive_api_key')
        API_SECRET_Interactive = Config.get(client_id, 'interactive_api_secret')

        # Market Data Login
        Market_Xt = Connect.XTSConnect(API_KEY_MarketData, API_SECRET_MarketData, source)
        market_response = Market_Xt.marketdata_login()

        print("Market_Data Login: ", market_response)

        set_marketDataToken = market_response['result']['token']
        set_muserID = market_response['result']['userID']

        # Interactive Login
        Interactive_Xt = Connect.XTSConnect(API_KEY_Interactive, API_SECRET_Interactive, source)
        interactive_response = Interactive_Xt.interactive_login()

        print("Interactive Login: ", interactive_response)

        set_Interactive_DataToken = interactive_response['result']['token']
        set_Int_userID = interactive_response['result']['userID']

        # Create connection dictionary
        Connect_Dict = {
            "Market_Xt": Market_Xt,
            "Interactive_Xt": Interactive_Xt,
            "set_marketDataToken": set_marketDataToken,
            "set_muserID": set_muserID,
            "set_Interactive_DataToken": set_Interactive_DataToken,
            "set_Int_userID": set_Int_userID,
            "ClientID": client_id,
            "ClientName": client_name
        }

        return Connect_Dict

    except configparser.Error as e:
        print(f"Config file error: {e}")
        raise
    except Exception as e:
        print(f"Error during login: {e}")
        raise

