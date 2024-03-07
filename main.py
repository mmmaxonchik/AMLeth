import asyncio
import os

from etherscan_sdk.sdk import Account
from report import Wallet


async def main():
    api_key = os.environ["ETHERSCAN_API_KEY"]
    wallet = Wallet(api_key, "0x3a1ba1e4510d36272d1e1d708787Befa1780b778")
    print(await wallet.get_report())

if __name__ == "__main__":
    asyncio.run(main())
