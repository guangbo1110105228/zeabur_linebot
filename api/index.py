import logging
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
import openai
import json
import os

# Import TOEIC and TOEFL info functions
from Toefl.kaos import get_toefl_info as get_kaohsiung_info
from Toefl.taichung import get_toefl_info as get_taichung_info
from Toefl.taipei import get_toefl_info as get_taipei_info
from Toeic.NTPC import get_ntpc_info
from Toeic.TVN import get_tvn_info
from Toeic.CHW import get_chw_info

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
LINE_BOT_API = os.getenv('LINE_BOT_API')
WEBHOOK_HANDLER = os.getenv('WEBHOOK_HANDLER')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Initialize LineBot API and WebhookHandler with environment variables
line_bot_api = LineBotApi(LINE_BOT_API)
handler = WebhookHandler(WEBHOOK_HANDLER)

# Create a single Flask instance
app = Flask(__name__)

def GPT_response(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        logging.info(f"GPT-3 response: {response.choices[0]['message']['content'].strip()}")
        return response.choices[0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"GPT error: {e}")
        return "gpt error."

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
        abort(400, description="Exception occurred.")
    return 'OK'

# Handle FollowEvent
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    welcome_message = TextSendMessage(text="感謝您添加我為好友！這是一些有用的資源文件：")
    line_bot_api.push_message(user_id, welcome_message)
    
    # 發送 JSON 文件
    try:
        with open('carousel.json', 'r', encoding='utf-8') as file:
            carousel_message = json.load(file)

        line_bot_api.push_message(user_id, FlexSendMessage(alt_text="Information Cards", contents=carousel_message))
    except FileNotFoundError:
        line_bot_api.push_message(user_id, TextSendMessage(text="Error: Flex message file not found."))
    except json.JSONDecodeError:
        line_bot_api.push_message(user_id, TextSendMessage(text="Error: Flex message file is not valid JSON."))
    except Exception:
        line_bot_api.push_message(user_id, TextSendMessage(text="An error occurred while loading the flex messages."))
    
    # 指示訊息
    instruction_message = TextSendMessage(text="如果您需要這些資訊，請隨時輸入 'HI' 來獲取。")
    line_bot_api.push_message(user_id, instruction_message)

# Handle MessageEvent
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    reply_token = event.reply_token
    message = event.message.text
    user_id = event.source.user_id
    logging.info(f"Received message: {message}")

    # Fetch the chat history from a simple JSON file (replace with your preferred storage)
    user_chat_path = f"chat_{user_id}.json"
    try:
        with open(user_chat_path, 'r', encoding='utf-8') as file:
            messages = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        messages = []

    if message.upper() == 'HI':
        try:
            with open('carousel.json', 'r', encoding='utf-8') as file:
                carousel_message = json.load(file)

            line_bot_api.reply_message(reply_token, FlexSendMessage(alt_text="Information Cards", contents=carousel_message))
        except FileNotFoundError:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="Error: Flex message file not found."))
        except json.JSONDecodeError:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="Error: Flex message file is not valid JSON."))
        except Exception:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="An error occurred while loading the flex messages."))
    elif message == "Please provide the latest TOEFL test centers and times.":
        kaohsiung_info = get_kaohsiung_info()
        taichung_info = get_taichung_info()
        taipei_info = get_taipei_info()
        
        response_message = "最新考試資訊：\n\n"
        
        if kaohsiung_info:
            response_message += f"高雄市：\n日期: {kaohsiung_info[0]}\n地區位置: {kaohsiung_info[1]}\n\n"
        
        if taichung_info:
            response_message += f"台中市：\n日期: {taichung_info[0]}\n地區位置: {taichung_info[1]}\n\n"
        
        if taipei_info:
            response_message += f"台北市：\n日期: {taipei_info[0]}\n地區位置: {taipei_info[1]}\n\n"

        if not kaohsiung_info and not taichung_info and not taipei_info:
            response_message = "无法获取最新考试信息。"
        
        line_bot_api.reply_message(reply_token, TextSendMessage(text=response_message))
    elif message == "The latest Toeic test centers and times.":
        ntpc_info = get_ntpc_info()
        tvn_info = get_tvn_info()
        chw_info = get_chw_info()
        
        response_message = "最新考試資訊：\n\n"
        
        if ntpc_info:
            response_message += f"新北市：\n日期: {ntpc_info[0]}\n報名期間: {ntpc_info[1]}\n追加報名期間: {ntpc_info[2]}\n報名狀態: {ntpc_info[3]}\n\n"
        
        if tvn_info:
            response_message += f"桃竹苗：\n日期: {tvn_info[0]}\n報名期間: {tvn_info[1]}\n追加報名期間: {tvn_info[2]}\n報名狀態: {tvn_info[3]}\n\n"
        
        if chw_info:
            response_message += f"中彰投：\n日期: {chw_info[0]}\n報名期間: {chw_info[1]}\n追加報名期間: {chw_info[2]}\n報名狀態: {chw_info[3]}\n\n"

        if not ntpc_info and not tvn_info and not chw_info:
            response_message = "无法获取最新考试信息。"
        
        line_bot_api.reply_message(reply_token, TextSendMessage(text=response_message))
        
    elif message == "呼叫客服":
        response_message = "已呼叫客服，稍後將有專人與您聯繫。"
        
    else:
        if message == '!清空':
            messages = []
            response_message = "對話歷史紀錄已經清空！"
        else:
            messages.append({"role": "user", "content": message})
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages
                )
                ai_message = response.choices[0].message['content'].strip()
                messages.append({"role": "assistant", "content": ai_message})
                response_message = ai_message
            except Exception as e:
                logging.error(f"GPT error: {e}")
                response_message = "An error occurred while generating the response."
                
        

        # Save the chat history
        with open(user_chat_path, 'w', encoding='utf-8') as file:
            json.dump(messages, file, ensure_ascii=False)

        line_bot_api.reply_message(reply_token, TextSendMessage(text=response_message))

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
