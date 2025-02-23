import pandas as pd
import time
from datetime import datetime


def Cancel_Order(Bt, OrderID, Identi):
    response = Bt.cancel_order(
        appOrderID=OrderID,
        orderUniqueIdentifier=Identi,
        clientID=None)
    print("Cancel Order: ", response)


def Get_Order_Book_DF(Bt, ClientID):
    res = Bt.get_order_book(ClientID)
    my = res["result"]
    Order_Book_DF = pd.DataFrame(my)

    return Order_Book_DF


def Get_Order_Status(Bt, ClientID, OrderID):
    Order_Book_DF = Get_Order_Book_DF(Bt, ClientID)
    Order_Stat = Order_Book_DF.query("AppOrderID == @OrderID")["OrderStatus"].iloc[0]
    return Order_Stat


def Extract_Order_ID(Response):
    if Response['type'] != 'error':
        OrderID = Response['result']['AppOrderID']

        print(OrderID)

    else:
        OrderID = 0

    return OrderID


def Get_Order_Details(Bt, ClientID, OrderID):
    Order_Book_DF = Get_Order_Book_DF(Bt, ClientID)
    Order_Stat = Order_Book_DF.query("AppOrderID == @OrderID")["OrderStatus"].iloc[0]

    if Order_Stat == "Filled":
        print("Entry BUY Order Traded")

        Entry_Traded = True
        Entry_Traded_Price = round(
            float(Order_Book_DF.query("AppOrderID == @OrderID")["OrderAverageTradedPrice"].iloc[0]), 1)

    else:
        Entry_Traded = False
        Entry_Traded_Price = 0
        print("Entry BUY Order NOT Traded")

    Order_Details_Dict = {"Order_Stat": Order_Stat, "Entry_Traded": Entry_Traded,
                          "Entry_Traded_Price": Entry_Traded_Price}

    return Order_Details_Dict


def Place_Exit_Limit_Order(Interactive_Xt, Instrument_Token, clientID, Ext_Limit_Price, Qty,Ex_Segment = 2):
    Exch_Segment = Exchange_Seg_Conversion_For_Order(Ex_Segment)
    Instrument_Token = str(Instrument_Token)
    response = Interactive_Xt.place_order(
        exchangeSegment=Exch_Segment,
        exchangeInstrumentID=Instrument_Token,
        productType=Interactive_Xt.PRODUCT_NRML,
        orderType=Interactive_Xt.ORDER_TYPE_LIMIT,
        orderSide=Interactive_Xt.TRANSACTION_TYPE_SELL,
        timeInForce=Interactive_Xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=Qty,
        limitPrice=Ext_Limit_Price,
        stopPrice=0,
        orderUniqueIdentifier="Lmt_Ex_Order",
        clientID=clientID)

    print("Place Order: ", response)

    OrderID = Extract_Order_ID(response)

    return OrderID


def Place_Entry_Market_Order(Interactive_Xt, Instrument_Token, clientID, Qty):
    Instrument_Token = str(Instrument_Token)
    response = Interactive_Xt.place_order(
        exchangeSegment=Interactive_Xt.EXCHANGE_NSEFO,
        exchangeInstrumentID=Instrument_Token,
        productType=Interactive_Xt.PRODUCT_NRML,
        orderType=Interactive_Xt.ORDER_TYPE_MARKET,
        orderSide=Interactive_Xt.TRANSACTION_TYPE_BUY,
        timeInForce=Interactive_Xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=Qty,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="En_Mkt_Order",
        clientID=clientID)

    print("Place Order: ", response)

    OrderID = Extract_Order_ID(response)

    return OrderID


def Place_Exit_Market_Order(Interactive_Xt, Instrument_Token, clientID, Qty,Ex_Segment = 2):
    Exch_Segment = Exchange_Seg_Conversion_For_Order(Ex_Segment)
    Instrument_Token = str(Instrument_Token)
    response = Interactive_Xt.place_order(
        exchangeSegment=Exch_Segment,
        exchangeInstrumentID=Instrument_Token,
        productType=Interactive_Xt.PRODUCT_NRML,
        orderType=Interactive_Xt.ORDER_TYPE_MARKET,
        orderSide=Interactive_Xt.TRANSACTION_TYPE_SELL,
        timeInForce=Interactive_Xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=Qty,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="Ex_Mkt_Order",
        clientID=clientID)

    print("Place Order: ", response)

    OrderID = Extract_Order_ID(response)

    return OrderID


def Place_Entry_Limit_Order(Interactive_Xt, Instrument_Token, clientID, Qty, Entry_Limit_Price):
    Instrument_Token = str(Instrument_Token)
    response = Interactive_Xt.place_order(
        exchangeSegment=Interactive_Xt.EXCHANGE_NSEFO,
        exchangeInstrumentID=Instrument_Token,
        productType=Interactive_Xt.PRODUCT_NRML,
        orderType=Interactive_Xt.ORDER_TYPE_LIMIT,
        orderSide=Interactive_Xt.TRANSACTION_TYPE_BUY,
        timeInForce=Interactive_Xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=Qty,
        limitPrice=Entry_Limit_Price,
        stopPrice=0,
        orderUniqueIdentifier="Ex_Mkt_Order",
        clientID=clientID)

    print("Place Order: ", response)

    OrderID = Extract_Order_ID(response)

    return OrderID


def Cancel_All_Orders(Bt, Instrument_Token, Exch_Seg):
    response = Bt.cancelall_order(exchangeInstrumentID=Instrument_Token, exchangeSegment=Exch_Seg)
    return response


