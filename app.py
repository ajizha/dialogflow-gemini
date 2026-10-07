import os
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/", methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    user_message = req.get('queryResult', {}).get('queryText', '')

    if not user_message:
        return jsonify({"fulfillmentText": "Maaf, pesan tidak terbaca."})

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
        )
        ai_reply = response.text
    except Exception as e:
        ai_reply = "Maaf, terjadi kesalahan pada sistem AI."

    return jsonify({"fulfillmentText": ai_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
