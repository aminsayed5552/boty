from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from transformers import pipeline
import random
import datetime

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
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_stats[user_id] = user_stats.get(user_id, 0) + 1
    update.message.reply_text(get_greeting())

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "الأوامر المتاحة:\n/بدايه - للترحيب\n/مساعده - لمعرفة الأوامر المتاحة\n/حول - لمعلومات عن البوت\nنكته - لنكتة\nتحفيز - اقتباس تحفيزي\nنصيحه - نصيحة يومية\nتفاعلي - إحصائيات التفاعل"
    )

def about_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "أنا بوت ذكي يعمل بنموذج GPT-2 وأستطيع التفاعل مع المستخدمين في المجموعات كأنني عضو عادي! 😃"
    )

def joke_command(update: Update, context: CallbackContext) -> None:
    jokes = ["لماذا لا يتكلم الكمبيوتر؟ لأنه دائمًا يحاول حفظ الطاقة! 😂", "مرة فيل وقع، قال: أخ أخ! 🐘"]
    update.message.reply_text(random.choice(jokes))

def quote_command(update: Update, context: CallbackContext) -> None:
    quotes = ["النجاح هو القدرة على الانتقال من فشل إلى فشل دون فقدان الحماس. - ونستون تشرشل", "لا تنتظر الفرصة، بل اصنعها. - جورج برنارد شو"]
    update.message.reply_text(random.choice(quotes))

def tip_command(update: Update, context: CallbackContext) -> None:
    tips = ["حافظ على شرب الماء بانتظام! 💧", "خذ استراحة قصيرة لتحسين تركيزك. 🧘‍♂️"]
    update.message.reply_text(random.choice(tips))

def stats_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    update.message.reply_text(f"لقد تحدثت معي {user_stats.get(user_id, 0)} مرة! 😊")

# دالة للرد التلقائي
def reply_to_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    user_id = update.message.from_user.id

    # تحديث إحصائيات المستخدم
    user_stats[user_id] = user_stats.get(user_id, 0) + 1

    # اختيار مزاج عشوائي للرد
    mood = random.choice(list(mood_responses.keys()))
    mood_greeting = random.choice(mood_responses[mood])

    # تحقق من أن الرسالة تحتوي على "تحدث معي" أو إذا كانت رد على رسالة البوت
    if "تحدث معي" in user_message or update.message.reply_to_message:
        update.message.chat.send_action(ChatAction.TYPING)

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
        update.message.reply_text(response)

# الدالة الرئيسية لتشغيل البوت
def main():
    TOKEN = "8035861490:AAGzQJbSrR2wYHBUcb__bELzoMlf_3CvSso"
    
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # إضافة الأوامر ومعالجة الرسائل
    dispatcher.add_handler(CommandHandler("بدايه", start))
    dispatcher.add_handler(CommandHandler("مساعده", help_command))
    dispatcher.add_handler(CommandHandler("حول", about_command))
    dispatcher.add_handler(CommandHandler("نكته", joke_command))
    dispatcher.add_handler(CommandHandler("تحفيز", quote_command))
    dispatcher.add_handler(CommandHandler("نصيحه", tip_command))
    dispatcher.add_handler(CommandHandler("تفاعلي", stats_command))

    # شرط لتفعيل المحادثة عند "تحدث معي" أو عند الرد على رسالة البوت
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command & (Filters.regex(r'تحدث معي') | Filters.reply), 
        reply_to_message
    ))

    # بدء البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()