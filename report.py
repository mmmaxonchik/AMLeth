
import asyncio
from functools import reduce
import os
from random import randint
from sre_constants import SUCCESS
from typing import List, Sequence, Tuple
from aiohttp import ClientError

from attr import dataclass
from sympy import false, true
from web3 import AsyncWeb3
from etherscan_sdk.sdk import Account
from etherscan_sdk.sdk_type import ERC20TransferEvent, NormalTransaction, Transaction


@dataclass
class WalletReport:
    # Countable data
    Normal_Txns: int
    Normal_Sent_txns: int
    Normal_Received_txns: int
    ERC20_txns: int
    ERC20_Sent_txns: int
    ERC20_Received_txns: int
    Internal_Txn: int
    # Currency and token data
    Eth_Volume: float
    Sent_Eth: float
    Received_Eth: float
    ERC20_Volume: float
    Sent_ERC20: float
    Received_ERC20: float
    Stable_Coin_Volume: float
    Sent_Stable_Coin: float
    Received_Stable_Coin: float
    # Time data
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
    Avg_Time_Btw_Txns: int
    Max_Time_Btw_Txns: int
    # Countable data
    Uniq_Wallet_In_Normal_Txns: int
    Uniq_SmrtCntrs_In_Normal_Txns: int
    Uniq_Wallet_In_ERC20_Txns: int
    Uniq_SmrtCntrs_In_ERC20_Txns: int


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
            "https://mainnet.infura.io/v3/"+os.environ["INFURA_API_KEY"]
        ]

        success = False
        code = "0x"
        while not success:
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
                rpc_nodes[randint(0, len(rpc_nodes)-1)]
            ))
            try:
                checksum_addr = w3.to_checksum_address(address)
                code = await w3.eth.get_code(checksum_addr)
                code = code.hex()
                success = True
            except Exception as err:
                print(err, type(err))
                await asyncio.sleep(2)

        return code == "0x"

    @staticmethod
    def _is_eq_addr(addr1: str, addr2: str):
        return addr1.lower() == addr2.lower()

    @staticmethod
    def _wei_to_eth(wei: int) -> float:
        return wei/1e18

    async def _txns_interaction(self, txns_list: Sequence[Transaction | ERC20TransferEvent]) -> Tuple[List[Transaction | ERC20TransferEvent], List[Transaction | ERC20TransferEvent]]:
        wallets: List[Transaction | ERC20TransferEvent] = list()
        smrt_cntrs: List[Transaction | ERC20TransferEvent] = list()

        for txn in txns_list:
            if self._is_eq_addr(self.address, txn.to_):
                if await self._is_wallet(txn.from_):
                    wallets.append(txn)
                else:
                    smrt_cntrs.append(txn)
            else:
                if await self._is_wallet(txn.to_):
                    wallets.append(txn)
                else:
                    smrt_cntrs.append(txn)

        return (wallets, smrt_cntrs)

    async def _prepared_data(self):
        self.normal_txns = await self.account.get_normal_transactions()
        self.internal_txns = await self.account.get_internal_transactions()
        self.erc20_events = await self.account.get_erc20_transfer_events()

        self.normal_txns_interaction = await self._txns_interaction(self.normal_txns)
        self.erc20_txns_interaction = await self._txns_interaction(self.erc20_events)

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

    def _uniq_addr(self, txns_list: Sequence[Transaction | ERC20TransferEvent]):
        return set(map(
            lambda txn: txn.to_.lower(),
            filter(self.sender, txns_list)
        )).union(map(
            lambda txn: txn.from_.lower(),
            filter(self.receiver, txns_list)
        ))

    # Filters
    def sender(self, txn: Transaction | ERC20TransferEvent): return self._is_eq_addr(
        txn.from_, self.address)

    def receiver(self, txn: Transaction | ERC20TransferEvent): return self._is_eq_addr(
        txn.to_, self.address)

    async def get_report(self) -> WalletReport:
        await self._prepared_data()

        def stable_coin(txn: ERC20TransferEvent):
            return txn.contract_address.lower() in list(map(str.lower, self.stable_coins_smrt_cntrs))

        # Data mappers
        def eth_value(txn): return self._wei_to_eth(int(txn.value))

        def erc20_value(txn: ERC20TransferEvent): return (
            int(txn.value)/10**int(txn.token_decimal)
        )

        # Constant data
        txns_timestamps = self._get_txns_timestamps(
            self.normal_txns+self.erc20_events
        )

        f_txn_time, l_txn_time = 0, 0
        if len(txns_timestamps) >= 1:
            f_txn_time = txns_timestamps[0]
            l_txn_time = txns_timestamps[-1]

        return WalletReport(
            len(self.normal_txns),
            len(list(filter(self.sender, self.normal_txns))),
            len(list(filter(self.receiver, self.normal_txns))),
            len(self.erc20_events),
            len(list(filter(self.sender, self.erc20_events))),
            len(list(filter(self.receiver, self.erc20_events))),
            len(self.internal_txns),
            sum(map(eth_value, self.normal_txns)),
            sum(map(eth_value, filter(self.sender, self.normal_txns))),
            sum(map(eth_value, filter(self.receiver, self.normal_txns))),
            sum(map(erc20_value, self.erc20_events)),
            sum(map(erc20_value, filter(self.sender, self.erc20_events))),
            sum(map(erc20_value, filter(self.receiver, self.erc20_events))),
            sum(map(erc20_value, filter(stable_coin, self.erc20_events))),
            sum(
                map(erc20_value, filter(
                    self.sender, filter(stable_coin, self.erc20_events)
                ))
            ),
            sum(
                map(erc20_value, filter(
                    self.receiver, filter(stable_coin, self.erc20_events)
                ))
            ),
            f_txn_time,
            l_txn_time,
            (l_txn_time-f_txn_time)*1000,
            *self._get_statistic_time_btw_txns(self.normal_txns),
            *self._get_statistic_time_btw_txns(self.erc20_events),
            *self._get_statistic_time_btw_txns(self.erc20_events+self.normal_txns),
            len(self._uniq_addr(self.normal_txns_interaction[0])),
            len(self._uniq_addr(self.normal_txns_interaction[1])),
            len(self._uniq_addr(self.erc20_txns_interaction[0])),
            len(self._uniq_addr(self.erc20_txns_interaction[1])),
        )
