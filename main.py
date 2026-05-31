# ============================================================
#        🎓 نظام الخدمات الطلابية - بوت تيليجرام الاحترافي
#        📌 الإصدار: 3.0 | python-telegram-bot v21+
# ============================================================

import json, os, random, datetime, asyncio
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters,
    ContextTypes
)

# ══════════════════════════════════════════════
#                ⚙️  إعدادات عامة
# ══════════════════════════════════════════════
TOKEN    = "8305933964:AAFIk27xGOrvnT0Fw7VS0rmXu3yHuXbotoU"
ADMIN_ID = 199870979          # ← أدمن رئيسي
ADMINS   = {ADMIN_ID}         # ← يمكن إضافة أدمن آخرين لاحقاً

DB_FILE      = "db.json"
USERS_FILE   = "users.json"
SETTINGS_FILE = "settings.json"

# ══════════════════════════════════════════════
#               🗄️  قاعدة البيانات
# ══════════════════════════════════════════════
def _load(path: str, default=None):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}

def _save(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db       = _load(DB_FILE,       {})      # الطلبات
users    = _load(USERS_FILE,    {})      # المستخدمون
settings = _load(SETTINGS_FILE, {       # الإعدادات الافتراضية
    "services": {
        "بحث علمي":      {"price": "80-200 ريال",  "emoji": "🔬", "time": "3-5 أيام"},
        "مشروع تخرج":   {"price": "300-800 ريال", "emoji": "🎓", "time": "7-21 يوم"},
        "عرض تقديمي":   {"price": "50-150 ريال",  "emoji": "📊", "time": "1-3 أيام"},
        "تلخيص":         {"price": "30-80 ريال",   "emoji": "📝", "time": "12-24 ساعة"},
        "ترجمة":         {"price": "20-60 ريال",   "emoji": "🌐", "time": "12-48 ساعة"},
        "حل واجبات":     {"price": "20-100 ريال",  "emoji": "✏️", "time": "6-24 ساعة"},
        "تقرير أكاديمي": {"price": "60-150 ريال",  "emoji": "📋", "time": "2-4 أيام"},
    },
    "payment_methods": [
        "🏦 تحويل بنكي - رقم الآيبان: SA00 0000 0000 0000 0000 0000",
        "📱 STC Pay - 05XXXXXXXX",
        "💳 مدى / Apple Pay",
    ],
    "contact": "📞 واتساب: 05XXXXXXXX\n📧 البريد: service@example.com",
    "welcome_msg": "مرحباً بك في نظام الخدمات الطلابية الاحترافي! 🎓",
    "bot_active": True
})

def save_all():
    _save(DB_FILE,      db)
    _save(USERS_FILE,   users)
    _save(SETTINGS_FILE, settings)

# ══════════════════════════════════════════════
#                🆔  مولّد الأرقام
# ══════════════════════════════════════════════
def gen_order_id() -> str:
    return "ORD-" + str(random.randint(100000, 999999))

def now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# ══════════════════════════════════════════════
#       📌  مراحل ConversationHandler
# ══════════════════════════════════════════════
(
    ASK_NAME, ASK_UNIVERSITY, ASK_COLLEGE,
    ASK_SERVICE, ASK_DETAILS, ASK_DEADLINE,
    CONFIRM_ORDER, AWAIT_PAYMENT
) = range(8)

# ══════════════════════════════════════════════
#           🎛️  أزرار لوحة التحكم (Admin)
# ══════════════════════════════════════════════
def admin_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 الطلبات الجديدة",    callback_data="adm_orders_new"),
         InlineKeyboardButton("🕐 قيد التنفيذ",         callback_data="adm_orders_progress")],
        [InlineKeyboardButton("✅ المنجزة",             callback_data="adm_orders_done"),
         InlineKeyboardButton("❌ الملغاة",             callback_data="adm_orders_cancelled")],
        [InlineKeyboardButton("👥 المستخدمون",          callback_data="adm_users"),
         InlineKeyboardButton("📊 الإحصائيات",          callback_data="adm_stats")],
        [InlineKeyboardButton("⚙️ إعدادات البوت",       callback_data="adm_settings"),
         InlineKeyboardButton("📣 إرسال إشعار جماعي",  callback_data="adm_broadcast")],
        [InlineKeyboardButton("🔒 إيقاف/تشغيل البوت",  callback_data="adm_toggle_bot")],
    ])

def order_actions_keyboard(order_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 قيد التنفيذ",    callback_data=f"st_{order_id}_قيد التنفيذ"),
         InlineKeyboardButton("✅ منجز",            callback_data=f"st_{order_id}_منجز")],
        [InlineKeyboardButton("⏸ معلّق",           callback_data=f"st_{order_id}_معلّق"),
         InlineKeyboardButton("❌ ملغي",            callback_data=f"st_{order_id}_ملغي")],
        [InlineKeyboardButton("💬 مراسلة العميل",  callback_data=f"msg_{order_id}"),
         InlineKeyboardButton("🗑️ حذف الطلب",      callback_data=f"del_{order_id}")],
        [InlineKeyboardButton("🔙 رجوع",           callback_data="adm_main")],
    ])

