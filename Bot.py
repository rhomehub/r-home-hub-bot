
import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

MENU = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🏠 ثبت ملک", callback_data="listing"),
        InlineKeyboardButton("🔎 ثبت درخواست", callback_data="request"),
    ],
    [
        InlineKeyboardButton("🔄 سایر معاملات", callback_data="other"),
        InlineKeyboardButton("🌍 شهرهای دیگر", callback_data="cities"),
    ],
    [
        InlineKeyboardButton("📋 جستجوی آگهی", callback_data="search"),
    ],
    [
        InlineKeyboardButton("👤 درباره من", callback_data="about"),
        InlineKeyboardButton("📞 ارتباط با من", callback_data="contact"),
    ],
])

BACK = InlineKeyboardMarkup([
    [InlineKeyboardButton("⬅️ منوی اصلی", callback_data="home")]
])

OPTIONS = {
    "listing": (
        "🏠 ثبت ملک\n\nنوع معامله را انتخاب کن:",
        [
            [InlineKeyboardButton("فروش", callback_data="sale")],
            [InlineKeyboardButton("اجاره", callback_data="rent")],
            [InlineKeyboardButton("رهن و اجاره", callback_data="deposit_rent")],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data="home")],
        ],
    ),
    "request": (
        "🔎 ثبت درخواست\n\nنوع درخواستت را انتخاب کن:",
        [
            [InlineKeyboardButton("خرید", callback_data="buy")],
            [InlineKeyboardButton("اجاره", callback_data="need_rent")],
            [InlineKeyboardButton("رهن و اجاره", callback_data="need_deposit_rent")],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data="home")],
        ],
    ),
    "other": (
        "🔄 سایر معاملات\n\nیک گزینه انتخاب کن:",
        [
            [InlineKeyboardButton("تهاتر", callback_data="barter")],
            [InlineKeyboardButton("باغ، ویلا و زمین", callback_data="land")],
            [InlineKeyboardButton("تهاتر مصالح", callback_data="materials")],
            [InlineKeyboardButton("سایر موارد", callback_data="other_request")],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data="home")],
        ],
    ),
    "cities": (
        "🌍 امور ملکی شهرها و کشورهای دیگر\n\n"
        "در نسخه بعدی، ثبت درخواست در شهر، استان یا کشور دلخواه را تکمیل می‌کنیم.",
        None,
    ),
    "search": (
        "📋 جستجوی آگهی\n\n"
        "به‌زودی این بخش به آگهی‌های ثبت‌شده متصل می‌شود.",
        None,
    ),
    "about": (
        "👤 درباره مشاور املاک\n\n"
        "نام برند: R-Estate\n"
        "نام و شماره تماس و آدرس دفتر پس از تکمیل اطلاعات اضافه می‌شود.",
        None,
    ),
    "contact": (
        "📞 ارتباط با مشاور\n\n"
        "در مرحله بعد لینک تماس، واتس‌اپ و شبکه‌های اجتماعی را اضافه می‌کنیم.",
        None,
    ),
}

LABELS = {
    "sale": "ثبت ملک برای فروش",
    "rent": "ثبت ملک برای اجاره",
    "deposit_rent": "ثبت ملک برای رهن و اجاره",
    "buy": "درخواست خرید",
    "need_rent": "درخواست اجاره",
    "need_deposit_rent": "درخواست رهن و اجاره",
    "barter": "تهاتر",
    "land": "باغ، ویلا یا زمین",
    "materials": "تهاتر مصالح ساختمانی",
    "other_request": "سایر موارد",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.effective_message.reply_text(
        "سلام و خوش آمدی! 👋\n\n"
        "به سامانه املاک R-Estate خوش آمدی.\n"
        "از منوی زیر گزینه موردنظرت را انتخاب کن:",
        reply_markup=MENU,
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data

    if key == "home":
        context.user_data.clear()
        await query.edit_message_text(
            "🏡 منوی اصلی R-Estate\n\nیک گزینه انتخاب کن:",
            reply_markup=MENU,
        )
        return

    if key in LABELS:
        context.user_data["form"] = key
        await query.edit_message_text(
            f"✅ {LABELS[key]}\n\n"
            "لطفاً شهر، بودجه یا قیمت، متراژ و توضیحات موردنظرت "
            "را در یک پیام بنویس.\n\n"
            "این نسخه اولیه است؛ ذخیره‌سازی و ارسال به مدیر را "
            "در مرحله بعد اضافه می‌کنیم.",
            reply_markup=BACK,
        )
        return

    if key in OPTIONS:
        message, rows = OPTIONS[key]
        keyboard = InlineKeyboardMarkup(rows) if rows else BACK
        await query.edit_message_text(message, reply_markup=keyboard)


async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "form" not in context.user_data:
        await update.effective_message.reply_text(
            "برای شروع از منوی اصلی یک گزینه انتخاب کن.",
            reply_markup=MENU,
        )
        return

    await update.effective_message.reply_text(
        "پیامت دریافت شد. در نسخه بعدی، ثبت اطلاعات و ارسال آن "
        "برای مدیر را فعال می‌کنیم.",
        reply_markup=BACK,
    )


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text))
    app.run_polling()


if __name__ == "__main__":
    main()
