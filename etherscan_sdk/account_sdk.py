from aiohttp import ClientSession
from yarl import URL

apikey: str = "XPS2VR66MZ2YZE1G1WBAM8S3FA6NN8VD13"
module: str = "account"
api_url: URL = URL("https://api.etherscan.io/api").update_query(
    {"module": module, "apikey": apikey}
)
request_headers = {"Accept": "application/json"}


async def get_ether_balance(addr: str):
    action: str = "balance"
    url = api_url.update_query({
        "action": action,
        "address": addr,
    })

    async with ClientSession(headers=request_headers) as session:
        async with session.get(url) as response:
            response = await response.json()
            return response["result"]


async def get_normal_transactions(addr: str):
    action: str = "txlist"
    url = api_url.update_query({
        "action": action,
        "address": addr,
    })

    async with ClientSession(headers=request_headers) as session:
        async with session.get(url) as response:
            response = await response.json()
            return response["result"]


async def get_internal_transactions(addr: str):
    action: str = "txlistinternal"
    url = api_url.update_query({
        "action": action,
        "address": addr,
    })

    async with ClientSession(headers=request_headers) as session:
        async with session.get(url) as response:
            response = await response.json()
            return response["result"]


async def get_erc20_transactions(addr: str):
    action: str = "tokentx"
    url = api_url.update_query({
        "action": action,
        "address": addr,
    })

    async with ClientSession(headers=request_headers) as session:
        async with session.get(url) as response:
            response = await response.json()
            return response["result"]
