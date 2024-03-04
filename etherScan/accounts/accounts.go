package account

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
)


type Request struct {
	client *http.Client
	apiKey string
	url string
}

func New(apiKey string) *Request {
	return &Request{
		client: &http.Client{},
		apiKey: apiKey,
		url: "https://api.etherscan.io/api",
	}
}

func (r *Request) genUrlReq(module, action string, additionalParams map[string]string) string {
	u, _:= url.Parse(r.url)
	q := u.Query()
	q.Add("apikey", r.apiKey)
	q.Add("module", module)
	q.Add("action", action)
	for k, v := range additionalParams {
		q.Add(k, v)	
	}
	u.RawQuery = q.Encode()
	return u.String()
}

func (r *Request) GetBalance(addr string) error {
	reqUrl := r.genUrlReq("account", "balance", map[string]string{
		"address": addr,
		"tag": "latest",
	})
	req, err := http.NewRequest(http.MethodGet, reqUrl, nil)
	if err != nil {
		return err
	}
	res, err := r.client.Do(req)
	if err != nil {
		return err
	}
	defer res.Body.Close()
	
	resB, err := io.ReadAll(res.Body)
	if err != nil {
		return err
	}
	fmt.Println(string(resB))
	return nil
}

func (r *Request) GetNormalTnx(addr string) ([]*NormalTnx, error) {
	reqUrl := r.genUrlReq("account", "txlist", map[string]string{
		"address": addr,
		"startblock": "0",
	})
	req, err := http.NewRequest(http.MethodGet, reqUrl, nil)
	if err != nil {
		return nil, err
	}

	res, err := r.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	
	resB, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	resJson := Response[NormalTnx]{}
	err = json.Unmarshal(resB, &resJson)
	if err != nil {
		return nil, err
	}

	if resJson.Message != "OK" {
		return nil, errors.New("bad response")
	}

	return resJson.Result, err
}

func (r *Request) GetInternalTnx(addr string) ([]*InternalTnx, error) {
	reqUrl := r.genUrlReq("account", "txlistinternal", map[string]string{
		"address": addr,
		"startblock": "0",
	})
	req, err := http.NewRequest(http.MethodGet, reqUrl, nil)
	if err != nil {
		return nil, err
	}
	res, err := r.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	
	resB, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	resJson := Response[InternalTnx]{}
	err = json.Unmarshal(resB, &resJson)
	if err != nil {
		return nil, err
	}

	if resJson.Message != "OK" {
		return nil, errors.New("bad response")
	}

	return resJson.Result, err
}

func (r *Request) GetERC20TransferEvents(addr string) ([]*ERC20TransferEvent, error) {
	reqUrl := r.genUrlReq("account", "tokentx", map[string]string{
		"address": addr,
		"startblock": "0",
	})
	req, err := http.NewRequest(http.MethodGet, reqUrl, nil)
	if err != nil {
		return nil, err
	}
	res, err := r.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	
	resB, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	resJson := Response[ERC20TransferEvent]{}
	err = json.Unmarshal(resB, &resJson)
	if err != nil {
		return nil, err
	}

	if resJson.Message != "OK" {
		return nil, errors.New("bad response")
	}

	return resJson.Result, err
}