def settings_keyboard():
    status = "🟢 مفعّل" if settings["bot_active"] else "🔴 موقوف"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 عرض الخدمات والأسعار", callback_data="adm_view_services")],
        [InlineKeyboardButton("💳 تعديل طرق الدفع",      callback_data="adm_edit_payment")],
        [InlineKeyboardButton("📞 تعديل التواصل",         callback_data="adm_edit_contact")],
        [InlineKeyboardButton(f"البوت: {status}",        callback_data="adm_toggle_bot")],
        [InlineKeyboardButton("🔙 رجوع للقائمة",         callback_data="adm_main")],
    ])

# ══════════════════════════════════════════════
#         🎛️  أزرار المستخدم (Inline)
# ══════════════════════════════════════════════
def main_menu_keyboard(uid: int):
    """القائمة الرئيسية - ReplyKeyboard ثابتة"""
    kb = [
        ["📚 الخدمات", "💰 الأسعار"],
        ["📝 طلب جديد", "📦 طلباتي"],
        ["💳 الدفع",    "📞 تواصل معنا"],
        ["ℹ️ عن البوت"]
    ]
    if uid in ADMINS:
        kb.append(["🛠 لوحة التحكم"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def services_inline_keyboard():
    svcs = settings["services"]
    rows = []
    row  = []
    for i, (name, info) in enumerate(svcs.items()):
        row.append(InlineKeyboardButton(
            f"{info['emoji']} {name}", callback_data=f"svc_{name}"
        ))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("📝 طلب خدمة الآن", callback_data="start_order")])
    return InlineKeyboardMarkup(rows)

def my_orders_inline(uid: int):
    my = [(k, v) for k, v in db.items() if v["user"] == uid]
    if not my:
        return None
    rows = []
    for oid, o in sorted(my, key=lambda x: x[1].get("date",""), reverse=True)[:10]:
        status_icon = {
            "جديد": "🆕", "قيد التنفيذ": "🔄",
            "منجز": "✅", "معلّق": "⏸", "ملغي": "❌"
        }.get(o["status"], "📌")
        rows.append([InlineKeyboardButton(
            f"{status_icon} {oid} | {o['service']}",
            callback_data=f"myorder_{oid}"
        )])
    return InlineKeyboardMarkup(rows)

def service_select_keyboard():
    svcs = settings["services"]
    rows = []
    row  = []
    for i, (name, info) in enumerate(svcs.items()):
        row.append(InlineKeyboardButton(
            f"{info['emoji']} {name}", callback_data=f"pick_{name}"
        ))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("❌ إلغاء الطلب", callback_data="cancel_order")])
    return InlineKeyboardMarkup(rows)

def confirm_order_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تأكيد الإرسال",  callback_data="confirm_yes"),
         InlineKeyboardButton("✏️ تعديل",           callback_data="confirm_edit")],
        [InlineKeyboardButton("❌ إلغاء",           callback_data="cancel_order")],
    ])

def payment_keyboard(order_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ أرسلت الدفع",    callback_data=f"paid_{order_id}"),
         InlineKeyboardButton("⏰ لاحقاً",          callback_data=f"paylater_{order_id}")],
        [InlineKeyboardButton("❌ إلغاء الطلب",    callback_data=f"paycancel_{order_id}")],
    ])

# ══════════════════════════════════════════════
#           📊  دوال الإحصائيات
# ══════════════════════════════════════════════
def get_stats() -> str:
    total   = len(db)
    new_    = sum(1 for v in db.values() if v["status"] == "جديد")
    prog    = sum(1 for v in db.values() if v["status"] == "قيد التنفيذ")
    done    = sum(1 for v in db.values() if v["status"] == "منجز")
    canc    = sum(1 for v in db.values() if v["status"] == "ملغي")
    total_u = len(users)

    svc_count: dict = {}
    for v in db.values():
        svc_count[v["service"]] = svc_count.get(v["service"], 0) + 1
    top_svc = max(svc_count, key=svc_count.get) if svc_count else "—"

    today   = datetime.date.today().strftime("%Y-%m-%d")
    today_o = sum(1 for v in db.values() if v.get("date","").startswith(today))

    return (
        "📊 *إحصائيات النظام*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 إجمالي الطلبات : `{total}`\n"
        f"🆕 جديدة          : `{new_}`\n"
        f"🔄 قيد التنفيذ   : `{prog}`\n"
        f"✅ منجزة          : `{done}`\n"
        f"❌ ملغاة          : `{canc}`\n"
        f"📅 طلبات اليوم    : `{today_o}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 المستخدمون     : `{total_u}`\n"
        f"🏆 أكثر خدمة      : `{top_svc}`\n"
        f"🕒 آخر تحديث      : `{now_str()}`"
    )

def order_detail_text(oid: str, o: dict) -> str:
    status_icon = {
        "جديد": "🆕", "قيد التنفيذ": "🔄",
        "منجز": "✅", "معلّق": "⏸", "ملغي": "❌"
    }.get(o["status"], "📌")
    return (
        f"🧾 *تفاصيل الطلب*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 رقم الطلب  : `{oid}`\n"
        f"👤 الاسم      : {o.get('name','—')}\n"
        f"🏫 الجامعة   : {o.get('university','—')}\n"
        f"🏛 الكلية     : {o.get('college','—')}\n"
        f"📚 الخدمة    : {o.get('service','—')}\n"
        f"📝 التفاصيل  : {o.get('details','—')}\n"
        f"⏰ الموعد    : {o.get('deadline','—')}\n"
        f"📅 التاريخ   : {o.get('date','—')}\n"
        f"{status_icon} الحالة     : *{o.get('status','—')}*\n"
        f"💳 الدفع     : {o.get('payment','لم يُرسل بعد')}"
    )

