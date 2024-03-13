from dataclasses import dataclass


@dataclass
class Transaction:
    block_number: str
    time_stamp: str
    hash_: str
    from_: str
    to_: str
    value: str
    gas: str
    is_error: str
    gas_used: str


@dataclass
class NormalTransaction(Transaction):
    nonce: str
    block_hash: str
    transaction_index: str
    gas_price: str
    tx_receipt_status: str
    input_: str
    contract_address: str
    cumulative_gas_used: str
    confirmations: str
    method_id: str
    function_name: str

    @staticmethod
    def from_dict(obj) -> "NormalTransaction":
        return NormalTransaction(
            str(obj.get("blockNumber")),
            str(obj.get("timeStamp")),
            str(obj.get("hash")),
            str(obj.get("from")),
            str(obj.get("to")),
            str(obj.get("value")),
            str(obj.get("gas")),
            str(obj.get("isError")),
            str(obj.get("gasUsed")),
            str(obj.get("nonce")),
            str(obj.get("blockHash")),
            str(obj.get("transactionIndex")),
            str(obj.get("gasPrice")),
            str(obj.get("txreceipt_status")),
            str(obj.get("input")),
            str(obj.get("contractAddress")),
            str(obj.get("cumulativeGasUsed")),
            str(obj.get("confirmations")),
            str(obj.get("methodId")),
            str(obj.get("functionName"))
        )


@dataclass
class InternalTransaction(Transaction):
    contract_address: str
    type: str
    trace_id: str
    err_code: str

    @staticmethod
    def from_dict(obj) -> "InternalTransaction":
        return InternalTransaction(
            str(obj.get("blockNumber")),
            str(obj.get("timeStamp")),
            str(obj.get("hash")),
            str(obj.get("from")),
            str(obj.get("to")),
            str(obj.get("value")),
            str(obj.get("gas")),
            str(obj.get("isError")),
            str(obj.get("gasUsed")),
            str(obj.get("contractAddress")),
            str(obj.get("type")),
            str(obj.get("traceId")),
            str(obj.get("errCode"))
        )


@dataclass
class ERC20TransferEvent:
    block_number: str
    time_stamp: str
    hash_: str
    nonce: str
    block_hash: str
    from_: str
    contract_address: str
    to_: str
    value: str
    token_name: str
    token_symbol: str
    token_decimal: str
    transaction_index: str
    gas: str
    gas_price: str
    gas_used: str
    cumulative_gas_used: str
    input_: str
    confirmations: str

    @staticmethod
    def from_dict(obj) -> 'ERC20TransferEvent':
        return ERC20TransferEvent(
            str(obj.get("blockNumber")),
            str(obj.get("timeStamp")),
            str(obj.get("hash")),
            str(obj.get("nonce")),
            str(obj.get("blockHash")),
            str(obj.get("from")),
            str(obj.get("contractAddress")),
            str(obj.get("to")),
            str(obj.get("value")),
            str(obj.get("tokenName")),
            str(obj.get("tokenSymbol")),
            str(obj.get("tokenDecimal")),
            str(obj.get("transactionIndex")),
            str(obj.get("gas")),
            str(obj.get("gasPrice")),
            str(obj.get("gasUsed")),
            str(obj.get("cumulativeGasUsed")),
            str(obj.get("input")),
            str(obj.get("confirmations"))
        )
