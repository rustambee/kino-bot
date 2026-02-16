# Bot konfiguratsiyasi
import json
import os

# Bot tokeni (hardcoded, o'zgartirilmaydigan)
BOT_TOKEN = "8561585026:AAHpSisbP2dbOp4ThqLb_6PsqCNI4EM0GdA"

# Boshlang'ich admin ID (o'zgartirilmaydigan super admin)
SUPER_ADMIN = 7360704654

# Baza kanal ID (mahfiy kanal bo'lishi mumkin) - DINAMIK
DEFAULT_BASE_CHANNEL = -1003781268251

# Ma'lumotlar bazasi fayllari
MOVIES_FILE = "movies.json"
USERS_FILE = "users.json"
CHANNELS_FILE = "channels.json"
PREMIUM_FILE = "premium.json"
ADMINS_FILE = "admins.json"
VIEWS_FILE = "views.json"
LIKES_FILE = "likes.json"
PENDING_CHANNELS_FILE = "pending_channels.json"
SETTINGS_FILE = "settings.json"  # Dinamik sozlamalar


def load_settings():
    """Dinamik sozlamalarni yuklash"""
    default_settings = {
        "instagram_url": "https://www.instagram.com/chirs.million?igsh=aHBteWoxdG1yZzZ1",
        "card_number": "9860 0466 0885 3290",
        "card_owner": "Jabaraliyev Rustambek",
        "base_channel": DEFAULT_BASE_CHANNEL
    }
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Default qiymatlarni qo'sh
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except Exception as e:
            print(f"[ERROR] Sozlamalarni yuklashda xatolik: {str(e)}")
            return default_settings
    else:
        save_settings(default_settings)
        return default_settings


def save_settings(settings):
    """Dinamik sozlamalarni saqlash"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Sozlamalarni saqlashda xatolik: {str(e)}")
        return False


def get_setting(key, default=None):
    """Bitta sozlamani olish"""
    settings = load_settings()
    return settings.get(key, default)


def set_setting(key, value):
    """Bitta sozlamani o'rnatish"""
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)


# Sozlamalarni yuklash
_settings = load_settings()
INSTAGRAM_URL = _settings.get("instagram_url")
CARD_NUMBER = _settings.get("card_number")
CARD_OWNER = _settings.get("card_owner")


def get_base_channel():
    """Baza kanalini dinamik olish"""
    return int(get_setting("base_channel", DEFAULT_BASE_CHANNEL))


# Orqaga tarafini oson qilish uchun
BASE_CHANNEL = get_base_channel()
