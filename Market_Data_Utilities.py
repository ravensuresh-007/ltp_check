import pandas as pd
import json
from time import sleep
from typing import Union
from datetime import datetime
from functools import wraps
from typing import Any, Dict
import random



from Supplement import Utilities as Ut


def Get_OHLC(Bt, Ins_Token, Exchange_Segment, Start_Time, End_Time,Compression_Value=60):
    response = Bt.get_ohlc(
        exchangeSegment=Exchange_Segment,
        exchangeInstrumentID=Ins_Token,
        startTime=Start_Time,
        endTime=End_Time,
        compressionValue=Compression_Value)
    print("OHLC: " + str(response))
    # Response_Json = response.json()
    # print(Response_Json)
    Result = response["result"]
    # print(Result)
    m = Result["dataReponse"]
    # ydf = pd.DataFrame(m)

    y = m.split(',')

    df = pd.DataFrame(y)

    df = df[0].str.split('|', expand=True)

    # Drop the last empty column (due to the trailing pipe in the data)
    df.drop(df.columns[-1], axis=1, inplace=True)
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Oi']

    df["Low"] = df["Low"].astype(float)
    df["High"] = df["High"].astype(float)
    df["Close"] = df["Close"].astype(float)
    df["Ins_Token"] = Ins_Token

    return df


def Fetch_Ltp(Bt, Exch_Seg, U_Token):
    Str_Token = str(U_Token)
    instruments = [{'exchangeSegment': Exch_Seg, 'exchangeInstrumentID': Str_Token}]

    response = Bt.get_quote(Instruments=instruments, xtsMessageCode=1501, publishFormat='JSON')
    # print(response)

    x = response["result"]

    k = x["listQuotes"]

    z = k[0]

    data = json.loads(z)

    LastTradedPrice = data['LastTradedPrice']
    return LastTradedPrice


def Fetch_Index_Atm_Strike(Market_Xt,Indx = "NIFTY", Excahnge_Segment =1):
    Indx_Dict = Ut.Index_Dict
    Toke = Indx_Dict[Indx]["Tok"]
    Point_P_Stp = Indx_Dict[Indx]["Points_Per_Step"]
    LastTradedPrice = Fetch_Ltp(Market_Xt, Excahnge_Segment, Toke)
    Atm_Strike = (int(LastTradedPrice / Point_P_Stp) + 1) * Point_P_Stp

    return Atm_Strike


def Old_Get_Top_Index_Expiry_List(DF, Indx):
    Index_Filtered_DF = DF[(DF['Und_Instrument'] == Indx)]
    Index_Unq_Expr_List = sorted(Index_Filtered_DF["Expiry_Short"].unique())
    Index_Top2_Expr_List = Index_Unq_Expr_List[:2]
    return Index_Top2_Expr_List


def Trailing_Stop_Loss(Market_Xt, Instrument_Token, Entry_Traded_Price, Trail_Points, Exch_Segment,
                       Check_Interval=1, Trailing_Start_Points=0):
    Highest_Price = Entry_Traded_Price
    Stop_Loss_Price = Entry_Traded_Price - Trail_Points
    Trailing_Stop_Triggered = False

    Stop_Loss_Initiation_Price = Entry_Traded_Price + Trailing_Start_Points

    if Trailing_Start_Points == 0:
        Ready_For_Trailing_Stop_Loss = True

    else:
        Ready_For_Trailing_Stop_Loss = False

    while not Ready_For_Trailing_Stop_Loss:

        Current_Price = Fetch_Ltp(Market_Xt, Exch_Segment, Instrument_Token)

        if Current_Price >= Stop_Loss_Initiation_Price:
            Ready_For_Trailing_Stop_Loss = True

        sleep(Check_Interval)

    while Ready_For_Trailing_Stop_Loss and not Trailing_Stop_Triggered:

        Current_Price = Fetch_Ltp(Market_Xt, Exch_Segment, Instrument_Token)

        if Current_Price > Highest_Price:
            Highest_Price = Current_Price
            Stop_Loss_Price = Highest_Price - Trail_Points
            print("Updated highest price and stop-loss")

        print(f"Current price: {Current_Price}")
        print(f"Trailing Stop Loss_Price: {Stop_Loss_Price}")

        if Current_Price <= Stop_Loss_Price:
            print("Trailing Stop loss triggered! ")
            Trailing_Stop_Triggered = True

        sleep(Check_Interval)
    return Trailing_Stop_Triggered


