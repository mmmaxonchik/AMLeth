import asyncio
from aiohttp import ClientError
from functools import reduce
from etherscan_sdk.account_sdk import get_normal_transactions
from etherscan_sdk.account_sdk import get_ether_balance
from etherscan_sdk.account_sdk import get_internal_transactions
from etherscan_sdk.account_sdk import get_erc20_transactions
from web3 import AsyncWeb3
from random import randint

nets = [
    "https://eth.drpc.org",
    "https://eth-pokt.nodies.app",
    "https://rpc.mevblocker.io",
    "https://cloudflare-eth.com",
    "https://rpc.mevblocker.io"
]


def _wei_to_eth(wei):
    return wei/1e18


def _get_uniq_addr(txns):
    uniq_addr = set(
        map(lambda txn: txn["from"], txns)
    ).union(map(lambda txn: txn["to"], txns))
    return uniq_addr


def _eth_distr(txns, place, addr):
    eth_in_txns = list(
        map(
            lambda txn: _wei_to_eth(int(txn["value"])),
            filter(lambda txn: txn[place] == addr, txns)
        )
    )
    if not len(eth_in_txns):
        return [0, 0, 0]
    return [min(eth_in_txns), sum(eth_in_txns)/len(eth_in_txns), max(eth_in_txns)]


async def _is_wallet(addr: str):
    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
        nets[randint(0, len(nets)-1)]
    ))

    try:
        checksum_addr = w3.to_checksum_address(addr)
        code = await w3.eth.get_code(checksum_addr)
    except Exception as err:
        if isinstance(err, ClientError):
            await _is_wallet(addr)
        print(err)
        return

    return code.hex() == "0x"


def _time_btw_txns(txns):
    txns_timestamps = list(map(
        lambda txn: int(txn["timeStamp"]),
        txns
    ))
    txns_timestamps.sort()

    if len(txns_timestamps) < 2:
        return [0, 0, 0]

    min_time = txns_timestamps[1]-txns_timestamps[0]
    for i in range(0, len(txns_timestamps)):
        if i == len(txns_timestamps)-1:
            break
        it_res = txns_timestamps[i+1]-txns_timestamps[i]
        if min_time > it_res:
            min_time = it_res

    avg_time = 0
    for i in range(len(txns_timestamps)-1, -1, -1):
        if i == 0:
            break
        avg_time += txns_timestamps[i]-txns_timestamps[i-1]
    avg_time /= len(txns_timestamps)

    max_time = txns_timestamps[1]-txns_timestamps[0]
    for i in range(0, len(txns_timestamps)):
        if i == len(txns_timestamps)-1:
            break
        it_res = txns_timestamps[i+1]-txns_timestamps[i]
        if max_time < it_res:
            max_time = it_res

    return [min_time, round(avg_time), max_time]


def _make_uniq_and_filter(txns):
    uniq_txns = {txn["hash"].lower(): txn for txn in txns}
    uniq_txns = list(uniq_txns.values())
    for txn in uniq_txns:
        txn["from"] = txn["from"].lower()
        txn["to"] = txn["to"].lower()
    return uniq_txns


