
import time
import asyncio


from Supplement import Market_Data_Utilities as Mdu
from Supplement import Ineractive_Data_Utilities as Idu
from Supplement.Market_Data_Utilities import Fetch_Ltp


def Custom_Trailing_Stop_Loss(Market_Xt: object, Interactive_Xt: object, ClientID: str, Instrument_Token: int,
                              Entry_Traded_Price: float,
                              Trail_Points: float,
                              Exch_Segment: int, Exit_Limit_Order_Id: int,
                              Check_Interval: int = 1):

    Highest_Price = round(float(Entry_Traded_Price), 1)
    Stop_Loss_Price = round(float(Entry_Traded_Price - Trail_Points), 1)
    Trailing_Stop_Triggered = False
    Exit_Limit_Order_Traded = False

    while not Trailing_Stop_Triggered and not Exit_Limit_Order_Traded:

        Exit_Order_Status = Idu.Get_Order_Status(Interactive_Xt, ClientID, Exit_Limit_Order_Id)
        print(f"{Exit_Order_Status = }")

        if Exit_Order_Status == "Filled":
            Exit_Limit_Order_Traded = True
            print(" Limit Exit order filled exiting loop")
            return Trailing_Stop_Triggered

        Current_Price = Mdu.Fetch_Ltp(Market_Xt, Exch_Segment, Instrument_Token)
        if Current_Price > Highest_Price:
            Highest_Price = Current_Price
            Stop_Loss_Price = round(float(Highest_Price - Trail_Points), 1)
            print("Updated highest price and stop-loss")

        print(f"{Current_Price = } {Highest_Price = } {Stop_Loss_Price =}")

        if Current_Price <= Stop_Loss_Price:
            print("Trailing Stop loss triggered! ")
            Trailing_Stop_Triggered = True
            return Trailing_Stop_Triggered

        time.sleep(Check_Interval)
    return Trailing_Stop_Triggered


def Get_New_Strategy_Details(DF, Percentage):
    Max_Value = round(float(DF["High"].max()), 1)
    Min_Value = round(float(DF["Low"].min()), 1)
    High_Low_Diff = round(float(Max_Value - Min_Value), 1)
    Percentage_Diff = round(float(High_Low_Diff * Percentage / 100), 1)
    Entry_Price = round(float(Min_Value + Percentage_Diff), 1)
    Stop_Price = round((Entry_Price - (High_Low_Diff * 0.3)), 1)
    Limit_Target_Price = round((Max_Value + High_Low_Diff), 1)

    Strategy_Dict = {"Max_Value": Max_Value, "Min_Value": Min_Value, "High_Low_Diff": High_Low_Diff,
                     "Percentage_Diff": Percentage_Diff, "Entry_Price": Entry_Price, "Stop_Price": Stop_Price,
                     "Limit_Target_Price": Limit_Target_Price}

    return Strategy_Dict


def Custom_Stop_Loss(Market_Xt: object, Interactive_Xt: object, ClientID: str, Instrument_Token: int,
                     Exch_Segment: int, Exit_Limit_Order_Id: int, Stop_Loss_Price: float,
                     Check_Interval: int = 1):
    Stop_Triggered = False
    Exit_Limit_Order_Traded = False

    while not Stop_Triggered and not Exit_Limit_Order_Traded:

        Exit_Order_Status = Idu.Get_Order_Status(Interactive_Xt, ClientID, Exit_Limit_Order_Id)
        print(f"{Exit_Order_Status = }")

        if Exit_Order_Status == "Filled":
            Exit_Limit_Order_Traded = True
            print(" Limit Exit order filled exiting loop")
            return Stop_Triggered

        Current_Price = Mdu.Fetch_Ltp(Market_Xt, Exch_Segment, Instrument_Token)

        if Current_Price <= Stop_Loss_Price:
            print("Stop loss triggered! ")
            Stop_Triggered = True
            return Stop_Triggered

        time.sleep(Check_Interval)
    return Stop_Triggered


async def Cross_From_Below(Market_Xt: object, Interactive_Xt: object, ClientID: str, Instrument_Token: int, Reference_Price: float):
    Was_Below = False
    Lowest_Price = float("inf")
    Highest_Price = -float("inf")
    Crossed = False
    while not Crossed:

        Ltp = Fetch_Ltp(Market_Xt, 2, Instrument_Token)

        if not Was_Below:
            if Ltp < Lowest_Price:
                Lowest_Price = Ltp
            if Ltp > Highest_Price:
                Highest_Price = Ltp
            if Lowest_Price < Reference_Price:
                Was_Below = True


        if Was_Below:
            if Ltp > Reference_Price:
                Crossed = True


        await asyncio.sleep(1)
    return Crossed



async def Cross_From_Above(Market_Xt: object, Interactive_Xt: object, ClientID: str, Instrument_Token: int,
                     Reference_Price: float):
    Was_Above = False
    Lowest_Price = float("inf")
    Highest_Price = -float("inf")
    Crossed = False
    while not Crossed:

        Ltp = Fetch_Ltp(Market_Xt, 2, Instrument_Token)

        if not Was_Above:

            if Ltp < Lowest_Price:
                Lowest_Price = Ltp
            if Ltp > Highest_Price:
                Highest_Price = Ltp
            if Highest_Price > Reference_Price:
                Was_Above = True

        if Was_Above:
            if Ltp < Reference_Price:
                Crossed = True


        await asyncio.sleep(1)
    return Crossed


