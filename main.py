# ============================================================
# 🎓 نظام الخدمات الطلابية الجامعية السعودية
# 📌 الإصدار: 4.0 المتكامل | python-telegram-bot v21+
# ✅ شامل جميع التخصصات والكليات والمواد الجامعية السعودية
# ============================================================

import json, os, random, datetime, asyncio, re
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
# ⚙️  الإعدادات الأساسية
# ══════════════════════════════════════════════
TOKEN    = "8305933964:AAFIk27x"
ADMIN_ID = 5707994417
ADMINS   = {ADMIN_ID}

DB_FILE       = "db.json"
USERS_FILE    = "users.json"
SETTINGS_FILE = "settings.json"

# ══════════════════════════════════════════════
# 🏛️  قاعدة بيانات التخصصات الجامعية السعودية
# ══════════════════════════════════════════════
SAUDI_UNIVERSITIES = {
    "جامعة الملك سعود": "🏛",
    "جامعة الملك عبدالعزيز": "🏛",
    "جامعة الملك فهد للبترول والمعادن": "⚙️",
    "جامعة الملك فيصل": "🏛",
    "جامعة أم القرى": "🕌",
    "جامعة الملك خالد": "🏛",
    "جامعة القصيم": "🏛",
    "جامعة الإمام محمد بن سعود": "📚",
    "جامعة طيبة": "🏛",
    "جامعة الطائف": "🏛",
    "جامعة حائل": "🏛",
    "جامعة جازان": "🏛",
    "جامعة نجران": "🏛",
    "جامعة الجوف": "🏛",
    "جامعة تبوك": "🏛",
    "جامعة الباحة": "🏛",
    "جامعة الحدود الشمالية": "🏛",
    "جامعة شقراء": "🏛",
    "جامعة المجمعة": "🏛",
    "جامعة الأمير سطام": "🏛",
    "جامعة بيشة": "🏛",
    "جامعة جدة": "🏛",
    "جامعة الأمير محمد بن فهد": "🏛",
    "جامعة الإمام عبدالرحمن بن فيصل": "🏛",
    "الجامعة الإسلامية": "🕌",
    "جامعة الملك عبدالله": "🔬",
    "جامعة الأميرة نورة": "👩‍🎓",
    "جامعة سعود الصحية": "🏥",
    "جامعة الأمير سلطان": "🏛",
    "جامعة دار العلوم": "📚",
    "أخرى": "🏫",
}

