import csv

temp = dict()

# Читаем данные из датасета Ethereum_Fraud_Detection_Dataset.csv
with open("./data/openSourceData/Ethereum_Fraud_Detection_Dataset.csv") as dataset_csv:
    dataset = list(csv.reader(dataset_csv))
    temp["0"], temp["1"] = set(), set()
    for row in dataset[1:]:
        temp[row[3]].add(row[2])

# Читаем данные из датасета Etherscan_Malicious_Labels.csv
with open("./data/openSourceData/Etherscan_Malicious_Labels.csv") as dataset_csv:
    dataset = list(csv.reader(dataset_csv))
    for row in dataset[1:]:
        temp["1"].add(row[0])

# Читаем данные из датасета Etherscan_Phish_Hack_Address.csv
with open("./data/openSourceData/Etherscan_Phish_Hack_Address.csv") as dataset_csv:
    dataset = list(csv.reader(dataset_csv))
    for row in dataset[1:]:
        temp[row[1]].add(row[0])


print(len(temp["1"]))

