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
        "الأوامر المتاحة:\n/start - للترحيب\n/help - لمعرفة الأوامر المتاحة\n/about - لمعلومات عن البوت\n/joke - لنكتة\n/quote - اقتباس تحفيزي\n/tip - نصيحة يومية\n/stats - إحصائيات التفاعل"
    )

async def about_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "أنا بوت ذكي يعمل بنموذج GPT-2 وأستطيع التفاعل مع المستخدمين في المجموعات كأنني عضو عادي! 😃"
    )

async def joke_command(update: Update, context: CallbackContext) -> None:
    jokes = ["لماذا لا يتكلم الكمبيوتر؟ لأنه دائمًا يحاول حفظ الطاقة! 😂", "مرة فيل وقع، قال: أخ أخ! 🐘"]
    await update.message.reply_text(random.choice(jokes))

async def quote_command(update: Update, context: CallbackContext) -> None:
    quotes = ["النجاح هو القدرة على الانتقال من فشل إلى فشل دون فقدان الحماس. - ونستون تشرشل", "لا تنتظر الفرصة، بل اصنعها. - جورج برنارد شو"]
    await update.message.reply_text(random.choice(quotes))

async def tip_command(update: Update, context: CallbackContext) -> None:
    tips = ["حافظ على شرب الماء بانتظام! 💧", "خذ استراحة قصيرة لتحسين تركيزك. 🧘‍♂️"]
    await update.message.reply_text(random.choice(tips))

async def stats_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    await update.message.reply_text(f"لقد تحدثت معي {user_stats.get(user_id, 0)} مرة! 😊")

# دالة للرد التلقائي
async def reply_to_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    user_id = update.message.from_user.id

    # تحديث إحصائيات المستخدم
    user_stats[user_id] = user_stats.get(user_id, 0) + 1

    # اختيار مزاج عشوائي للرد
    mood = random.choice(list(mood_responses.keys()))
    mood_greeting = random.choice(mood_responses[mood])

    # تحقق من أن الرسالة تحتوي على "تحدث معي" أو إذا كانت رد على رسالة البوت
    if "تحدث معي" in user_message or update.message.reply_to_message:
        await update.message.chat.send_action("typing")

        # ردود خاصة لبعض الكلمات الشائعة
        if any(keyword in user_message for keyword in ["أهلاً", "مرحباً", "كيف الحال؟"]):
            response = f"{mood_greeting} كيف يمكنني مساعدتك؟"
        elif "شكراً" in user_message:
            response = f"على الرحب والسعة! 😊 إذا كان لديك سؤال آخر، لا تتردد في طرحه."
        else:
            # توليد الرد باستخدام GPT-2
            gpt_response = chatbot(user_message, max_length=50, num_return_sequences=1)[0]['generated_text']
            
            # إضافة ذاكرة قصيرة الأمد
            if user_id in last_topic:
                response = f"كما ذكرتُ سابقًا عن '{last_topic[user_id]}': {mood_greeting} {gpt_response}"
            else:
                response = f"{mood_greeting} {gpt_response}"
            
            # تحديث الموضوع الأخير
            last_topic[user_id] = user_message

        # الرد على الرسالة
        await update.message.reply_text(response)

# الدالة الرئيسية لتشغيل البوت
async def main():
    TOKEN = "8035861490:AAGzQJbSrR2wYHBUcb__bELzoMlf_3CvSso"
    
    application = Application.builder().token(TOKEN).build()

    # إضافة الأوامر ومعالجة الرسائل
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("joke", joke_command))
    application.add_handler(CommandHandler("quote", quote_command))
    application.add_handler(CommandHandler("tip", tip_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # شرط لتفعيل المحادثة عند "تحدث معي" أو عند الرد على رسالة البوت
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & (filters.Regex(r'تحدث معي') | filters.REPLY), 
        reply_to_message
    ))

    # بدء البوت
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())