# ─────────────────────────────────────────────
# 🎓 الكليات والتخصصات والمواد الكاملة
# ─────────────────────────────────────────────
COLLEGES_DATA = {
    "كلية الطب": {
        "emoji": "🏥",
        "majors": ["طب بشري"],
        "levels": ["المستوى الأول", "المستوى الثاني", "المستوى الثالث",
                   "المستوى الرابع", "المستوى الخامس", "المستوى السادس",
                   "السنة التحضيرية"],
        "subjects": {
            "السنة التحضيرية": [
                "كيمياء عامة", "أحياء عامة", "فيزياء طبية",
                "رياضيات", "إنجليزي طبي", "مهارات الدراسة الجامعية"
            ],
            "المستوى الأول": [
                "تشريح 1", "فسيولوجيا 1", "كيمياء حيوية 1",
                "نسيجية وأجنّة", "مهارات التواصل الطبي", "ثقافة إسلامية"
            ],
            "المستوى الثاني": [
                "تشريح 2", "فسيولوجيا 2", "كيمياء حيوية 2",
                "علم الأحياء الدقيقة 1", "علم الأمراض العام", "الأخلاقيات الطبية"
            ],
            "المستوى الثالث": [
                "علم الأحياء الدقيقة 2", "علم الأمراض الخاص", "علم العقاقير 1",
                "طب المجتمع", "الطب الشرعي", "علم المناعة"
            ],
            "المستوى الرابع": [
                "الجراحة العامة", "الباطنة العامة", "طب الأطفال",
                "النساء والولادة", "الطوارئ الطبية", "علم العقاقير 2"
            ],
            "المستوى الخامس": [
                "العيون", "الأنف والأذن والحنجرة", "الجلدية",
                "الأمراض النفسية", "العظام", "طب المجتمع المتقدم"
            ],
            "المستوى السادس": [
                "الطب الداخلي المتقدم", "الجراحة المتقدمة", "طب الأطفال المتقدم",
                "التوليد المتقدم", "مشروع التخرج", "الامتياز"
            ],
        }
    },
    "كلية طب الأسنان": {
        "emoji": "🦷",
        "majors": ["طب أسنان"],
        "levels": ["السنة التحضيرية", "المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع", "المستوى الخامس"],
        "subjects": {
            "السنة التحضيرية": [
                "كيمياء عامة", "أحياء عامة", "فيزياء", "إنجليزي", "رياضيات"
            ],
            "المستوى الأول": [
                "تشريح الرأس والرقبة", "علم الأنسجة الفموية", "الكيمياء الحيوية",
                "الفسيولوجيا", "مقدمة في طب الأسنان"
            ],
            "المستوى الثاني": [
                "تشريح الأسنان", "مواد طب الأسنان", "علم الأمراض الفموية",
                "الأحياء الدقيقة الفموية", "صحة الفم والأسنان"
            ],
            "المستوى الثالث": [
                "علاج جذور الأسنان", "طب أسنان الأطفال", "جراحة الفم والوجه والفكين",
                "تقويم الأسنان", "أمراض اللثة", "الأشعة الفموية"
            ],
            "المستوى الرابع": [
                "التعويضات السنية الثابتة", "التعويضات السنية المتحركة",
                "طب المجتمع وصحة الأسنان", "تجميل الأسنان",
                "إدارة عيادة أسنان"
            ],
            "المستوى الخامس": [
                "التدريب السريري الشامل", "مشروع التخرج",
                "جراحة الأسنان المتقدمة", "زراعة الأسنان"
            ],
        }
    },
    "كلية الصيدلة": {
        "emoji": "💊",
        "majors": ["صيدلة"],
        "levels": ["السنة التحضيرية", "المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع", "المستوى الخامس"],
        "subjects": {
            "السنة التحضيرية": [
                "كيمياء عامة", "أحياء عامة", "فيزياء", "رياضيات", "إنجليزي"
            ],
            "المستوى الأول": [
                "الكيمياء العضوية", "التشريح وعلم وظائف الأعضاء",
                "علم الخلية والأحياء الجزيئية", "مقدمة في الصيدلة"
            ],
            "المستوى الثاني": [
                "الكيمياء التحليلية", "الكيمياء الحيوية الصيدلانية",
                "التحليل الدوائي", "الأحياء الدقيقة"
            ],
            "المستوى الثالث": [
                "علم الصيدلانيات 1", "الكيمياء الدوائية 1",
                "الديناميكية الدوائية", "الحرائك الدوائية"
            ],
            "المستوى الرابع": [
                "علم الصيدلانيات 2", "الكيمياء الدوائية 2",
                "الصيدلة الإكلينيكية 1", "علم السموم", "تقنية الأدوية"
            ],
            "المستوى الخامس": [
                "الصيدلة الإكلينيكية 2", "صيدلة المجتمع",
                "التدريب الميداني الصيدلاني", "مشروع التخرج",
                "إدارة الصيدلية"
            ],
        }
    },
    "كلية التمريض": {
        "emoji": "👨‍⚕️",
        "majors": ["تمريض"],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "مبادئ التمريض", "تشريح وفسيولوجيا", "الكيمياء الحيوية",
                "مهارات التواصل", "الثقافة الإسلامية", "اللغة الإنجليزية"
            ],
            "المستوى الثاني": [
                "تمريض الباطنة والجراحة", "الأحياء الدقيقة",
                "الصحة النفسية", "علم الأدوية", "تمريض الأمومة"
            ],
            "المستوى الثالث": [
                "تمريض الأطفال", "تمريض الطوارئ والعناية المركزة",
                "تمريض المجتمع", "تمريض الصحة النفسية المتقدم",
                "البحث التمريضي"
            ],
            "المستوى الرابع": [
                "الإدارة التمريضية", "التدريب الميداني الشامل",
                "مشروع التخرج", "تمريض المسنين", "القيادة في التمريض"
            ],
        }
    },
    "كلية العلوم الصحية والطبية": {
        "emoji": "🔬",
        "majors": [
            "علم المختبرات الطبية", "الأشعة التشخيصية",
            "العلاج الطبيعي", "العلاج الوظيفي",
            "علم التغذية والتغذية العلاجية", "الصحة العامة",
            "التقنية الطبية الحيوية"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "تشريح وفسيولوجيا 1", "الكيمياء العامة", "الأحياء العامة",
                "مقدمة في العلوم الصحية", "اللغة الإنجليزية", "ثقافة إسلامية"
            ],
            "المستوى الثاني": [
                "تشريح وفسيولوجيا 2", "الأحياء الدقيقة", "الكيمياء الحيوية",
                "علم الأمراض العام", "مناعة", "إحصاء حيوي"
            ],
            "المستوى الثالث": [
                "كيمياء سريرية", "هيماتولوجيا", "بنك الدم",
                "علم الإشعاع التشخيصي", "فيزياء طبية", "أخلاقيات الرعاية الصحية"
            ],
            "المستوى الرابع": [
                "التدريب الميداني", "مشروع البحث", "إدارة الجودة الصحية",
                "الصحة المهنية", "نظم المعلومات الصحية"
            ],
        }
    },
    "كلية الهندسة": {
        "emoji": "⚙️",
        "majors": [
            "الهندسة المدنية", "الهندسة الكهربائية",
            "الهندسة الميكانيكية", "الهندسة الكيميائية",
            "هندسة البترول", "هندسة المعادن والمواد",
            "الهندسة الصناعية", "هندسة الطيران",
            "هندسة البيئة", "هندسة نظم الطاقة",
            "هندسة الاتصالات", "الهندسة المعمارية"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني", "المستوى الثالث",
                   "المستوى الرابع", "المستوى الخامس", "السنة التحضيرية"],
        "subjects": {
            "السنة التحضيرية": [
                "رياضيات تحضيري", "فيزياء تحضيري", "كيمياء تحضيري",
                "إنجليزي تحضيري", "حاسب آلي مقدمة", "مهارات الاتصال"
            ],
            "المستوى الأول": [
                "تفاضل وتكامل 1", "الفيزياء الهندسية 1", "رسم هندسي",
                "برمجة حاسب", "استاتيكا", "مواد هندسية"
            ],
            "المستوى الثاني": [
                "تفاضل وتكامل 2", "الفيزياء الهندسية 2", "ديناميكا",
                "مقاومة المواد", "معادلات تفاضلية", "كيمياء هندسية"
            ],
            "المستوى الثالث": [
                "ميكانيكا الموائع", "نقل الحرارة", "آلات كهربائية",
                "دوائر كهربائية", "الاحتمالات والإحصاء", "اقتصاديات هندسية"
            ],
            "المستوى الرابع": [
                "تصميم المنشآت", "هندسة الجودة", "أنظمة التحكم",
                "التصميم الهندسي", "بحوث العمليات", "مشروع التخرج 1"
            ],
            "المستوى الخامس": [
                "مشروع التخرج 2", "التدريب الميداني", "إدارة المشاريع",
                "أخلاقيات الهندسة", "الهندسة والمجتمع"
            ],
        }
    },
    "كلية علوم الحاسب وتقنية المعلومات": {
        "emoji": "💻",
        "majors": [
            "علوم الحاسب", "هندسة البرمجيات",
            "نظم المعلومات", "أمن المعلومات",
            "الذكاء الاصطناعي", "علوم البيانات",
            "الحوسبة السحابية", "هندسة الحاسب",
            "تقنية المعلومات", "الأمن السيبراني"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني", "المستوى الثالث",
                   "المستوى الرابع", "السنة التحضيرية"],
        "subjects": {
            "السنة التحضيرية": [
                "رياضيات", "إنجليزي", "مقدمة في الحاسب",
                "فيزياء", "مهارات الاتصال والتقديم"
            ],
            "المستوى الأول": [
                "مقدمة في البرمجة (Python)", "رياضيات منفصلة",
                "تفاضل وتكامل", "هياكل البيانات المنطقية",
                "مقدمة في نظم المعلومات", "ثقافة إسلامية"
            ],
            "المستوى الثاني": [
                "هياكل البيانات والخوارزميات", "قواعد البيانات",
                "البرمجة كائنية التوجه (Java/C++)",
                "معمارية الحاسب", "نظرية الحوسبة",
                "احتمالات وإحصاء"
            ],
            "المستوى الثالث": [
                "نظم التشغيل", "شبكات الحاسب",
                "هندسة البرمجيات", "الذكاء الاصطناعي",
                "أمن المعلومات والشبكات", "قواعد البيانات المتقدمة"
            ],
            "المستوى الرابع": [
                "تعلم الآلة", "معالجة اللغات الطبيعية",
                "تطوير تطبيقات الويب", "تطوير تطبيقات الجوال",
                "الحوسبة السحابية", "مشروع التخرج",
                "أخلاقيات تقنية المعلومات", "التدريب الميداني"
            ],
        }
    },
    "كلية إدارة الأعمال": {
        "emoji": "📊",
        "majors": [
            "إدارة الأعمال", "المحاسبة",
            "التسويق", "إدارة الموارد البشرية",
            "المالية والاستثمار", "إدارة المشاريع",
            "الاقتصاد", "إدارة سلسلة الإمداد",
            "ريادة الأعمال", "التجارة الإلكترونية",
            "نظم المعلومات الإدارية"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "مبادئ الإدارة", "مبادئ المحاسبة 1",
                "مبادئ الاقتصاد الجزئي", "رياضيات الأعمال",
                "إنجليزي الأعمال", "مهارات الاتصال"
            ],
            "المستوى الثاني": [
                "مبادئ المحاسبة 2", "مبادئ الاقتصاد الكلي",
                "مبادئ التسويق", "إحصاء الأعمال",
                "قانون الأعمال", "الحاسب في الأعمال"
            ],
            "المستوى الثالث": [
                "إدارة الموارد البشرية", "إدارة العمليات",
                "الإدارة المالية", "سلوك المستهلك",
                "إدارة الجودة الشاملة", "نظم المعلومات الإدارية"
            ],
            "المستوى الرابع": [
                "الإدارة الاستراتيجية", "ريادة الأعمال",
                "التخطيط الضريبي", "التحليل المالي",
                "مشروع التخرج", "التدريب الميداني",
                "الأعمال الدولية"
            ],
        }
    },
    "كلية العلوم": {
        "emoji": "🔭",
        "majors": [
            "الرياضيات", "الفيزياء",
            "الكيمياء", "الأحياء",
            "علوم الأرض والبيئة", "الإحصاء",
            "علوم الفضاء والفلك", "الكيمياء الحيوية",
            "علم الجيولوجيا"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "تفاضل وتكامل 1", "فيزياء عامة 1",
                "كيمياء عامة 1", "أحياء عامة",
                "إنجليزي", "ثقافة إسلامية", "مهارات جامعية"
            ],
            "المستوى الثاني": [
                "تفاضل وتكامل 2", "فيزياء عامة 2",
                "كيمياء عامة 2", "الكيمياء العضوية 1",
                "الرياضيات المنفصلة", "الإحصاء الحيوي"
            ],
            "المستوى الثالث": [
                "الجبر الخطي", "المعادلات التفاضلية",
                "الكيمياء العضوية 2", "علم الوراثة",
                "الفيزياء الحديثة", "الكيمياء الحيوية"
            ],
            "المستوى الرابع": [
                "مشروع البحث العلمي", "التدريب الميداني",
                "الكيمياء التحليلية المتقدمة", "علم الأحياء الجزيئي",
                "الميكانيكا الكمية", "نظرية المجموعات"
            ],
        }
    },
    "كلية التربية والآداب": {
        "emoji": "📚",
        "majors": [
            "اللغة العربية وآدابها", "اللغة الإنجليزية وآدابها",
            "التاريخ والحضارة", "الجغرافيا",
            "علم الاجتماع", "علم النفس",
            "التربية الخاصة", "رياض الأطفال",
            "التربية البدنية", "الخدمة الاجتماعية",
            "الفلسفة والعلوم الإنسانية",
            "تربية إسلامية", "اللغة الفرنسية"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "مهارات اللغة العربية", "مهارات اللغة الإنجليزية",
                "مقدمة في علم النفس", "مقدمة في علم الاجتماع",
                "التاريخ الإسلامي", "الثقافة الإسلامية"
            ],
            "المستوى الثاني": [
                "النحو والصرف", "علم الدلالة",
                "نظريات التعلم", "طرق التدريس",
                "علم النفس التربوي", "المناهج وطرق التدريس"
            ],
            "المستوى الثالث": [
                "الأدب العربي الحديث", "البلاغة العربية",
                "الإرشاد والتوجيه النفسي", "قياس وتقويم",
                "التخطيط التربوي", "الإدارة التربوية"
            ],
            "المستوى الرابع": [
                "مشروع التخرج", "التدريب الميداني (التربية العملية)",
                "البحث العلمي في التربية", "قضايا تربوية معاصرة"
            ],
        }
    },
    "كلية الشريعة والدراسات الإسلامية": {
        "emoji": "🕌",
        "majors": [
            "الشريعة الإسلامية", "أصول الدين",
            "الدراسات الإسلامية", "الفقه وأصوله",
            "القرآن الكريم وعلومه", "الحديث الشريف"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "القرآن الكريم (تلاوة وتجويد)", "علوم القرآن",
                "الفقه العبادات", "العقيدة الإسلامية",
                "النحو والصرف", "السيرة النبوية"
            ],
            "المستوى الثاني": [
                "الحديث وعلومه", "أصول الفقه 1",
                "الفقه المعاملات", "التفسير وعلومه",
                "تاريخ الفقه الإسلامي", "اللغة الإنجليزية"
            ],
            "المستوى الثالث": [
                "أصول الفقه 2", "الفقه الجنائي",
                "القضاء والتقاضي", "فقه الأسرة",
                "المقارنة في الأديان", "المذاهب الفقهية"
            ],
            "المستوى الرابع": [
                "الاجتهاد والفتوى", "فقه الأقليات",
                "الاقتصاد الإسلامي", "مشروع التخرج",
                "التدريب الميداني"
            ],
        }
    },
    "كلية القانون والأنظمة": {
        "emoji": "⚖️",
        "majors": [
            "النظام (القانون)", "الأنظمة والقانون التجاري",
            "القانون الدولي", "قانون الأعمال"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "مقدمة في علم القانون", "النظام الدستوري",
                "الفقه الإسلامي", "اللغة الإنجليزية القانونية",
                "علم الاجتماع القانوني"
            ],
            "المستوى الثاني": [
                "نظام العقود", "نظام الشركات",
                "القانون الجنائي", "نظام الإجراءات الجزائية",
                "القانون الدولي العام"
            ],
            "المستوى الثالث": [
                "نظام العمل والعمال", "نظام الأحوال الشخصية",
                "التحكيم التجاري", "القانون الإداري",
                "نظام الملكية الفكرية"
            ],
            "المستوى الرابع": [
                "نظام الأوراق التجارية", "نظام الإفلاس",
                "الدراسات القانونية المقارنة",
                "مشروع التخرج", "التدريب الميداني"
            ],
        }
    },
    "كلية الاقتصاد والعلوم السياسية": {
        "emoji": "🌐",
        "majors": [
            "الاقتصاد", "العلوم السياسية",
            "العلاقات الدولية", "الإدارة العامة"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "مبادئ الاقتصاد الجزئي", "مبادئ العلوم السياسية",
                "تاريخ الفكر الاقتصادي", "الرياضيات الاقتصادية",
                "مقدمة في العلاقات الدولية"
            ],
            "المستوى الثاني": [
                "مبادئ الاقتصاد الكلي", "النظرية السياسية",
                "الاقتصاد الدولي", "الإحصاء الاقتصادي",
                "حكومات ودول مقارنة"
            ],
            "المستوى الثالث": [
                "اقتصاديات التنمية", "نظرية العلاقات الدولية",
                "السياسة المالية والنقدية", "التكامل الاقتصادي الإقليمي",
                "القانون الدولي"
            ],
            "المستوى الرابع": [
                "اقتصاد التخرج", "السياسة الخارجية السعودية",
                "المنظمات الدولية", "مشروع التخرج",
                "التدريب الميداني"
            ],
        }
    },
    "كلية الفنون والتصميم": {
        "emoji": "🎨",
        "majors": [
            "التصميم الجرافيكي", "التصميم الداخلي",
            "الفنون البصرية", "تصميم الأزياء",
            "الإعلام الرقمي وتقنية المعلومات",
            "تصميم المنتجات", "التصوير الفوتوغرافي"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "أسس الفنون البصرية", "رسم وتصوير أساسي",
                "نظرية الألوان", "مقدمة في التصميم",
                "تاريخ الفن", "فوتوشوب ومهارات رقمية"
            ],
            "المستوى الثاني": [
                "تصميم الهوية البصرية", "طباعة وإخراج فني",
                "الرسوم المتحركة الثنائية الأبعاد",
                "تصميم الويب", "التصوير الفوتوغرافي"
            ],
            "المستوى الثالث": [
                "تصميم الرسوم المتحركة ثلاثية الأبعاد",
                "تصميم تجربة المستخدم (UX/UI)",
                "التسويق الإبداعي",
                "إنتاج الوسائط المتعددة"
            ],
            "المستوى الرابع": [
                "مشروع التخرج التصميمي", "التدريب المهني",
                "إدارة مشاريع التصميم", "معرض الأعمال"
            ],
        }
    },
    "كلية الإعلام والاتصال": {
        "emoji": "📺",
        "majors": [
            "الصحافة والإعلام الرقمي", "العلاقات العامة",
            "الإذاعة والتلفزيون", "الإنتاج الإعلامي",
            "الاتصال الجماهيري", "الإعلام الاجتماعي"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "مقدمة في الإعلام والاتصال", "الكتابة الصحفية",
                "مبادئ العلاقات العامة", "اللغة العربية الإعلامية",
                "الإعلام الرقمي"
            ],
            "المستوى الثاني": [
                "الصحافة المكتوبة والإلكترونية", "فن التحرير الإذاعي والتلفزيوني",
                "التصوير الصحفي", "الإعلام الدولي",
                "قانون وأخلاقيات الإعلام"
            ],
            "المستوى الثالث": [
                "الإنتاج الإذاعي والتلفزيوني", "التسويق الإعلامي",
                "وسائل التواصل الاجتماعي", "الإعلام والمجتمع",
                "إدارة الأزمات الإعلامية"
            ],
            "المستوى الرابع": [
                "مشروع التخرج الإعلامي", "التدريب الميداني",
                "الصحافة الاستقصائية",
                "مستقبل الإعلام وتحولاته الرقمية"
            ],
        }
    },
    "كلية الزراعة والبيطرة": {
        "emoji": "🌾",
        "majors": [
            "الإنتاج الحيواني", "وقاية النبات",
            "الإنتاج النباتي", "الطب البيطري",
            "الاقتصاد الزراعي", "علوم التقنية الحيوية الزراعية",
            "الأحياء الدقيقة الزراعية"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "مقدمة في العلوم الزراعية", "الكيمياء الزراعية",
                "الأحياء الزراعية", "التربة والمياه",
                "إنجليزي", "ثقافة إسلامية"
            ],
            "المستوى الثاني": [
                "إنتاج المحاصيل", "الوراثة والتربية",
                "فسيولوجيا الحيوان", "الاقتصاد الزراعي",
                "أمراض النبات", "الحشرات الزراعية"
            ],
            "المستوى الثالث": [
                "تغذية الحيوان", "الإنتاج الداجني",
                "هندسة الري والصرف", "الأمراض البيطرية",
                "تكنولوجيا الأغذية"
            ],
            "المستوى الرابع": [
                "الزراعة المائية والمحمية", "الإرشاد الزراعي",
                "مشروع التخرج", "التدريب الميداني",
                "الاقتصاد الريفي وإدارة المزارع"
            ],
        }
    },
    "كلية السياحة والضيافة": {
        "emoji": "✈️",
        "majors": [
            "إدارة الفنادق والمطاعم", "السياحة والسفر",
            "الترفيه وإدارة الفعاليات",
            "الطيران التجاري وخدماته"
        ],
        "levels": ["المستوى الأول", "المستوى الثاني",
                   "المستوى الثالث", "المستوى الرابع"],
        "subjects": {
            "المستوى الأول": [
                "مقدمة في صناعة الضيافة والسياحة",
                "جغرافية السياحة", "اللغة الإنجليزية للسياحة",
                "مبادئ الإدارة الفندقية"
            ],
            "المستوى الثاني": [
                "إدارة الغرف", "إدارة الطعام والشراب",
                "اتجاهات السياحة الدولية",
                "سلوك المستهلك السياحي", "التسويق السياحي"
            ],
            "المستوى الثالث": [
                "إدارة الفعاليات والمؤتمرات",
                "الاستدامة في السياحة", "قانون السياحة",
                "إدارة المطارات"
            ],
            "المستوى الرابع": [
                "مشروع التخرج السياحي", "التدريب الميداني",
                "إدارة المنتجعات السياحية",
                "مستقبل السياحة في رؤية 2030"
            ],
        }
    },
}