def Wait_For_Limit_Trade_Or_Stop_Exit_Trigger(Market_Xt: object, Interactive_Xt: object, Cli_Id: str,Instrument_Token,Stop_Loss_Price,Exit_Limit_Order_Id,Exch_Segment,Check_Interval=1):
    Stop_Triggered = False

    while True:

        Exit_Order_Status = Idu.Get_Order_Status(Interactive_Xt, Cli_Id, Exit_Limit_Order_Id)
        print(f"{Exit_Order_Status = }")

        if Exit_Order_Status == "Filled":
            Exit_Limit_Order_Traded = True
            print(" Limit Exit order filled exiting loop")
            return Stop_Triggered


        Current_Price = Mdu.Fetch_Ltp(Market_Xt, Exch_Segment, Instrument_Token)


        if Current_Price <= Stop_Loss_Price:
            print("Trailing Stop loss triggered! ")
            Trailing_Stop_Triggered = True
            return Trailing_Stop_Triggered

        time.sleep(Check_Interval)

def Scenario_1_Module(Market_Xt,Interactive_Xt,ClientID,Instrument_Token,L1,L3,L4,H1,H3,H4,Qty):
    Was_Below_L3 = False
    Was_Above_H3 = False

    Entry_Taken = False
    Exited = False

    Lowest_Price = float("inf")
    Highest_Price = -float("inf")

    while not Exited:

        Ltp = Fetch_Ltp(Market_Xt, 2, Instrument_Token)

        if not Entry_Taken:
            if Ltp < Lowest_Price:
                Lowest_Price = Ltp
            if Ltp > Highest_Price:
                Highest_Price = Ltp


        if not Was_Below_L3 and not Entry_Taken:

            if Lowest_Price < L3:
                Was_Below_L3 = True



        if not Was_Above_H3 and not Entry_Taken:

            if Highest_Price > H3:
                Was_Above_H3 = True

        print(f"{Was_Below_L3 = } {Was_Above_H3 = }")

        if Was_Below_L3 and not Entry_Taken:
            if Ltp > L3:
                Entry_Type = "Buy"
                Entry_Market_Order_No = Idu.Place_Buy_Market_Order(Interactive_Xt, Instrument_Token, ClientID, Qty=Qty)
                Entry_Taken = True

                print(f"{Ltp = } above {L3 =}, Entry taken , {Entry_Type = }")

        if Was_Above_H3 and not Entry_Taken:
            if Ltp < H3:
                Entry_Type = "Sell"
                Entry_Market_Order_No = Idu.Place_Sell_Market_Order(Interactive_Xt, Instrument_Token, ClientID, Qty=Qty)
                Entry_Taken = True
                print(f"{Ltp = } below {H3 =}, Entry taken , {Entry_Type = }")

        if Entry_Taken and not Exited:
            if Entry_Type == "Buy":

                if Ltp > H1:
                    Exit_Market_Order_No = Idu.Place_Sell_Market_Order(Interactive_Xt, Instrument_Token, ClientID,
                                                                       Qty=Qty)
                    Exited = True
                    print(f"{Ltp = } above {H1 =} Exited at Profit ")

            if Ltp < L4:
                Exit_Market_Order_No = Idu.Place_Sell_Market_Order(Interactive_Xt, Instrument_Token, ClientID,
                                                                   Qty=Qty)
                Exited = True
                print(f"{Ltp = } below {L4 =}, Exited at Loss ")

            elif Entry_Type == "Sell":
                if Ltp > H4:
                    Exit_Market_Order_No = Idu.Place_Buy_Market_Order(Interactive_Xt, Instrument_Token, ClientID,
                                                                      Qty=Qty)
                    Exited = True
                    print(f"{Ltp = } above {H4 =} ,Exited at Loss ")

                if Ltp < L1:
                    Exit_Market_Order_No = Idu.Place_Buy_Market_Order(Interactive_Xt, Instrument_Token, ClientID,
                                                                      Qty=Qty)
                    Exited = True
                    print(f"{Ltp = } Below {L1 =} ,Exited at Profit ")

        time.sleep(1)


def One_Cancels_Other_Stop_And_Limit(Market_Xt: object, Interactive_Xt: object, ClientID: str, Instrument_Token: int,
                     Exch_Segment: int, Exit_Limit_Order_Id: int, Stop_Loss_Price: float,
                     Check_Interval: int = 1):
    Stop_Triggered = False
    Exit_Limit_Order_Traded = False

    while not Stop_Triggered and not Exit_Limit_Order_Traded:

        Exit_Order_Status = Idu.Get_Order_Status(Interactive_Xt, ClientID, Exit_Limit_Order_Id)
        print(f"{Exit_Order_Status = }")

        if Exit_Order_Status == "Filled":
            Exit_Limit_Order_Traded = True
            print(" Limit Exit order filled, exiting loop")
            Stop_Triggered = False
            return Stop_Triggered

        elif Exit_Order_Status in ("Cancelled", "Rejected"):
            print("Order Cancelled or Rejected")
            print("Exiting")
            quit()

        Current_Price = Mdu.Fetch_Ltp(Market_Xt, Exch_Segment, Instrument_Token)
        print(f"{Current_Price = } {Stop_Loss_Price = }")

        if Current_Price <= Stop_Loss_Price:
            print("Stop loss triggered! ")
            Stop_Triggered = True
            return Stop_Triggered

        time.sleep(Check_Interval)
    return Stop_Triggered






