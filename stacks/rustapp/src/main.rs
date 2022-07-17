use std::env;
use actix_web::{get, App, HttpServer, Responder, web};

#[get("/data")]
async fn data() -> impl Responder {
    let client = awc::Client::default();
    let nginx_base = env::var("NGINX_BASE_URL")
        .unwrap_or("http://nginx".to_string());
    let url = format!("{}/0.json", nginx_base);
    let mut response = client.get(url).send().await.unwrap();
    let val = response.json::<serde_json::Value>().await.unwrap();
    web::Json(val)
}

#[actix_web::main]
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