def Get_Index_List(Bt,exchangeSegment=1):
    response = Bt.get_index_list(exchangeSegment)
    print('Index List:', str(response))


def Get_Series(Bt,exchangeSegment=1):
    response = Bt.get_series(exchangeSegment)
    print('Series:', str(response))


def Get_Expiry_Dates(Bt, Exch_Seg=2, Series='OPTIDX', Symbol='NIFTY'):
    response = Bt.get_expiry_date(
        exchangeSegment=Exch_Seg,
        series=Series,
        symbol=Symbol)
    return response


def Get_Option_Symbol_Details(Bt, strikePrice, exchangeSegment=2, series='OPTIDX', symbol='NIFTY',
                              expiryDate='29Aug2024',
                              optionType='CE'):
    Symbol_Details = Bt.get_option_symbol(
        exchangeSegment=exchangeSegment,
        series=series,
        symbol=symbol,
        expiryDate=expiryDate,
        optionType=optionType,
        strikePrice=strikePrice)

    return Symbol_Details


def Get_Nearest_Expiry_From_Market_Data(Bt, Exch_Seg=2, Series='OPTIDX', Symbol='NIFTY'):
    x = Get_Expiry_Dates(Bt, Exch_Seg, Series, Symbol)
    xz = x["result"]
    Nearest_Expiry = min(xz)
    return Nearest_Expiry


def Format_Date_For_Finding_Symbol(Sel_Date):
    Formatted_Date = Ut.Convert_Date_Format_For_Expiry(Sel_Date)
    return Formatted_Date


def Get_Option_Symbol_Token(Symbol_Details):
    Symbol_Token = Symbol_Details['result'][0]['ExchangeInstrumentID']

    return Symbol_Token


def Get_Nearest_Expiry_Token(Bt, strikePrice, Exch_Seg=2, Series='OPTIDX', Symbol='NIFTY', optionType='CE'):
    Nearest_Expiry_Date = Get_Nearest_Expiry_From_Market_Data(Bt, Exch_Seg, Series, Symbol)
    Formatted_Date = Format_Date_For_Finding_Symbol(Nearest_Expiry_Date)
    Symbol_Token = Get_Option_Symbol_Token(
        Get_Option_Symbol_Details(Bt, strikePrice, Exch_Seg, Series, Symbol,
                                  Formatted_Date,
                                  optionType))

    return Symbol_Token

def Get_Latest_Expiry_Dates(Bt, Exch_Seg=2, Series='OPTIDX', Symbol='NIFTY',Count=2):
    Expiry_List = Get_Expiry_Dates(Bt, Exch_Seg, Series, Symbol)
    Sorted_Expiry_List = sorted(Expiry_List["result"])
    Latest_Expiry_List = Sorted_Expiry_List[:Count]

    return Latest_Expiry_List

def Custom(Ltp,Rebound_Points,Trailing_Points,Check_Interval,Activation_Price):
    Lowest_Price = float("inf")
    Ready_To_Trade = False

    if Ltp <= Activation_Price:
        Ready_To_Trade = True


    Lowest_Price = Ltp if Ltp<Lowest_Price else Lowest_Price

    pass

def Trailing_Down(Bt,Exch_Segment,Instrument_token,Down_Trailing_Points,Check_Interval):
    Lowest_Price = float("inf")
    Trailing_Triggered = False

    while not Trailing_Triggered:
        Ltp = Fetch_Ltp(Bt, Exch_Segment, Instrument_token)

        Lowest_Price = Ltp if Ltp < Lowest_Price else Lowest_Price
        Trigger_Price = Lowest_Price + Down_Trailing_Points

        if Ltp >= Trigger_Price:
            Trailing_Triggered = True
            return Trailing_Triggered

        sleep(Check_Interval)

    return Trailing_Triggered

