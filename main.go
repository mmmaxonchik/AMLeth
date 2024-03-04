package main

import (
	account "eth/etherScan/accounts"
	"fmt"
	"strconv"
)


type AccountReport struct {
	// Wallet address
	Address string
	// Total count of sent transaction
	TotalSentTnx uint64
	// Total count of sent transaction
	TotalReceivedTnx uint64
	// Maximum of eth balance at wallet
	MaxEthBalance float64
	// Minimum of eth balance at wallet
	MinEthBalance float64
	// Average of eth balance at wallet
	AvgEthBalance float64
	// Total eth volume
	EthVolume float64
}

func GenerateAccReport() {
	weiToEth :=  func(wei uint64) float64 {
		return float64(wei) / float64(1e18)
	}
	
	newReport := AccountReport{}
	
	addr := "0x0945198dd98c78d88568004d775e33800cfe4bfa"
	tnx, err := account.New(apiKey).GetNormalTnx(addr)	
	if err != nil {
		return
	}
	for _, v := range tnx {
		if v.From == addr {
			newReport.TotalSentTnx += 1
			wei, _ := strconv.ParseUint(v.Value, 10, 64)
			newReport.EthVolume += weiToEth(wei)
		}
		if v.To == addr {
			newReport.TotalReceivedTnx += 1
			wei, _ := strconv.ParseUint(v.Value, 10, 64)
			newReport.EthVolume += weiToEth(wei)			
		}
	}

	fmt.Println(newReport)

}

func main() {
	GenerateAccReport()
}