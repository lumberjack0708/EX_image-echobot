from flask import Flask, request, abort
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, ImageSendMessage

app = Flask(__name__)

# 設定你的 LINE Bot 的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = 'HRPz1stAAOGnaGMyGH3LYiLFs2tpaYgfigaixfB65HrvkAE5J0LlQwe9JWgMsgOKYqH23+yKg7IBreS6RQ0yPs8hWNVIFU8PR+v8pSNYPApK9V1UdDLKLveuq9SfomFWWOsLO9YnWMeyGNDrC+WEvAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'acd24b1ccb99fec2cb9c06a348f0ae84'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 請將此變數替換成你的 ngrok 網域 (例如 "https://xxxx.ngrok.io")
NGROK_PUBLIC_URL = "https://d66f-59-125-140-67.ngrok-free.app"

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 LINE 平台傳來的簽名
    signature = request.headers['X-Line-Signature']

    # 獲取請求的 body
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 驗證簽名
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    # 下載使用者傳送的圖片並儲存至 static 資料夾
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    # 儲存檔案，這裡以 message_id 命名，副檔名依需求調整
    file_name = f"{message_id}.jpg"
    file_path = os.path.join("static", file_name)
    with open(file_path, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
    # 使用 ngrok 公網網址組成圖片 URL
    image_url = NGROK_PUBLIC_URL + "/static/" + file_name
    # 回覆相同的圖片給使用者
    line_bot_api.reply_message(
        event.reply_token,
        ImageSendMessage(
            original_content_url=image_url,
            preview_image_url=image_url
        )
    )

if __name__ == "__main__":
    app.run()