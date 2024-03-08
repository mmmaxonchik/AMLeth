
import asyncio
from functools import reduce
import os
from random import randint
from typing import List, Sequence, Tuple
from aiohttp import ClientError

from attr import dataclass
from web3 import AsyncWeb3
from etherscan_sdk.sdk import Account
from etherscan_sdk.sdk_type import ERC20TransferEvent, NormalTransaction, Transaction


@dataclass
class WalletReport:
    Normal_Txns: int
    Normal_Sent_txns: int
    Normal_Received_txns: int
    ERC20_txns: int
    ERC20_Sent_txns: int
    ERC20_Received_txns: int
    Internal_Txn: int
    Eth_Volume: float
    Sent_Eth: float
    Received_Eth: float
    ERC20_Volume: float
    Sent_ERC20: float
    Received_ERC20: float
    Stable_Coin_Volume: float
    Sent_Stable_Coin: float
    Received_Stable_Coin: float
    First_Txn_Timestamp: int
    Last_Txn_Timestamp: int
    Wallet_LifeTime: int
    Min_Time_Btw_Normal_Txns: int
    Avg_Time_Btw_Normal_Txns: int
    Max_Time_Btw_Normal_Txns: int
    Min_Time_Btw_ERC20_Txns: int
    Avg_Time_Btw_ERC20_Txns: int
    Max_Time_Btw_ERC20_Txns: int
    Min_Time_Btw_Txns: int
    Min_Time_Btw_Txns: int
    Min_Time_Btw_Txns: int
    # First_Time_Txn: int
    # Last_Time_Txn: int
    # Deployed_SmrtCnts: int
    # Uniq_Wallets: int
    # Uniq_SmrtCnts: int
    # Uniq_ERC20: int
    # Uniq_ERC20_Wallets: int
    # Normal_Sent_txns: int
    # Normal_Received_txns: int
    # Min_Time_Btw_ERC20_Txns: int
    # Avg_Time_Btw_ERC20_Txns: int
    # Max_Time_Btw_ERC20_Txns: int
    # StableCoins_Volume: float
    # Sent_StableCoins: float
    # Received_StableCoins: float


