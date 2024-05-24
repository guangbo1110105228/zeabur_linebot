from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import json
import openai
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
LINE_BOT_API = os.getenv('LINE_BOT_API')
WEBHOOK_HANDLER = os.getenv('WEBHOOK_HANDLER')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize LineBot API and WebhookHandler with environment variables
line_bot_api = LineBotApi(LINE_BOT_API)
handler = WebhookHandler(WEBHOOK_HANDLER)
openai.api_key = OPENAI_API_KEY

# Create a single Flask instance
app = Flask(__name__)

def GPT_response(text):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            temperature=0.5,
            max_tokens=500
        )
        return response['choices'][0]['text'].strip()
    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        return "An error occurred while generating the response."

@app.route("/", methods=['GET'])
def home():
    return "Hello, this is the home page!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400, description="Invalid signature. Please check your channel access token/channel secret.")
    except Exception as e:
        app.logger.error(f"Exception: {e}")
    return 'OK'

@handler.add(MessageEvent)
def handle_message(event):
    reply_token = event.reply_token
    message = event.message.text
    if message == 'HI':
        with open('tofel.json', 'r', encoding='utf-8') as file:
            flex_message = json.load(file)
        line_bot_api.reply_message(reply_token, FlexSendMessage('Profile Card', flex_message))
    else:
        gpt_answer = GPT_response(message)
        line_bot_api.reply_message(reply_token, TextSendMessage(text=gpt_answer))

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)