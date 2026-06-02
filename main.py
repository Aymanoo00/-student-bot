import telebot
import sqlite3
import random
import time
from datetime import datetime
import json
import string

# -------------------- إعدادات البوت --------------------
BOT_TOKEN = "8599384103:AAH-N8xGX8HIZTteolimOV5c5mwog1LtLtg"
ADMIN_ID = 5707994417
CHANNEL_USERNAME = "@SanadStudentsBot"
REQUIRED_REFERRALS = 7  # عدد الإحالات المطلوبة للحصول على خدمة مجانية

bot = telebot.TeleBot(BOT_TOKEN)
user_service_data = {}
admin_actions = {}
user_states = {}

# -------------------- إعدادات قابلة للتعديل --------------------
def load_settings():
    try:
        with open('bot_settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "maintenance_mode": False,
            "accepting_orders": True,
            "admin_notifications": True,
            "required_subscription": True,
            "payment_required": False,
            "default_price": 50.0,
            "welcome_message": "👋 أهلاً بك في بوت الخدمات الطلابية\n\nاختر من القائمة:",
            "help_message": "🆘 كيفية استخدام البوت:\n- اختر الخدمة المطلوبة\n- اتبع التعليمات\n- يمكنك التواصل معنا عند الحاجة",
            "subscription_message": f"⚠️ يجب الاشتراك في القناة أولاً لاستخدام البوت:\n{CHANNEL_USERNAME}"
        }

def save_settings():
    with open('bot_settings.json', 'w') as f:
        json.dump(bot_settings, f, indent=4, ensure_ascii=False)

bot_settings = load_settings()

# -------------------- قاموس المواد والخدمات --------------------
ALL_MATERIALS = {
    # مواد الاوريا
    "MATH 001": "رياضيات 001",
    "MATH 002": "رياضيات 002",
    "ALEKS": "أليكس",
    "ENGLISH 01": "إنجليزي 01",
    "ENGLISH 02": "إنجليزي 02",
    "ENGLISH 03": "إنجليزي 03",
    "ENGLISH 04": "إنجليزي 04",
    "PYP001": "نماذج اختبارات 001",

    # مواد الفرشمن العامة
    "PHYS 101": "فيزياء 101",
    "PHYS 102": "فيزياء 102",
    "CHEM 101": "كيمياء 101",
    "CHEM 102": "كيمياء 102",
    "MATH 101": "رياضيات 101",
    "MATH 102": "رياضيات 102",
    "MATH 105": "رياضيات 105",
    "MATH 106": "رياضيات 106",
    "ICS 104": "مقدمة في الحاسب 104",
    "ENGLISH 101": "إنجليزي 101",
    "ENGLISH 102": "إنجليزي 102",
    "ECON 101": "اقتصاد 101",
    "ACCT 110": "محاسبة 110",
    "IAS 121": "دراسات إسلامية 121",
    "IAS 111": "دراسات إسلامية 111",
    "RES100": "بحث 100",

    # مواد السفمور العامة
    "MATH 208": "رياضيات 208",
    "MATH 201": "رياضيات 201",
    "ISE 291": "هندسة نظم 291",
    "COE 292": "هندسة حاسب 292",
    "ENGLISH 214": "إنجليزي 214",
    "IAS 212": "دراسات إسلامية 212",
    "IAS 321": "دراسات إسلامية 321",
    "IAS 322": "دراسات إسلامية 322",
    "BUS 200": "إدارة أعمال 200",
    "ECON 102": "اقتصاد 102",
    "ACCT 210": "محاسبة 210",
    "STAT 214": "إحصاء 214",
    "PHYS 204": "فيزياء 204",
    "CGS 392": "دراسات ثقافية 392",
    "IAS 330": "دراسات إسلامية 330",
    "OM 210": "إدارة عمليات 210",
    "MGT 210": "إدارة 210",
    "MGT 311": "إدارة 311",

    # مواد التخصص
    "ACCT 301": "محاسبة 301",
    "AE 211": "هندسة طيران 211",
    "AE 222": "هندسة طيران 222",
    "AE 228": "هندسة طيران 228",
    "AE358": "هندسة طيران 358",
    "CE 101": "هندسة مدنية 101",
    "CE 201": "هندسة مدنية 201",
    "CE 202": "هندسة مدنية 202",
    "CHE 200": "هندسة كيميائية 200",
    "CHE 204": "هندسة كيميائية 204",
    "CHE 212": "هندسة كيميائية 212",
    "CHE 300": "هندسة كيميائية 300",
    "CHE 304": "هندسة كيميائية 304",
    "CHE 306": "هندسة كيميائية 306",
    "CHE 402": "هندسة كيميائية 402",
    "CHE 405": "هندسة كيميائية 405",
    "CHEM 311": "كيمياء 311",
    "COE 202": "هندسة حاسب 202",
    "COE 233": "هندسة حاسب 233",
    "EE 201": "هندسة كهربائية 201",
    "EE 203": "هندسة كهربائية 203",
    "EE 204": "هندسة كهربائية 204",
    "EE 207": "هندسة كهربائية 207",
    "EE 213": "هندسة كهربائية 213",
    "EE 234/235": "هندسة كهربائية 234/235",
    "EE 236/237": "هندسة كهربائية 236/237",
    "EE 303": "هندسة كهربائية 303",
    "EE 311": "هندسة كهربائية 311",
    "EE 315": "هندسة كهربائية 315",
    "EE 340": "هندسة كهربائية 340",
    "EE 360": "هندسة كهربائية 360",
    "EE 370": "هندسة كهربائية 370",
    "EE 380": "هندسة كهربائية 380",
    "EE 390": "هندسة كهربائية 390",
    "FIN 315": "تمويل 315",
    "FIN 320": "تمويل 320",
    "PHYS 305": "فيزياء 305",
    "ISE 205": "هندسة نظم 205",
    "ISE 315": "هندسة نظم 315",
    "ISE 303": "هندسة نظم 303",
    "ISE 307": "هندسة نظم 307",
    "ICS 108": "حاسب 108",
    "ICS 202": "حاسب 202",
    "ICS 253": "حاسب 253",
    "ME 201": "هندسة ميكانيكية 201",
    "ME 203": "هندسة ميكانيكية 203",
    "ME 207": "هندسة ميكانيكية 207",
    "ME 210": "هندسة ميكانيكية 210",
    "ME 216/17": "هندسة ميكانيكية 216/17",
    "ME 218": "هندسة ميكانيكية 218",
    "ME 204": "هندسة ميكانيكية 204",
    "ME 301": "هندسة ميكانيكية 301",
    "ME 302/303": "هندسة ميكانيكية 302/303",
    "ME 311": "هندسة ميكانيكية 311",
    "ME 315/316": "هندسة ميكانيكية 315/316",
    "ME 322/323": "هندسة ميكانيكية 322/323",
    "ME 401/402": "هندسة ميكانيكية 401/402",
    "MSE 203": "علوم المواد 203",
    "STAT 319": "إحصاء 319",
    "MATH 371": "رياضيات 371",
    "SWE 206": "هندسة برمجيات 206",
    "SWE 216": "هندسة برمجيات 216",
    "GS 321": "دراسات عامة 321"
}

