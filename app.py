import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from google import genai

app = Flask(__name__)

# Konfigurasi LINE & Gemini dari Environment Variables Railway
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    # Cetak log untuk memastikan webhook LINE benar-benar masuk ke server
    print(f"Incoming request body: {body}")

    if not signature and not body:
        return 'OK'

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        print(f"Invalid signature error: {e}")
        abort(400)
    except Exception as e:
        print(f"Webhook handling error: {e}")
        abort(500)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    print(f"Pesan diterima dari user: {user_message}")
    
    try:
        # Meminta jawaban dari Gemini AI
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
        )
        ai_reply = response.text
        print(f"Jawaban Gemini: {ai_reply}")
    except Exception as e:
        print(f"Gemini API Error: {e}")
        ai_reply = "Maaf, terjadi kesalahan pada sistem AI."

    # Membalas pesan secara otomatis ke LINE user/grup
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ai_reply)
    )
    print("Pesan balasan berhasil dikirim ke LINE!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