async def create_wallet_report(addr: str):
    addr = addr.lower()
    # balance = await get_ether_balance(addr)
    normal_txns = await get_normal_transactions(
        addr
    )
    normal_txns = _make_uniq_and_filter(normal_txns)

    internal_txns = await get_internal_transactions(addr)
    internal_txns = _make_uniq_and_filter(internal_txns)

    erc20_txns = await get_erc20_transactions(addr)
    erc20_txns = _make_uniq_and_filter(erc20_txns)

    # Обычные транзакции с кошельками
    normal_wallets_txns = list(
        filter(lambda txn: txn["methodId"] == "0x", normal_txns)
    )

    async def filter_txns(txns, place):
        filtered_txns = []
        for txn in txns:
            if not await _is_wallet(txn[place]):
                filtered_txns.append(txn)
        return filtered_txns

    # Обычные транзакции со смарт-контрактами
    smart_contract_txns_out = await filter_txns(normal_txns, "to")

    smart_contract_txns_in = await filter_txns(normal_txns, "from")

    smart_contract_txns = smart_contract_txns_out + smart_contract_txns_in

    # Все транзакции
    all_txns = _make_uniq_and_filter(normal_txns+internal_txns+erc20_txns)

    txns_timestamps = list(sorted(map(
        lambda txn: int(txn["timeStamp"]),
        all_txns
    )))

    ###### Заполнение отчета ######
    report = dict()

    # Время между всеми обычными транзакциями(минимальное, среднее, максимальное)
    report["Min_Time_Btw_Normal_Txns"], report["Avg_Time_Btw_Normal_Txns"], report["Max_Time_Btw_Normal_Txns"] = _time_btw_txns(
        normal_txns
    )

    # Время между внутренними транзакциями(минимальное, среднее, максимальное)
    report["Min_Time_Btw_Internal_Txns"], report["Avg_Time_Btw_Internal_Txns"], report["Max_Time_Btw_Internal_Txns"] = _time_btw_txns(
        internal_txns
    )

    # Время между транзакциями с ERC20(минимальное, среднее, максимальное)
    report["Min_Time_Btw_ERC20_Txns"], report["Avg_Time_Btw_ERC20_Txns"], report["Max_Time_Btw_ERC20_Txns"] = _time_btw_txns(
        erc20_txns
    )

    # Количество всех транзакций
    report["Txns"] = len(all_txns)

    # Количество обычных(normal) транзакций
    report["Normal_Txns"] = len(normal_txns)

    # Количество внутренних(internal) транзакций
    report["Internal_Txns"] = len(internal_txns)

    # Количество транзакций со стандартом токена ERC20
    report["ERC20_Txns"] = len(erc20_txns)

    # Общий объем Eth пропущенного через кошелек
    report["Eth_Volume"] = reduce(
        lambda a, b: a+b,
        map(
            lambda txn: _wei_to_eth(int(txn["value"])),
            normal_txns
        ),
        0
    )

    # Количество транзакций с кошельками
    report["Wallet_Txns"] = len(normal_wallets_txns)

    # Количество транзакций с кошельками инициированных иным кошельком
    report["Wallet_Txns_In"] = len(
        list(
            filter(
                lambda txn: txn["to"] == addr,
                normal_wallets_txns
            )
        )
    )

    # Количество транзакций с кошельками инициированных владельцем
    report["Wallet_Txns_Out"] = report["Wallet_Txns"] - \
        report["Wallet_Txns_In"]

    # Количество транзакций со смарт-контрактами
    report["Smart_Contract_Txns"] = len(smart_contract_txns)

    # Количество транзакций со смарт-контрактами инициированных контрактом
    report["Smart_Contract_Txns_In"] = len(
        smart_contract_txns_in
    )

    # Количество транзакций со смарт-контрактами инициированных кошельком
    report["Smart_Contract_Txns_Out"] = len(
        smart_contract_txns_out
    )

    # Минимальное/Среднее/Максимальное количество отправленного Ethereum
    report["Min_Eth_Send_By_Txn"], report["Avg_Eth_Send_By_Txn"], report["Max_Eth_Send_By_Txn"] = _eth_distr(
        normal_txns, "from", addr
    )

    # Минимальное/Среднее/Максимальное количество полученного Ethereum
    report["Min_Eth_Get_By_Txn"], report["Avg_Eth_Get_By_Txn"], report["Max_Eth_Get_By_Txn"] = _eth_distr(
        normal_txns, "to", addr
    )

    # Общее количество транзакций с уникальными адресами
    report["Txns_With_Uniq_Addr"] = len(_get_uniq_addr(all_txns))-1

    # Количество обычных транзакций с уникальными адресами
    report["Normal_Txns_With_Uniq_Addr"] = len(_get_uniq_addr(normal_txns))-1

    # Количество внутренних транзакций с уникальными адресами
    report["Internal_Txns_With_Uniq_Addr"] = len(
        _get_uniq_addr(internal_txns)
    )-1

    # Количество транзакций с ERC20 токенами с уникальными адресами
    report["ERC20_Txns_With_Uniq_Addr"] = len(_get_uniq_addr(erc20_txns))-1

    # Разница между первой и последней транзакцией
    report["Time_Btw_FTxn_LTxn"] = (
        txns_timestamps[-1]-txns_timestamps[0]
    )*1000

    print(report)


async def main():
    txns = await create_wallet_report(
        "0xE84774afe41f7d76188Cc78605d50FBd677fa1D3"
    )

if __name__ == "__main__":
    asyncio.run(main())
