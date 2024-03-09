import asyncio
import os
from pprint import pprint

from etherscan_sdk.sdk import Account
from report import Wallet


async def main():
    some = "Fraud,Normal_Txns,Normal_Sent_txns,Normal_Received_txns,ERC20_txns,ERC20_Sent_txns,ERC20_Received_txns,Internal_Txn,Eth_Volume,Sent_Eth,Received_Eth,ERC20_Volume,Sent_ERC20,Received_ERC20,Stable_Coin_Volume,Sent_Stable_Coin,Received_Stable_Coin,First_Txn_Timestamp,Last_Txn_Timestamp,Wallet_LifeTime,Min_Time_Btw_Normal_Txns,Avg_Time_Btw_Normal_Txns,Max_Time_Btw_Normal_Txns,Min_Time_Btw_ERC20_Txns,Avg_Time_Btw_ERC20_Txns,Max_Time_Btw_ERC20_Txns,Min_Time_Btw_Txns,Avg_Time_Btw_Txns,Max_Time_Btw_Txns,Uniq_Wallet_In_Normal_Txns,Uniq_SmrtCntrs_In_Normal_Txns,Uniq_Wallet_In_ERC20_Txns,Uniq_SmrtCntrs_In_ERC20_Txns"
    print(len(some.split(",")))
    # api_key = os.environ["ETHERSCAN_API_KEY"]

    # acc = Account(api_key, "0x3a1ba1e4510d36272d1e1d708787Befa1780b778")

    # pprint(await acc.get_normal_transactions())

    # wallet = Wallet(api_key, "0x3a1ba1e4510d36272d1e1d708787Befa1780b778")
    # pprint(await wallet.get_report())

if __name__ == "__main__":
    asyncio.run(main())
