use futures_util::{SinkExt, StreamExt};
use serde::{Deserialize, Serialize};
use serde_json::json;
use serde_json::Value;
use std::collections::HashMap;
use std::str::FromStr;
use std::thread;
use std::time::Duration;
use tauri::AppHandle;
use tokio::runtime::Runtime;
use tokio_websockets::{ClientBuilder, Message};

use crate::{
    close_window, create_window,
    settings::{get_settings, Settings},
    BACKEND_HOST, WINDOW_NOTIFICATION_HEIGHT,
};

#[derive(Debug, Serialize, Deserialize)]
pub struct Notification {
    title: String,
    message: Option<String>,
    icon: Option<String>,
    image: Option<String>,
    actions: Option<Vec<Action>>,
    timeout: Option<f32>,
    audio: Option<Audio>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Action {
    command: String,
    label: String,
    data: Option<HashMap<String, String>>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Audio {
    source: String,
    volume: Option<f32>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GetData {
    modules: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Request {
    id: String,
    event: String,
    data: HashMap<String, String>,
    #[doc(hidden)]
    token: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Response {
    id: String,
    r#type: String,
    data: Value,
    subtype: Option<String>,
    message: Option<String>,
    module: Option<String>,
}

pub async fn setup_websocket_client(
    app_handle: AppHandle,
) -> Result<(), Box<dyn std::error::Error>> {
    // Get settings
    let settings: Settings = get_settings();

    let ws_url = format!(
        "ws://{}:{}/api/websocket",
        BACKEND_HOST,
        settings.api.port.to_string(),
    );
    let ws_uri = http::uri::Uri::from_str(ws_url.as_str()).unwrap();

    let (mut client, _) = ClientBuilder::from_uri(ws_uri).connect().await?;

    let mut request = Request {
        id: uuid::Uuid::new_v4().to_string(),
        event: "".to_string(),
        data: HashMap::new(),
        token: settings.api.token.clone(),
    };

    request.event = "REGISTER_DATA_LISTENER".to_string();
    let mut request_json = json!(request);
    request_json["data"] = json!({
      "modules": ["system"]
    });

    let request_string = serde_json::to_string(&request_json).unwrap();
    println!("Sending request: {}", request_string);
    client.send(Message::text(request_string)).await?;

    while let Some(item) = client.next().await {
        // Read the message
        let message = item.unwrap();

        if message.is_close() {
            break;
        }

        if message.is_text() {
            let message_string = message.as_text().unwrap();
            println!("Received message: {}", message_string);

            // Deserialize the message
            let response_result = serde_json::from_str(&message_string);
            if response_result.is_err() {
                println!(
                    "Failed to deserialize message: {}",
                    response_result.unwrap_err()
                );
                continue;
            }
            let response: Response = response_result.unwrap();

            // Handle the message
            match response.r#type.as_str() {
                "DATA_UPDATE" => {
                    println!("Received data update: {:?}", response.data);
                    // TODO: Handle data update
                }
                "NOTIFICATION" => {
                    println!("Received notification: {:?}", response.data);

                    let notification_result = serde_json::from_value(response.data);
                    if notification_result.is_err() {
                        println!(
                            "Failed to deserialize notification: {}",
                            notification_result.unwrap_err()
                        );
                        continue;
                    }
                    let notification: Notification = notification_result.unwrap();
                    let timeout = notification.timeout.unwrap_or(5.0) as u64;

                    // Calculate the window height
                    let mut height: i32 = WINDOW_NOTIFICATION_HEIGHT as i32;
                    let title_lines: i32 =
                        1 + (notification.title.len() as f64 / 52.0).round() as i32;
                    println!("Title Lines: {}", title_lines);
                    if title_lines > 1 {
                        height += 64 * title_lines;
                    }
                    if let Some(message) = &notification.message {
                        height += 24;
                        let message_lines: i32 = 1 + (message.len() as f64 / 62.0).round() as i32;
                        println!("Message Lines: {}", message_lines);
                        if message_lines > 1 {
                            height += 20 * message_lines;
                        }
                    }
                    if notification.image.is_some() {
                        height += 280;
                    }
                    if let Some(actions) = &notification.actions {
                        if !actions.is_empty() {
                            height += 72;
                        }
                    }
                    println!("Window Height: {}", height);

                    let actions_string = if notification.actions.is_some() {
                        serde_json::to_string(notification.actions.as_ref().unwrap()).unwrap()
                    } else {
                        "".to_string()
                    };

                    let audio_string = if notification.audio.is_some() {
                        serde_json::to_string(notification.audio.as_ref().unwrap()).unwrap()
                    } else {
                        "".to_string()
                    };

                    let notification_json = json!({
                        "title": notification.title,
                        "message": notification.message.unwrap_or_else(|| String::from("") ),
                        "icon": notification.icon.unwrap_or_else(|| String::from("") ),
                        "image": notification.image.unwrap_or_else(|| String::from("") ),
                        "actions": actions_string,
                        "timeout": timeout.to_string(),
                        "audio": audio_string,
                    });
                    println!("Notification JSON: {}", notification_json.to_string());

                    let query_string_result = serde_urlencoded::to_string(notification_json);
                    if query_string_result.is_err() {
                        println!(
                            "Failed to serialize notification to query string: {}",
                            query_string_result.unwrap_err()
                        );
                        continue;
                    }
                    let query_string = format!("&{}", query_string_result.unwrap());
                    println!("Query string: {}", query_string);

                    let app_handle_clone_1 = app_handle.clone();
                    let app_handle_clone_2 = app_handle.clone();
                    create_window(
                        app_handle_clone_1,
                        "notification".to_string(),
                        Some(query_string),
                        Some(height),
                    );

                    let _handle = thread::spawn(move || {
                        let rt = Runtime::new().unwrap();
                        rt.block_on(async {
                            println!("Waiting for {} seconds to close the notification", timeout);
                            thread::sleep(Duration::from_secs(timeout));

                            close_window(app_handle_clone_2, "notification".to_string());
                        });
                    });
                }
                _ => {
                    println!("Received event: {}", response.r#type);
                }
            }
        }
    }

    Ok(())
}