# ══════════════════════════════════════════════
# 🗄️  قاعدة البيانات
# ══════════════════════════════════════════════
def _load(path: str, default=None):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}

def _save(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db       = _load(DB_FILE, {})
users    = _load(USERS_FILE, {})
settings = _load(SETTINGS_FILE, {
    "services": {
        "بحث علمي":        {"price": "80-200",  "currency": "ريال", "emoji": "🔬", "time": "3-5 أيام",    "active": True},
        "مشروع تخرج":     {"price": "300-800", "currency": "ريال", "emoji": "🎓", "time": "7-21 يوم",    "active": True},
        "عرض تقديمي":     {"price": "50-150",  "currency": "ريال", "emoji": "📊", "time": "1-3 أيام",    "active": True},
        "تلخيص":           {"price": "30-80",   "currency": "ريال", "emoji": "📝", "time": "12-24 ساعة", "active": True},
        "ترجمة":           {"price": "20-60",   "currency": "ريال", "emoji": "🌐", "time": "12-48 ساعة", "active": True},
        "حل واجبات":       {"price": "20-100",  "currency": "ريال", "emoji": "✏️", "time": "6-24 ساعة",  "active": True},
        "تقرير أكاديمي":   {"price": "60-150",  "currency": "ريال", "emoji": "📋", "time": "2-4 أيام",   "active": True},
        "سكاليف":          {"price": "50-200",  "currency": "ريال", "emoji": "📄", "time": "1-3 أيام",   "active": True},
        "أعذار طبية":      {"price": "30-100",  "currency": "ريال", "emoji": "🏥", "time": "12-24 ساعة", "active": True},
        "حل اختبارات":     {"price": "50-300",  "currency": "ريال", "emoji": "📝", "time": "حسب الموعد", "active": True},
        "كويزات ومهام":    {"price": "20-80",   "currency": "ريال", "emoji": "✅", "time": "6-12 ساعة",  "active": True},
    },
    "payment_methods": [
        "🏦 تحويل بنكي - رقم الآيبان: SA00 0000 0000 0000 0000 0000",
        "📱 STC Pay - 05XXXXXXXX",
        "💳 مدى / Apple Pay",
    ],
    "contact":     "📞 واتساب: 05XXXXXXXX\n📧 البريد: service@example.com",
    "welcome_msg": "مرحباً بك في نظام الخدمات الطلابية الاحترافي! 🎓",
    "bot_active":  True,
    "prices_editable": True,
})

def save_all():
    _save(DB_FILE,       db)
    _save(USERS_FILE,    users)
    _save(SETTINGS_FILE, settings)

# ══════════════════════════════════════════════
# 🆔  مساعدات عامة
# ══════════════════════════════════════════════
def gen_order_id() -> str:
    return "ORD-" + str(random.randint(100000, 999999))

def now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def get_active_services() -> dict:
    return {k: v for k, v in settings["services"].items() if v.get("active", True)}

def is_banned(uid: int) -> bool:
    return users.get(str(uid), {}).get("banned", False)

# ══════════════════════════════════════════════
# 📌  مراحل ConversationHandler
# ══════════════════════════════════════════════
(
    ASK_NAME,           # 0
    ASK_UNIVERSITY,     # 1
    ASK_COLLEGE,        # 2
    ASK_MAJOR,          # 3
    ASK_LEVEL,          # 4
    ASK_SUBJECT,        # 5
    ASK_SERVICE,        # 6
    ASK_DETAILS,        # 7
    ASK_DEADLINE,       # 8
    CONFIRM_ORDER,      # 9
    AWAIT_PAYMENT,      # 10
    # Admin states
    ADM_EDIT_PRICE,     # 11
    ADM_EDIT_TIME,      # 12
    ADM_BROADCAST,      # 13
    ADM_MSG_USER,       # 14
    ADM_MSG_ORDER,      # 15
    ADM_ADD_SVC_NAME,   # 16
    ADM_ADD_SVC_PRICE,  # 17
    ADM_ADD_SVC_TIME,   # 18
    ADM_ADD_SVC_EMOJI,  # 19
    ADM_EDIT_WELCOME,   # 20
    ADM_EDIT_CONTACT,   # 21
    ADM_EDIT_PAYMENT,   # 22
) = range(23)

# ══════════════════════════════════════════════
# 🎛️  لوحات المفاتيح - المستخدم
# ══════════════════════════════════════════════
def main_menu_kb(uid: int) -> ReplyKeyboardMarkup:
    kb = [
        ["📚 الخدمات",     "💰 الأسعار"],
        ["📝 طلب جديد",    "📦 طلباتي"],
        ["💳 الدفع",        "📞 تواصل معنا"],
        ["🏛️ الكليات والتخصصات", "ℹ️ عن البوت"],
    ]
    if uid in ADMINS:
        kb.append(["🛠 لوحة التحكم"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def universities_kb(page: int = 0) -> InlineKeyboardMarkup:
    items = list(SAUDI_UNIVERSITIES.items())
    per   = 8
    start = page * per
    chunk = items[start: start + per]
    rows  = []
    row   = []
    for i, (name, em) in enumerate(chunk):
        row.append(InlineKeyboardButton(f"{em} {name}", callback_data=f"uni_{name}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ السابق", callback_data=f"uni_page_{page-1}"))
    if start + per < len(items):
        nav.append(InlineKeyboardButton("التالي ▶️", callback_data=f"uni_page_{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("✍️ اكتب جامعتك", callback_data="uni_custom")])
    rows.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_order")])
    return InlineKeyboardMarkup(rows)

def colleges_kb() -> InlineKeyboardMarkup:
    items = list(COLLEGES_DATA.items())
    rows  = []
    row   = []
    for i, (name, info) in enumerate(items):
        row.append(InlineKeyboardButton(
            f"{info['emoji']} {name}", callback_data=f"col_{name}"
        ))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("✍️ اكتب كليتك", callback_data="col_custom")])
    rows.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_order")])
    return InlineKeyboardMarkup(rows)

def majors_kb(college: str) -> InlineKeyboardMarkup:
    majors = COLLEGES_DATA.get(college, {}).get("majors", [])
    rows   = []
    row    = []
    for i, major in enumerate(majors):
        row.append(InlineKeyboardButton(major, callback_data=f"maj_{major}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("✍️ اكتب تخصصك", callback_data="maj_custom")])
    rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_colleges"),
                 InlineKeyboardButton("❌ إلغاء", callback_data="cancel_order")])
    return InlineKeyboardMarkup(rows)

def levels_kb(college: str) -> InlineKeyboardMarkup:
    levels = COLLEGES_DATA.get(college, {}).get("levels", [
        "المستوى الأول", "المستوى الثاني", "المستوى الثالث",
        "المستوى الرابع", "المستوى الخامس", "المستوى السادس",
        "السنة التحضيرية"
    ])
    rows = []
    row  = []
    for lvl in levels:
        row.append(InlineKeyboardButton(lvl, callback_data=f"lvl_{lvl}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_order")])
    return InlineKeyboardMarkup(rows)

def subjects_kb(college: str, level: str) -> InlineKeyboardMarkup:
    subs = (COLLEGES_DATA.get(college, {})
            .get("subjects", {})
            .get(level, []))
    rows = []
    row  = []
    for i, sub in enumerate(subs):
        row.append(InlineKeyboardButton(sub, callback_data=f"sub_{sub}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("✍️ اكتب المادة", callback_data="sub_custom")])
    rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_levels"),
                 InlineKeyboardButton("❌ إلغاء", callback_data="cancel_order")])
    return InlineKeyboardMarkup(rows)

def services_kb() -> InlineKeyboardMarkup:
    svcs = get_active_services()
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
    rows.append([InlineKeyboardButton("📝 اطلب الآن", callback_data="start_order")])
    return InlineKeyboardMarkup(rows)

def service_select_kb() -> InlineKeyboardMarkup:
    svcs = get_active_services()
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

def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تأكيد الإرسال", callback_data="confirm_yes"),
         InlineKeyboardButton("✏️ تعديل",          callback_data="confirm_edit")],
        [InlineKeyboardButton("❌ إلغاء",           callback_data="cancel_order")],
    ])

