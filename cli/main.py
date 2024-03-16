import asyncio
import csv
import os
import numpy as np
import xgboost

from web3 import AsyncWeb3
from report import Wallet
from etherscan_sdk.sdk import Account
from compare_clis.cryptowallet_risk_scoring.januus_riskreport.client import riskreport_on_entity


async def main():
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
    if ETHERSCAN_API_KEY is None:
        print("Необходим etherscan api key для получения транзакций!")
        os._exit(1)

    INFURA_API_KEY = os.getenv("INFURA_API_KEY")
    if INFURA_API_KEY is None:
        print("Необходим infura api key для запросов в сеть Ethereum!")
        os._exit(1)

    address = input("Введите проверяемый адрес: ")

    is_real_fraud = int(input(
        "Является ли проверяемый адрес мошенническим:\n0) Нет\n1) Да\n2) Не знаю\n"
    ))

    if is_real_fraud not in range(0, 3):
        print("Введено не верное значение!")
        os._exit(1)

    account = Account(ETHERSCAN_API_KEY, address)
    provider = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
        f"https://mainnet.infura.io/v3/{INFURA_API_KEY}")
    )

    wallet = Wallet(account, provider)

    model = xgboost.XGBClassifier()
    model.load_model("./model.json")

    report = await wallet.get_report()
    report_array = np.array([report])

    prediction = model.predict(report_array)[0]

    if prediction == 1:
        print(f"Адрес: {address} является мошенническим")
    else:
        print(f"Address: {address} является нормальным")

    with open("./data/history.csv", "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([address, is_real_fraud, prediction])

if __name__ == "__main__":
    asyncio.run(main())
