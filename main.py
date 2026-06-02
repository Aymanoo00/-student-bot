# -*- coding: utf-8 -*-
import json
import os
import logging
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ==================== الإعدادات ====================
BOT_TOKEN = "8599384103:AAH-N8xGX8HIZTteolimOV5c5mwog1LtLtg"
ADMIN_ID = 123456789  # ضع آيدي المشرف هنا
BOT_NAME = "سند الطلاب للخدمات الطلابية"
SUPPORT_CONTACT = "@SanadStudents"

DATA_FILE = "data.json"

# ==================== اللوجر ====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ==================== حالات المحادثة ====================
(
    STATE_NAME,
    STATE_MAJOR,
    STATE_LEVEL,
    STATE_DESC,
    STATE_CONFIRM,
) = range(5)

STATE_BROADCAST = 100
STATE_CHANGE_STATUS_ID = 200
STATE_CHANGE_STATUS_VALUE = 201

# ==================== الخدمات ====================
SERVICES = [
    "حل الواجبات والتكاليف",
    "إعداد البحوث والتقارير",
    "عروض PowerPoint",
    "تلخيص الكتب",
    "مشاريع التخرج",
    "الترجمة الأكاديمية",
    "البرمجة والمشاريع",
    "تحليل البيانات",
]

ORDER_STATUSES = ["جديد", "قيد التنفيذ", "مكتمل"]

# ==================== أزرار القوائم ====================
BTN_SERVICES = "📚 الخدمات"
BTN_MY_ORDERS = "📋 طلباتي"
BTN_SUPPORT = "📞 الدعم"
BTN_ABOUT = "ℹ️ من نحن"
BTN_ADMIN = "👨‍💼 لوحة المشرف"
BTN_BACK = "🔙 رجوع"
BTN_CANCEL = "❌ إلغاء"
BTN_CONFIRM = "✅ تأكيد الطلب"


# ==================== إدارة البيانات JSON ====================
def init_data():
    if not os.path.exists(DATA_FILE):
        data = {"users": {}, "orders": {}, "counter": 0}
        save_data(data)
        return data
    return load_data()


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "users" not in data:
            data["users"] = {}
        if "orders" not in data:
            data["orders"] = {}
        if "counter" not in data:
            data["counter"] = 0
        return data
    except (json.JSONDecodeError, FileNotFoundError):
        data = {"users": {}, "orders": {}, "counter": 0}
        save_data(data)
        return data


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"خطأ في حفظ البيانات: {e}")