# ══════════════════════════════════════════════
#              🚀  /start
# ══════════════════════════════════════════════
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.effective_user.first_name or "مستخدم"

    # تسجيل المستخدم
    if str(uid) not in users:
        users[str(uid)] = {
            "name": name,
            "username": update.effective_user.username or "",
            "joined": now_str(),
            "orders": 0
        }
        _save(USERS_FILE, users)

    if not settings["bot_active"] and uid not in ADMINS:
        await update.message.reply_text(
            "⚠️ البوت متوقف مؤقتاً للصيانة. سنعود قريباً! 🔧"
        )
        return

    welcome = (
        f"السلام عليكم {name} 👋\n\n"
        f"{settings['welcome_msg']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎓 نوفر لك خدمات أكاديمية احترافية بأسعار مناسبة\n"
        "⚡ جودة عالية | تسليم في الوقت المحدد | دعم مستمر\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "اختر من القائمة أدناه 👇"
    )
    await update.message.reply_text(
        welcome,
        reply_markup=main_menu_keyboard(uid)
    )

# ══════════════════════════════════════════════
#       📨  معالج الرسائل الرئيسي (Reply KB)
# ══════════════════════════════════════════════
async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid  = update.effective_user.id

    if not settings["bot_active"] and uid not in ADMINS:
        await update.message.reply_text("⚠️ البوت متوقف مؤقتاً للصيانة.")
        return

    # ─────── 📚 الخدمات ───────
    if text == "📚 الخدمات":
        msg = "📚 *خدماتنا الأكاديمية*\nاضغط على أي خدمة لمعرفة تفاصيلها:\n"
        await update.message.reply_text(
            msg, parse_mode="Markdown",
            reply_markup=services_inline_keyboard()
        )

    # ─────── 💰 الأسعار ───────
    elif text == "💰 الأسعار":
        svcs = settings["services"]
        msg  = "💰 *قائمة الأسعار الكاملة*\n━━━━━━━━━━━━━━━━━━━━\n"
        for name, info in svcs.items():
            msg += (
                f"{info['emoji']} *{name}*\n"
                f"   💵 السعر : {info['price']}\n"
                f"   ⏱ المدة  : {info['time']}\n\n"
            )
        msg += "━━━━━━━━━━━━━━━━━━━━\n📝 للطلب اضغط 'طلب جديد'"
        await update.message.reply_text(msg, parse_mode="Markdown")

    # ─────── 💳 الدفع ───────
    elif text == "💳 الدفع":
        methods = "\n".join(settings["payment_methods"])
        msg = (
            "💳 *طرق الدفع المتاحة*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{methods}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📎 بعد الدفع أرسل صورة الإيصال لتأكيد طلبك\n"
            "⚠️ لا يُقبل الطلب إلا بعد التأكيد"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    # ─────── 📞 تواصل معنا ───────
    elif text == "📞 تواصل معنا":
        msg = (
            "📞 *تواصل معنا*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{settings['contact']}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🕐 أوقات العمل: 8 صباحاً - 12 منتصف الليل\n"
            "✅ نرد خلال 30 دقيقة"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    # ─────── 📦 طلباتي ───────
    elif text == "📦 طلباتي":
        my_kb = my_orders_inline(uid)
        if my_kb:
            my_list = [(k, v) for k, v in db.items() if v["user"] == uid]
            done_c  = sum(1 for _, v in my_list if v["status"] == "منجز")
            prog_c  = sum(1 for _, v in my_list if v["status"] == "قيد التنفيذ")
            msg = (
                f"📦 *طلباتك ({len(my_list)} طلب)*\n"
                f"✅ منجز: {done_c} | 🔄 جاري: {prog_c}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "اضغط على أي طلب لعرض تفاصيله:"
            )
            await update.message.reply_text(
                msg, parse_mode="Markdown", reply_markup=my_kb
            )
        else:
            await update.message.reply_text(
                "📦 لا توجد طلبات سابقة.\n💡 اضغط 'طلب جديد' لإنشاء طلبك الأول!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📝 طلب جديد الآن", callback_data="start_order")
                ]])
            )

    # ─────── ℹ️ عن البوت ───────
    elif text == "ℹ️ عن البوت":
        msg = (
            "ℹ️ *عن النظام*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 بوت الخدمات الطلابية الاحترافي\n"
            "📌 الإصدار: 3.0\n"
            f"👥 عدد المستخدمين: {len(users)}\n"
            f"📦 إجمالي الطلبات: {len(db)}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ مدعوم بتقنية Telegram Bot API\n"
            "🔒 بياناتك محمية وآمنة"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    # ─────── 🛠 لوحة التحكم (Admin) ───────
    elif text == "🛠 لوحة التحكم":
        if uid not in ADMINS:
            await update.message.reply_text("⛔ غير مصرّح لك.")
            return
        await update.message.reply_text(
            "🛠 *لوحة تحكم المشرف*\n━━━━━━━━━━━━━━━━━━━━\n"
            "اختر القسم المطلوب:",
            parse_mode="Markdown",
            reply_markup=admin_main_keyboard()
        )

# ══════════════════════════════════════════════
#     🔘 Callback Queries - المستخدم
# ══════════════════════════════════════════════
async def callback_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    uid  = q.from_user.id
    await q.answer()

    # ─── عرض تفاصيل خدمة ───
    if data.startswith("svc_"):
        svc_name = data[4:]
        if svc_name in settings["services"]:
            info = settings["services"][svc_name]
            msg  = (
                f"{info['emoji']} *{svc_name}*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💵 السعر : {info['price']}\n"
                f"⏱ المدة  : {info['time']}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                "📝 هل تريد طلب هذه الخدمة؟"
            )
            await q.edit_message_text(
                msg, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ اطلب الآن",       callback_data="start_order"),
                     InlineKeyboardButton("🔙 رجوع",            callback_data="back_services")],
                ])
            )

    # ─── رجوع لقائمة الخدمات ───
    elif data == "back_services":
        await q.edit_message_text(
            "📚 *خدماتنا الأكاديمية*\nاضغط على أي خدمة:",
            parse_mode="Markdown",
            reply_markup=services_inline_keyboard()
        )

    # ─── بدء طلب (من inline) ───
    elif data == "start_order":
        await q.edit_message_text(
            "📝 *طلب جديد*\nسيتم توجيهك لنموذج الطلب...",
            parse_mode="Markdown"
        )
        # إطلاق ConversationHandler عبر رسالة وهمية
        await context.bot.send_message(
            uid,
            "👤 *الخطوة 1/6* — اكتب اسمك الكامل:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["order"] = {"step": ASK_NAME, "id": gen_order_id()}

    # ─── تفاصيل طلب المستخدم ───
    elif data.startswith("myorder_"):
        oid = data[8:]
        if oid in db and db[oid]["user"] == uid:
            o   = db[oid]
            txt = order_detail_text(oid, o)
            await q.edit_message_text(
                txt, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 رجوع لطلباتي", callback_data="back_myorders")
                ]])
            )

    # ─── رجوع لقائمة طلباتي ───
    elif data == "back_myorders":
        my_kb = my_orders_inline(uid)
        if my_kb:
            await q.edit_message_text(
                "📦 *طلباتك:*", parse_mode="Markdown",
                reply_markup=my_kb
            )

    # ─── تم الدفع ───
    elif data.startswith("paid_"):
        oid = data[5:]
        if oid in db:
            db[oid]["payment"] = f"✅ أُرسل بتاريخ {now_str()}"
            save_all()
            await q.edit_message_text(
                f"✅ تم تسجيل إرسال الدفع للطلب `{oid}`\n"
                "⏳ سيتم مراجعة الدفع وتأكيد الطلب خلال 30 دقيقة.",
                parse_mode="Markdown"
            )
            # إشعار الأدمن
            for adm in ADMINS:
                await context.bot.send_message(
                    adm,
                    f"💳 *إشعار دفع جديد*\n🆔 الطلب: `{oid}`\n"
                    f"👤 المستخدم: `{uid}`\nالوقت: {now_str()}",
                    parse_mode="Markdown"
                )

    elif data.startswith("paylater_"):
        oid = data[9:]
        await q.edit_message_text(
            f"⏰ تم الحفظ. يمكنك إرسال الدفع لاحقاً.\n"
            f"🆔 رقم طلبك: `{oid}`\n"
            "استخدم 'طلباتي' لمتابعة حالة طلبك.",
            parse_mode="Markdown"
        )

    elif data.startswith("paycancel_"):
        oid = data[10:]
        if oid in db:
            db[oid]["status"] = "ملغي"
            save_all()
        await q.edit_message_text("❌ تم إلغاء الطلب.")


