from typing import List, Sequence, Tuple
from web3 import AsyncWeb3

from etherscan_sdk.sdk_type import (
    ERC20TransferEvent,
    InternalTransaction,
    NormalTransaction,
    Transaction
)

from etherscan_sdk.sdk import Account

all_txns_type = Transaction | ERC20TransferEvent


class Wallet:
    def __init__(self, account: Account, provider: AsyncWeb3):
        self.address = account.address
        self.account = account
        self.provider = provider

    async def _is_wallet(self, address: str):
        checksum_addr = self.provider.to_checksum_address(address)
        code = await self.provider.eth.get_code(checksum_addr)
        code = code.hex()
        return code == "0x"

    @staticmethod
    def _is_eq_addr(addr1: str, addr2: str):
        return addr1.lower() == addr2.lower()

    @staticmethod
    def _wei_to_eth(wei: int) -> float:
        return wei/1e18

    @staticmethod
    def _get_txns_timestamps(txns_list: Sequence[all_txns_type]):
        txns_timestamps = list(map(lambda txn: int(txn.time_stamp), txns_list))
        txns_timestamps.sort()
        return txns_timestamps

    def _get_statistic_time_btw_txns(self, txns_list: Sequence[all_txns_type]) -> Tuple[int, int, int]:
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

        return (min_time, round(avg_time), max_time)

    # Filters

    def sender(self, txn: all_txns_type):
        return self._is_eq_addr(txn.from_, self.address)

    def receiver(self, txn: all_txns_type):
        return self._is_eq_addr(txn.to_, self.address)

    async def get_internal_transactions(self) -> List[InternalTransaction]:
        return await self.account.get_internal_transactions()

    async def get_normal_txns(self) -> List[NormalTransaction]:
        return await self.account.get_normal_transactions()

    async def get_erc20_events(self) -> List[ERC20TransferEvent]:
        return await self.account.get_erc20_transfer_events()

    async def get_report(self) -> List[int | float]:
        feature_result = []

        normal_txns = await self.get_normal_txns()
        sender_normal_txns = list(filter(self.sender, normal_txns))
        receiver_normal_txns = list(filter(self.receiver, normal_txns))

        receives_txns_values = list(map(
            lambda txn: round(self._wei_to_eth(int(txn.value)), 6),
            receiver_normal_txns
        ))

        sends_txns_values = list(map(
            lambda txn: round(self._wei_to_eth(int(txn.value)), 6),
            sender_normal_txns
        ))

        total_received = sum(receives_txns_values)
        total_send = sum(sends_txns_values)

        ts = self._get_txns_timestamps(normal_txns)
        ts_sender_statistic = self._get_statistic_time_btw_txns(
            sender_normal_txns)
        ts_receiver_statistic = self._get_statistic_time_btw_txns(
            receiver_normal_txns)

        erc20_events = await self.get_erc20_events()
        sender_erc20_txns = list(filter(self.sender, erc20_events))
        receiver_erc20_txns = list(filter(self.receiver, erc20_events))

        send_txns_stat_erc20_time = self._get_statistic_time_btw_txns(
            sender_erc20_txns
        )
        rec_txns_stat_erc20_time = self._get_statistic_time_btw_txns(
            receiver_erc20_txns
        )

        rec_tokens = list(map(
            lambda txn: int(txn.value)/(10**int(txn.token_decimal)),
            receiver_erc20_txns
        ))

        send_tokens = list(map(
            lambda txn: int(txn.value)/(10**int(txn.token_decimal)),
            sender_erc20_txns
        ))

        if len(ts) > 0:
            # Avg_min_between_sent_tnx
            feature_result.append(ts_sender_statistic[1]/60)
            # Avg_min_between_received_tnx
            feature_result.append(ts_receiver_statistic[1]/60)
            # Time_Diff_between_first_and_last_(Mins)
            feature_result.append((max(ts)-min(ts))/60)
        else:
            feature_result.append(0)
            feature_result.append(0)
            feature_result.append(0)

        # Sent_tnx
        feature_result.append(len(sender_normal_txns))
        # Received_tnx
        feature_result.append(len(receiver_normal_txns))
        # Number_of_Created_Contracts - TODO
        feature_result.append(0)
        # Unique_Received_From_Addresses
        feature_result.append(
            len(set(map(lambda txn: txn.from_, receiver_normal_txns))))
        # Unique_Sent_To_Addresses
        feature_result.append(
            len(set(map(lambda txn: txn.to_, sender_normal_txns))))

        if len(receives_txns_values) > 0:
            # Min_Value_Received
            feature_result.append(min(receives_txns_values))
            # Max_Value_Received
            feature_result.append(max(receives_txns_values))
            # Avg_Value_Received
            feature_result.append(sum(receives_txns_values) /
                                  len(receives_txns_values))
        else:
            feature_result.append(0)
            feature_result.append(0)
            feature_result.append(0)

        if len(sends_txns_values) > 0:
            # Min_Val_Sent
            feature_result.append(min(sends_txns_values))
            # Max_Val_Sent
            feature_result.append(max(sends_txns_values))
            # Avg_Val_Sent
            feature_result.append(sum(sends_txns_values) /
                                  len(sends_txns_values))
        else:
            feature_result.append(0)
            feature_result.append(0)
            feature_result.append(0)

        # Min_Value_Sent_To_Contract - TODO
        feature_result.append(0)
        # Max_Value_Sent_To_Contract - TODO
        feature_result.append(0)
        # Avg_Value_Sent_To_Contract - TODO
        feature_result.append(0)
        # Total_Transactions(Including_Tnx_to_Create_Contract) - TODO
        feature_result.append(len(normal_txns)+0)
        # Total_Ether_Sent
        feature_result.append(total_send)
        # Total_Ether_Received
        feature_result.append(total_received)
        # Total_Ether_Sent_Contracts - TODO
        feature_result.append(0)
        # Total_Ether_Balance
        feature_result.append(total_received - total_send)
        # Total_ERC20_Tnxs
        feature_result.append(len(erc20_events))
        # ERC20_Total_Ether_Received
        feature_result.append(sum(map(
            lambda txn: int(txn.value)/(10**int(txn.token_decimal)),
            receiver_erc20_txns
        )))
        # ERC20_Total_Ether_Sent
        feature_result.append(sum(map(
            lambda txn: int(txn.value)/(10**int(txn.token_decimal)),
            sender_erc20_txns
        )))
        # ERC20_Total_Ether_Sent_Contract
        feature_result.append(0)
        # ERC20_Uniq_Sent_Addr
        feature_result.append(
            len(set(map(lambda txn: txn.to_, sender_erc20_txns)))
        )
        # ERC20_Uniq_Rec_Addr
        feature_result.append(
            len(set(map(lambda txn: txn.from_, receiver_erc20_txns)))
        )
        # ERC20_Uniq_Rec_Contract_Addr - TODO
        feature_result.append(0)
        # ERC20_Avg_Time_Between_Sent_Tnx
        feature_result.append(send_txns_stat_erc20_time[1]/60)
        # ERC20_Avg_Time_Between_Rec_Tnx
        feature_result.append(rec_txns_stat_erc20_time[1]/60)
        # ERC20_Avg_Time_Between_Contract_Tnx - TODO
        feature_result.append(0)

        if len(rec_tokens) > 0:
            # ERC20_Min_Val_Rec
            feature_result.append(min(rec_tokens))
            # ERC20_Max_Val_Rec
            feature_result.append(max(rec_tokens))
            # ERC20_Avg_Val_Rec
            feature_result.append(sum(rec_tokens)/len(rec_tokens))
        else:
            feature_result.append(0)
            feature_result.append(0)
            feature_result.append(0)

        if len(send_tokens) > 0:
            # ERC20_Min_Val_Sent
            feature_result.append(min(send_tokens))
            # ERC20_Max_Val_Sent
            feature_result.append(max(send_tokens))
            # ERC20_Avg_Val_Sent
            feature_result.append(sum(send_tokens)/len(send_tokens))
        else:
            feature_result.append(0)
            feature_result.append(0)
            feature_result.append(0)

        return feature_result