def register_user(user):
    data = load_data()
    uid = str(user.id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "id": user.id,
            "name": user.full_name,
            "username": user.username or "",
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        save_data(data)


def generate_order_number():
    data = load_data()
    data["counter"] += 1
    save_data(data)
    year = datetime.now().year
    return f"KYAN-{year}-{data['counter']:04d}"


# ==================== لوحات المفاتيح ====================
def main_keyboard(user_id):
    keyboard = [
        [BTN_SERVICES, BTN_MY_ORDERS],
        [BTN_SUPPORT, BTN_ABOUT],
    ]
    if user_id == ADMIN_ID:
        keyboard.append([BTN_ADMIN])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def services_keyboard():
    keyboard = []
    row = []
    for i, service in enumerate(SERVICES, start=1):
        row.append(service)
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([BTN_BACK])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def cancel_keyboard():
    return ReplyKeyboardMarkup([[BTN_CANCEL]], resize_keyboard=True)


def confirm_keyboard():
    return ReplyKeyboardMarkup(
        [[BTN_CONFIRM], [BTN_CANCEL]], resize_keyboard=True
    )


def admin_keyboard():
    keyboard = [
        ["📊 الإحصائيات", "🗂 آخر الطلبات"],
        ["🔄 تغيير حالة طلب", "📢 إرسال إعلان"],
        [BTN_BACK],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ==================== الأوامر الأساسية ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)
    text = (
        f"👋 أهلاً بك في *{BOT_NAME}*\n\n"
        "نحن هنا لمساعدتك في خدماتك الطلابية والأكاديمية.\n"
        "اختر من القائمة بالأسفل للبدء 👇"
    )
    await update.message.reply_text(
        text,
        reply_markup=main_keyboard(user.id),
        parse_mode="Markdown",
    )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        "📌 القائمة الرئيسية:",
        reply_markup=main_keyboard(user.id),
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"ℹ️ *من نحن*\n\n"
        f"*{BOT_NAME}* منصة متخصصة في تقديم الخدمات الطلابية "
        "والأكاديمية بجودة واحترافية عالية.\n\n"
        "نقدم حلولاً متكاملة تشمل البحوث، التقارير، العروض، "
        "البرمجة، الترجمة وغيرها الكثير.\n\n"
        "✨ هدفنا تسهيل رحلتك الدراسية وتحقيق التميز الأكاديمي."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📞 *الدعم الفني*\n\n"
        "لأي استفسار أو مساعدة يمكنك التواصل معنا عبر:\n"
        f"👤 {SUPPORT_CONTACT}\n\n"
        "نسعد بخدمتك في أي وقت 💬"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📚 *الخدمات المتاحة*\n\nاختر الخدمة التي ترغب بطلبها 👇"
    await update.message.reply_text(
        text, reply_markup=services_keyboard(), parse_mode="Markdown"
    )


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    user_orders = [
        o for o in data["orders"].values() if o["user_id"] == user.id
    ]
    if not user_orders:
        await update.message.reply_text(
            "📋 لا توجد لديك أي طلبات حتى الآن.\n"
            "اختر 📚 الخدمات لإنشاء طلب جديد."
        )
        return

    text = "📋 *طلباتك:*\n\n"
    for o in user_orders:
        status_icon = {
            "جديد": "🆕",
            "قيد التنفيذ": "⏳",
            "مكتمل": "✅",
        }.get(o["status"], "❔")
        text += (
            f"🔖 *رقم الطلب:* `{o['order_number']}`\n"
            f"📚 *الخدمة:* {o['service']}\n"
            f"{status_icon} *الحالة:* {o['status']}\n"
            f"📅 *التاريخ:* {o['date']}\n"
            "━━━━━━━━━━━━━━━\n"
        )
    await update.message.reply_text(text, parse_mode="Markdown")


# ==================== نظام الطلبات (Conversation) ====================
async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service not in SERVICES:
        return ConversationHandler.END

    context.user_data["service"] = service
    await update.message.reply_text(
        f"✅ اخترت خدمة: *{service}*\n\n"
        "الرجاء إدخال *اسمك الكامل*:",
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown",
    )
    return STATE_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == BTN_CANCEL:
        return await cancel_order(update, context)
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        "📘 الرجاء إدخال *تخصصك الدراسي*:",
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown",
    )
    return STATE_MAJOR


