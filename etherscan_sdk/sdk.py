from aiohttp import ClientSession
from yarl import URL

from etherscan_sdk.sdk_type import ERC20TransferEvent, InternalTransaction, NormalTransaction


class TooManyRequestError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EtherScanApi:
    api_url = URL("https://api.etherscan.io/api")

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key


class Account(EtherScanApi):
    module = "account"
    request_headers = {"Accept": "application/json"}

    @staticmethod
    def handle_response(res):
        if res["message"] == "NOTOK":
            raise TooManyRequestError()
        else:
            return res

    def __init__(self, api_key: str, address: str) -> None:
        super().__init__(api_key)

        self.address = address
        self.api_url = self.api_url.update_query(
            {
                "module": self.module,
                "apikey": self.api_key,
                "address": self.address
            }
        )

    async def _send_request(self, url: URL):
        async with ClientSession(headers=self.request_headers) as session:
            async with session.get(url) as response:
                return await response.json()

    async def get_ether_balance(self):
        action: str = "balance"
        url = self.api_url.update_query({
            "action": action,
        })

        response = await self._send_request(url)
        return int(self.handle_response(response)["result"])/1e18

    async def get_normal_transactions(self):
        action: str = "txlist"
        url = self.api_url.update_query({
            "action": action,
        })

        response = await self._send_request(url)
        return list(map(lambda txn: NormalTransaction.from_dict(txn), self.handle_response(response)["result"]))

    async def get_internal_transactions(self):
        action: str = "txlistinternal"
        url = self.api_url.update_query({
            "action": action,
        })

        response = await self._send_request(url)
        return list(map(lambda txn: InternalTransaction.from_dict(txn), self.handle_response(response)["result"]))

    async def get_erc20_transfer_events(self):
        action: str = "tokentx"
        url = self.api_url.update_query({
            "action": action,
        })

        response = await self._send_request(url)
        return list(map(lambda txn: ERC20TransferEvent.from_dict(txn), self.handle_response(response)["result"]))