# -------------------- وظائف قواعد البيانات --------------------
def connect_db():
    conn = sqlite3.connect('university_bot.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service TEXT,
        sub_service TEXT,
        description TEXT,
        order_code TEXT UNIQUE,
        status TEXT DEFAULT 'قيد الانتظار',
        price REAL DEFAULT 0,
        deadline TEXT,
        assigned_to INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT,
        payment_status TEXT DEFAULT 'غير مدفوع',
        is_free INTEGER DEFAULT 0
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        full_name TEXT,
        join_date TEXT DEFAULT CURRENT_TIMESTAMP,
        balance REAL DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        phone_number TEXT,
        is_subscribed INTEGER DEFAULT 0,
        referral_link TEXT UNIQUE,
        referral_points INTEGER DEFAULT 0,
        referred_by TEXT,
        referrals_count INTEGER DEFAULT 0,
        last_referral_notification TEXT,
        last_subscription_check TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        order_id INTEGER,
        amount REAL,
        payment_method TEXT,
        transaction_id TEXT,
        status TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER UNIQUE,
        referral_date TEXT DEFAULT CURRENT_TIMESTAMP,
        points_earned INTEGER DEFAULT 1,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (referrer_id) REFERENCES users(user_id),
        FOREIGN KEY (referred_id) REFERENCES users(user_id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        activity_type TEXT,
        details TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )''')

    conn.commit()
    return conn

def check_db_columns():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'is_subscribed' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_subscribed INTEGER DEFAULT 0")

    for column in ['referral_link', 'referral_points', 'referred_by', 'referrals_count', 'last_referral_notification', 'last_subscription_check']:
        if column not in columns:
            if column in ['referral_points', 'referrals_count']:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column} INTEGER DEFAULT 0")
            else:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column} TEXT DEFAULT ''")

    cursor.execute("PRAGMA table_info(orders)")
    order_columns = [column[1] for column in cursor.fetchall()]
    if 'is_free' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN is_free INTEGER DEFAULT 0")

    db.commit()
    db.close()

# -------------------- وظائف مساعدة --------------------
def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

def generate_order_code():
    return f"ORD-{random.randint(100000, 999999)}"

def generate_referral_link(user_id):
    return f"https://t.me/{bot.get_me().username}?start=ref_{user_id}"

def get_referral_stats(user_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('SELECT referral_link, referral_points, referrals_count FROM users WHERE user_id=?', (user_id,))
    user_data = cursor.fetchone()

    if not user_data:
        referral_link = generate_referral_link(user_id)
        cursor.execute('UPDATE users SET referral_link=? WHERE user_id=?', (referral_link, user_id))
        db.commit()
        user_data = (referral_link, 0, 0)

    referral_link, points, count = user_data
    points = points if points is not None else 0
    count = count if count is not None else 0

    db.close()
    return {'link': referral_link, 'points': points, 'count': count}

def update_user_referral_info(user_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('''
    UPDATE users 
    SET referrals_count = (SELECT COUNT(*) FROM referrals WHERE referrer_id=? AND is_active=1),
        referral_points = (SELECT SUM(points_earned) FROM referrals WHERE referrer_id=? AND is_active=1)
    WHERE user_id=?
    ''', (user_id, user_id, user_id))
    db.commit()
    db.close()

def create_order(user_id, service, sub_service, description, price=None, is_free=False):
    if bot_settings["maintenance_mode"]:
        return None, "⛔ البوت في وضع الصيانة حالياً، الرجاء المحاولة لاحقاً", None

    if not bot_settings["accepting_orders"]:
        return None, "⛔ تم تعطيل استقبال الطلبات مؤقتاً", None

    order_code = generate_order_code()
    db = connect_db()
    cursor = db.cursor()

    final_price = 0 if is_free else (price if price is not None else bot_settings["default_price"])

    try:
        cursor.execute('''
        INSERT INTO orders (user_id, service, sub_service, description, order_code, price, is_free)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, service, sub_service, description, order_code, final_price, 1 if is_free else 0))
        db.commit()
        order_id = cursor.lastrowid

        if bot_settings["admin_notifications"]:
            notify_admin(order_id, user_id, service, sub_service, final_price, order_code, is_free)

        log_activity(user_id, "create_order", f"{service} - {sub_service}")
        return order_code, "✅ تم إنشاء طلبك بنجاح برقم: {}".format(order_code), final_price
    except sqlite3.IntegrityError:
        return None, "⚠️ حدث خطأ، رمز الطلب موجود بالفعل. حاول مرة أخرى.", None
    finally:
        db.close()

