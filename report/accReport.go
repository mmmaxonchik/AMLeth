package report

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
}

func GenerateAccReport() {

}