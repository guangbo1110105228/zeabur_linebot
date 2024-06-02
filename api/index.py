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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
        )
        logging.info(f"GPT-3 response: {response}")
        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI Error: {e}")
        return "An error occurred with OpenAI API."
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "An unexpected error occurred."

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
        app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400, description="Invalid signature. Please check your channel access token/channel secret.")
    except Exception as e:
        app.logger.error(f"Exception: {e}")
    return 'OK'

@handler.add(MessageEvent)
def handle_message(event):
    reply_token = event.reply_token
    message = event.message.text
    logging.info(f"Received message: {message}")
    if message == 'Hi':
        try:
            with open('tofel.json', 'r', encoding='utf-8') as file1, \
                 open('ielts.json', 'r', encoding='utf-8') as file2, \
                 open('bigexam.json', 'r', encoding='utf-8') as file3:
                
                flex_message1 = json.load(file1)
                flex_message2 = json.load(file2)
                flex_message3 = json.load(file3)

            messages = [
                FlexSendMessage('TOFEL Profile Card', flex_message1),
                FlexSendMessage('IELTS Profile Card', flex_message2),
                FlexSendMessage('Big Exam Profile Card', flex_message3)
            ]

            line_bot_api.reply_message(reply_token, messages)
        except FileNotFoundError as e:
            logging.error(f"The JSON file was not found: {e}")
            line_bot_api.reply_message(reply_token, TextSendMessage(text="Error: One or more Flex message files not found."))
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            line_bot_api.reply_message(reply_token, TextSendMessage(text="Error: One or more Flex message files are not valid JSON."))
        except Exception as e:
            logging.error(f"Error while reading flex message files: {e}")
            line_bot_api.reply_message(reply_token, TextSendMessage(text="An error occurred while loading the flex messages."))
    else:
        try:
            gpt_answer = GPT_response(message)
            logging.info(f"GPT-3 answer: {gpt_answer}")
            line_bot_api.reply_message(reply_token, TextSendMessage(text=gpt_answer))
        except Exception as e:
            logging.error(f"Error in GPT response: {e}")
            line_bot_api.reply_message(reply_token, TextSendMessage(text="An error occurred while generating the response."))

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