def payment_kb(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ أرسلت الدفع",   callback_data=f"paid_{order_id}"),
         InlineKeyboardButton("⏰ لاحقاً",          callback_data=f"paylater_{order_id}")],
        [InlineKeyboardButton("❌ إلغاء الطلب",   callback_data=f"paycancel_{order_id}")],
    ])

def my_orders_kb(uid: int) -> InlineKeyboardMarkup | None:
    my = [(k, v) for k, v in db.items() if v["user"] == uid]
    if not my:
        return None
    rows = []
    for oid, o in sorted(my, key=lambda x: x[1].get("date", ""), reverse=True)[:10]:
        icon = {"جديد":"🆕","قيد التنفيذ":"🔄","منجز":"✅","معلّق":"⏸","ملغي":"❌"}.get(o["status"],"📌")
        rows.append([InlineKeyboardButton(
            f"{icon} {oid} | {o.get('service','—')} | {o.get('status','—')}",
            callback_data=f"myorder_{oid}"
        )])
    return InlineKeyboardMarkup(rows)

def order_detail_user_kb(oid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 تحديث الحالة",   callback_data=f"refresh_{oid}"),
         InlineKeyboardButton("🔙 رجوع لطلباتي",  callback_data="back_myorders")],
        [InlineKeyboardButton("💬 تواصل مع الدعم", callback_data="contact_support")],
    ])