def Position_Convert_MIS_To_NRML(Bt, Exch_Seg, Instr_Tok, Convert_Qty, clientID):
    """Position Convert Request"""
    response = Bt.convert_position(
        exchangeSegment=Exch_Seg,
        exchangeInstrumentID=Instr_Tok,
        targetQty=Convert_Qty,
        isDayWise=True,
        oldProductType=Bt.PRODUCT_MIS,
        newProductType=Bt.PRODUCT_NRML,
        clientID=clientID)
    print("Position Convert: ", response)


def Position_Convert_NRML_To_MIS(Bt, Exch_Seg, Instr_Tok, Convert_Qty, clientID):
    """Position Convert Request"""
    response = Bt.convert_position(
        exchangeSegment=Exch_Seg,
        exchangeInstrumentID=Instr_Tok,
        targetQty=Convert_Qty,
        isDayWise=True,
        oldProductType=Bt.PRODUCT_NRML,
        newProductType=Bt.PRODUCT_MIS,
        clientID=clientID)
    print("Position Convert: ", response)


def Place_Buy_Market_Order(Interactive_Xt, Instrument_Token, clientID, Qty):
    Instrument_Token = str(Instrument_Token)
    response = Interactive_Xt.place_order(
        exchangeSegment=Interactive_Xt.EXCHANGE_NSEFO,
        exchangeInstrumentID=Instrument_Token,
        productType=Interactive_Xt.PRODUCT_NRML,
        orderType=Interactive_Xt.ORDER_TYPE_MARKET,
        orderSide=Interactive_Xt.TRANSACTION_TYPE_BUY,
        timeInForce=Interactive_Xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=Qty,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="En_Mkt_Order",
        clientID=clientID)

    print("Place Order: ", response)

    OrderID = Extract_Order_ID(response)

    return OrderID

def Place_Sell_Market_Order(Interactive_Xt, Instrument_Token, clientID, Qty):
    Instrument_Token = str(Instrument_Token)
    response = Interactive_Xt.place_order(
        exchangeSegment=Interactive_Xt.EXCHANGE_NSEFO,
        exchangeInstrumentID=Instrument_Token,
        productType=Interactive_Xt.PRODUCT_NRML,
        orderType=Interactive_Xt.ORDER_TYPE_MARKET,
        orderSide=Interactive_Xt.TRANSACTION_TYPE_SELL,
        timeInForce=Interactive_Xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=Qty,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="Ex_Mkt_Order",
        clientID=clientID)

    print("Place Order: ", response)

    OrderID = Extract_Order_ID(response)

    return OrderID

def Exchange_Seg_Conversion_For_Order(Ex_Seg):
    exchange_map = {
        1: "NSECM",
        2: "NSEFO",
        51: "MCXFO",
        11: "BSECM",
        12: "BSEFO"
    }
    return exchange_map.get(Ex_Seg, None)


def Place_SL_Lmt_Buy_Order(Interactive_Xt, Instrument_Token, clientID,Trigger_Price, Limit_Price, Qty,Ex_Segment = 2):
    Exch_Segment = Exchange_Seg_Conversion_For_Order(Ex_Segment)
    Instrument_Token = str(Instrument_Token)
    response = Interactive_Xt.place_order(
        exchangeSegment=Exch_Segment,
        exchangeInstrumentID=Instrument_Token,
        productType=Interactive_Xt.PRODUCT_NRML,
        orderType=Interactive_Xt.ORDER_TYPE_STOPLIMIT,
        orderSide=Interactive_Xt.TRANSACTION_TYPE_BUY,
        timeInForce=Interactive_Xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=Qty,
        limitPrice=Limit_Price,
        stopPrice=Trigger_Price,
        orderUniqueIdentifier="Sl_Lmt_Buy_Order",
        clientID=clientID)

    print("Place Order: ", response)

    OrderID = Extract_Order_ID(response)

    return OrderID

def Get_Order_Book_DF_New(bt_client, client_id, max_attempts=100, delay=1):

    for attempt in range(max_attempts):
        try:
            # Try to fetch order book
            response = bt_client.get_order_book(client_id)
            orders = response["result"]
            return pd.DataFrame(orders)

        except Exception as e:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"[{current_time}] Connection timed out. Reconnecting... (Attempt {attempt + 1}/{max_attempts})")

            if attempt == max_attempts - 1:
                print("Connection timed out. Max attempts reached.")
                return None


            time.sleep(delay)



def Place_Buy_Market_Order_New(Interactive_Xt, Instrument_Token, clientID, Qty):
    Instrument_Token = str(Instrument_Token)
    response = Interactive_Xt.place_order(
        exchangeSegment=Interactive_Xt.EXCHANGE_NSECM,
        exchangeInstrumentID=Instrument_Token,
        productType=Interactive_Xt.PRODUCT_MIS,
        orderType=Interactive_Xt.ORDER_TYPE_MARKET,
        orderSide=Interactive_Xt.TRANSACTION_TYPE_BUY,
        timeInForce=Interactive_Xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=Qty,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="En_Mkt_Order",
        clientID=clientID)

    print("Place Order: ", response)

    OrderID = Extract_Order_ID(response)

    return OrderID

def Place_Sell_Market_Order_New(Interactive_Xt, Instrument_Token, clientID, Qty):
    Instrument_Token = str(Instrument_Token)
    response = Interactive_Xt.place_order(
        exchangeSegment=Interactive_Xt.EXCHANGE_NSECM,
        exchangeInstrumentID=Instrument_Token,
        productType=Interactive_Xt.PRODUCT_MIS,
        orderType=Interactive_Xt.ORDER_TYPE_MARKET,
        orderSide=Interactive_Xt.TRANSACTION_TYPE_SELL,
        timeInForce=Interactive_Xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=Qty,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="En_Mkt_Order",
        clientID=clientID)

    print("Place Order: ", response)

    OrderID = Extract_Order_ID(response)

    return OrderID