# ══════════════════════════════════════════════
#   🔘 Callback Queries - لوحة تحكم الأدمن
# ══════════════════════════════════════════════
async def callback_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    uid  = q.from_user.id
    await q.answer()

    if uid not in ADMINS:
        await q.answer("⛔ غير مصرّح!", show_alert=True)
        return

    # ─── القائمة الرئيسية ───
    if data == "adm_main":
        await q.edit_message_text(
            "🛠 *لوحة تحكم المشرف*",
            parse_mode="Markdown",
            reply_markup=admin_main_keyboard()
        )

    # ─── عرض الطلبات حسب الحالة ───
    elif data.startswith("adm_orders_"):
        status_map = {
            "adm_orders_new":       ("جديد",        "🆕"),
            "adm_orders_progress":  ("قيد التنفيذ", "🔄"),
            "adm_orders_done":      ("منجز",         "✅"),
            "adm_orders_cancelled": ("ملغي",         "❌"),
        }
        stat, icon = status_map.get(data, ("جديد", "📦"))
        filtered   = [(k, v) for k, v in db.items() if v["status"] == stat]

        if not filtered:
            await q.edit_message_text(
                f"{icon} لا توجد طلبات بحالة *{stat}*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 رجوع", callback_data="adm_main")
                ]])
            )
            return

        rows = []
        for oid, o in sorted(filtered, key=lambda x: x[1].get("date",""), reverse=True):
            rows.append([InlineKeyboardButton(
                f"{icon} {oid} | {o['name'][:10]} | {o['service'][:8]}",
                callback_data=f"adm_view_{oid}"
            )])
        rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="adm_main")])

        await q.edit_message_text(
            f"{icon} *طلبات '{stat}' ({len(filtered)})*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(rows)
        )

    # ─── عرض تفاصيل طلب (أدمن) ───
    elif data.startswith("adm_view_"):
        oid = data[9:]
        if oid not in db:
            await q.edit_message_text("❌ الطلب غير موجود.")
            return
        o   = db[oid]
        txt = order_detail_text(oid, o)
        await q.edit_message_text(
            txt, parse_mode="Markdown",
            reply_markup=order_actions_keyboard(oid)
        )

    # ─── تغيير حالة طلب ───
    elif data.startswith("st_"):
        parts      = data.split("_", 2)
        oid        = parts[1]
        new_status = parts[2]
        if oid in db:
            old_status      = db[oid]["status"]
            db[oid]["status"] = new_status
            save_all()
            user_id = db[oid]["user"]
            status_icon = {
                "جديد": "🆕", "قيد التنفيذ": "🔄",
                "منجز": "✅", "معلّق": "⏸", "ملغي": "❌"
            }.get(new_status, "📌")

            # إشعار العميل
            try:
                await context.bot.send_message(
                    user_id,
                    f"🔔 *تحديث على طلبك*\n"
                    f"🆔 رقم الطلب: `{oid}`\n"
                    f"📌 الحالة الجديدة: {status_icon} *{new_status}*\n"
                    f"🕒 {now_str()}\n\n"
                    + ("✅ تم إنجاز طلبك! نشكر ثقتك بنا 🙏" if new_status == "منجز" else "")
                    + ("🔄 طلبك قيد التنفيذ الآن، سيتم التسليم في الموعد المحدد." if new_status == "قيد التنفيذ" else ""),
                    parse_mode="Markdown"
                )
            except Exception:
                pass

            await q.edit_message_text(
                f"✅ *تم تحديث الطلب `{oid}`*\n"
                f"الحالة: {old_status} ← {status_icon} {new_status}",
                parse_mode="Markdown",
                reply_markup=order_actions_keyboard(oid)
            )

    # ─── مراسلة عميل ───
    elif data.startswith("msg_"):
        oid = data[4:]
        context.user_data["messaging_order"] = oid
        await q.edit_message_text(
            f"💬 اكتب رسالتك لصاحب الطلب `{oid}`:\n"
            "(أرسل الرسالة الآن وسيتم إرسالها للعميل)",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ إلغاء", callback_data="adm_main")
            ]])
        )
        context.user_data["admin_action"] = "messaging"

    # ─── حذف طلب ───
    elif data.startswith("del_"):
        oid = data[4:]
        if oid in db:
            del db[oid]
            save_all()
        await q.edit_message_text(
            f"🗑️ تم حذف الطلب `{oid}` بنجاح.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data="adm_main")
            ]])
        )

    # ─── إحصائيات ───
    elif data == "adm_stats":
        await q.edit_message_text(
            get_stats(), parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 تحديث",  callback_data="adm_stats"),
                InlineKeyboardButton("🔙 رجوع",   callback_data="adm_main")
            ]])
        )

    # ─── المستخدمون ───
    elif data == "adm_users":
        msg  = f"👥 *قائمة المستخدمين ({len(users)})*\n━━━━━━━━━━━━━━━━━━━━\n"
        rows = []
        for uid_str, u in list(users.items())[-20:]:
            orders_c = sum(1 for v in db.values() if v["user"] == int(uid_str))
            rows.append([InlineKeyboardButton(
                f"👤 {u['name'][:12]} | طلبات: {orders_c}",
                callback_data=f"adm_user_{uid_str}"
            )])
        rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="adm_main")])
        await q.edit_message_text(
            msg + f"(آخر 20 مستخدم)",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(rows)
        )

    # ─── تفاصيل مستخدم ───
    elif data.startswith("adm_user_"):
        uid_str = data[9:]
        u       = users.get(uid_str, {})
        orders_c = [(k, v) for k, v in db.items() if v["user"] == int(uid_str)]
        msg = (
            f"👤 *معلومات المستخدم*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID     : `{uid_str}`\n"
            f"📛 الاسم  : {u.get('name','—')}\n"
            f"🔗 يوزر   : @{u.get('username','—')}\n"
            f"📅 انضم   : {u.get('joined','—')}\n"
            f"📦 طلباته : {len(orders_c)}\n"
        )
        await q.edit_message_text(
            msg, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 مراسلته", callback_data=f"adm_msguser_{uid_str}"),
                 InlineKeyboardButton("🚫 حظر",     callback_data=f"adm_ban_{uid_str}")],
                [InlineKeyboardButton("🔙 رجوع",    callback_data="adm_users")]
            ])
        )

    # ─── حظر مستخدم ───
    elif data.startswith("adm_ban_"):
        uid_str = data[8:]
        if uid_str in users:
            users[uid_str]["banned"] = True
            _save(USERS_FILE, users)
        await q.edit_message_text(
            f"🚫 تم حظر المستخدم `{uid_str}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data="adm_users")
            ]])
        )

    # ─── إعدادات ───
    elif data == "adm_settings":
        await q.edit_message_text(
            "⚙️ *إعدادات البوت*\n━━━━━━━━━━━━━━━━━━━━\nاختر ما تريد تعديله:",
            parse_mode="Markdown",
            reply_markup=settings_keyboard()
        )

    # ─── تشغيل/إيقاف البوت ───
    elif data == "adm_toggle_bot":
        settings["bot_active"] = not settings["bot_active"]
        _save(SETTINGS_FILE, settings)
        stat = "🟢 مفعّل" if settings["bot_active"] else "🔴 موقوف"
        await q.edit_message_text(
            f"✅ تم تغيير حالة البوت إلى: *{stat}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 الإعدادات", callback_data="adm_settings")
            ]])
        )

    # ─── عرض الخدمات والأسعار (أدمن) ───
    elif data == "adm_view_services":
        svcs = settings["services"]
        msg  = "📋 *الخدمات الحالية:*\n━━━━━━━━━━━━━━━━━━━━\n"
        for name, info in svcs.items():
            msg += f"{info['emoji']} *{name}*: {info['price']} | {info['time']}\n"
        await q.edit_message_text(
            msg, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data="adm_settings")
            ]])
        )

    # ─── إشعار جماعي ───
    elif data == "adm_broadcast":
        context.user_data["admin_action"] = "broadcast"
        await q.edit_message_text(
            "📣 *إرسال إشعار جماعي*\nاكتب الرسالة الآن وسيتم إرسالها لجميع المستخدمين:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ إلغاء", callback_data="adm_main")
            ]])
        )

    # ─── مراسلة مستخدم ───
    elif data.startswith("adm_msguser_"):
        uid_str = data[12:]
        context.user_data["admin_action"]    = "msg_user"
        context.user_data["msg_target_uid"]  = uid_str
        await q.edit_message_text(
            f"💬 اكتب رسالتك للمستخدم `{uid_str}`:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ إلغاء", callback_data="adm_main")
            ]])
        )


