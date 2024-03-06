import asyncio
from etherscan_sdk.account_sdk import get_normal_transactions
from etherscan_sdk.account_sdk import get_ether_balance
from etherscan_sdk.account_sdk import get_internal_transactions
from etherscan_sdk.account_sdk import get_erc20_transactions


async def get_wallet_characteristics(addr: str):
    balance = await get_ether_balance(addr)
    normal_txns = await get_normal_transactions(
        addr
    )
    internal_txns = await get_internal_transactions(addr)
    erc20_txns = await get_erc20_transactions(addr)
    print(normal_txns)


async def main():
    print(
        await get_normal_transactions(
            "0xc55ca254045A09565A3eed7a0Cb32D38b7062E52"
        )
    )

if __name__ == "__main__":
    asyncio.run(main())
