from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update
import random
import datetime
from transformers import pipeline

# إعداد نموذج GPT-2
chatbot = pipeline("text-generation", model="gpt2")

# قائمة رسائل ترحيب متنوعة بناءً على الوقت
def get_greeting():
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        return "صباح الخير! كيف أقدر أساعدك؟ ☀️"
    elif 12 <= current_hour < 18:
        return "مساء النور! ماذا يمكنني أن أفعل لأجلك؟ 🌞"
    else:
        return "مساء الخير! جاهز للدردشة! 🌙"

# قائمة مزاجات عشوائية للردود
mood_responses = {
    "مرح": ["ههه، سؤال رائع! 😄", "أحب هذا النوع من الأسئلة! 😁"],
    "جاد": ["دعني أجيبك بجدية...", "سؤال مهم. إليك ما أفكر فيه:"],
    "متفائل": ["أشعر بأن الأمور ستكون جيدة! 😊", "دائمًا هناك فرصة جديدة! 🌞"]
}

# ذاكرة قصيرة الأمد للاحتفاظ بآخر موضوع تم مناقشته
last_topic = {}
user_stats = {}

# أوامر البوت الأساسية
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_stats[user_id] = user_stats.get(user_id, 0) + 1
    await update.message.reply_text(get_greeting())

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "الأوامر المتاحة:\n/start - للترحيب\n/help - لمعرفة الأوامر المتاحة\n/حول - لمعلومات عن البوت"
    )

# الدالة الرئيسية لتشغيل البوت
async def main():
    TOKEN = "8035861490:AAGzQJbSrR2wYHBUcb__bELzoMlf_3CvSso"
    
    application = Application.builder().token(TOKEN).build()

    # إضافة الأوامر ومعالجة الرسائل
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # بدء البوت
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())