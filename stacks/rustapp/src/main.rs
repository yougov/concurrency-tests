use std::env;
use actix_web::{get, App, HttpServer, Responder, web};

async fn fetch_json(i: i32) -> serde_json::Value {
    let nginx_base = env::var("NGINX_BASE_URL")
        .unwrap_or("http://nginx".to_string());
    let client = awc::Client::default();
    let url = format!("{}/{}.json", nginx_base, i);
    let req = client.get(url);
    let mut response = req.send().await.unwrap();
    let value = response.json::<serde_json::Value>().await.unwrap();

    value
}

#[get("/data")]
async fn data() -> impl Responder {
    let mut handles = vec![];

    for i in 0..50 {
        let handle = actix_web::rt::spawn(async move {
            let result = fetch_json(i).await;
            result
        });
        handles.push(handle);
    }

    let mut results: Vec<serde_json::Value> = vec![];

    for handle in handles {
        let result = handle.await.unwrap();
        results.push(result);
    }

    web::Json(results)
}

#[tokio::main]
async fn main() -> std::io::Result<()> {
    let port_string = env::var("PORT").unwrap_or("8000".to_string());
    let port: u16 = port_string.parse().unwrap();

    HttpServer::new(|| {
        App::new()
            .service(data)
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