def Trailing_Up(Bt,Instrument_token,Up_Trailing_Points,Exch_Segment =2,Check_Interval=1):
    Highest_Price = -float("inf")
    Trailing_Triggered = False

    while not Trailing_Triggered:
        Ltp = Fetch_Ltp(Bt, Exch_Segment, Instrument_token)

        Highest_Price = Ltp if Ltp > Highest_Price else Highest_Price
        Trigger_Price = Highest_Price - Up_Trailing_Points

        if Ltp <= Trigger_Price:
            Trailing_Triggered = True
            return Trailing_Triggered

        sleep(Check_Interval)

    return Trailing_Triggered

def Get_Index_Strike_List(Indx, Bt, Indx_Dict):
    Toke = Indx_Dict[Indx]["Tok"]
    Point_P_Stp = Indx_Dict[Indx]["Points_Per_Step"]
    LastTradedPrice = Fetch_Ltp(Bt,1, Toke)
    Atm_Strike = (int(LastTradedPrice / Point_P_Stp) + 1) * Point_P_Stp
    print(Atm_Strike)
    Strike_List = Ut.Generate_Range(Atm_Strike, 5, Point_P_Stp)

    return Strike_List

def Get_Future_Symbol_Token(Bt,expiryDate,   Symbol='NIFTY'):
    response = Bt.get_future_symbol(
        exchangeSegment=2,
        series='FUTIDX',
        symbol=Symbol,
        expiryDate=expiryDate)
    # print('Future Symbol:', str(response))

    Symbol_Token = response["result"][0]["ExchangeInstrumentID"]

    return Symbol_Token

def Get_Open_Price(Bt, Exch_Seg, U_Token):
    Str_Token = str(U_Token)
    instruments = [{'exchangeSegment': Exch_Seg, 'exchangeInstrumentID': Str_Token}]

    response = Bt.get_quote(Instruments=instruments, xtsMessageCode=1501, publishFormat='JSON')
    print(response)

    x = response["result"]

    k = x["listQuotes"]

    z = k[0]

    data = json.loads(z)

    Open_Price = data['Open']
    return Open_Price

def Get_Master_Instruments(Bt):
    """Get Master Instruments Request"""
    exchangesegments = [Bt.EXCHANGE_NSECM, Bt.EXCHANGE_NSEFO]
    response = Bt.get_master(exchangeSegmentList=exchangesegments)
    print("Master: " + str(response))
    res = response["result"]
    rows = res.strip().split('\n')

    # Step 2: Split each row by the pipe `|` delimiter
    data = [row.split('|') for row in rows]

    # Step 3: Create a DataFrame from the data
    df = pd.DataFrame(data, columns=[
        'Market', 'InstrumentID', 'Segment', 'Symbol', 'InstrumentName',
        'InstrumentType', 'Underlying', 'Token', 'LTP', 'Change', 'OpenInterest',
        'PriceBandLower', 'PriceBandUpper', 'LotSize', 'Multiplier', 'ISIN',
        'TradingSymbol', 'ExpiryDate', 'StrikePrice', 'OptionType', 'Name',
        'OptionCode', 'InstrumentCode'
    ])


    return df

def Fetch_Ltp_New(bt_client, exch_seg: str, u_token: Union[str, int], max_attempts: int = 100, delay: int = 1) -> float:

    str_token = str(u_token)
    instruments = [{'exchangeSegment': exch_seg, 'exchangeInstrumentID': str_token}]

    for attempt in range(max_attempts):
        try:
            # Attempt to fetch quote
            response = bt_client.get_quote(
                Instruments=instruments,
                xtsMessageCode=1501,
                publishFormat='JSON'
            )

            # Process response
            x = response["result"]
            k = x["listQuotes"]
            z = k[0]
            data = json.loads(z)
            last_traded_price = data['LastTradedPrice']

            # If successful, return the LTP
            return last_traded_price

        except Exception as e:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"[{current_time}] Connection timed out. Reconnecting... (Attempt {attempt + 1}/{max_attempts})")

            # If this was the last attempt, raise the error
            if attempt == max_attempts - 1:
                raise RuntimeError(f"Failed to fetch LTP after {max_attempts} attempts")

            # Wait before next attempt
            sleep(delay)

    # This line should never be reached due to the raise in the loop
    raise RuntimeError("Unexpected error in fetch_ltp")