# ══════════════════════════════════════════════
#   🗂️  ConversationHandler - نموذج الطلب
# ══════════════════════════════════════════════
async def conv_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not settings["bot_active"] and update.effective_user.id not in ADMINS:
        await update.message.reply_text("⚠️ البوت متوقف مؤقتاً.")
        return ConversationHandler.END
    context.user_data["order"] = {"id": gen_order_id()}
    await update.message.reply_text(
        "📝 *نموذج الطلب الجديد*\n━━━━━━━━━━━━━━━━━━━━\n"
        "👤 *الخطوة 1/6* — اكتب اسمك الكامل:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_NAME

async def conv_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["name"] = update.message.text
    await update.message.reply_text(
        "🏫 *الخطوة 2/6* — اكتب اسم جامعتك:",
        parse_mode="Markdown"
    )
    return ASK_UNIVERSITY

async def conv_university(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["university"] = update.message.text
    await update.message.reply_text(
        "🏛 *الخطوة 3/6* — اكتب اسم كليتك / تخصصك:",
        parse_mode="Markdown"
    )
    return ASK_COLLEGE

async def conv_college(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["college"] = update.message.text
    await update.message.reply_text(
        "📚 *الخطوة 4/6* — اختر نوع الخدمة:",
        parse_mode="Markdown",
        reply_markup=service_select_keyboard()
    )
    return ASK_SERVICE

async def conv_service_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اختيار الخدمة عبر Inline Button"""
    q    = update.callback_query
    data = q.data
    await q.answer()
    if data == "cancel_order":
        await q.edit_message_text("❌ تم إلغاء الطلب.")
        return ConversationHandler.END
    svc_name = data[5:]   # pick_اسم الخدمة
    context.user_data["order"]["service"] = svc_name
    await q.edit_message_text(
        f"✅ اخترت: *{svc_name}*\n\n"
        "📝 *الخطوة 5/6* — اكتب تفاصيل طلبك كاملة:\n"
        "(المادة، عدد الصفحات، المتطلبات، ...)",
        parse_mode="Markdown"
    )
    return ASK_DETAILS

async def conv_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["details"] = update.message.text
    await update.message.reply_text(
        "📅 *الخطوة 6/6* — ما هو الموعد النهائي للتسليم؟\n"
        "مثال: غداً / بعد 3 أيام / 15/6/2025",
        parse_mode="Markdown"
    )
    return ASK_DEADLINE

async def conv_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["deadline"] = update.message.text
    o   = context.user_data["order"]
    svc = settings["services"].get(o.get("service",""), {})
    msg = (
        "📋 *مراجعة طلبك*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 رقم الطلب  : `{o['id']}`\n"
        f"👤 الاسم      : {o.get('name','—')}\n"
        f"🏫 الجامعة   : {o.get('university','—')}\n"
        f"🏛 الكلية     : {o.get('college','—')}\n"
        f"📚 الخدمة    : {o.get('service','—')}\n"
        f"📝 التفاصيل  : {o.get('details','—')}\n"
        f"📅 الموعد    : {o.get('deadline','—')}\n"
        f"💵 السعر     : {svc.get('price','يحدد لاحقاً')}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "هل تريد تأكيد إرسال الطلب؟"
    )
    await update.message.reply_text(
        msg, parse_mode="Markdown",
        reply_markup=confirm_order_keyboard()
    )
    return CONFIRM_ORDER

async def conv_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    uid  = q.from_user.id
    await q.answer()

    if data == "cancel_order":
        await q.edit_message_text("❌ تم إلغاء الطلب.")
        return ConversationHandler.END

    if data == "confirm_edit":
        await q.edit_message_text(
            "✏️ أعد إرسال /neworder لتعديل طلبك من البداية."
        )
        return ConversationHandler.END

    if data == "confirm_yes":
        o         = context.user_data["order"]
        order_id  = o["id"]

        db[order_id] = {
            "user":       uid,
            "name":       o.get("name",""),
            "university": o.get("university",""),
            "college":    o.get("college",""),
            "service":    o.get("service",""),
            "details":    o.get("details",""),
            "deadline":   o.get("deadline",""),
            "status":     "جديد",
            "payment":    "لم يُرسل بعد",
            "date":       now_str()
        }

        # تحديث عدد طلبات المستخدم
        if str(uid) in users:
            users[str(uid)]["orders"] = users[str(uid)].get("orders", 0) + 1
        save_all()

        # إشعار الأدمن
        for adm in ADMINS:
            try:
                await context.bot.send_message(
                    adm,
                    f"🆕 *طلب جديد وارد!*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 `{order_id}`\n"
                    f"👤 {o.get('name','')}\n"
                    f"🏫 {o.get('university','')}\n"
                    f"📚 {o.get('service','')}\n"
                    f"📅 الموعد: {o.get('deadline','')}\n"
                    f"🕒 {now_str()}",
                    parse_mode="Markdown",
                    reply_markup=order_actions_keyboard(order_id)
                )
            except Exception:
                pass

        await q.edit_message_text(
            f"✅ *تم إرسال طلبك بنجاح!*\n"
            f"🆔 رقم طلبك: `{order_id}`\n\n"
            "يرجى إتمام الدفع لتأكيد الطلب:",
            parse_mode="Markdown",
            reply_markup=payment_keyboard(order_id)
        )
        context.user_data.pop("order", None)
        return AWAIT_PAYMENT

    return CONFIRM_ORDER

async def conv_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ تم إلغاء الطلب.",
        reply_markup=main_menu_keyboard(update.effective_user.id)
    )
    context.user_data.pop("order", None)
    return ConversationHandler.END

# ══════════════════════════════════════════════
#   📨  معالج رسائل الأدمن (Broadcast / Msg)
# ══════════════════════════════════════════════
async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid    = update.effective_user.id
    action = context.user_data.get("admin_action")

    if uid not in ADMINS or not action:
        return False  # مرر للمعالج التالي

    text = update.message.text

    # ─── إشعار جماعي ───
    if action == "broadcast":
        context.user_data.pop("admin_action", None)
        sent = failed = 0
        for uid_str in users:
            try:
                await context.bot.send_message(
                    int(uid_str),
                    f"📣 *إشعار من الإدارة*\n━━━━━━━━━━━━━━━━━━━━\n{text}",
                    parse_mode="Markdown"
                )
                sent += 1
                await asyncio.sleep(0.05)
            except Exception:
                failed += 1
        await update.message.reply_text(
            f"✅ تم الإرسال!\n📤 وصل: {sent} | ❌ فشل: {failed}",
            reply_markup=admin_main_keyboard()
        )
        return True

    # ─── مراسلة عميل طلب ───
    elif action == "messaging":
        oid = context.user_data.pop("messaging_order", None)
        context.user_data.pop("admin_action", None)
        if oid and oid in db:
            user_id = db[oid]["user"]
            try:
                await context.bot.send_message(
                    user_id,
                    f"💬 *رسالة من فريق الدعم*\n"
                    f"بخصوص طلبك `{oid}`:\n\n{text}",
                    parse_mode="Markdown"
                )
                await update.message.reply_text("✅ تم إرسال الرسالة للعميل.")
            except Exception as e:
                await update.message.reply_text(f"❌ فشل الإرسال: {e}")
        return True

    # ─── مراسلة مستخدم مباشر ───
    elif action == "msg_user":
        target = context.user_data.pop("msg_target_uid", None)
        context.user_data.pop("admin_action", None)
        if target:
            try:
                await context.bot.send_message(
                    int(target),
                    f"💬 *رسالة من الإدارة:*\n{text}",
                    parse_mode="Markdown"
                )
                await update.message.reply_text("✅ تم إرسال الرسالة.")
            except Exception as e:
                await update.message.reply_text(f"❌ فشل: {e}")
        return True

    return False

# ══════════════════════════════════════════════
#    📎 معالج الصور (إيصالات الدفع)
# ══════════════════════════════════════════════
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid      = update.effective_user.id
    caption  = update.message.caption or ""
    my_orders = [k for k, v in db.items() if v["user"] == uid and v["status"] == "جديد"]

    if not my_orders:
        await update.message.reply_text(
            "📎 تم استلام الصورة.\n"
            "⚠️ لا توجد طلبات معلّقة بانتظار الدفع. "
            "إذا أرسلت إيصالاً يرجى ذكر رقم الطلب."
        )
        return

    oid = my_orders[-1]
    db[oid]["payment"] = f"✅ إيصال مُرسَل بتاريخ {now_str()}"
    save_all()

    await update.message.reply_text(
        f"✅ تم استلام إيصال الدفع للطلب `{oid}`\n"
        "⏳ سيتم مراجعته خلال 30 دقيقة وسنُخطرك فور التأكيد.",
        parse_mode="Markdown"
    )

    # إعادة توجيه الصورة للأدمن
    for adm in ADMINS:
        try:
            await context.bot.forward_message(adm, uid, update.message.message_id)
            await context.bot.send_message(
                adm,
                f"💳 *إيصال دفع*\nالطلب: `{oid}` | العميل: `{uid}`",
                parse_mode="Markdown",
                reply_markup=order_actions_keyboard(oid)
            )
        except Exception:
            pass

# ══════════════════════════════════════════════
#          🔀  المعالج الإجمالي للنصوص
# ══════════════════════════════════════════════
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    # تحقق من الحظر
    if users.get(str(uid), {}).get("banned"):
        await update.message.reply_text("🚫 تم حظرك من استخدام البوت.")
        return

    # معالجة إجراءات الأدمن أولاً
    if uid in ADMINS:
        handled = await handle_admin_text(update, context)
        if handled:
            return

    # القائمة الرئيسية
    await handle_main_menu(update, context)

# ══════════════════════════════════════════════
#          🔀  الـ Callback الإجمالي
# ══════════════════════════════════════════════
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    # توجيه callbacks الأدمن
    if data.startswith("adm_") or data.startswith("st_") or \
       data.startswith("del_") or data.startswith("msg_"):
        await callback_admin(update, context)
    else:
        await callback_user(update, context)

# ══════════════════════════════════════════════
#       📦  أوامر إضافية /commands
# ══════════════════════════════════════════════
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg = (
        "📖 *الأوامر المتاحة*\n━━━━━━━━━━━━━━━━━━━━\n"
        "/start    — الصفحة الرئيسية\n"
        "/neworder — طلب جديد\n"
        "/myorders — عرض طلباتي\n"
        "/help     — المساعدة\n"
    )
    if uid in ADMINS:
        msg += (
            "\n🛠 *أوامر الأدمن*\n━━━━━━━━━━━━━━━━━━━━\n"
            "/admin    — لوحة التحكم\n"
            "/stats    — الإحصائيات\n"
            "/list     — جميع الطلبات\n"
            "/status [ID] [الحالة] — تغيير الحالة\n"
            "/broadcast [رسالة] — إشعار جماعي\n"
        )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_myorders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    my_kb = my_orders_inline(uid)
    if my_kb:
        await update.message.reply_text(
            "📦 *طلباتك:*", parse_mode="Markdown",
            reply_markup=my_kb
        )
    else:
        await update.message.reply_text("📦 لا توجد طلبات بعد.")

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ADMINS:
        await update.message.reply_text("⛔ غير مصرّح.")
        return
    await update.message.reply_text(
        "🛠 *لوحة تحكم المشرف*",
        parse_mode="Markdown",
        reply_markup=admin_main_keyboard()
    )

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return
    await update.message.reply_text(get_stats(), parse_mode="Markdown")

async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ADMINS:
        return
    if not db:
        await update.message.reply_text("📦 لا توجد طلبات.")
        return
    msg = "📦 *جميع الطلبات:*\n━━━━━━━━━━━━━━━━━━━━\n"
    for oid, o in list(db.items())[-20:]:
        icon = {"جديد":"🆕","قيد التنفيذ":"🔄","منجز":"✅","معلّق":"⏸","ملغي":"❌"}.get(o["status"],"📌")
        msg += f"{icon} `{oid}` | {o['name']} | {o['service']} | {o['status']}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    if uid not in ADMINS:
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("الاستخدام: /status [ID] [الحالة]")
        return
    oid        = args[0]
    new_status = " ".join(args[1:])
    if oid not in db:
        await update.message.reply_text("❌ الطلب غير موجود.")
        return
    db[oid]["status"] = new_status
    save_all()
    user_id = db[oid]["user"]
    try:
        await context.bot.send_message(
            user_id,
            f"🔔 تحديث طلبك `{oid}`\n📌 الحالة: *{new_status}*",
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await update.message.reply_text(f"✅ تم تحديث `{oid}` إلى: {new_status}")

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ADMINS:
        return
    if not context.args:
        await update.message.reply_text("الاستخدام: /broadcast [الرسالة]")
        return
    msg  = " ".join(context.args)
    sent = failed = 0
    for uid_str in users:
        try:
            await context.bot.send_message(
                int(uid_str),
                f"📣 *إشعار من الإدارة*\n{msg}",
                parse_mode="Markdown"
            )
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
    await update.message.reply_text(f"📤 وصل: {sent} | ❌ فشل: {failed}")

# ══════════════════════════════════════════════
#            🚀  تشغيل البوت
# ══════════════════════════════════════════════
def main():
    app = Application.builder().token(TOKEN).build()

    # ─── ConversationHandler لنموذج الطلب ───
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("neworder", conv_start),
            MessageHandler(filters.Regex("^📝 طلب جديد$"), conv_start),
        ],
        states={
            ASK_NAME:       [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_name)],
            ASK_UNIVERSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_university)],
            ASK_COLLEGE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_college)],
            ASK_SERVICE:    [CallbackQueryHandler(conv_service_pick, pattern="^(pick_|cancel_order)")],
            ASK_DETAILS:    [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_details)],
            ASK_DEADLINE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_deadline)],
            CONFIRM_ORDER:  [CallbackQueryHandler(conv_confirm, pattern="^(confirm_|cancel_order)")],
            AWAIT_PAYMENT:  [CallbackQueryHandler(handle_callback)],
        },
        fallbacks=[
            CommandHandler("cancel", conv_cancel),
            MessageHandler(filters.Regex("^❌ إلغاء$"), conv_cancel),
        ],
        allow_reentry=True,
    )

    # ─── تسجيل الـ Handlers ───
    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("help",       cmd_help))
    app.add_handler(CommandHandler("myorders",   cmd_myorders))
    app.add_handler(CommandHandler("admin",      cmd_admin))
    app.add_handler(CommandHandler("stats",      cmd_stats))
    app.add_handler(CommandHandler("list",       cmd_list))
    app.add_handler(CommandHandler("status",     cmd_status))
    app.add_handler(CommandHandler("broadcast",  cmd_broadcast))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("=" * 50)
    print("  🎓 نظام الخدمات الطلابية - v3.0")
    print("  ✅ البوت يعمل بنجاح...")
    print("=" * 50)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
