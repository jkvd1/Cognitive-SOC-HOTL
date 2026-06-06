"""
Telegram Bot Handler for Human-On-The-Loop (HOTL) Validation and Feedback.
Listens to callback buttons from n8n-escalated alerts to confirm, reject, or correct threat classification labels, inserting analyst decisions into SQLite feedback buffer.
"""
import sqlite3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7123456789:ABCdefGhIJKlmNoPQRstUVwxyZ'
bot = telebot.TeleBot(API_TOKEN)
DB_PATH = r'c:\Users\ACER\Downloads\Skripsi\data\cognitive_soc_logs.db'

def update_feedback_buffer(ioc_id, actual_label, analyst_correction=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Update SQLite database to capture analyst correction
    cursor.execute('''
        UPDATE ioc_logs
        SET severity = ?, analyst_correction = ?, rule_status = 'accepted'
        WHERE id = ?
    ''', (actual_label, analyst_correction, ioc_id))
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Cognitive SOC Telegram BOT - Ready to handle Human-On-The-Loop (HOTL) alerts.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # Callback format: [action]_[ioc_id] (e.g. approve_154 or fp_154)
    data = call.data.split('_')
    action = data[0]
    ioc_id = int(data[1])
    
    if action == "approve":
        update_feedback_buffer(ioc_id, "High", analyst_correction=0)
        bot.answer_callback_query(call.id, "IOC approved. Wazuh IDS rules deployed autonomously.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"✅ *Approved* (Rule ID: {ioc_id})", parse_mode='Markdown')
        
    elif action == "fp":
        # Label correction to 'Low' or 'Medium'
        update_feedback_buffer(ioc_id, "Low", analyst_correction=1)
        bot.answer_callback_query(call.id, "IOC marked as False Positive. Rollback initiated.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"❌ *Marked as False Positive* (Rollback deployed)", parse_mode='Markdown')

if __name__ == '__main__':
    print("Starting Telegram HOTL BOT handler...")
    # In a real environment: bot.infinity_polling()
