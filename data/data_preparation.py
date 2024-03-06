import csv
import asyncio
import random
from aiohttp.client_exceptions import ClientError, ClientResponseError
from web3 import AsyncWeb3
import aiofiles

nets = [
    "https://eth.drpc.org",
    "https://eth-pokt.nodies.app",
    "https://rpc.mevblocker.io",
    "https://cloudflare-eth.com",
    "https://rpc.mevblocker.io"
]

temp = dict()


def open_dataset(file_name):
    return open(file_name, "r", encoding="UTF-8")


def open_write_to_dataset(file_name):
    return open(file_name, "w", encoding="UTF-8", newline="")


contr = {"0": set(), "1": set()}
wall = {"0": set(), "1": set()}


async def is_wallet(addr: str, queue: asyncio.Queue, FLAG: str, sleep: int):
    await asyncio.sleep(sleep)

    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
        nets[random.randint(0, len(nets)-1)]
    ))

    try:
        checksum_addr = w3.to_checksum_address(addr)
        code = await w3.eth.get_code(checksum_addr)
    except Exception as err:
        if isinstance(err, ClientError):
            print("Make recursive")
            is_wallet(addr, queue, FLAG, sleep)
        print(err)
        return

    code = code.hex()

    await queue.put((addr, len(code) == 2, FLAG))


async def producer(queue: asyncio.Queue):
    for FLAG in ["0", "1"]:
        addresses = temp[FLAG]

        async with asyncio.TaskGroup() as group:
            for i, addr in enumerate(addresses):
                group.create_task(is_wallet(addr, queue, FLAG, i//5))


async def consumer(queue):
    async with (
        aiofiles.open("./data/prepared_data/Fraud_Wallets.csv", "a", newline="") as fraud_wallets_dataset,
        aiofiles.open("./data/prepared_data/Normal_Wallets.csv", "a", newline="") as normal_wallets_dataset,
        aiofiles.open("./data/prepared_data/Fraud_Contracts.csv", "a", newline="") as fraud_contracts_dataset
    ):
        w1, w2, w3 = (
            csv.writer(fraud_wallets_dataset),
            csv.writer(normal_wallets_dataset),
            csv.writer(fraud_contracts_dataset),
        )

        while True:
            item = await queue.get()
            if item is None:
                break
            addr, is_wall, flag = item

            print("success:", addr)

            if flag == "0" and is_wall:
                await w2.writerow([addr])
            if flag == "1" and is_wall:
                await w1.writerow([addr])
            if flag == "1" and not is_wall:
                await w3.writerow([addr])


async def main():
    queue = asyncio.Queue()
    await asyncio.gather(producer(queue), consumer(queue))


if __name__ == "__main__":
    # Читаем данные из датасета Ethereum_Fraud_Detection_Dataset.csv
    with open_dataset("./data/open_source_data/Ethereum_Fraud_Detection_Dataset.csv") as dataset_csv:
        dataset = list(csv.reader(dataset_csv))
        temp["0"], temp["1"] = set(), set()
        for row in dataset[1:]:
            temp[row[3]].add(row[2].lower())

    # Читаем данные из датасета Etherscan_Malicious_Labels.csv
    with open_dataset("./data/open_source_data/Etherscan_Malicious_Labels.csv") as dataset_csv:
        dataset = list(csv.reader(dataset_csv))
        for row in dataset[1:]:
            temp["1"].add(row[0].lower())

    # Читаем данные из датасета Etherscan_Phish_Hack_Address.csv
    with open_dataset("./data/open_source_data/Etherscan_Phish_Hack_Address.csv") as dataset_csv:
        dataset = list(csv.reader(dataset_csv))
        for row in dataset[1:]:
            temp[row[1]].add(row[0].lower())

    # Читаем данные из датасета Ethereum_Malicious_Smart_Contracts.csv
    with open_dataset("./data/open_source_data/Ethereum_Malicious_Smart_Contracts.csv") as dataset_csv:
        dataset = list(csv.reader(dataset_csv))
        for row in dataset[1:]:
            temp["1"].add(row[0].lower())
            temp["1"].add(row[2].lower())

        # Читаем данные из датасета Ethereum_Malicious_Smart_Contracts.csv
    with open_dataset("./data/open_source_data/Phishing_Scams.csv") as dataset_csv:
        dataset = list(csv.reader(dataset_csv))
        for row in dataset[1:]:
            temp["1"].add(row[0].lower())

    with open_write_to_dataset("./data/prepared_data/Fraud_Wallets.csv") as fraud_wallets_dataset, \
            open_write_to_dataset("./data/prepared_data/Normal_Wallets.csv") as normal_wallets_dataset, \
            open_write_to_dataset("./data/prepared_data/Fraud_Contracts.csv") as fraud_contracts_dataset:

        writer_wall_fraud = csv.writer(fraud_wallets_dataset)
        writer_wall_normal = csv.writer(normal_wallets_dataset)
        writer_cnt_fraud = csv.writer(fraud_contracts_dataset)

        writer_wall_fraud.writerow(["Fraud_Wallets"])
        writer_wall_normal.writerow(["Normal_Wallets"])
        writer_cnt_fraud.writerow(["Fraud_Contracts"])

    asyncio.run(main())
