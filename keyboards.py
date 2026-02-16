# Tugma va klaviaturalar

from telebot import types


def movie_keyboard(movie_code, user_id):
    """Kinoning tugmalari (faqat like va ulashish)"""
    from database import load_data
    from config import LIKES_FILE
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Likes bazasini yuklash
    likes_db = load_data(LIKES_FILE)
    
    # Yoqdi tugmasi
    user_likes = likes_db.get(movie_code, [])
    likes_count = len(user_likes) if isinstance(user_likes, list) else 0
    
    if isinstance(user_likes, list) and user_id in user_likes:
        like_text = f"❤️ {likes_count}"
    else:
        like_text = f"🤍 {likes_count}"
    
    markup.add(
        types.InlineKeyboardButton(
            text=like_text,
            callback_data=f"like:{movie_code}"
        ),
        types.InlineKeyboardButton(
            text="📤 Ulashish",
            switch_inline_query=f"{movie_code}"
        )
    )
    
    return markup

def subscription_keyboard(not_subscribed=None, bot=None):
    """Obuna bo'lish uchun tugmalar - FAQAT MAJBURIY OCHIQ KANALLAR"""
    from utils import get_all_channels_for_display
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # MAJBURIY OCHIQ KANALLAR
    if not_subscribed:
        for channel in not_subscribed:
            if not channel.get('is_private'):  # Faqat ochiq majburiy kanallar
                markup.add(types.InlineKeyboardButton(
                    text=f"{channel['name']}",
                    url=channel['invite_link']
                ))
    
    # IXTIYORIY MAHFIY KANALLAR - Alohida tugmalar
    try:
        if bot:
            all_channels = get_all_channels_for_display(bot)
            
            # Mahfiy ixtiyoriy kanallarni qo'shish
            private_channels = [ch for ch in all_channels if ch.get('is_private')]
            
            if private_channels:
               
                
                for channel in private_channels:
                    markup.add(types.InlineKeyboardButton(
                        text=f"{channel['name']}",
                        url=channel['invite_link']
                    ))
    except Exception as e:
        print(f"[ERROR] Ixtiyoriy kanallarni ko'rsatishda xatolik: {str(e)}")
    
    # Tasdiq va premium tugmalari
    markup.add(
        types.InlineKeyboardButton(
            text="✔️ Obuna bo'ldim",
            callback_data="check_subscription"
        ),
        types.InlineKeyboardButton(
            text="⭐️ Premium",
            callback_data="premium_info"
        )
    )
    return markup

def premium_tariffs_keyboard():
    """Premium tarif tanlovning tugmalari"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            text="1️⃣ 1 oyga - 10,000 so'm",
            callback_data="tariff:1:10000"
        ),
        types.InlineKeyboardButton(
            text="3️⃣ 3 oyga - 20,000 so'm",
            callback_data="tariff:3:20000"
        ),
        types.InlineKeyboardButton(
            text="🔟 12 oyga - 50,000 so'm",
            callback_data="tariff:12:50000"
        ),
        types.InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data="back_to_main"
        )
    )
    return markup

def admin_keyboard():
    """Admin menyu"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎬 Kino yuklash", "🗑 Kinoni o'chirish")
    markup.add("➕ Kanal qo'shish", "➖ Kanal o'chirish")
    markup.add("📋 Kanallar ro'yxati", "📊 Statistika")
    markup.add("🎬➡️ Kinoni kanalga", "📤 Kinoni ulashish")
    markup.add("🎞️ Kinolar ro'yxati", "📢 Xabar yuborish")
    markup.add("⭐️ Premium a'zolar", "👤 Admin qo'shish")
    markup.add("🗑 Admin o'chirish", "👥 Adminlar ro'yxati")
    markup.add("⚙️ Sozlamalar")
    return markup

def user_keyboard(is_premium=False):
    """Oddiy foydalanuvchi menyu"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎬 Kino qidirish")
    if is_premium:
        markup.add("⭐️ Premium status")
    markup.add("ℹ️ Yordam", "📱 Instagram")
    return markup
