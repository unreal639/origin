package main

/* Go implement of WebBench */

import (
	"context"
	"fmt"
	flag "github.com/spf13/pflag"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"

	"time"
)

/*
 * (C) Radim Kolar 1997-2004
 * This is free software, see GNU Public License version 2 for
 * details.
 *
 * Simple forking WWW Server benchmark:
 *
 * Usage:
 *   webbench --help
 *
 */

var (
	method string

	benchTime int
	clients   int

	force       bool
	forceReload bool
)

var request *http.Request
var urlArg string

var err error

type Count struct {
	speed  int
	failed int
	bytes  int
}

func init() {

	flag.StringVarP(&method, "method", "m", "get",
		"Use request methods with get/head/options/trace.")

	flag.IntVarP(&benchTime, "time", "t", 30,
		"Run benchmark for <sec> seconds.")
	flag.IntVarP(&clients, "client", "c", 1,
		"Run <n> HTTP clients at once.")

	flag.BoolVarP(&force, "force", "f", false,
		"Don't wait for reply from server.")
	flag.BoolVarP(&forceReload, "reload", "r", false,
		"Send reload request - Pragma: no-cache.")

	flag.Parse()

	urlArg = flag.Arg(0)
	_, err := url.ParseRequestURI(urlArg)
	if err != nil {
		log.Fatal(err)
	}

}

func main() {

	buildRequest(urlArg)
	printInfo()
	bench()
}

// Deprecated:
func usage() {
	fmt.Println(`webbench [option]... URL
  -f|--force               Don't wait for reply from server.
  -r|--reload              Send reload request - Pragma: no-cache.
  -t|--time <sec>          Run benchmark for <sec> seconds. Default 30.
  -p|--proxy <server:port> Use proxy server for request.
  -c|--clients <n>         Run <n> HTTP clients at once. Default one.
  -9|--http09              Use HTTP/0.9 style requests.
  -1|--http10              Use HTTP/1.0 protocol.
  -2|--http11              Use HTTP/1.1 protocol.
  --get                    Use GET request method.
  --head                   Use HEAD request method.
  --options                Use OPTIONS request method.
  --trace                  Use TRACE request method.
  -?|-h|--help             This information.
  -V|--version             Display program version.`)
}

func buildRequest(url string) {

	request, err = http.NewRequest(method, url, nil)

	if err != nil {
		fmt.Println(err)
		return
	}
	if forceReload {
		request.Header.Add("Pragma", "no-cache")
	}
}

func printInfo() {
	fmt.Println("Benchmarking: ")
	fmt.Println("request url: ", urlArg)
	fmt.Printf("%d clients\t", clients)
	fmt.Printf("running %d sec\n", benchTime)
	if force {
		fmt.Println("early socket close")
	}
	if forceReload {
		fmt.Println("forcing reload")
	}
}

func bench() {
	result := make(chan Count)

	ctx, _ := context.WithTimeout(context.Background(), time.Duration(benchTime)*time.Second)

	for i := 0; i < clients; i++ {
		go benchCore(ctx, request, result)
	}

	var speedTotal, failedTotal, bytesTotal int

	for {
		cnt := <-result

		speedTotal += cnt.speed
		failedTotal += cnt.failed
		bytesTotal += cnt.bytes

		clients--
		if clients == 0 {
			break
		}
	}

	close(result)

	fmt.Println("------ result ------")
	fmt.Printf("Speed=%d pages/min, %d bytes/sec.\nRequests: %d succeed, %d failed.\n",
		(speedTotal+failedTotal)/benchTime*60, bytesTotal/benchTime, speedTotal, failedTotal)

}

func benchCore(ctx context.Context, req *http.Request, ch chan Count) {

	var client http.Client

	cnt := Count{0, 0, 0}

	client.Timeout = 30 * time.Second
	for {
		select {
		case <-ctx.Done():
			if cnt.failed > 0 {
				cnt.failed--
			}
			ch <- cnt
			return
		default:
			res, err := client.Do(req)
			if err != nil {
				cnt.failed++
				continue
			}

			if !force {
				body, err := ioutil.ReadAll(res.Body)
				if err != nil {
					cnt.failed++
					continue
				}

				err = res.Body.Close()
				if err != nil {
					cnt.failed++
					continue
				}

				cnt.bytes += len(body)

			}
			cnt.speed++
		}
	}
}