# ══════════════════════════════════════════════
# 🛠  لوحات مفاتيح الأدمن
# ══════════════════════════════════════════════
def admin_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 الطلبات الجديدة",   callback_data="adm_orders_new"),
         InlineKeyboardButton("🔄 قيد التنفيذ",        callback_data="adm_orders_progress")],
        [InlineKeyboardButton("✅ المنجزة",             callback_data="adm_orders_done"),
         InlineKeyboardButton("❌ الملغاة",             callback_data="adm_orders_cancelled")],
        [InlineKeyboardButton("⏸ المعلّقة",            callback_data="adm_orders_pending"),
         InlineKeyboardButton("📋 جميع الطلبات",       callback_data="adm_orders_all")],
        [InlineKeyboardButton("👥 إدارة المستخدمين",  callback_data="adm_users"),
         InlineKeyboardButton("📊 الإحصائيات",         callback_data="adm_stats")],
        [InlineKeyboardButton("💰 الأسعار والخدمات",  callback_data="adm_services"),
         InlineKeyboardButton("⚙️ إعدادات البوت",      callback_data="adm_settings")],
        [InlineKeyboardButton("📣 إشعار جماعي",        callback_data="adm_broadcast"),
         InlineKeyboardButton("🔒 تشغيل/إيقاف",        callback_data="adm_toggle_bot")],
    ])

