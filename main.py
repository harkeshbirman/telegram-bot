import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from google import genai
from google.genai import types
import mysql.connector

# loading secrets
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("TG_BOT_TOKEN") 
MYSQL_HOST = os.getenv("DB_HOST")
MYSQL_USER = os.getenv("DB_USER")
MYSQL_PASS = os.getenv("DB_PASSWORD")
MYSQL_DB_NAME = os.getenv("DB_NAME")

# mysql connection
conn = mysql.connector.connect(
    host = MYSQL_HOST,  
    user = MYSQL_USER,
    password = MYSQL_PASS,
    database = MYSQL_DB_NAME
)

# gemini client 
gemini_client = genai.Client(api_key = GEMINI_KEY)

# logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start command 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!\nUse /gemini and type your Query...\nHappy to Help!"
    )

# /caps command
async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    caps_text = ' '.join(context.args).upper()
    await context.bot.send_message(update.effective_chat.id, caps_text)


# /add command
async def add_entry(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    node_message = ' '.join(context.args)
    user_id = update.effective_chat.id

    create_database_entry(node_message, user_id)
    await context.bot.send_message(user_id, "added!")

def create_database_entry(message: str, user_id: int): 
    with conn.cursor() as cursor: 
        sql = "INSERT INTO notes (note_content, user_id) VALUES (%s, %s)"
        values = (message, user_id)
        cursor.execute(sql, values)
        conn.commit()


# /get command
async def get_entries(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_chat.id
    entries = get_all_entries(user_id)
    response = '\n'.join(entries) if entries else "no notes found!"

    await context.bot.send_message(user_id, response)

def get_all_entries(user_id: int) -> list: 
    with conn.cursor() as cursor: 
        sql = f"SELECT n.note_content FROM notes n WHERE n.user_id = {user_id}"
        cursor.execute(sql)
        results = cursor.fetchall()
        result_list = [note[0] for note in results]
        return result_list

# /clear command
async def remove_entries(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_chat.id
    remove_all_db(user_id)

    await context.bot.send_message(user_id, "cleared!")

def remove_all_db(user_id: int): 
    with conn.cursor() as cursor: 
        sql = f"DELETE FROM notes WHERE user_id = {user_id}"
        cursor.execute(sql)
        conn.commit()

# /g command 
async def ask_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_prompt = (' '.join(context.args)).strip()
    system_prompt = f"""Hi, My name is {update.effective_chat.first_name} and I'm curious about few things,
        can you please, give me a short and concise answer about the following topic, 
        also, keeep the language frank, you can roast me for my dumbness, but don't be abusive."""
    
    response = gemini_client.models.generate_content(
        model = "gemini-2.0-flash",
        config = types.GenerateContentConfig(
            system_instruction = system_prompt,
            temperature=0.6
        ),
        contents =  user_prompt
    )

    await context.bot.send_message(update.effective_chat.id, response.text)
    
# main method
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    add_handler = CommandHandler('add', add_entry)
    get_handler = CommandHandler('get', get_entries)
    remove_handler = CommandHandler('clear', remove_entries)
    gemini_handler = CommandHandler('g', ask_gemini)
    caps_handler = CommandHandler('caps', caps)

    # add the handlers
    application.add_handlers([
        start_handler,
        add_handler,
        get_handler,
        remove_handler,
        caps_handler, 
        gemini_handler
    ])

    # start the bot
    application.run_polling()