def notify_admin(order_id, user_id, service, sub_service, price, order_code, is_free=False):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('SELECT username, full_name FROM users WHERE user_id=?', (user_id,))
    user_data = cursor.fetchone()
    username = f"@{user_data[0]}" if user_data and user_data[0] else f"معرف غير متوفر ({user_id})"
    full_name = user_data[1] if user_data and user_data[1] else "اسم غير متوفر"

    free_tag = " (خدمة مجانية)" if is_free else ""
    admin_msg = f"""
📬 طلب جديد #{order_id}{free_tag}
📦 الخدمة: {service} - {sub_service}
💰 السعر: {price} ريال
🆔 كود الطلب: {order_code}
👤 المستخدم: {full_name} ({username})
🕒 الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    try:
        bot.send_message(ADMIN_ID, admin_msg)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Error sending notification to admin: {e}")
    finally:
        db.close()

def check_subscription(user_id):
    if not bot_settings["required_subscription"]:
        return True

    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        is_member = member.status in ['member', 'administrator', 'creator']

        db = connect_db()
        cursor = db.cursor()
        cursor.execute('UPDATE users SET is_subscribed=? WHERE user_id=?', (1 if is_member else 0, user_id))

        if is_member:
            cursor.execute('SELECT last_subscription_check FROM users WHERE user_id=?', (user_id,))
            last_check = cursor.fetchone()[0]

            if not last_check:  # أول مرة يشترك
                cursor.execute('UPDATE users SET balance=balance+? WHERE user_id=?', 
                              (bot_settings["default_price"] * 0.5, user_id))  # مكافأة 50% من سعر الخدمة
                db.commit()
                try:
                    bot.send_message(user_id, f"🎉 مبروك! لقد حصلت على مكافأة اشتراك بقيمة {bot_settings['default_price'] * 0.5} ريال!")
                except:
                    pass

        cursor.execute('UPDATE users SET last_subscription_check=? WHERE user_id=?', 
                      (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
        db.commit()
        db.close()

        return is_member
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Error checking subscription for user {user_id}: {e}")
        return False

def show_subscription_alert(chat_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text="✨ اشترك في القناة",
        url="https://t.me/mazenya244"
    ))
    markup.add(telebot.types.InlineKeyboardButton(
        text="✅ تأكيد الاشتراك",
        callback_data="verify_subscription"
    ))

    bot.send_message(
        chat_id,
        bot_settings["subscription_message"],
        reply_markup=markup
    )




def ensure_subscription(message):
    if bot_settings["required_subscription"] and not check_subscription(message.from_user.id):
        show_subscription_alert(message.chat.id)
        return False
    return True
def get_user_orders(user_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('''
    SELECT order_code, service, sub_service, status, created_at, is_free
    FROM orders
    WHERE user_id=?
    ORDER BY created_at DESC
    LIMIT 10
    ''', (user_id,))
    orders = cursor.fetchall()
    db.close()
    return orders

def get_main_keyboard(user_id=None):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["📚 الخدمات الطلابية", "📋 طلباتي", "💬 الدعم الفني", "📢 نظام الإحالات"]
    if user_id:
        buttons.append("⚙️ الإعدادات")
        if bot_settings["required_subscription"]:
            buttons.append("🔔 التحقق من الاشتراك")
    markup.add(*buttons)
    markup.add("🔙 الرئيسية")
    return markup

def get_admin_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "📊 الإحصائيات", "📦 إدارة الطلبات",
        "👥 إدارة المستخدمين", "⚙️ إعدادات البوت",
        "📢 إرسال إشعار عام", "✉️ رسالة مستخدم",
        "➕ إدارة الخدمات", "📊 إحصائيات متقدمة",
        "📅 التقرير اليومي", "⏰ إرسال تذكيرات"
    ]
    markup.add(*buttons)
    markup.add("🔙 الخروج من لوحة التحكم")
    return markup

def log_user(user_id, username, full_name):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        referral_link = generate_referral_link(user_id)

        cursor.execute('''
        INSERT INTO users (user_id, username, full_name, referral_link, referral_points, referrals_count)
        VALUES (?, ?, ?, ?, 0, 0)
        ''', (user_id, username, full_name, referral_link))
        db.commit()

        bot.send_message(ADMIN_ID, f"👤 مستخدم جديد دخل البوت:\nالاسم: {full_name}\nالمعرف: @{username}\nID: {user_id}")
    db.close()

def update_order_field(message, order_id, field_name):
    user_id = message.from_user.id
    new_value = message.text.strip()
    db = connect_db()
    cursor = db.cursor()

    try:
        if field_name == 'price':
            new_value = float(new_value)
            cursor.execute(f'UPDATE orders SET {field_name}=?, updated_at=? WHERE id=?', (new_value, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_id))
        elif field_name == 'status':
            valid_statuses = ['قيد الانتظار', 'قيد التنفيذ', 'مكتمل', 'ملغي']
            if new_value not in valid_statuses:
                bot.send_message(message.chat.id, "❌ حالة غير صالحة. يرجى اختيار من: قيد الانتظار, قيد التنفيذ, مكتمل, ملغي.")
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add("قيد الانتظار", "قيد التنفيذ", "مكتمل", "ملغي")
                msg = bot.send_message(message.chat.id, "اختر الحالة الجديدة:", reply_markup=markup)
                bot.register_next_step_handler(msg, lambda m: update_order_field(m, order_id, 'status'))
                return
            cursor.execute(f'UPDATE orders SET {field_name}=?, updated_at=? WHERE id=?', (new_value, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_id))
            cursor.execute('SELECT user_id, order_code, service, sub_service FROM orders WHERE id=?', (order_id,))
            order_info = cursor.fetchone()
            if order_info:
                target_user_id, order_code, service, sub_service = order_info
                bot.send_message(target_user_id, f"🔔 تم تحديث حالة طلبك: #{order_code} ({service} - {sub_service}) إلى **{new_value}**", parse_mode='Markdown')
        else:
            cursor.execute(f'UPDATE orders SET {field_name}=?, updated_at=? WHERE id=?', (new_value, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_id))

        db.commit()
        bot.send_message(message.chat.id, f"✅ تم تحديث {field_name} الطلب بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ قيمة غير صالحة. يرجى إدخال رقم صحيح للسعر.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ أثناء التحديث: {e}")
    finally:
        db.close()
        del admin_actions[user_id]
        process_order_edit_after_update(message, order_id)

def process_order_edit_after_update(message, order_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('SELECT order_code, service, sub_service, status, price, deadline, description FROM orders WHERE id=?', (order_id,))
    order = cursor.fetchone()
    db.close()

    if not order:
        return bot.send_message(message.chat.id, "❌ الطلب غير موجود")

    order_code, service, sub_service, status, price, deadline, description = order
    admin_actions[message.from_user.id] = {'action': 'edit_order', 'order_id': order_id}

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(f"💰 السعر: {price}", f"🔄 الحالة: {status}")
    markup.add(f"📅 الموعد النهائي: {deadline if deadline else 'غير محدد'}", "📝 وصف الطلب")
    markup.add("❌ حذف الطلب", "🔙 إدارة الطلبات")
    bot.send_message(message.chat.id, f"تعديل الطلب رقم {order_code}:\nالخدمة: {service} - {sub_service}", reply_markup=markup)

def check_and_reward_referrals(user_id):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute('SELECT COUNT(*) FROM referrals WHERE referrer_id=? AND is_active=1', (user_id,))
    active_referrals = cursor.fetchone()[0]

    cursor.execute('SELECT last_referral_notification FROM users WHERE user_id=?', (user_id,))
    last_notification = cursor.fetchone()[0]

    if active_referrals >= REQUIRED_REFERRALS and not last_notification:
        cursor.execute('UPDATE users SET balance=balance+?, last_referral_notification=? WHERE user_id=?', 
                      (bot_settings["default_price"], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
        db.commit()

        try:
            bot.send_message(user_id, f"🎉 مبروك! لقد أحلت {REQUIRED_REFERRALS} أشخاص إلى البوت.\n\n🆓 يمكنك الآن الحصول على خدمة مجانية بقيمة {bot_settings['default_price']} ريال!")
        except:
            pass

    db.close()

def get_user_balance(user_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id=?', (user_id,))
    balance = cursor.fetchone()[0] or 0
    db.close()
    return balance

def add_user_balance(user_id, amount):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET balance=balance+? WHERE user_id=?', (amount, user_id))
    db.commit()
    db.close()

def get_referral_history(user_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('''
    SELECT r.referred_id, u.username, u.full_name, r.referral_date 
    FROM referrals r
    JOIN users u ON r.referred_id = u.user_id
    WHERE r.referrer_id=?
    ORDER BY r.referral_date DESC
    LIMIT 10
    ''', (user_id,))
    referrals = cursor.fetchall()
    db.close()
    return referrals

def send_notification(user_id, message):
    try:
        bot.send_message(user_id, message)
        return True
    except:
        return False

def notify_new_feature(message_text):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('SELECT user_id FROM users WHERE is_banned=0')
    users = cursor.fetchall()
    db.close()

    success = 0
    failed = 0
    for user in users:
        if send_notification(user[0], message_text):
            success += 1
        else:
            failed += 1

    return success, failed

def log_activity(user_id, activity_type, details=""):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('''
    INSERT INTO user_activities (user_id, activity_type, details)
    VALUES (?, ?, ?)
    ''', (user_id, activity_type, details))
    db.commit()
    db.close()

def send_reminders():
    db = connect_db()
    cursor = db.cursor()

    cursor.execute('''
    SELECT o.user_id, o.order_code, u.username 
    FROM orders o
    JOIN users u ON o.user_id = u.user_id
    WHERE o.status NOT IN ('مكتمل', 'ملغي') 
    AND date(o.updated_at) < date('now', '-3 days')
    ''')
    overdue_orders = cursor.fetchall()

    for order in overdue_orders:
        user_id, order_code, username = order
        message = f"⏰ تذكير: طلبك #{order_code} لا يزال قيد التنفيذ. يمكنك متابعة حالته من قائمة 'طلباتي'"
        send_notification(user_id, message)

    db.close()
    return len(overdue_orders)

def generate_daily_report():
    db = connect_db()
    cursor = db.cursor()

    yesterday = datetime.now().strftime('%Y-%m-%d')

    cursor.execute('SELECT COUNT(*) FROM users WHERE date(join_date)=?', (yesterday,))
    new_users = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM orders WHERE date(created_at)=?', (yesterday,))
    new_orders = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(price) FROM orders WHERE date(created_at)=? AND is_free=0', (yesterday,))
    daily_revenue = cursor.fetchone()[0] or 0

    cursor.execute('''
    SELECT u.user_id, u.username, COUNT(r.id) as referrals
    FROM referrals r
    JOIN users u ON r.referrer_id = u.user_id
    WHERE date(r.referral_date) = ?
    GROUP BY r.referrer_id
    ORDER BY referrals DESC
    LIMIT 3
    ''', (yesterday,))
    top_referrers = cursor.fetchall()

    db.close()

    report_text = f"""
