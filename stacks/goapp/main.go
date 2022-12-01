package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"github.com/gofiber/fiber/v2"
	"net/http"
)

const N_FILES = 50

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}

func fetchUrl(url string) map[string]any {
	resp, err := http.Get(url)
	if err != nil {
		log.Fatalln(err)
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatalln(err)
	}
	var result map[string]any
	err = json.Unmarshal([]byte(body), &result)
	if err != nil {
		log.Fatalln(err)
	}

	return result
}

func main() {
	log.SetFlags(0)
	app := fiber.New()
	nginxBaseUrl := getEnv("NGINX_BASE_URL", "http://nginx")
	portString := getEnv("PORT", "8000")
	urls := make([]string, N_FILES)

	for i := 0; i < N_FILES; i++ {
		urls[i] = fmt.Sprintf("%v/%v.json", nginxBaseUrl, i)
	}

	app.Get("/data", func(c *fiber.Ctx) error {
		var channels [N_FILES]chan map[string]any
		results := make([]map[string]any, N_FILES)

		for i := 0; i < N_FILES; i++ {
			channels[i] = make(chan map[string]any, 1)
		}

		for i := 0; i < N_FILES; i++ {
			go func(channel chan map[string]any, i int) {
				result := fetchUrl(urls[i])
				channel <- result
			}(channels[i], i)
		}

		for i := 0; i < N_FILES; i++ {
			results[i] = <-channels[i]
		}

		body, err := json.Marshal(results)

		if err != nil {
			log.Fatalln(err)
		}

		return c.Send(body)
	})

	app.Listen(fmt.Sprintf(":%v", portString))
}
