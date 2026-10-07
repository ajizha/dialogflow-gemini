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
    
    # Daftar urutan model yang akan dicoba secara otomatis
    models_to_try = [
        'gemini-3.6-flash',
        'gemini-3.5-flash-lite',
        'gemini-3.1-pro'
    ]
    
    ai_reply = None
    for model_name in models_to_try:
        try:
            print(f"Mencoba menggunakan model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
            )
            ai_reply = response.text
            if ai_reply:
                print(f"Berhasil dengan model {model_name}! Jawaban: {ai_reply}")
                break
        except Exception as e:
            print(f"Gagal dengan model {model_name}: {e}")
            continue

    if not ai_reply:
        ai_reply = "Maaf, semua model AI sedang sibuk atau mengalami kendala."

    # Membalas pesan secara otomatis ke LINE user/grup
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ai_reply)
    )
    print("Pesan balasan berhasil dikirim ke LINE!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
