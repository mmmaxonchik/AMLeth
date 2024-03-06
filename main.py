import asyncio
from etherscan_sdk.account_sdk import get_ether_balance


async def main():
    await get_ether_balance(
        "0x224f461604f57a8b9ac10dbcc2fc5fcf0aa669937476b3a221aafc1bc946778e"
    )

if __name__ == "__main__":
    asyncio.run(main())
