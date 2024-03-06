from aiohttp import ClientSession
from yarl import URL

module: str = "account"
api_url: URL = URL("https://api.etherscan.io/api").update_query(
    {"module": module}
)
request_headers = {"Accept": "application/json"}


async def get_ether_balance(addr: str):
    action: str = "balance"
    url = api_url.update_query({
        "action": action,
        "apikey": "XPS2VR66MZ2YZE1G1WBAM8S3FA6NN8VD13",
        "address": addr,
    })

    async with ClientSession(headers=request_headers) as session:
        async with session.get(url) as response:
            return await response.json()

# def get_ether_balance(addr: str):
#     pass


# def get_ether_balance(addr: str):
#     pass


# def get_ether_balance(addr: str):
#     pass


# def get_ether_balance(addr: str):
#     pass
