# Kanal operatsiyalari

from telebot import types
from database import (
    channels_db, pending_channels_db, users_db,
    save_data, add_pending_channel, approve_pending_channel, 
    reject_pending_channel, get_pending_channel,
    CHANNELS_FILE, PENDING_CHANNELS_FILE
)
from keyboards import admin_keyboard
from admin_handlers import user_states
import uuid

def start_add_channel(user_id, bot):
    """Kanal qo'shishni boshlash"""
    user_states[user_id] = {"action": "adding_channel_link"}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ Bekor qilish")
    bot.send_message(
        user_id,
        "🔗 Kanal silkasini yuboring:\n\n"
        "Ochiq kanal: https://t.me/kanal_nomi\n"
        "Yoki: @kanal_nomi\n\n"
        "⚠️ Mahfiy kanallar uchun invite linkni yuboring:\n"
        "https://t.me/+xxxx yoki t.me/joinchat/xxxx\n\n"
        "Diqqat:\n"
        "1. Botni kanalga admin qiling (yoki shaxsiy kanal uchun invite link bering)\n"
        "2. Faqat siz qo'shgan kanallar ro'yxatlanadi",
        reply_markup=markup
    )

def add_channel_link_callback(user_id, link_text, bot):
    """Kanal silkasini qabul qilish"""
    if link_text == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(user_id, "❌ Bekor qilindi", reply_markup=admin_keyboard())
        return
    
    link = link_text.strip()
    is_private = False
    
    try:
        # Mahfiy kanal ekanligini tekshirish
        if "+" in link or "joinchat" in link:
            is_private = True
            
            # MAHFIY KANAL TEKSHIRISH
            # Mahfiy kanalni verify qilish uchun try-catch orqali kirish
            verification_success = False
            real_channel_id = None
            
            try:
                # Invite link orqali chat info olish (agar mavjud bo'lsa)
                # Mahfiy kanalda bot a'zo bo'lsa, chat info olish mumkin
                chat_info = bot.get_chat(link)
                verification_success = True
                real_channel_id = chat_info.id  # Real channel ID ni saqlash
            except:
                # Agar direct tekshira olmasa, yo'q
                real_channel_id = None
            
            # Mahfiy kanal uchun state saqlash va approval jarayoni boshlash
            user_states[user_id] = {
                "action": "adding_private_channel",
                "invite_link": link,
                "verified": verification_success,
                "real_channel_id": real_channel_id  # Real channel ID ni state'ga saqlash
            }
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            markup.add("❌ Bekor qilish")
            
            bot.send_message(
                user_id,
                f"✅ Mahfiy kanal linkni qabul qildim!\n\n"
                f"🔗 Link: {link}\n\n"
                f"📝 Endi kanal nomini kiriting (tugmada ko'rsatiladigan nom):\n\n"
                f"Masalan: Kino kanali",
                reply_markup=markup
            )
            return
        
        # Ochiq kanal
        if "t.me/" in link:
            username = link.split("t.me/")[1].split("?")[0].split("/")[0].strip()
        elif link.startswith("@"):
            username = link[1:]
        else:
            username = link
        
        if not username.startswith("@"):
            username = "@" + username
        
        chat = bot.get_chat(username)
        
        if chat.type != 'channel':
            bot.send_message(
                user_id,
                "❌ Bu kanal emas!",
                reply_markup=admin_keyboard()
            )
            user_states.pop(user_id, None)
            return
        
        channel_id = chat.id
        channel_title = chat.title
        invite_link = f"https://t.me/{username[1:]}"
        
        if str(channel_id) in channels_db:
            bot.send_message(
                user_id,
                f"⚠️ {channel_title} kanali allaqachon ro'yxatda!",
                reply_markup=admin_keyboard()
            )
            user_states.pop(user_id, None)
            return
        
        bot_member = bot.get_chat_member(channel_id, bot.get_me().id)
        if bot_member.status not in ['administrator', 'creator']:
            bot.send_message(
                user_id,
                f"❌ Botni {channel_title} kanaliga admin qiling!\n\n"
                f"Keyin qayta urinib ko'ring.",
                reply_markup=admin_keyboard()
            )
            user_states.pop(user_id, None)
            return
        
        user_states[user_id] = {
            "action": "adding_public_channel_name",
            "channel_id": channel_id,
            "channel_title": channel_title,
            "invite_link": invite_link
        }
        
        bot.send_message(
            user_id,
            f"✅ Kanal topildi!\n\n"
            f"📢 Kanal: {channel_title}\n"
            f"🆔 ID: {channel_id}\n"
            f"🔗 Link: {invite_link}\n\n"
            f"📝 Endi kanal nomini kiriting (tugmada ko'rsatiladigan nom):\n\n"
            f"Masalan: Kino kanali"
        )
        
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ Xatolik: {str(e)}\n\n"
            f"Iltimos:\n"
            f"1. Silka to'g'ri ekanligini tekshiring\n"
            f"2. Kanal ochiq (username bilan) ekanligini tekshiring\n"
            f"3. Botni kanalga admin qiling\n"
            f"4. Qayta urinib ko'ring",
            reply_markup=admin_keyboard()
        )
        user_states.pop(user_id, None)

