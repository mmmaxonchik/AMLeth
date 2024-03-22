import asyncio
import csv
import os
import numpy as np
import xgboost

from web3 import HTTPProvider
from report import Wallet
from etherscan_sdk.sdk import Account
from compare_clis.cryptowallet_risk_scoring.januus_riskreport.client import riskreport_on_entity
import pandas as pd


async def main():
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
    if ETHERSCAN_API_KEY is None:
        print("Необходим etherscan api key для получения транзакций!")
        os._exit(1)

    INFURA_API_KEY = os.getenv("INFURA_API_KEY")
    if INFURA_API_KEY is None:
        print("Необходим infura api key для запросов в сеть Ethereum!")
        os._exit(1)

    wallets = pd.read_csv("./data/wallets.csv")

    model = xgboost.XGBClassifier()
    model.load_model("./model.json")

    it = 0
    with open("./data/compare_history.csv", "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        for row in list(wallets.iterrows())[4285:]:
            if it % 10 == 0:
                file.flush()

            row = row[1]
            address = row["Address"]
            is_real_fraud = row["Fraud"]

            account = Account(ETHERSCAN_API_KEY, address)
            provider = HTTPProvider(
                f"https://mainnet.infura.io/v3/{INFURA_API_KEY}"
            )

            wallet = Wallet(account, provider)

            report = await wallet.get_report()
            report_array = np.array([report])

            prediction_own = model.predict(report_array)[0]

            prediction_compare = 0 if riskreport_on_entity(
                eth_addresses=[address]).risk_scores.fraud_risk < 60 else 1

            writer.writerow(
                [
                    address, is_real_fraud, prediction_own, prediction_compare
                ]
            )
            it += 1
            print(it)


if __name__ == "__main__":
    asyncio.run(main())
