# from flask import Flask, request, abort
# from linebot import LineBotApi, WebhookHandler
# from linebot.exceptions import InvalidSignatureError
# from linebot.models import *
# from openai import OpenAI
# import json
# import logging
# import os

# # gets API Key from environment variable OPENAI_API_KEY
# logging.basicConfig(level=logging.INFO)

# # Load environment variables
# LINE_BOT_API = os.getenv('LINE_BOT_API')
# WEBHOOK_HANDLER = os.getenv('WEBHOOK_HANDLER')
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# client = OpenAI(api_key=OPENAI_API_KEY)

# # Initialize LineBot API and WebhookHandler with environment variables
# line_bot_api = LineBotApi(LINE_BOT_API)
# handler = WebhookHandler(WEBHOOK_HANDLER)

# # Create a single Flask instance
# app = Flask(__name__)

# # Non-streaming:
# print("----- standard request -----")
# completion = client.chat.completions.create(
#     model="gpt-4",
#     messages=[
#         {
#             "role": "user",
#             "content": "Say this is a test",
#         },
#     ],
# )
# print(completion.choices[0].message.content)

# @app.route("/", methods=['GET'])
# def home():
#     return "Hello, this is the home page!"

# @app.route("/callback", methods=['POST'])
# def callback():
#     signature = request.headers['X-Line-Signature']
#     body = request.get_data(as_text=True)
#     app.logger.info(f"Request body: {body}")
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
#         abort(400, description="Invalid signature. Please check your channel access token/channel secret.")
#     except Exception as e:
#         app.logger.error(f"Exception: {e}")
#     return 'OK'

# @handler.add(FollowEvent)
# def handle_follow(event):
#     user_id = event.source.user_id
#     welcome_message = TextSendMessage(text="感謝您添加我為好友！這是一些有用的資源文件：")
#     line_bot_api.push_message(user_id, welcome_message)
    
#     # 發送 JSON 文件
#     try:
#         with open('carousel.json', 'r', encoding='utf-8') as file:
#             carousel_message = json.load(file)

#         line_bot_api.push_message(user_id, FlexSendMessage(alt_text="Information Cards", contents=carousel_message))
#     except FileNotFoundError as e:
#         line_bot_api.push_message(user_id, TextSendMessage(text="Error: Flex message file not found."))
#     except json.JSONDecodeError as e:
#         line_bot_api.push_message(user_id, TextSendMessage(text="Error: Flex message file is not valid JSON."))
#     except Exception as e:
#         line_bot_api.push_message(user_id, TextSendMessage(text="An error occurred while loading the flex messages."))
    
#     # 指示訊息
#     instruction_message = TextSendMessage(text="如果您需要這些資訊，請隨時輸入 'HI' 來獲取。")
#     line_bot_api.push_message(user_id, instruction_message)


# @handler.add(MessageEvent)
# def handle_message(event):
#     reply_token = event.reply_token
#     message = event.message.text
#     logging.info(f"Received message: {message}")
#     if message.upper() == 'HI':
#         try:
#             with open('carousel.json', 'r', encoding='utf-8') as file:
#                 carousel_message = json.load(file)

#             line_bot_api.reply_message(reply_token, FlexSendMessage(alt_text="Information Cards", contents=carousel_message))
#         except FileNotFoundError as e:
#             line_bot_api.reply_message(reply_token, TextSendMessage(text="Error: Flex message file not found."))
#         except json.JSONDecodeError as e:
#             line_bot_api.reply_message(reply_token, TextSendMessage(text="Error: Flex message file is not valid JSON."))
#         except Exception as e:
#             line_bot_api.reply_message(reply_token, TextSendMessage(text="An error occurred while loading the flex messages."))
#     else:
#         try:
#             gpt_answer = GPT_response(message)
#             line_bot_api.reply_message(reply_token, TextSendMessage(text=gpt_answer))
#         except Exception as e:
#             line_bot_api.reply_message(reply_token, TextSendMessage(text="An error occurred while generating the response."))
            
            
# if __name__ == "__main__":
#     port = int(os.getenv('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)