📅 تقرير يومي لتاريخ {yesterday}

👤 مستخدمون جدد: {new_users}
📦 طلبات جديدة: {new_orders}
💰 إيرادات اليوم: {daily_revenue} ريال

🏆 أفضل المحيلين:
"""
    for i, (user_id, username, referrals) in enumerate(top_referrers, 1):
        report_text += f"\n{i}. @{username} - {referrals} إحالة"

    return report_text

def show_main_features(chat_id):
    features_text = """
✨ الميزات الرئيسية:

1. 📚 خدمات طلابية شاملة لجميع المواد
2. 📢 نظام إحالات يحقق لك مكافآت مجانية
3. 💬 دعم فني متاح على مدار الساعة
4. ⚙️ إعدادات شخصية لحسابك

استخدم الأزرار في الأسفل للتنقل بين الميزات!
"""
    bot.send_message(chat_id, features_text)

# -------------------- واجهة المستخدم --------------------

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if bot_settings["maintenance_mode"]:
        return bot.send_message(message.chat.id, "⛔ البوت في وضع الصيانة حالياً")

    user_id = message.from_user.id
    username = message.from_user.username or "بدون معرف"
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()

    if len(message.text.split()) > 1 and message.text.split()[1].startswith('ref_'):
        referrer_id = int(message.text.split()[1][4:])
        if referrer_id != user_id:
            db = connect_db()
            cursor = db.cursor()

            cursor.execute('SELECT id FROM referrals WHERE referred_id=?', (user_id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)', (referrer_id, user_id))
                db.commit()

                update_user_referral_info(referrer_id)

                try:
                    bot.send_message(referrer_id, f"🎉 تم تسجيل إحالة جديدة بواسطة {full_name} (@{username})\n\nعدد إحالاتك الآن: {get_referral_stats(referrer_id)['count']}")
                except:
                    pass

                try:
                    bot.send_message(ADMIN_ID, f"📢 إحالة جديدة!\nالمحيل: {referrer_id}\nالمستخدم الجديد: {user_id} (@{username})")
                except:
                    pass

                check_and_reward_referrals(referrer_id)

            db.close()

    if bot_settings["required_subscription"] and not check_subscription(user_id):
        show_subscription_alert(message.chat.id)
        return

    log_user(user_id, username, full_name)

    if is_admin(user_id):
        bot.send_message(message.chat.id, "🛠️ لوحة تحكم الإدمن", reply_markup=get_admin_keyboard())
    else:
        welcome_msg = bot_settings["welcome_message"]
        if check_subscription(user_id):
            welcome_msg += "\n\n🎉 أنت مشترك في القناة! يمكنك استخدام جميع ميزات البوت."
        else:
            welcome_msg += "\n\n⚠️ يرجى الاشتراك في القناة لاستخدام البوت."

        bot.send_message(message.chat.id, welcome_msg, reply_markup=get_main_keyboard(user_id))
        show_main_features(message.chat.id)
        bot.send_message(message.chat.id, "🔽 إذا لم تظهر الأزرار، اضغط على رمز المربع الصغير بجانب خانة الكتابة لإظهار القائمة.")

@bot.callback_query_handler(func=lambda call: call.data == "verify_subscription")
def verify_subscription_callback(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "✅ تم التحقق من اشتراكك بنجاح!")
        bot.send_message(user_id, "/start")
    else:
        bot.answer_callback_query(call.id, "⚠️ لم يتم العثور على اشتراكك، يرجى الاشتراك أولاً", show_alert=True)
        show_subscription_alert(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "referral_history")
def show_referral_history(call):
    user_id = call.from_user.id
    referrals = get_referral_history(user_id)

    if not referrals:
        bot.answer_callback_query(call.id, "لا توجد إحالات مسجلة بعد", show_alert=True)
        return

    history_text = "📜 آخر 10 إحالات:\n\n"
    for ref in referrals:
        referred_id, username, full_name, date = ref
        history_text += f"👤 {full_name or 'بدون اسم'} (@{username or 'بدون معرف'})\n🆔 {referred_id}\n📅 {date.split()[0]}\n\n"

    bot.send_message(call.message.chat.id, history_text)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text == "📚 الخدمات الطلابية")
def show_services(message):
    if bot_settings["maintenance_mode"]:
        return bot.send_message(message.chat.id, "⛔ البوت في وضع الصيانة حالياً")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🌐 جميع المواد")
    markup.add(
        "بحوث", "برمجة", "تصميم انفوجرافيك",
        "تحليل إحصائي", "كتابة مقالات", "تقارير وتجارب",
        "مراجعة", "ترجمة", "تنسيق أوراق"
    )
    markup.add("🔙 الرئيسية")
    bot.send_message(message.chat.id, "اختر الخدمة المطلوبة:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🌐 جميع المواد")
def show_all_materials_list(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    sorted_materials = sorted(ALL_MATERIALS.items(), key=lambda item: item[1])
    for code, name in sorted_materials:
        markup.add(f"{name} ({code})")
    markup.add("🔙 الخدمات الطلابية")
    bot.send_message(message.chat.id, "📚 قائمة جميع المواد والخدمات:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ALL_MATERIALS.values() or m.text.endswith(')'))
def process_material_selection(message):
    if "(" in message.text and ")" in message.text:
        service_name = message.text
        service_code = message.text.split('(')[-1][:-1]
    else:
        service_name = message.text
        service_code = next((code for code, name in ALL_MATERIALS.items() if name == service_name), "غير محدد")

    user_states[message.from_user.id] = {'action': 'request_details', 'service': "خدمات طلابية", 'sub_service': service_name}
    msg = bot.send_message(message.chat.id, f"📝 يرجى وصف تفاصيل طلبك لخدمة '{service_name}' (مثلاً: عدد الأسئلة، الموعد النهائي، أي متطلبات خاصة):")
    bot.register_next_step_handler(msg, get_order_description)

@bot.message_handler(func=lambda m: m.text in [
    "بحوث", "برمجة", "تصميم انفوجرافيك", "تحليل إحصائي", "كتابة مقالات",
    "تقارير وتجارب", "مراجعة", "ترجمة", "تنسيق أوراق",
    "جامعية", "مدرسية", "أخرى", "تجريبية",
    "بحث متكامل", "حسب تحديد الفصول", "بحث عام", "رسالة الماجستير", "مراجعة مصادر",
    "مواقع ويب", "تطبيقات موبايل", "مشاريع تخرج", "لغة بايثون", "لغة سي بلاس بلاس", "سي شارب", "اتش تي ام ال",
    "سوشيال ميديا", "عروض بوربوينت", "مطويات", "برشورات", "شعارات", "هوية بصرية", "بوستات", "موشين جرافيك", "تايبو جرافيك", "بوسترات ترويجية",
    "SPSS", "جداول ونتائج", "تحليل بياني",
    "مقال رأي", "مقال علمي", "مقال تحليلي",
    "مختبرات", "تقارير دورية", "مشاريع تطبيقية",
    "مراجعة شاملة", "مراجعة قصيرة",
    "ترجمة نصوص", "ترجمة أوراق بحثية",
    "تنسيق APA", "tنسيق MLA", "تنسيق جامعي عام"
])
def process_service_selection(message):
    service_type = message.text
    user_id = message.from_user.id

    if service_type in ["بحوث", "برمجة", "تصميم انفوجرافيك", "تحليل إحصائي", "كتابة مقالات",
                        "تقارير وتجارب", "مراجعة", "ترجمة", "تنسيق أوراق"]:
        user_states[user_id] = {'action': 'select_sub_service', 'service': service_type}

        sub_services_options = {
            "بحوث": ["بحث متكامل", "حسب تحديد الفصول", "بحث عام", "رسالة الماجستير", "مراجعة مصادر"],
            "برمجة": ["مواقع ويب", "تطبيقات موبايل", "مشاريع تخرج", "لغة بايثون", "لغة سي بلاس بلاس", "سي شارب", "اتش تي ام ال"],
            "تصميم انفوجرافيك": ["سوشيال ميديا", "عروض بوربوينت", "مطويات", "برشورات", "شعارات", "هوية بصرية", "بوستات", "موشين جرافيك", "تايبو جرافيك", "بوسترات ترويجية"],
            "تحليل إحصائي": ["SPSS", "جداول ونتائج", "تحليل بياني"],
            "كتابة مقالات": ["مقال رأي", "مقال علمي", "مقال تحليلي"],
            "تقارير وتجارب": ["مختبرات", "تقارير دورية", "مشاريع تطبيقية"],
            "مراجعة": ["مراجعة شاملة", "مراجعة قصيرة"],
            "ترجمة": ["ترجمة نصوص", "ترجمة أوراق بحثية"],
            "تنسيق أوراق": ["تنسيق APA", "tنسيق MLA", "تنسيق جامعي عام"]
        }
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for sub in sub_services_options.get(service_type, []):
            markup.add(sub)
        markup.add("🔙 الخدمات الطلابية")
        bot.send_message(message.chat.id, f"اختر نوع {service_type}:", reply_markup=markup)
    elif service_type in ["جامعية", "مدرسية", "أخرى", "تجريبية"]:
        if user_id in user_states and user_states[user_id].get('action') == 'select_sub_service':
            main_service = user_states[user_id]['service']
            user_states[user_id]['sub_service'] = service_type
            user_states[user_id]['action'] = 'request_details'
            msg = bot.send_message(message.chat.id, f"📝 يرجى وصف تفاصيل طلبك لـ '{main_service} - {service_type}':")
            bot.register_next_step_handler(msg, get_order_description)
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى البدء باختيار الخدمة الرئيسية أولاً.")
    else:
        if user_id in user_states and user_states[user_id].get('action') == 'select_sub_service':
            main_service = user_states[user_id]['service']
            user_states[user_id]['sub_service'] = service_type
            user_states[user_id]['action'] = 'request_details'
            msg = bot.send_message(message.chat.id, f"📝 يرجى وصف تفاصيل طلبك لـ '{main_service} - {service_type}':")
            bot.register_next_step_handler(msg, get_order_description)
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى البدء باختيار الخدمة الرئيسية أولاً.")

def get_order_description(message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id]['action'] != 'request_details':
        return bot.send_message(message.chat.id, "⚠️ حدث خطأ غير متوقع. يرجى البدء من جديد.", reply_markup=get_main_keyboard(user_id))

    description = message.text.strip()
    user_states[user_id]['description'] = description

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ تأكيد الطلب", "❌ إلغاء")
    bot.send_message(message.chat.id, "هل أنت متأكد من تفاصيل الطلب؟", reply_markup=markup)
    bot.register_next_step_handler(message, confirm_order)

def confirm_order(message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id]['action'] != 'request_details':
        return bot.send_message(message.chat.id, "⚠️ حدث خطأ غير متوقع. يرجى البدء من جديد.", reply_markup=get_main_keyboard(user_id))

    if message.text == "✅ تأكيد الطلب":
        service_name = user_states[user_id]['service']
        sub_service_name = user_states[user_id]['sub_service']
        description = user_states[user_id]['description']

        # التحقق من رصيد المستخدم لخدمة مجانية
        user_balance = get_user_balance(user_id)
        is_free = user_balance >= bot_settings["default_price"]

        if is_free:
            add_user_balance(user_id, -bot_settings["default_price"])

        order_code, response_message, price = create_order(user_id, service_name, sub_service_name, description, None, is_free)

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            text="📞 اضغط هنا للتواصل معنا بخصوص الطلب",
            url="https://t.me/mazenya244"
        ))

        bot.send_message(user_id, response_message)
        if is_free:
            bot.send_message(user_id, "🎉 تم استخدام رصيدك للحصول على هذه الخدمة المجانية.")
        bot.send_message(user_id, "سيتم التواصل معك قريباً لتنفيذ طلبك.", reply_markup=markup)

        if bot_settings["payment_required"] and order_code and not is_free:
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("💳 الدفع", "🔙 الرئيسية")
            bot.send_message(user_id, f"💰 قيمة الطلب: {price} ريال. يرجى الدفع للمتابعة.", reply_markup=markup)
        else:
            bot.send_message(user_id, "سيتم التواصل معك قريباً لتنفيذ طلبك.", reply_markup=get_main_keyboard(user_id))

        del user_states[user_id]
    elif message.text == "❌ إلغاء":
        bot.send_message(user_id, "تم إلغاء الطلب.", reply_markup=get_main_keyboard(user_id))
        del user_states[user_id]
    else:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✅ تأكيد الطلب", "❌ إلغاء")
        bot.send_message(user_id, "يرجى اختيار تأكيد الطلب أو إلغائه.", reply_markup=markup)
        bot.register_next_step_handler(message, confirm_order)

@bot.message_handler(func=lambda m: m.text == "📋 طلباتي")
def show_user_orders(message):
    user_id = message.from_user.id
    orders = get_user_orders(user_id)

    if not orders:
        return bot.send_message(message.chat.id, "📭 لا توجد لديك أي طلبات بعد")

    orders_text = "📋 طلباتك الأخيرة:\n\n"
    for order in orders:
        order_code, service, sub_service, status, created_at, is_free = order
        free_tag = " (مجانية)" if is_free else ""
        orders_text += f"""
