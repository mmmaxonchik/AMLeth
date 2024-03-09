from ast import Tuple
import asyncio
import csv
from io import StringIO
import os
from pprint import pprint
from time import sleep

import aiofiles
from regex import E

from etherscan_sdk.sdk import Account, TooManyRequestError
from report import Wallet

queue_size = 2


async def write_to_final_dataset(queue: asyncio.Queue):
    async with aiofiles.open("./data/final_data/Wallets.csv", "a", newline="") as final_data_set:
        writer = csv.writer(final_data_set)
        # await writer.writerow(["Fraud"]+list(WalletReport.__match_args__))
        while True:
            item = await queue.get()
            if item is None:
                break
            await writer.writerow([int(item[0])]+list(item[1].values()))


async def call_report(api_key: str, address: str, is_fraud: bool, queue: asyncio.Queue):
    wallet = Wallet(api_key, address)

    success = False
    while not success:
        try:
            report = await wallet.get_report()
            success = True
            await queue.put((is_fraud, report.__dict__))
        except Exception as err:
            print(err, type(err))
            if isinstance(err, TooManyRequestError):
                await asyncio.sleep(10)
            else:
                break


async def write_reports(queue: asyncio.Queue):
    async with (
        aiofiles.open("./data/prepared_data/Normal_Wallets.csv", "r") as normal_wallets,
        aiofiles.open("./data/prepared_data/Fraud_Wallets.csv", "r") as fraud_wallet
    ):
        normal_content = await normal_wallets.read()
        fraud_content = await fraud_wallet.read()

        normal_reader = csv.reader(StringIO(normal_content))
        fraud_reader = csv.reader(StringIO(fraud_content))
        _ = next(normal_reader), next(fraud_reader)

        api_key = os.environ["ETHERSCAN_API_KEY"]

        fraud_addresses = [row[0] for row in fraud_reader if row]

        # Allowing 5 concurrent executions
        semaphore = asyncio.Semaphore(3)

        async def create_tasks(address_list: list[str], is_fraud: bool):
            index = 0
            while index < len(address_list):
                free_size = queue_size - queue.qsize()
                if free_size <= 0:
                    continue
                tasks = []
                for address in address_list[index: index + free_size]:
                    async with semaphore:
                        task = call_report(api_key, address, is_fraud, queue)
                        tasks.append(task)
                if tasks:
                    await asyncio.gather(*tasks)
                index += free_size
                print(f"Processed {index} items")

        await create_tasks(fraud_addresses, True)


async def main():
    queue = asyncio.Queue(queue_size)
    await asyncio.gather(
        write_to_final_dataset(queue),
        write_reports(queue)
    )


if __name__ == "__main__":
    asyncio.run(main())