async def get_major(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == BTN_CANCEL:
        return await cancel_order(update, context)
    context.user_data["major"] = update.message.text
    await update.message.reply_text(
        "🎓 الرجاء إدخال *المستوى الدراسي* (مثال: السنة الثالثة):",
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown",
    )
    return STATE_LEVEL


async def get_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == BTN_CANCEL:
        return await cancel_order(update, context)
    context.user_data["level"] = update.message.text
    await update.message.reply_text(
        "📝 الرجاء كتابة *وصف تفصيلي للطلب*:",
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown",
    )
    return STATE_DESC


async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == BTN_CANCEL:
        return await cancel_order(update, context)
    context.user_data["description"] = update.message.text

    summary = (
        "🔎 *مراجعة الطلب:*\n\n"
        f"📚 *الخدمة:* {context.user_data['service']}\n"
        f"👤 *الاسم:* {context.user_data['name']}\n"
        f"📘 *التخصص:* {context.user_data['major']}\n"
        f"🎓 *المستوى:* {context.user_data['level']}\n"
        f"📝 *الوصف:* {context.user_data['description']}\n\n"
        "هل تريد تأكيد الطلب؟"
    )
    await update.message.reply_text(
        summary, reply_markup=confirm_keyboard(), parse_mode="Markdown"
    )
    return STATE_CONFIRM


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == BTN_CANCEL:
        return await cancel_order(update, context)

    if text != BTN_CONFIRM:
        await update.message.reply_text(
            "الرجاء الضغط على ✅ تأكيد الطلب أو ❌ إلغاء.",
            reply_markup=confirm_keyboard(),
        )
        return STATE_CONFIRM

    order_number = generate_order_number()
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    order = {
        "order_number": order_number,
        "user_id": user.id,
        "user_name": context.user_data["name"],
        "username": user.username or "",
        "service": context.user_data["service"],
        "major": context.user_data["major"],
        "level": context.user_data["level"],
        "description": context.user_data["description"],
        "status": "جديد",
        "date": order_date,
    }

    data = load_data()
    data["orders"][order_number] = order
    save_data(data)

    await update.message.reply_text(
        f"🎉 *تم استلام طلبك بنجاح!*\n\n"
        f"🔖 رقم الطلب: `{order_number}`\n"
        f"📚 الخدمة: {order['service']}\n\n"
        "سيتم التواصل معك قريباً ✅",
        reply_markup=main_keyboard(user.id),
        parse_mode="Markdown",
    )

    # إشعار المشرف
    try:
        admin_text = (
            "🔔 *طلب جديد!*\n\n"
            f"🔖 رقم الطلب: `{order_number}`\n"
            f"👤 الاسم: {order['user_name']}\n"
            f"🆔 المستخدم: {user.id}\n"
            f"📛 المعرف: @{order['username'] or 'غير متوفر'}\n"
            f"📚 الخدمة: {order['service']}\n"
            f"📘 التخصص: {order['major']}\n"
            f"🎓 المستوى: {order['level']}\n"
            f"📝 الوصف: {order['description']}\n"
            f"📅 التاريخ: {order['date']}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"خطأ في إشعار المشرف: {e}")

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    await update.message.reply_text(
        "❌ تم إلغاء الطلب.",
        reply_markup=main_keyboard(user.id),
    )
    return ConversationHandler.END


# ==================== لوحة المشرف ====================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("⛔ هذا القسم مخصص للمشرف فقط.")
        return
    await update.message.reply_text(
        "👨‍💼 *لوحة المشرف*\n\nاختر الإجراء المطلوب 👇",
        reply_markup=admin_keyboard(),
        parse_mode="Markdown",
    )


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    data = load_data()
    total_orders = len(data["orders"])
    total_users = len(data["users"])
    new_orders = sum(
        1 for o in data["orders"].values() if o["status"] == "جديد"
    )
    in_progress = sum(
        1 for o in data["orders"].values() if o["status"] == "قيد التنفيذ"
    )
    completed = sum(
        1 for o in data["orders"].values() if o["status"] == "مكتمل"
    )
    text = (
        "📊 *الإحصائيات*\n\n"
        f"👥 عدد المستخدمين: *{total_users}*\n"
        f"📦 عدد الطلبات: *{total_orders}*\n\n"
        f"🆕 جديد: *{new_orders}*\n"
        f"⏳ قيد التنفيذ: *{in_progress}*\n"
        f"✅ مكتمل: *{completed}*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def admin_last_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    data = load_data()
    orders = list(data["orders"].values())
    if not orders:
        await update.message.reply_text("🗂 لا توجد طلبات حتى الآن.")
        return
    last = orders[-10:][::-1]
    text = "🗂 *آخر الطلبات:*\n\n"
    for o in last:
        text += (
            f"🔖 `{o['order_number']}`\n"
            f"👤 {o['user_name']}\n"
            f"📚 {o['service']}\n"
            f"📌 الحالة: {o['status']}\n"
            f"📅 {o['date']}\n"
            "━━━━━━━━━━━━━━━\n"
        )
    await update.message.reply_text(text, parse_mode="Markdown")


# ----- تغيير حالة الطلب -----
async def change_status_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    await update.message.reply_text(
        "🔄 أرسل *رقم الطلب* الذي تريد تغيير حالته:\n(مثال: KYAN-2026-0001)",
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown",
    )
    return STATE_CHANGE_STATUS_ID


async def change_status_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == BTN_CANCEL:
        return await admin_cancel(update, context)
    order_number = update.message.text.strip()
    data = load_data()
    if order_number not in data["orders"]:
        await update.message.reply_text(
            "⚠️ رقم الطلب غير موجود. حاول مرة أخرى أو اضغط ❌ إلغاء.",
            reply_markup=cancel_keyboard(),
        )
        return STATE_CHANGE_STATUS_ID

    context.user_data["status_order_number"] = order_number
    keyboard = ReplyKeyboardMarkup(
        [[s] for s in ORDER_STATUSES] + [[BTN_CANCEL]],
        resize_keyboard=True,
    )
    await update.message.reply_text(
        f"اختر الحالة الجديدة للطلب `{order_number}`:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    return STATE_CHANGE_STATUS_VALUE


async def change_status_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_CANCEL:
        return await admin_cancel(update, context)
    if text not in ORDER_STATUSES:
        await update.message.reply_text("⚠️ الرجaa اختيار حالة صحيحة من الأزرار.")
        return STATE_CHANGE_STATUS_VALUE

    order_number = context.user_data.get("status_order_number")
    data = load_data()
    if order_number not in data["orders"]:
        await update.message.reply_text("⚠️ الطلب لم يعد موجوداً.")
        return await admin_cancel(update, context)

    data["orders"][order_number]["status"] = text
    save_data(data)
    target_user = data["orders"][order_number]["user_id"]

    await update.message.reply_text(
        f"✅ تم تحديث حالة الطلب `{order_number}` إلى *{text}*.",
        reply_markup=admin_keyboard(),
        parse_mode="Markdown",
    )

    # إشعار العميل
    try:
        await context.bot.send_message(
            chat_id=target_user,
            text=(
                f"🔔 تم تحديث حالة طلبك\n\n"
                f"🔖 رقم الطلب: `{order_number}`\n"
                f"📌 الحالة الجديدة: *{text}*"
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"تعذر إشعار العميل: {e}")

    context.user_data.clear()
    return ConversationHandler.END


# ----- الإعلانات -----
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    await update.message.reply_text(
        "📢 أرسل نص الإعلان الذي تريد إرساله لجميع المستخدمين:",
        reply_markup=cancel_keyboard(),
    )
    return STATE_BROADCAST


async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == BTN_CANCEL:
        return await admin_cancel(update, context)

    message = update.message.text
    data = load_data()
    sent = 0
    failed = 0
    for uid in data["users"]:
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=f"📢 *إعلان من {BOT_NAME}*\n\n{message}",
                parse_mode="Markdown",
            )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ تم إرسال الإعلان.\n\n"
        f"📨 نجح: {sent}\n"
        f"⚠️ فشل: {failed}",
        reply_markup=admin_keyboard(),
    )
    return ConversationHandler.END


async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ تم الإلغاء.", reply_markup=admin_keyboard()
    )
    return ConversationHandler.END


# ==================== معالج النصوص العام ====================
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_SERVICES:
        await show_services(update, context)
    elif text == BTN_MY_ORDERS:
        await my_orders(update, context)
    elif text == BTN_SUPPORT:
        await support(update, context)
    elif text == BTN_ABOUT:
        await about(update, context)
    elif text == BTN_ADMIN:
        await admin_panel(update, context)
    elif text == BTN_BACK:
        await show_main_menu(update, context)
    elif text == "📊 الإحصائيات":
        await admin_stats(update, context)
    elif text == "🗂 آخر الطلبات":
        await admin_last_orders(update, context)
    else:
        await show_main_menu(update, context)


# ==================== معالج الأخطاء ====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("حدث خطأ:", exc_info=context.error)
    try:
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ حدث خطأ غير متوقع. حاول مرة أخرى."
            )
    except Exception:
        pass


# ==================== التشغيل ====================
def main():
    init_data()
    app = Application.builder().token(BOT_TOKEN).build()

    # محادثة الطلبات
    order_conv = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.TEXT & filters.Regex(f"^({'|'.join(SERVICES)})$"),
                select_service,
            )
        ],
        states={
            STATE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            STATE_MAJOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_major)],
            STATE_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_level)],
            STATE_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            STATE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[
            CommandHandler("start", cancel_order),
            MessageHandler(filters.Regex(f"^{BTN_CANCEL}$"), cancel_order),
        ],
        allow_reentry=True,
    )

    # محادثة تغيير الحالة
    status_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🔄 تغيير حالة طلب$"), change_status_start)
        ],
        states={
            STATE_CHANGE_STATUS_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_status_get_id)
            ],
            STATE_CHANGE_STATUS_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_status_set)
            ],
        },
        fallbacks=[
            CommandHandler("start", admin_cancel),
            MessageHandler(filters.Regex(f"^{BTN_CANCEL}$"), admin_cancel),
        ],
        allow_reentry=True,
    )

    # محادثة الإعلانات
    broadcast_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📢 إرسال إعلان$"), broadcast_start)
        ],
        states={
            STATE_BROADCAST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_send)
            ],
        },
        fallbacks=[
            CommandHandler("start", admin_cancel),
            MessageHandler(filters.Regex(f"^{BTN_CANCEL}$"), admin_cancel),
        ],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(order_conv)
    app.add_handler(status_conv)
    app.add_handler(broadcast_conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.add_error_handler(error_handler)

    logger.info("✅ البوت يعمل الآن...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