📦 {service} - {sub_service}{free_tag}
🆔 {order_code}
🟢 الحالة: {status}
📅 {created_at.split()[0]}
------------------------
"""
    bot.send_message(message.chat.id, orders_text)

@bot.message_handler(func=lambda m: m.text == "💬 الدعم الفني")
def contact_support(message):
    support_message = "للتواصل مع الدعم الفني، يرجى إرسال رسالتك وسيتم الرد عليك في أقرب وقت ممكن."
    bot.send_message(message.chat.id, support_message)
    user_states[message.from_user.id] = {'action': 'send_support_message'}
    bot.register_next_step_handler(message, process_support_message)

def process_support_message(message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id]['action'] != 'send_support_message':
        return bot.send_message(message.chat.id, "⚠️ حدث خطأ غير متوقع.")

    support_text = f"✉️ رسالة دعم من المستخدم {message.from_user.id} (@{message.from_user.username}):\n\n{message.text}"
    try:
        bot.send_message(ADMIN_ID, support_text)
        bot.send_message(user_id, "✅ تم إرسال رسالتك إلى الدعم الفني. سيتم الرد عليك قريباً.", reply_markup=get_main_keyboard(user_id))
    except telebot.apihelper.ApiTelegramException as e:
        bot.send_message(user_id, f"❌ فشل إرسال الرسالة إلى الدعم الفني. حاول مرة أخرى لاحقاً. ({e})", reply_markup=get_main_keyboard(user_id))
    finally:
        del user_states[user_id]

@bot.message_handler(func=lambda m: m.text == "⚙️ الإعدادات" and not is_admin(m.from_user.id))
def user_settings(message):
    user_id = message.from_user.id
    stats = get_referral_stats(user_id)
    balance = get_user_balance(user_id)

    settings_text = f"""