class Wallet:
    stable_coins_smrt_cntrs = [
        "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "0x853d955acef822db058eb8505911ed77f175b99e",
        "0x6b175474e89094c44da98b954eedeac495271d0f",
        "0xc5f0f7b66764F6ec8C8Dff7BA683102295E16409",
        "0x0000000000085d4780B73119b644AE5ecd22b376",
        "0x4c9edd5852cd905f086c759e8383e09bff1e68b3",
        "0x0C10bF8FcB7Bf5412187A595ab97a3609160b5c6",
    ]

    def __init__(self, api_key: str, address: str):
        self.address = address
        self.account = Account(api_key, self.address)

    @classmethod
    async def _is_wallet(cls, address: str):
        rpc_nodes = [
            "https://eth.drpc.org",
            "https://eth-pokt.nodies.app",
            "https://rpc.mevblocker.io",
            "https://cloudflare-eth.com",
            "https://rpc.mevblocker.io"
            "https://mainnet.infura.io/v3/"+os.environ["INFURA_API_KEY"]
        ]

        w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
            rpc_nodes[randint(0, len(rpc_nodes)-1)]
        ))

        try:
            checksum_addr = w3.to_checksum_address(address)
            code = await w3.eth.get_code(checksum_addr)
        except Exception as err:
            await asyncio.sleep(10)
            if isinstance(err, ClientError):
                await cls._is_wallet(address)
            return True

        return code.hex() == "0x"

    @staticmethod
    def _is_eq_addr(addr1: str, addr2: str):
        return addr1.lower() == addr2.lower()

    @staticmethod
    def _wei_to_eth(wei: int) -> float:
        return wei/1e18

    async def _prepared_data(self):
        self.normal_txns = await self.account.get_normal_transactions()
        self.internal_txns = await self.account.get_internal_transactions()
        self.erc20_events = await self.account.get_erc20_transfer_events()

        self.wallets: List[NormalTransaction] = list()
        self.smrt_cntrs: List[NormalTransaction] = list()

        for txn in self.normal_txns:
            if self._is_eq_addr(self.address, txn.to_):
                if await self._is_wallet(txn.from_):
                    self.wallets.append(txn)
                else:
                    self.smrt_cntrs.append(txn)
            else:
                if await self._is_wallet(txn.to_):
                    self.wallets.append(txn)
                else:
                    self.smrt_cntrs.append(txn)

    def _eth_volume(self, txns_list: Sequence[Transaction]) -> float:
        return reduce(
            lambda a, b: a + b,
            map(lambda txn: self._wei_to_eth(int(txn.value)), txns_list), 0
        )

    def _sent_eth_volume(self) -> float:
        return reduce(
            lambda a, b: a + b,
            map(lambda txn: self._wei_to_eth(int(txn.value)), self.normal_txns), 0
        )

    @staticmethod
    def _get_txns_timestamps(txns_list: Sequence[Transaction | ERC20TransferEvent]):
        txns_timestamps = list(map(lambda txn: int(txn.time_stamp), txns_list))
        txns_timestamps.sort()
        return txns_timestamps

    def _get_statistic_time_btw_txns(self, txns_list: Sequence[Transaction | ERC20TransferEvent]) -> Tuple[int, int, int]:
        txns_timestamps = self._get_txns_timestamps(txns_list)

        if len(txns_timestamps) < 2:
            return (0, 0, 0)

        min_time, avg_time, max_time = max(txns_timestamps), 0, 0

        for i in range(len(txns_timestamps)-1, -1, -1):
            if i == 0:
                break
            diff = txns_timestamps[i]-txns_timestamps[i-1]

            avg_time += diff
            if min_time >= diff:
                min_time = diff
            else:
                max_time = diff
        avg_time /= len(txns_timestamps)

        min_time, avg_time, max_time = map(
            lambda seconds: seconds*1000, (min_time, round(avg_time), max_time)
        )

        return (min_time, avg_time, max_time)

    def _get_stable_coin_info(self) -> Tuple[float, float, float]:
        stable_coins_volume = 0
        stable_coins_received = 0
        stable_coins_sent = 0

        for txn in self.erc20_events:
            for stable_coin_addr in self.stable_coins_smrt_cntrs:
                if self._is_eq_addr(stable_coin_addr, txn.contract_address):
                    val = int(txn.value) / 10**int(txn.token_decimal)
                    stable_coins_volume += val
                    if self._is_eq_addr(txn.to_, self.address):
                        stable_coins_sent += val
                    else:
                        stable_coins_received += val

        return (stable_coins_volume, stable_coins_sent, stable_coins_received)

    async def get_report(self) -> WalletReport:
        await self._prepared_data()

        # Filters
        def sender(txn: Transaction | ERC20TransferEvent): return self._is_eq_addr(
            txn.from_, self.address)

        def receiver(txn: Transaction | ERC20TransferEvent): return self._is_eq_addr(
            txn.to_, self.address)

        def stable_coin(txn: ERC20TransferEvent):
            return txn.contract_address.lower() in list(map(str.lower, self.stable_coins_smrt_cntrs))

        # Data mappers
        def eth_value(txn): return int(txn.value)/1e18

        def erc20_value(txn: ERC20TransferEvent): return int(
            txn.value)/10**int(txn.token_decimal)

        # Constant data
        txns_timestamps = self._get_txns_timestamps(
            self.normal_txns+self.erc20_events
        )

        f_txn_time, l_txn_time = 0, 0
        if len(txns_timestamps) >= 1:
            f_txn_time = txns_timestamps[0]
            l_txn_time = txns_timestamps[-1]

        # self._get_stable_coin_info()

        # sent_txns = list(
        #     filter(
        #         lambda txn: self._is_eq_addr(txn.from_, self.address),
        #         self.normal_txns
        #     )
        # )

        # received_txns = list(
        #     filter(
        #         lambda txn: self._is_eq_addr(txn.to_, self.address),
        #         self.normal_txns
        #     )
        # )

        # txns_time_stamps = list(
        #     map(
        #         lambda txn: int(txn.time_stamp),
        #         self.normal_txns+self.internal_txns+self.erc20_events
        #     )
        # )

        # uniq_smrt_cntrs = set(
        #     map(
        #         lambda txn: txn.to_,
        #         filter(lambda txn: not self._is_eq_addr(
        #             txn.to_.lower(), self.address), self.smrt_cntrs)
        #     )
        # ).union(set(
        #     map(
        #         lambda txn: txn.from_,
        #         filter(lambda txn: not self._is_eq_addr(
        #             txn.from_.lower(), self.address), self.smrt_cntrs)
        #     )
        # ))

        # uniq_wallets = set(
        #     map(
        #         lambda txn: txn.to_.lower(),
        #         filter(
        #             lambda txn: not self._is_eq_addr(
        #                 txn.to_, self.address
        #             ), self.wallets)
        #     )
        # ).union(set(
        #     map(
        #         lambda txn: txn.from_.lower(),
        #         filter(
        #             lambda txn: not self._is_eq_addr(txn.from_, self.address),
        #             self.wallets
        #         )
        #     )
        # ))

        # uniq_erc20_smrt_cntrs = set([
        #     txn.contract_address.lower()
        #     for txn in self.erc20_events
        # ])

        # uniq_erc20_wallets = set(
        #     map(
        #         lambda txn: txn.to_.lower(),
        #         filter(
        #             lambda txn: not self._is_eq_addr(
        #                 txn.to_, self.address
        #             ), self.erc20_events)
        #     )
        # ).union(set(
        #     map(
        #         lambda txn: txn.from_.lower(),
        #         filter(
        #             lambda txn: not self._is_eq_addr(txn.from_, self.address),
        #             self.erc20_events
        #         )
        #     )
        # ))

        # if len(txns_time_stamps) > 1:
        #     first_time_txn = max(txns_time_stamps)
        #     last_time_txn = min(txns_time_stamps)
        # else:
        #     first_time_txn, last_time_txn = 0, 0

        # wallet_life_time = (first_time_txn-last_time_txn)*1000

        normal_txns_sent = list(filter(sender, self.normal_txns))

        normal_txns_received = list(filter(
            lambda txn: self._is_eq_addr(txn.from_, self.address),
            self.normal_txns
        ))

        return WalletReport(
            len(self.normal_txns),
            len(list(filter(sender, self.normal_txns))),
            len(list(filter(receiver, self.normal_txns))),
            len(self.erc20_events),
            len(list(filter(sender, self.erc20_events))),
            len(list(filter(receiver, self.erc20_events))),
            len(self.internal_txns),
            sum(map(eth_value, self.normal_txns)),
            sum(map(eth_value, filter(sender, self.normal_txns))),
            sum(map(eth_value, filter(receiver, self.normal_txns))),
            sum(map(erc20_value, self.erc20_events)),
            sum(map(erc20_value, filter(sender, self.erc20_events))),
            sum(map(erc20_value, filter(receiver, self.erc20_events))),
            sum(map(erc20_value, filter(stable_coin, self.erc20_events))),
            sum(
                map(erc20_value, filter(
                    sender, filter(stable_coin, self.erc20_events)
                ))
            ),
            sum(
                map(erc20_value, filter(
                    receiver, filter(stable_coin, self.erc20_events)
                ))
            ),
            f_txn_time,
            l_txn_time,
            (l_txn_time-f_txn_time)*1000,
            *self._get_statistic_time_btw_txns(self.normal_txns),
            *self._get_statistic_time_btw_txns(self.erc20_events),
            *self._get_statistic_time_btw_txns(self.erc20_events+normal_txns),


            # len(self.internal_txns),
            # len(self.erc20_events),
            # self._eth_volume(self.normal_txns),
            # self._eth_volume(sent_txns),
            # self._eth_volume(received_txns),
            # *self._get_statistic_time_btw_txns(self.normal_txns),
            # wallet_life_time,
            # first_time_txn,
            # last_time_txn,
            # # TODO
            # 0,
            # len(uniq_wallets),
            # len(uniq_smrt_cntrs),
            # len(uniq_erc20_smrt_cntrs),
            # len(uniq_erc20_wallets),
            # len(sent_txns),
            # len(received_txns),
            # *self._get_statistic_time_btw_txns(self.erc20_events),
            # *self._get_stable_coin_info()
        )
