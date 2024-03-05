import csv
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://cloudflare-eth.com"))

temp = dict()


def open_dataset(file_name):
    return open(file_name, "r", encoding="UTF-8")


# Читаем данные из датасета Ethereum_Fraud_Detection_Dataset.csv
with open_dataset("./data/open_source_data/Ethereum_Fraud_Detection_Dataset.csv") as dataset_csv:
    dataset = list(csv.reader(dataset_csv))
    temp["0"], temp["1"] = set(), set()
    for row in dataset[1:]:
        temp[row[3]].add(row[2])

# Читаем данные из датасета Etherscan_Malicious_Labels.csv
with open_dataset("./data/open_source_data/Etherscan_Malicious_Labels.csv") as dataset_csv:
    dataset = list(csv.reader(dataset_csv))
    for row in dataset[1:]:
        temp["1"].add(row[0])

# Читаем данные из датасета Etherscan_Phish_Hack_Address.csv
with open_dataset("./data/open_source_data/Etherscan_Phish_Hack_Address.csv") as dataset_csv:
    dataset = list(csv.reader(dataset_csv))
    for row in dataset[1:]:
        temp[row[1]].add(row[0])

for FLAG in ["0", "1"]:
    print(len(temp[FLAG]))


def is_wallet(addr: str) -> bool:
    checksum_addr = Web3.to_checksum_address(addr)
    code = w3.eth.get_code(checksum_addr).hex()
    print(len(code) == 2, addr)
    return len(code) == 2


def open_write_to_dataset(file_name):
    return open(file_name, "w", encoding="UTF-8", newline="")


with (
    open_write_to_dataset("./data/prepared_data/Fraud_Wallets.csv") as fraud_wallets_dataset,
    open_write_to_dataset("./data/prepared_data/Normal_Wallets.csv") as normal_wallets_dataset,
    open_write_to_dataset("./data/prepared_data/Fraud_Contracts.csv") as fraud_contracts_dataset,
):
    writer_wall_fraud, writer_wall_normal = (
        csv.writer(fraud_wallets_dataset),
        csv.writer(normal_wallets_dataset)
    )

    writer_cnt_fraud = csv.writer(fraud_contracts_dataset)

    writer_wall_fraud.writerow(["Fraud_Wallets"])
    writer_wall_normal.writerow(["Normal_Wallets"])
    writer_cnt_fraud.writerow(["Fraud_Contracts"])

    counter = 0
    for FLAG in ["0", "1"]:
        for addr in temp[FLAG]:
            counter += 1
            if counter % 20 == 0:
                fraud_wallets_dataset.flush()
                normal_wallets_dataset.flush()
                fraud_contracts_dataset.flush()
            try:
                if is_wallet(addr):
                    if FLAG == "0":
                        writer_wall_normal.writerow([addr])
                    else:
                        writer_wall_fraud.writerow([addr])
                    continue
                if FLAG == "1":
                    writer_cnt_fraud.writerow([addr])
            except:
                continue


print(len(wallet["0"], wallet["1"], cnt["0"], cnt["1"]))