⚙️ إعدادات حسابك:

🆔 معرفك: {user_id}
📢 عدد الإحالات: {stats['count']}
🎯 نقاط الإحالة: {stats['points']}
💰 رصيدك الحالي: {balance} ريال
"""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔙 الرئيسية")
    bot.send_message(message.chat.id, settings_text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔙 الرئيسية")
def go_to_main_menu(message):
    bot.send_message(message.chat.id, "🏠 العودة إلى القائمة الرئيسية.", reply_markup=get_main_keyboard(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "🔔 التحقق من الاشتراك")
def verify_subscription_command(message):
    if check_subscription(message.from_user.id):
        bot.send_message(message.chat.id, "✅ أنت مشترك في القناة بالفعل!")
    else:
        show_subscription_alert(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "📢 نظام الإحالات")
def show_referral_system(message):
    try:
        user_id = message.from_user.id
        stats = get_referral_stats(user_id)

        # التحقق من وجود رابط إحالة صالح
        if not stats.get('link') or not stats['link'].startswith("https://"):
            new_link = f"https://t.me/{bot.get_me().username}?start=ref_{user_id}"
            db = connect_db()
            cursor = db.cursor()
            cursor.execute('UPDATE users SET referral_link=? WHERE user_id=?', (new_link, user_id))
            db.commit()
            db.close()
            stats['link'] = new_link

        balance = get_user_balance(user_id)

        # النص المعدل مع تنسيق Markdown
        referral_text = f"""