def add_channel_name_callback(user_id, channel_name, bot, is_private=False):
    """Kanal nomini qabul qilish"""
    if channel_name == "❌ Bekor qilish":
        user_states.pop(user_id, None)
        bot.send_message(user_id, "❌ Bekor qilindi", reply_markup=admin_keyboard())
        return
    
    state = user_states[user_id]
    channel_name = channel_name.strip()
    
    if is_private:
        # Mahfiy kanal
        invite_link = state.get("invite_link")
        verified = state.get("verified", False)
        real_channel_id = state.get("real_channel_id")  # Real channel ID ni olish
        
        # Unique ID yaratish
        request_id = str(uuid.uuid4())
        
        channel_data = {
            "name": channel_name,
            "invite_link": invite_link,
            "is_private": True,
            "verified": verified,  # Kanal tekshirilganmi yoki yo'qmi
            "chat_id": real_channel_id,  # Real Telegram channel ID (agar mavjud bo'lsa)
            "requested_by": user_id,
            "requested_at": __import__('datetime').datetime.now().isoformat()
        }
        
        add_pending_channel(request_id, channel_data)
        
        status_text = "✅ Tekshirildi" if verified else "⚠️ Tasdiq kutmoqda"
        
        bot.send_message(
            user_id,
            f"✅ Mahfiy kanal so'rovi yuborildi!\n\n"
            f"📝 Kanal nomi: {channel_name}\n"
            f"🔗 Link: {invite_link}\n"
            f"🔐 Status: {status_text}\n\n"
            f"⏳ Admin tasdiqlanishini kuting...",
            reply_markup=admin_keyboard()
        )
        
        # Adminlarga xabar
        notify_admins_about_pending_channel(user_id, channel_name, invite_link, request_id, bot, verified)
    else:
        # Ochiq kanal
        channel_id = state["channel_id"]
        channel_title = state["channel_title"]
        invite_link = state["invite_link"]
        
        channels_db[str(channel_id)] = {
            "chat_id": channel_id,
            "title": channel_title,
            "name": channel_name,
            "invite_link": invite_link,
            "is_private": False
        }
        save_data(CHANNELS_FILE, channels_db)
        
        bot.send_message(
            user_id,
            f"✅ Kanal muvaffaqiyatli qo'shildi!\n\n"
            f"📢 Kanal: {channel_title}\n"
            f"📝 Tugma nomi: {channel_name}\n"
            f"🆔 ID: {channel_id}\n"
            f"🔗 Link: {invite_link}",
            reply_markup=admin_keyboard()
        )
    
    user_states.pop(user_id, None)

def start_delete_channel(user_id, bot):
    """Kanal o'chirishni boshlash"""
    if not channels_db:
        bot.send_message(
            user_id,
            "❌ Hozircha kanallar ro'yxati bo'sh!",
            reply_markup=admin_keyboard()
        )
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for channel_id, channel_data in channels_db.items():
        markup.add(types.InlineKeyboardButton(
            text=f"🗑 {channel_data['name']} ({channel_data.get('title', 'Mahfiy')})",
            callback_data=f"delete_channel:{channel_id}"
        ))
    markup.add(types.InlineKeyboardButton(
        text="❌ Bekor qilish",
        callback_data="cancel_delete_channel"
    ))
    
    bot.send_message(
        user_id,
        "🗑 O'chirmoqchi bo'lgan kanalni tanlang:",
        reply_markup=markup
    )

def delete_channel_callback(channel_id, bot):
    """Kanalni o'chirish"""
    if channel_id in channels_db:
        channel_data = channels_db[channel_id]
        del channels_db[channel_id]
        save_data(CHANNELS_FILE, channels_db)
        return channel_data
    return None

