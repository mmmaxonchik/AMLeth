import asyncio
from datetime import datetime
from functools import reduce
from etherscan_sdk.account_sdk import get_normal_transactions
from etherscan_sdk.account_sdk import get_ether_balance
from etherscan_sdk.account_sdk import get_internal_transactions
from etherscan_sdk.account_sdk import get_erc20_transactions


async def get_wallet_dataset(addr: str):
    # balance = await get_ether_balance(addr)
    normal_txns = await get_normal_transactions(
        addr
    )
    internal_txns = await get_internal_transactions(addr)
    erc20_txns = await get_erc20_transactions(addr)

    all_txns_types = erc20_txns + internal_txns + erc20_txns

    dataset = dict()

    # Количество обычных(normal) транзакций
    dataset["Normal_Txns"] = len(normal_txns)

    # Обычные транзакции с кошельками
    normal_wallets_txns = list(
        filter(lambda txn: txn["methodId"] == "0x", normal_txns)
    )

    # Обычные транзакции со смарт-контрактами
    smart_contract_txns = list(
        filter(lambda txn: txn["methodId"] != "0x", normal_txns)
    )

    # Метки времени для всех транзакций
    txns_timestamps = list(map(
        lambda txn: int(txn["timeStamp"]),
        all_txns_types
    ))

    # Время жизни кошелька от первой транзакции до последней
    wallet_life = datetime.fromtimestamp(
        max(txns_timestamps)
    ) - datetime.fromtimestamp(
        min(txns_timestamps)
    )

    # Время жизни кошелька от первой транзакции до последней(в секундах)
    dataset["Wallet_Lifetime"] = wallet_life.total_seconds()

    # Среднее количество транзакций в день
    dataset["Avg_txns_per_day"] = round(wallet_life.days / len(all_txns_types))

    filtered_txns_by_timeStamp = {
        timeStamp: list(filter(lambda txn: txn["timeStamp"] == str(
            timeStamp), all_txns_types))
        for timeStamp in txns_timestamps
    }

    # # Максимальное количество транзакций в день
    # dataset["Max_txns_per_day"] = sorted(
    #     filtered_txns_by_timeStamp.items(),
    #     key=lambda pair: len(pair[1]),
    # )

    # print(filtered_txns_by_timeStamp)

    # Общий объем Eth пропущенного через кошелек
    dataset["Eth_Volume"] = reduce(
        lambda a, b: a+b,
        map(
            lambda txn: int(txn["value"])/1e18,
            normal_txns
        ),
        0
    )

    # Количество транзакций с кошельками
    dataset["Wallet_Contract_Txns"] = len(normal_wallets_txns)

    # Количество транзакций с кошельками инициированных отправителем
    dataset["Wallet_Contract_Txns_In"] = len(
        list(
            filter(
                lambda txn: txn["to"].lower() == addr.lower(),
                normal_wallets_txns
            )
        )
    )

    # Количество транзакций с кошельками инициированных владельцем
    dataset["Wallet_Contract_Txns_Out"] = dataset["Wallet_Contract_Txns"] - \
        dataset["Wallet_Contract_Txns_In"]

    # Количество транзакций со смарт-контрактами
    dataset["Smart_Contract_Txns"] = len(smart_contract_txns)

    # Количество транзакций со смарт-контрактами инициированных контрактом
    dataset["Smart_Contract_Txns_In"] = len(
        list(
            filter(
                lambda txn: txn["to"].lower() == addr.lower(),
                smart_contract_txns
            )
        )
    )

    # Количество транзакций со смарт-контрактами инициированных кошельком
    dataset["Smart_Contract_Txns_Out"] = dataset["Smart_Contract_Txns"] - \
        dataset["Smart_Contract_Txns_In"]

    print(dataset)


async def main():
    txns = await get_wallet_dataset(
        "0xb961F2a5eeD42fc1607f4Fb795EF6D36D341CD56"
    )

if __name__ == "__main__":
    asyncio.run(main())