*📢 نظام الإحالات الخاص بك*

🎯 *النقاط المتراكمة:* {stats['points']}
👥 *عدد الإحالات:* {stats['count']}
💰 *رصيدك الحالي:* {balance:.1f} ريال

💎 *كيفية الاستفادة:*
1. شارك رابطك الخاص مع الأصدقاء
2. عند تسجيل كل صديق: +1 نقطة
3. عند جمع *{REQUIRED_REFERRALS}* نقاط: خدمة مجانية!

🔗 *رابطك الخاص:*
`{stats['link']}`
"""

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton(
                text="📋 نسخ الرابط", 
                callback_data="copy_referral_link"
            ),
            telebot.types.InlineKeyboardButton(
                text="↗️ مشاركة", 
                url=f"https://t.me/share/url?url={stats['link']}&text=انضم%20إلى%20بوت%20الخدمات%20الطلابية%20واستفد%20من%20خدماتنا%20المميزة!"
            )
        )
        markup.add(
            telebot.types.InlineKeyboardButton(
                text="📊 تفاصيل الإحالات", 
                callback_data="referral_details"
            )
        )

        bot.send_message(
            message.chat.id,
            referral_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )

    except Exception as e:
        print(f"Error in referral system: {str(e)}")
        bot.send_message(
            message.chat.id,
            "⚠️ حدث خطأ في عرض نظام الإحالات. يرجى المحاولة لاحقاً."
        )

@bot.callback_query_handler(func=lambda call: call.data == "copy_referral_link")
def handle_copy_referral(call):
    try:
        user_id = call.from_user.id
        stats = get_referral_stats(user_id)

        bot.answer_callback_query(
            call.id,
            "✓ تم نسخ الرابط بنجاح",
            show_alert=True
        )

        bot.send_message(
            call.message.chat.id,
            f"🔗 *رابط الإحالة الخاص بك:*\n\n`{stats['link']}`\n\n"
            "يمكنك مشاركته مع الأصدقاء للحصول على نقاط إحالة!",
            parse_mode='Markdown'
        )

    except Exception as e:
        print(f"Error in copy referral: {str(e)}")
        bot.answer_callback_query(
            call.id,
            "⚠️ فشل نسخ الرابط، يرجى المحاولة لاحقاً",
            show_alert=True
        )
@bot.callback_query_handler(func=lambda call: call.data == "copy_referral_link")
def copy_referral_link(call):
    user_id = call.from_user.id
    stats = get_referral_stats(user_id)
    referral_link = stats['link']

    bot.answer_callback_query(call.id, "تم نسخ الرابط بنجاح!", show_alert=True)

    text = f"""📢 هذا هو رابط الإحالة الخاص بك:

{referral_link}