def show_channels_list(user_id, bot):
    """Kanallar ro'yxatini ko'rsatish"""
    if not channels_db:
        bot.send_message(
            user_id,
            "❌ Hozircha kanallar ro'yxati bo'sh!",
            reply_markup=admin_keyboard()
        )
        return
    
    # Ochiq va mahfiy kanallarni alohida ko'rsatish
    public_channels = []
    private_channels = []
    
    for channel_id, channel_data in channels_db.items():
        if channel_data.get('is_private'):
            private_channels.append((channel_id, channel_data))
        else:
            public_channels.append((channel_id, channel_data))
    
    text = "📋 <b>KANALLAR RO'YXATI</b>\n\n"
    
    if public_channels:
        text += "� <b>MAJBURIY OCHIQ KANALLAR</b> (Foydalanuvchilar obuna bo'lishi shart):\n\n"
        for i, (channel_id, channel_data) in enumerate(public_channels, 1):
            text += f"{i}. {channel_data['name']}\n"
            text += f"   📢 Kanal: {channel_data.get('title', 'Noma\'lum')}\n"
            text += f"   🆔 ID: {channel_id}\n"
            text += f"   🔗 {channel_data['invite_link']}\n\n"
    
    if private_channels:
        text += "\n🔒 <b>IXTIYORIY MAHFIY KANALLAR</b> (Shunchaki link bosish ixtiyoriy):\n\n"
        for i, (channel_id, channel_data) in enumerate(private_channels, 1):
            text += f"{i}. {channel_data['name']}\n"
            text += f"   📝 Link: {channel_data['invite_link']}\n\n"
    
    # Pending kanallarni ham ko'rsatish
    if pending_channels_db:
        pending_private = [
            (req_id, req_data) for req_id, req_data in pending_channels_db.items()
            if isinstance(req_data, dict) and req_data.get('is_private')
        ]
        
        if pending_private:
            text += "\n⏳ <b>TASDIQ KUTAYOTGAN MAHFIY KANALLAR</b>:\n\n"
            for req_id, req_data in pending_private:
                text += f"• {req_data.get('name', 'Noma\'lum')}\n"
                text += f"   📝 Link: {req_data.get('invite_link', 'Yo\'q')}\n"
                text += f"   👤 Foydalanuvchi ID: {req_data.get('requested_by', 'Yo\'q')}\n"
                text += f"   🔐 Status: {'✅ Tekshirildi' if req_data.get('verified') else '⚠️ Tasdiq kutmoqda'}\n\n"
    
    bot.send_message(
        user_id,
        text,
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )

def notify_admins_about_pending_channel(user_id, channel_name, invite_link, request_id, bot, verified=False):
    """Adminlarga tasdiqlanmagan kanal haqida xabar"""
    try:
        from database import load_data, USERS_FILE
        
        users_data = load_data(USERS_FILE)
        if not isinstance(users_data, dict):
            users_data = {}
        
        user_info = users_data.get(str(user_id), {})
        first_name = user_info.get("first_name", "Noma'lum")
        username = user_info.get("username", "Yo'q")
        
        username_text = f"@{username}" if username != "Yo'q" else "Yo'q"
        
        # Tekshirish statusi
        verify_status = "✅ Tekshirildi - Bot kanal a'zosi" if verified else "⚠️ Tavsiyalash - Bot kanal a'zosi emas"
        
        text = (
            f"🔔 <b>YANGI KANAL SO'ROVI!</b>\n\n"
            f"👤 <b>Foydalanuvchi:</b> {first_name}\n"
            f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
            f"📱 <b>Username:</b> {username_text}\n\n"
            f"📝 <b>Kanal nomi:</b> {channel_name}\n"
            f"🔗 <b>Link:</b> <code>{invite_link}</code>\n"
            f"🔒 <b>Tur:</b> Mahfiy kanal\n"
            f"🔐 <b>Status:</b> {verify_status}\n\n"
            f"<b>⏳ Tasdiq yoki Rad esingiz kerak:</b>"
        )
        
        from database import admins_list
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data=f"approve_channel:{request_id}"
            ),
            types.InlineKeyboardButton(
                text="❌ Rad etish",
                callback_data=f"reject_channel:{request_id}"
            )
        )
        markup.add(
            types.InlineKeyboardButton(
                text="📋 Batafsil",
                callback_data=f"view_pending:{request_id}"
            )
        )
        
        sent_count = 0
        for admin_id in admins_list:
            try:
                bot.send_message(
                    int(admin_id),
                    text,
                    parse_mode="HTML",
                    reply_markup=markup
                )
                sent_count += 1
                print(f"[OK] Admin {admin_id} ga kanal so'rovi yuborildi: {request_id}")
            except Exception as admin_error:
                print(f"[ERROR] Admin {admin_id} ga xabar yuborishda xatolik: {str(admin_error)}")
        
        if sent_count == 0:
            print(f"[WARNING] Hech qanday adminni topib bo'lmadi! admins_list: {admins_list}")
        
        return sent_count > 0
    except Exception as e:
        print(f"[ERROR] Adminlarga xabar yuborishda xatolik: {str(e)}")
        return False
