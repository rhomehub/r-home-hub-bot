
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MENU = [
    [("🏠 ثبت ملک برای فروش یا اجاره", "property")],
    [("🔎 درخواست خرید یا اجاره ملک", "request")],
    [("🤝 سایر معاملات و تهاتر", "other")],
    [("🌍 ملک در شهرها و کشورهای دیگر", "cities")],
    [("📋 جستجوی ملک", "search")],
    [("ℹ️ درباره ما", "about"), ("☎️ تماس", "contact")],
]

MESSAGES = {
    "property": (
        "🏠 ثبت ملک\n\n"
        "لطفاً اطلاعات ملک را در یک پیام بفرست:\n"
        "نوع معامله، شهر و محله، متراژ، قیمت یا مبلغ رهن و اجاره، "
        "تعداد اتاق و شماره تماس.\n\n"
        "هر اطلاعاتی را که فعلاً داری بنویس."
    ),
    "request": (
        "🔎 درخواست ملک\n\n"
        "دنبال چه ملکی هستی؟ شهر، محله، بودجه، متراژ و نوع معامله "
        "(خرید، رهن یا اجاره) را بنویس."
    ),
    "other": (
        "🤝 سایر معاملات\n\n"
        "برای تهاتر، زمین، باغ، ویلا، مصالح ساختمانی یا خدمات ساختمان، "
        "توضیحات درخواستت را بنویس."
    ),
    "cities": (
        "🌍 درخواست در شهرها و کشورهای دیگر\n\n"
        "نام شهر یا کشور، نوع ملک و بودجه‌ات را بنویس."
    ),
    "search": (
        "📋 جستجوی ملک\n\n"
        "برای راهنمایی در جستجو، شهر، محله، نوع معامله و بودجه‌ات را بنویس."
    ),
    "about": (
        "ℹ️ درباره R-Estate\n\n"
        "خدمات معرفی و پیگیری درخواست‌های ملکی، خرید، فروش، رهن، اجاره "
        "و سایر معاملات ملکی.\n\n"
        "اطلاعات تماس و مشخصات مجموعه باید بعداً تکمیل شود."
    ),
    "contact": (
        "☎️ ارتباط با R-Estate\n\n"
        "برای ارتباط، درخواستت را همین‌جا بنویس. "
        "شماره تماس و راه‌های ارتباطی مجموعه بعداً اضافه می‌شود."
    ),
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("waiting_for", None)
    keyboard = [
        [InlineKeyboardButton(label, callback_data=key)
         for label, key in row]
        for row in MENU
    ]
    await update.message.reply_text(
        "سلام! به ربات املاک R-Estate خوش آمدی 🏡\n\n"
        "از منوی زیر یکی از گزینه‌ها را انتخاب کن.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def menu_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    key = query.data
    if key not in MESSAGES:
        return

    if key in ("property", "request", "other", "cities", "search"):
        context.user_data["waiting_for"] = key
    else:
        context.user_data.pop("waiting_for", None)

    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="home")]]
    await query.message.reply_text(
        MESSAGES[key],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def home_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("waiting_for", None)

    keyboard = [
        [InlineKeyboardButton(label, callback_data=key)
         for label, key in row]
        for row in MENU
    ]
    await query.message.reply_text(
        "منوی اصلی R-Estate:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def receive_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    waiting_for = context.user_data.get("waiting_for")

    if not waiting_for:
        await update.message.reply_text(
            "برای شروع یا دیدن گزینه‌ها، دستور /start را بفرست."
        )
        return

    logger.info(
        "Request received: category=%s user_id=%s",
        waiting_for,
        update.effective_user.id,
    )

    context.user_data.pop("waiting_for", None)
    await update.message.reply_text(
        "✅ اطلاعاتت در همین گفت‌وگو دریافت شد.\n\n"
        "توجه: در نسخه فعلی اطلاعات در پایگاه داده ذخیره نمی‌شود "
        "و هنوز برای مدیر ارسال نمی‌شود.\n\n"
        "برای ثبت درخواست دیگری، /start را بفرست."
    )


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    base_url = os.environ.get("RENDER_EXTERNAL_URL")

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    if not base_url:
        raise RuntimeError("RENDER_EXTERNAL_URL is not set")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(home_handler, pattern="^home$"))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text)
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        url_path="telegram-webhook",
        webhook_url=f"{base_url.rstrip('/')}/telegram-webhook",
    )


if __name__ == "__main__":
    main()