انسخه وشاركه مع أصدقائك، وستصل على نقاط مقابل كل تسجيل من خلاله."""
    bot.send_message(call.message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🎁 استبدال النقاط")
def redeem_points(message):
    user_id = message.from_user.id
    stats = get_referral_stats(user_id)

    if stats['count'] < REQUIRED_REFERRALS:
        bot.send_message(user_id, f"⚠️ تحتاج إلى {REQUIRED_REFERRALS} إحالات للحصول على خدمة مجانية. لديك حالياً {stats['count']} إحالة.")
        return

    db = connect_db()
    cursor = db.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id=?', (user_id,))
    current_balance = cursor.fetchone()[0] or 0
    db.close()

    if current_balance >= bot_settings["default_price"]:
        bot.send_message(user_id, f"🎉 لديك بالفعل رصيد كافي للحصول على خدمة مجانية ({current_balance} ريال). يمكنك طلب خدمة الآن وسيتم خصمها تلقائياً.")
        return

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ نعم، أريد الخدمة المجانية", "❌ لا، إلغاء")

    msg = bot.send_message(user_id, f"هل تريد استبدال {REQUIRED_REFERRALS} إحالات للحصول على خدمة مجانية بقيمة {bot_settings['default_price']} ريال؟", reply_markup=markup)
    bot.register_next_step_handler(msg, process_redeem_points)

def process_redeem_points(message):
    user_id = message.from_user.id

    if message.text == "✅ نعم، أريد الخدمة المجانية":
        db = connect_db()
        cursor = db.cursor()

        try:
            cursor.execute('UPDATE users SET balance=balance+?, last_referral_notification=? WHERE user_id=?', 
                          (bot_settings["default_price"], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
            db.commit()

            bot.send_message(user_id, f"🎉 تم منحك رصيد بقيمة {bot_settings['default_price']} ريال! يمكنك الآن طلب خدمة وسيتم خصمها تلقائياً من رصيدك.", reply_markup=get_main_keyboard(user_id))
        except Exception as e:
            bot.send_message(user_id, f"❌ حدث خطأ أثناء عملية الاستبدال: {e}", reply_markup=get_main_keyboard(user_id))
        finally:
            db.close()
    else:
        bot.send_message(user_id, "تم إلغاء عملية الاستبدال.", reply_markup=get_main_keyboard(user_id))

# -------------------- لوحة تحكم الأدمن --------------------
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📊 الإحصائيات")
def admin_stats(message):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM orders')
    total_orders = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM referrals WHERE is_active=1')
    total_referrals = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(balance) FROM users')
    total_balance = cursor.fetchone()[0] or 0

    cursor.execute('''
    SELECT u.user_id, u.full_name, u.username, COUNT(r.id) as referrals_count, SUM(r.points_earned) as total_points
    FROM referrals r
    JOIN users u ON r.referrer_id = u.user_id
    WHERE r.is_active = 1
    GROUP BY r.referrer_id
    ORDER BY total_points DESC
    LIMIT 10
    ''')
    top_referrers = cursor.fetchall()

    cursor.execute('''
    SELECT COUNT(*) FROM users 
    WHERE is_subscribed = 1 AND user_id IN (SELECT user_id FROM orders)
    ''')
    active_subscribed_users = cursor.fetchone()[0]

    db.close()

    stats_text = f"""
📊 إحصائيات البوت:

👥 إجمالي المستخدمين: {total_users}
📦 إجمالي الطلبات: {total_orders}
📢 إجمالي الإحالات: {total_referrals}
💰 إجمالي الرصيد المجاني: {total_balance} ريال
🔔 المستخدمون النشطون المشتركون: {active_subscribed_users}

🏆 أفضل 10 محيلين:
"""

    for i, (user_id, full_name, username, count, points) in enumerate(top_referrers, 1):
        stats_text += f"\n{i}. {full_name or 'بدون اسم'} (@{username or 'بدون معرف'}) - {points} نقطة ({count} إحالة)"

    bot.send_message(message.chat.id, stats_text)

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📊 إحصائيات متقدمة")
def advanced_stats(message):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute('SELECT COUNT(*) FROM users WHERE is_banned=0')
    active_users = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM users WHERE is_banned=1')
    banned_users = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed=1')
    subscribed_users = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM orders WHERE status="مكتمل"')
    completed_orders = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM orders WHERE status="قيد الانتظار"')
    pending_orders = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM orders WHERE is_free=1')
    free_orders = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(price) FROM orders WHERE status="مكتمل" AND is_free=0')
    total_revenue = cursor.fetchone()[0] or 0

    cursor.execute('SELECT SUM(balance) FROM users')
    total_balance = cursor.fetchone()[0] or 0

    db.close()

    stats_text = f"""
📊 إحصائيات متقدمة:

👥 المستخدمون:
- نشط: {active_users}
- محظور: {banned_users}
- مشترك: {subscribed_users}

📦 الطلبات:
- مكتملة: {completed_orders}
- قيد الانتظار: {pending_orders}
- مجانية: {free_orders}

💰 مالية:
- إجمالي الإيرادات: {total_revenue} ريال
- إجمالي الرصيد المجاني: {total_balance} ريال
"""
    bot.send_message(message.chat.id, stats_text)

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📅 التقرير اليومي")
def send_daily_report(message):
    report = generate_daily_report()
    bot.send_message(message.chat.id, report)

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📦 إدارة الطلبات")
def manage_orders(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📥 الطلبات الجديدة", "🔄 الطلبات النشطة", "✅ الطلبات المكتملة")
    markup.add("✏️ تعديل طلب", "🔙 الخروج من لوحة التحكم")
    bot.send_message(message.chat.id, "اختر الإجراء:", reply_markup=markup)

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "📥 الطلبات الجديدة")
def view_new_orders(message):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('''
    SELECT o.id, o.order_code, o.user_id, o.service, o.sub_service, o.description, o.is_free, u.username 
    FROM orders o
    LEFT JOIN users u ON o.user_id = u.user_id
    WHERE o.status=?
    ORDER BY o.created_at DESC
    LIMIT 20
    ''', ('قيد الانتظار',))
    new_orders = cursor.fetchall()
    db.close()

    if not new_orders:
        return bot.send_message(message.chat.id, "لا توجد طلبات جديدة.")

    orders_text = "📥 آخر 20 طلب جديد:\n\n"
    for order in new_orders:
        order_id, order_code, user_id, service, sub_service, description, is_free, username = order
        free_tag = " (مجاني)" if is_free else ""
        orders_text += f"#{order_id} | كود: {order_code}{free_tag}\n👤 {user_id} (@{username})\n📦 {service} - {sub_service}\nالوصف: {description[:50]}...\n\n"
    bot.send_message(message.chat.id, orders_text)

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.text == "✏️ تعديل طلب")
def edit_orde