def admin_services_kb() -> InlineKeyboardMarkup:
    svcs = settings["services"]
    rows = []
    for name, info in svcs.items():
        status = "✅" if info.get("active", True) else "❌"
        rows.append([
            InlineKeyboardButton(
                f"{info['emoji']} {name} | {info['price']} {info.get('currency','ريال')}",
                callback_data=f"adm_svc_view_{name}"
            ),
            InlineKeyboardButton(status, callback_data=f"adm_svc_toggle_{name}"),
        ])
    rows.append([
        InlineKeyboardButton("➕ إضافة خدمة جديدة", callback_data="adm_svc_add"),
    ])
    rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="adm_main")])
    return InlineKeyboardMarkup(rows)

def admin_svc_edit_kb(svc_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ تعديل السعر", callback_data=f"adm_edit_price_{svc_name}"),
         InlineKeyboardButton("⏱ تعديل المدة", callback_data=f"adm_edit_time_{svc_name}")],
        [InlineKeyboardButton("🗑️ حذف الخدمة",  callback_data=f"adm_svc_del_{svc_name}"),
         InlineKeyboardButton("🔙 رجوع",          callback_data="adm_services")],
    ])

def order_actions_kb(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 قيد التنفيذ",  callback_data=f"st_{order_id}_قيد التنفيذ"),
         InlineKeyboardButton("✅ منجز",           callback_data=f"st_{order_id}_منجز")],
        [InlineKeyboardButton("⏸ معلّق",          callback_data=f"st_{order_id}_معلّق"),
         InlineKeyboardButton("❌ ملغي",           callback_data=f"st_{order_id}_ملغي")],
        [InlineKeyboardButton("💬 مراسلة العميل", callback_data=f"msg_{order_id}"),
         InlineKeyboardButton("🗑️ حذف الطلب",     callback_data=f"del_{order_id}")],
        [InlineKeyboardButton("🔙 رجوع",          callback_data="adm_main")],
    ])

