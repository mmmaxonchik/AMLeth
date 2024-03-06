import aiohttp
import asyncio

from aiohttp.hdrs import METH_GET

addr = "0x11112f684cB88d43CA0E132E585e882606063Fbe"

etherscan_api = "https://api.etherscan.io/api"


def parse_wallet_info():
    aiohttp.ClientRequest(METH_GET, "")
