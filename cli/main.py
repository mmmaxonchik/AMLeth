import asyncio
import os

from web3 import AsyncWeb3
import xgboost
from report import Wallet
from etherscan_sdk.sdk import Account
import numpy as np


async def main():
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
    if ETHERSCAN_API_KEY is None:
        print("")
        os._exit(1)

    INFURA_API_KEY = os.getenv("INFURA_API_KEY")
    if INFURA_API_KEY is None:
        print("")
        os._exit(1)

    address = input("Введите проверяемый адрес: ")

    account = Account(ETHERSCAN_API_KEY, address)
    provider = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
        f"https://mainnet.infura.io/v3/{INFURA_API_KEY}")
    )

    wallet = Wallet(account, provider)

    report = await wallet.get_report()
    report_array = np.array([report])

    model = xgboost.XGBClassifier()
    model.load_model("./model.json")

    prediction = model.predict(report_array)

    if prediction == 1:
        print(f"Адрес: {address} является мошенническим")
    else:
        print(f"Address: {address} является нормальным")

if __name__ == "__main__":
    asyncio.run(main())


# "0xD816FB91C7688eCB56A75757AF3631821297bC4b" - Fraud - 1
# "0x2e16bd350cb5db830fb50328ab4df62fd4c16ae8" - Fraud - 1
