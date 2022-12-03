package main

import (
	"encoding/json"
	"fmt"
	"github.com/gin-gonic/gin"
	"io"
	"log"
	"net/http"
	"os"
)

const N_FILES = 50

type ResultMap = map[string]any
type Result struct {
	index int
	data ResultMap
}

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}

func fetchUrl(url string) ResultMap {
	response, err := http.Get(url)
	if err != nil {
		log.Fatalln(err)
	}

	body, err := io.ReadAll(response.Body)
	if err != nil {
		log.Fatalln(err)
	}

	var result ResultMap
	err = json.Unmarshal([]byte(body), &result)
	if err != nil {
		log.Fatalln(err)
	}

	return result
}

func main() {
	log.SetFlags(0)
	r := gin.Default()
	nginxBaseUrl := getEnv("NGINX_BASE_URL", "http://nginx")
	portString := getEnv("PORT", "8000")
	urls := make([]string, N_FILES)

	for i := 0; i < N_FILES; i++ {
		urls[i] = fmt.Sprintf("%v/%v.json", nginxBaseUrl, i)
	}

	r.GET("/data", func(c *gin.Context) {
		log.Println("Received data request.")
		results := make([]ResultMap, N_FILES)
		channel := make(chan Result, N_FILES)

		for i := 0; i < N_FILES; i++ {
			go func(i int, channel chan Result) {
				data := fetchUrl(urls[i])
				channel <- Result{i, data}
			}(i, channel)
		}

		for i := 0; i < N_FILES; i++ {
			result := <-channel
			results[result.index] = result.data
		}

		c.JSON(http.StatusOK, results)
	})

	r.Run(fmt.Sprintf(":%v", portString))
}