def admin_settings_kb() -> InlineKeyboardMarkup:
    status = "🟢 مفعّل" if settings["bot_active"] else "🔴 موقوف"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ تعديل رسالة الترحيب", callback_data="adm_edit_welcome")],
        [InlineKeyboardButton("💳 تعديل طرق الدفع",      callback_data="adm_edit_payment")],
        [InlineKeyboardButton("📞 تعديل التواصل",         callback_data="adm_edit_contact")],
        [InlineKeyboardButton(f"البوت: {status}",         callback_data="adm_toggle_bot")],
        [InlineKeyboardButton("🔙 رجوع",                  callback_data="adm_main")],
    ])

def admin_user_kb(uid_str: str, is_banned: bool) -> InlineKeyboardMarkup:
    ban_btn = (
        InlineKeyboardButton("✅ رفع الحظر", callback_data=f"adm_unban_{uid_str}")
        if is_banned else
        InlineKeyboardButton("🚫 حظر",       callback_data=f"adm_ban_{uid_str}")
    )
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 مراسلته",  callback_data=f"adm_msguser_{uid_str}"),
         ban_btn],
        [InlineKeyboardButton("⏹ إيقاف مؤقت", callback_data=f"adm_suspend_{uid_str}"),
         InlineKeyboardButton("📦 طلباته",      callback_data=f"adm_userorders_{uid_str}")],
        [InlineKeyboardButton("🔙 رجوع",       callback_data="adm_users")],
    ])

# ══════════════════════════════════════════════
# 📊  نصوص الإحصاء وتفاصيل الطلب
# ══════════════════════════════════════════════
def get_stats() -> str:
    total   = len(db)
    new_    = sum(1 for v in db.values() if v["status"] == "جديد")
    prog    = sum(1 for v in db.values() if v["status"] == "قيد التنفيذ")
    done    = sum(1 for v in db.values() if v["status"] == "منجز")
    canc    = sum(1 for v in db.values() if v["status"] == "ملغي")
    pend    = sum(1 for v in db.values() if v["status"] == "معلّق")
    total_u = len(users)
    banned  = sum(1 for u in users.values() if u.get("banned", False))
    today   = datetime.date.today().strftime("%Y-%m-%d")
    today_o = sum(1 for v in db.values() if v.get("date", "").startswith(today))
    svc_count: dict = {}
    for v in db.values():
        svc_count[v.get("service", "—")] = svc_count.get(v.get("service", "—"), 0) + 1
    top_svc = max(svc_count, key=svc_count.get) if svc_count else "—"
    return (
        "📊 إحصائيات النظام\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 إجمالي الطلبات  : {total}\n"
        f"🆕 جديدة           : {new_}\n"
        f"🔄 قيد التنفيذ    : {prog}\n"
        f"✅ منجزة           : {done}\n"
        f"⏸ معلّقة          : {pend}\n"
        f"❌ ملغاة           : {canc}\n"
        f"📅 طلبات اليوم     : {today_o}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 المستخدمون      : {total_u}\n"
        f"🚫 المحظورون       : {banned}\n"
        f"🏆 أكثر خدمة       : {top_svc}\n"
        f"🕒 آخر تحديث       : {now_str()}"
    )

def order_text(oid: str, o: dict) -> str:
    icon = {"جديد":"🆕","قيد التنفيذ":"🔄","منجز":"✅","معلّق":"⏸","ملغي":"❌"}.get(o["status"],"📌")
    return (
        "🧾 تفاصيل الطلب\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 رقم الطلب   : {oid}\n"
        f"👤 الاسم       : {o.get('name','—')}\n"
        f"🏛 الجامعة    : {o.get('university','—')}\n"
        f"🏫 الكلية      : {o.get('college','—')}\n"
        f"🎓 التخصص     : {o.get('major','—')}\n"
        f"📶 المستوى    : {o.get('level','—')}\n"
        f"📖 المادة      : {o.get('subject','—')}\n"
        f"🛠 الخدمة     : {o.get('service','—')}\n"
        f"📝 التفاصيل   : {o.get('details','—')}\n"
        f"⏰ الموعد     : {o.get('deadline','—')}\n"
        f"📅 التاريخ    : {o.get('date','—')}\n"
        f"{icon} الحالة      : {o.get('status','—')}\n"
        f"💳 الدفع      : {o.get('payment','لم يُرسل بعد')}"
    )

# ══════════════════════════════════════════════
# 🚀  /start
# ══════════════════════════════════════════════
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.effective_user.first_name or "مستخدم"
    if str(uid) not in users:
        users[str(uid)] = {
            "name":     name,
            "username": update.effective_user.username or "",
            "joined":   now_str(),
            "orders":   0,
            "banned":   False,
            "suspended": False,
        }
        _save(USERS_FILE, users)
    if is_banned(uid):
        await update.message.reply_text("🚫 تم حظرك من استخدام البوت.")
        return
    if not settings["bot_active"] and uid not in ADMINS:
        await update.message.reply_text("⚠️ البوت متوقف مؤقتاً للصيانة. سنعود قريباً! 🔧")
        return
    await update.message.reply_text(
        f"السلام عليكم {name} 👋\n\n"
        f"{settings['welcome_msg']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎓 خدمات أكاديمية احترافية\n"
        "⚡ جودة عالية | تسليم في الوقت | دعم متواصل\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "اختر من القائمة أدناه 👇",
        reply_markup=main_menu_kb(uid)
    )

