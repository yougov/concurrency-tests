package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/gofiber/fiber/v2"
	jsoniter "github.com/json-iterator/go"
	"log"
	"net/http"
	"os"
)

const N_FILES = 50

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}

func fetchUrl(url string) map[string]any {
	var json = jsoniter.ConfigCompatibleWithStandardLibrary
	a := fiber.AcquireAgent()
	req := a.Request()
	req.Header.SetMethod(fiber.MethodGet)
	req.SetRequestURI(url)

	if err := a.Parse(); err != nil {
		panic(err)
	}

	_, body, errs := a.Bytes()
	if errs != nil {
		log.Fatalln(errs)
	}

	var result map[string]any
	err := json.Unmarshal([]byte(body), &result)
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
		results := make([]map[string]any, N_FILES)
		var channels [N_FILES]chan map[string]any

		for i := 0; i < N_FILES; i++ {
			channels[i] = make(chan map[string]any, 1)
		}

		for i := 0; i < N_FILES; i++ {
			go func(i int, channel chan map[string]any) {
				result := fetchUrl(urls[i])
				channel <- result
			}(i, channels[i])
		}

		for i := 0; i < N_FILES; i++ {
			results[i] = <-channels[i]
		}

		c.JSON(http.StatusOK, results)
	})

	r.Run(fmt.Sprintf(":%v", portString))
}