def Fetch_Multi_Ltp_Old(Bt,instruments):
    # Exch_Seg = 1
    # Instruments = [{'exchangeSegment': Exch_Seg, 'exchangeInstrumentID': "2885"},{'exchangeSegment': Exch_Seg, 'exchangeInstrumentID': "22"}]
    Ltp_Dict = {}

    response = Bt.get_quote(Instruments=instruments, xtsMessageCode=1501, publishFormat='JSON')
    x = response["result"]
    print(x)

    k = x["listQuotes"]
    print(k)
    for i in range (len(instruments)):
        z = k[i]
        data = json.loads(z)
        LastTradedPrice = data['LastTradedPrice']
        Ltp_Dict[instruments[i]['exchangeInstrumentID']] = LastTradedPrice
    return Ltp_Dict


def Fetch_Multi_Ltp(Bt, instruments):

    response = Bt.get_quote(
        Instruments=instruments,
        xtsMessageCode=1501,
        publishFormat='JSON'
    )

    # Extract quotes and create price dictionary
    quotes = response["result"]["listQuotes"]
    prices = {}

    for quote, instrument in zip(quotes, instruments):
        data = json.loads(quote)
        instrument_id = instrument['exchangeInstrumentID']
        prices[instrument_id] = data['LastTradedPrice']

    return prices


"""Search Instrument by Scriptname Request"""

def Search_Scrip_By_Name(Bt,Search_string):
    response = Bt.search_by_scriptname(searchString=Search_string)
    print('Search By Symbol :', str(response))

def Search_Scrip_By_Id(Bt,Scrip_Id):
    """Search Instrument by ID Request"""
    response = Bt.search_by_instrumentid(Instruments=Scrip_Id)
    # print('Search By Instrument ID:', str(response))

    return response


import json
import time
from functools import wraps
from typing import Any, Dict
import random


def retry_with_backoff(max_retries=5, initial_delay=1, max_delay=10, exponential_base=2):
    """
    Decorator for implementing retry logic with exponential backoff
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for retry in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e
                    if retry + 1 == max_retries:
                        raise

                    # Calculate delay with jitter
                    jitter = random.uniform(0, 0.1 * delay)
                    current_delay = min(delay + jitter, max_delay)

                    time.sleep(current_delay)
                    delay = min(delay * exponential_base, max_delay)

            raise last_exception

        return wrapper

    return decorator


def validate_response(response: Dict[str, Any]) -> None:
    """
    Validates the API response structure
    """
    if not isinstance(response, dict):
        raise ValueError("Response is not a dictionary")

    if 'result' not in response:
        raise ValueError("Response missing 'result' key")

    if 'listQuotes' not in response['result']:
        raise ValueError("Response missing 'listQuotes' in result")

    if not response['result']['listQuotes']:
        raise ValueError("Empty quotes list in response")


@retry_with_backoff(max_retries=5, initial_delay=1, max_delay=10)
def Fetch_Ltp_With_Retry(Bt, Exch_Seg: str, U_Token: str) -> float:
    """
    Fetches Last Traded Price with retry logic and error handling

    Args:
        Bt: Broker trading object
        Exch_Seg: Exchange segment
        U_Token: Instrument token

    Returns:
        float: Last traded price

    Raises:
        ValueError: If response validation fails
        Exception: For other errors after max retries
    """
    try:
        # Convert token to string and create instruments list
        Str_Token = str(U_Token)
        instruments = [{
            'exchangeSegment': Exch_Seg,
            'exchangeInstrumentID': Str_Token
        }]

        # Get quote
        response = Bt.get_quote(
            Instruments=instruments,
            xtsMessageCode=1501,
            publishFormat='JSON'
        )

        # Validate response structure
        validate_response(response)

        # Parse quote data
        quote_data = json.loads(response["result"]["listQuotes"][0])

        if 'LastTradedPrice' not in quote_data:
            raise ValueError("LastTradedPrice not found in quote data")

        return float(quote_data['LastTradedPrice'])

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in response: {str(e)}")

    except Exception as e:
        raise

