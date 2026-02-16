# Ma'lumotlar bazasi operatsiyalari

import json
import os
from config import (
    MOVIES_FILE, USERS_FILE, CHANNELS_FILE, PREMIUM_FILE, 
    ADMINS_FILE, VIEWS_FILE, LIKES_FILE, PENDING_CHANNELS_FILE, SUPER_ADMIN
)

def load_data(filename):
    """JSON fayildan ma'lumotni yuklash (dict yoki list)"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Agar fayl buzilgan bo'lsa
            if filename in [MOVIES_FILE, USERS_FILE]:
                return []
            return {}
    # Default qaytarish
    if filename in [MOVIES_FILE, USERS_FILE]:
        return []
    return {}

def save_data(filename, data):
    """Ma'lumotni JSON fayliga saqlash"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"[ERROR] {filename} saqlashda xatolik: {str(e)}")
        return False

def load_list(filename):
    """JSON fayildan ro'yxatni yuklash"""
    return load_data(filename)

def save_list(filename, data):
    """Ro'yxatni JSON fayliga saqlash"""
    return save_data(filename, data)

# Bazalarni yuklash va boshlang'ich o'rnatish
movies_db = load_data(MOVIES_FILE)

# Users faylini yuklash (HECH QACHON QAYTA BOSHLASHNI YO'Q)
# Users dict sifatida saqlash: {user_id: user_info}
premium_db = load_data(PREMIUM_FILE)
users_db = load_data(USERS_FILE)
if not isinstance(users_db, dict):
    users_db = {}
    save_data(USERS_FILE, users_db)

channels_db = load_data(CHANNELS_FILE)
admins_list = load_list(ADMINS_FILE)
views_db = load_data(VIEWS_FILE)
likes_db = load_data(LIKES_FILE)
pending_channels_db = load_data(PENDING_CHANNELS_FILE)

print("[*] Bot boshlandi - ma'lumotlar uchrashtirildi")

# Asosiy faollashtirishlar
if not admins_list:
    admins_list = [SUPER_ADMIN]
    save_list(ADMINS_FILE, admins_list)

if not channels_db:
    channels_db = {}
    save_data(CHANNELS_FILE, channels_db)

if not premium_db:
    premium_db = {}
    save_data(PREMIUM_FILE, premium_db)

if not views_db:
    views_db = {}
    save_data(VIEWS_FILE, views_db)

if not likes_db:
    likes_db = {}
    save_data(LIKES_FILE, likes_db)

if not pending_channels_db:
    pending_channels_db = {}
    save_data(PENDING_CHANNELS_FILE, pending_channels_db)

# Tasdiqlanmagan kanalda ma'lumot saqlash
def add_pending_channel(request_id, channel_data):
    """Tasdiqlanmaydigan kanalga so'rovni qo'shish"""
    try:
        pending_channels_db[str(request_id)] = channel_data
        save_data(PENDING_CHANNELS_FILE, pending_channels_db)
        print(f"[OK] Kanal so'rovi saqlandi: {request_id}")
        return True
    except Exception as e:
        print(f"[ERROR] Kanal so'rovini saqlashda xatolik: {str(e)}")
        return False

def approve_pending_channel(request_id):
    """Kanalni tasdiqlash"""
    try:
        if str(request_id) in pending_channels_db:
            channel_data = pending_channels_db[str(request_id)].copy()
            
            # Private channels uchun unique ID yaratish
            if channel_data.get("is_private"):
                # Agar real channel ID mavjud bo'lsa, uni ishlat; aks holda UUID yarat
                if channel_data.get("chat_id"):
                    channel_id = channel_data.get("chat_id")
                else:
                    channel_id = str(__import__('uuid').uuid4())
                    channel_data["chat_id"] = channel_id
            else:
                channel_id = channel_data.get("chat_id")
            
            # Channels bazasiga qo'shish
            channels_db[str(channel_id)] = channel_data
            
            # Pending kanaldan o'chirish
            del pending_channels_db[str(request_id)]
            
            # Saqlash
            save_data(CHANNELS_FILE, channels_db)
            save_data(PENDING_CHANNELS_FILE, pending_channels_db)
            print(f"[OK] Kanal tasdiqlandi: {channel_id}")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Kanal tasdiqlanishda xatolik: {str(e)}")
        return False

def reject_pending_channel(request_id):
    """Kanalni rad etish"""
    try:
        if str(request_id) in pending_channels_db:
            del pending_channels_db[str(request_id)]
            save_data(PENDING_CHANNELS_FILE, pending_channels_db)
            print(f"[OK] Kanal rad etildi: {request_id}")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Kanal radda xatolik: {str(e)}")
        return False

def get_pending_channel(request_id):
    """Tasdiqlanmaydigan kanalni olish"""
    return pending_channels_db.get(str(request_id))