# ══════════════════════════════════════════════
# 📨  معالج القائمة الرئيسية
# ══════════════════════════════════════════════
async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid  = update.effective_user.id

    if is_banned(uid):
        await update.message.reply_text("🚫 تم حظرك من استخدام البوت.")
        return
    if not settings["bot_active"] and uid not in ADMINS:
        await update.message.reply_text("⚠️ البوت متوقف مؤقتاً للصيانة.")
        return

    if text == "📚 الخدمات":
        await update.message.reply_text(
            "📚 خدماتنا الأكاديمية\nاضغط على أي خدمة لمعرفة تفاصيلها:",
            reply_markup=services_kb()
        )

    elif text == "💰 الأسعار":
        svcs = get_active_services()
        msg  = "💰 قائمة الأسعار الكاملة\n━━━━━━━━━━━━━━━━━━━━\n"
        for name, info in svcs.items():
            msg += (
                f"{info['emoji']} {name}\n"
                f"   💵 السعر : {info['price']} {info.get('currency','ريال')}\n"
                f"   ⏱ المدة  : {info['time']}\n\n"
            )
        msg += "━━━━━━━━━━━━━━━━━━━━\n📝 للطلب اضغط 'طلب جديد'"
        await update.message.reply_text(msg)

    elif text == "💳 الدفع":
        methods = "\n".join(settings["payment_methods"])
        await update.message.reply_text(
            "💳 طرق الدفع المتاحة\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{methods}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📎 بعد الدفع أرسل صورة الإيصال لتأكيد طلبك"
        )

    elif text == "📞 تواصل معنا":
        await update.message.reply_text(
            "📞 تواصل معنا\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{settings['contact']}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🕐 أوقات العمل: 8ص - 12 منتصف الليل\n"
            "✅ نرد خلال 30 دقيقة"
        )

    elif text == "📦 طلباتي":
        my_kb = my_orders_kb(uid)
        if my_kb:
            my_list = [(k, v) for k, v in db.items() if v["user"] == uid]
            done_c  = sum(1 for _, v in my_list if v["status"] == "منجز")
            prog_c  = sum(1 for _, v in my_list if v["status"] == "قيد التنفيذ")
            await update.message.reply_text(
                f"📦 طلباتك ({len(my_list)} طلب)\n"
                f"✅ منجز: {done_c} | 🔄 جاري: {prog_c}\n"
                "━━━━━━━━━━━━━━━━━━━━\nاضغط على أي طلب لعرض تفاصيله:",
                reply_markup=my_kb
            )
        else:
            await update.message.reply_text(
                "📦 لا توجد طلبات بعد.\n💡 اضغط 'طلب جديد' لإنشاء أول طلب!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📝 طلب جديد الآن", callback_data="start_order")
                ]])
            )

    elif text == "🏛️ الكليات والتخصصات":
        msg = "🏛️ الكليات والتخصصات في الجامعات السعودية\n━━━━━━━━━━━━━━━━━━━━\n"
        for col, data in COLLEGES_DATA.items():
            majors_list = "، ".join(data["majors"][:3])
            more = f" و{len(data['majors'])-3} آخرون" if len(data["majors"]) > 3 else ""
            msg += f"{data['emoji']} {col}\n   📌 {majors_list}{more}\n\n"
        await update.message.reply_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📝 اطلب الآن", callback_data="start_order")
            ]])
        )

    elif text == "ℹ️ عن البوت":
        active_svcs = sum(1 for v in settings["services"].values() if v.get("active", True))
        await update.message.reply_text(
            "ℹ️ عن النظام\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 بوت الخدمات الطلابية الاحترافي\n"
            "📌 الإصدار: 4.0\n"
            f"👥 المستخدمون: {len(users)}\n"
            f"📦 إجمالي الطلبات: {len(db)}\n"
            f"📚 الخدمات المتاحة: {active_svcs}\n"
            f"🏛️ الكليات المدعومة: {len(COLLEGES_DATA)}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ مدعوم بـ Telegram Bot API\n"
            "🔒 بياناتك محمية وآمنة"
        )

    elif text == "🛠 لوحة التحكم":
        if uid not in ADMINS:
            await update.message.reply_text("⛔ غير مصرّح لك.")
            return
        await update.message.reply_text(
            "🛠 لوحة تحكم المشرف\n━━━━━━━━━━━━━━━━━━━━\nاختر القسم:",
            reply_markup=admin_main_kb()
        )

# ══════════════════════════════════════════════
# 📝  ConversationHandler - نموذج الطلب الكامل
# ══════════════════════════════════════════════
async def conv_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_banned(uid):
        if update.message:
            await update.message.reply_text("🚫 تم حظرك من استخدام البوت.")
        return ConversationHandler.END
    if not settings["bot_active"] and uid not in ADMINS:
        if update.message:
            await update.message.reply_text("⚠️ البوت متوقف مؤقتاً.")
        return ConversationHandler.END
    context.user_data["order"] = {"id": gen_order_id()}
    msg = (
        "📝 نموذج الطلب الجديد\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👤 الخطوة 1/9 — اكتب اسمك الكامل:"
    )
    if update.callback_query:
        await update.callback_query.answer()
        await context.bot.send_message(uid, msg, reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ASK_NAME

async def conv_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 3:
        await update.message.reply_text(
            "⚠️ الاسم قصير جداً. يرجى كتابة اسمك الكامل (3 أحرف على الأقل):"
        )
        return ASK_NAME
    context.user_data["order"]["name"] = name
    await update.message.reply_text(
        "🏛️ الخطوة 2/9 — اختر جامعتك:",
        reply_markup=universities_kb(0)
    )
    return ASK_UNIVERSITY

async def conv_university_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    await q.answer()

    if data == "cancel_order":
        await q.edit_message_text("❌ تم إلغاء الطلب.")
        return ConversationHandler.END

    if data == "uni_custom":
        await q.edit_message_text("✍️ اكتب اسم جامعتك:")
        context.user_data["awaiting_custom"] = "university"
        return ASK_UNIVERSITY

    if data.startswith("uni_page_"):
        page = int(data.split("_")[2])
        await q.edit_message_text(
            "🏛️ اختر جامعتك:",
            reply_markup=universities_kb(page)
        )
        return ASK_UNIVERSITY

    if data.startswith("uni_"):
        uni = data[4:]
        context.user_data["order"]["university"] = uni
        context.user_data.pop("awaiting_custom", None)
        await q.edit_message_text(
            f"✅ الجامعة: {uni}\n\n🏫 الخطوة 3/9 — اختر كليتك:",
            reply_markup=colleges_kb()
        )
        return ASK_COLLEGE
    return ASK_UNIVERSITY

async def conv_university_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_custom") == "university":
        context.user_data["order"]["university"] = update.message.text.strip()
        context.user_data.pop("awaiting_custom", None)
        await update.message.reply_text(
 
