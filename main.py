import requests
import json
import os
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Cấu hình stdout hỗ trợ utf-8 trên Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from colorama import init, Fore, Style, Back

# Khởi tạo colorama
init(autoreset=True)

import re

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def visual_len(text):
    stripped = strip_ansi(text)
    length = 0
    for char in stripped:
        if ord(char) == 0x3000 or (0x1100 <= ord(char) <= 0x115f) or \
           (0x2e80 <= ord(char) <= 0xa4cf) or (0xac00 <= ord(char) <= 0xd7a3) or \
           (0xf900 <= ord(char) <= 0xfaff) or (0xfe30 <= ord(char) <= 0xfe6f) or \
           (0xff00 <= ord(char) <= 0xffef) or (0x1f000 <= ord(char) <= 0x1f9ff):
            length += 2
        else:
            length += 1
    return length

# ==================== LOGO ====================
LOGO = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════════════════════╗
{Fore.YELLOW}║  ███████╗ █████╗ ███╗   ██╗ ██████╗     ██████╗ ███████╗██╗   ██╗        ║
{Fore.YELLOW}║  ██╔════╝██╔══██╗████╗  ██║██╔════╝     ██╔══██╗██╔════╝██║   ██║        ║
{Fore.YELLOW}║  ███████╗███████║██╔██╗ ██║██║  ███╗    ██║  ██║█████╗  ██║   ██║        ║
{Fore.YELLOW}║  ╚════██║██╔══██║██║╚██╗██║██║   ██║    ██║  ██║██╔══╝  ╚██╗ ██╔╝        ║
{Fore.YELLOW}║  ███████║██║  ██║██║ ╚████║╚██████╔╝    ██████╔╝███████╗ ╚████╔╝         ║
{Fore.YELLOW}║  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝     ╚═════╝ ╚══════╝  ╚═══╝          ║
{Fore.CYAN}╠════════════════════════════════════════════════════════════════════════════╣
{Fore.MAGENTA}║                  {Fore.WHITE}🔍 CHECK TÀI KHOẢN FREE FIRE                         {Fore.MAGENTA}║
{Fore.CYAN}╠════════════════════════════════════════════════════════════════════════════╣
{Fore.GREEN}║  {Fore.WHITE}📱 Admin: {Fore.CYAN}0335764804    {Fore.WHITE}🌐 Web: {Fore.CYAN}sangdev.online                          {Fore.GREEN}║
{Fore.CYAN}╚════════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""



# ==================== BẢNG TÊN ITEM MỞ RỘNG ====================
KNOWN_ITEMS = {
    # === TRANG PHỤC (Clothes) ===
    # Tops (2xx)
    '203054007': 'Quần Skyler Huyền Thoại',
    '203033014': 'Quần Jogger Đen',
    '203051002': 'Quần Jean Xanh',
    '204054007': 'Áo Skyler Huyền Thoại',
    '204033014': 'Áo Thể Thao Đen',
    '204051002': 'Áo Khoác Xanh',
    '205054007': 'Giày Skyler Huyền Thoại',
    '205033014': 'Giày Thể Thao Đen',
    '205051002': 'Giày Sneaker Trắng',
    '211054011': 'Mũ Skyler Huyền Thoại (Vàng)',
    '211054010': 'Mũ Skyler Huyền Thoại (Đen)',
    '211033014': 'Mũ Lưỡi Trai Đen',
    '211051002': 'Mũ Thể Thao Xanh',
    '214033014': 'Quần Jogger Xám',
    '214054007': 'Quần Cargo Huyền Thoại',
    # Tops phổ biến
    '211000000': 'Không đội mũ',
    '203000000': 'Không mặc quần',
    '204000000': 'Không mặc áo',

    # === VŨ KHÍ SKIN ===
    '912053001': 'M4A1 - Bộ Sưu Tập Đặc Biệt',
    '912051002': 'M4A1 - Ngọc Bích',
    '912051001': 'M4A1 - Huyền Thoại Đỏ',
    '912050001': 'M4A1 - Mặc Định',
    '914053001': 'AK47 - Bộ Sưu Tập Đặc Biệt',
    '914051001': 'AK47 - Hỏa Long',
    '914051002': 'AK47 - Vàng',
    '914050001': 'AK47 - Mặc Định',
    '907105346': 'SCAR - Thiên Thần',
    '907053001': 'SCAR - Bộ Sưu Tập',
    '913053001': 'AWM - Huyền Thoại',
    '913051001': 'AWM - Đặc Biệt',
    '911053001': 'Groza - Huyền Thoại',
    '916053001': 'M1887 - Huyền Thoại',
    '916051001': 'M1887 - Đặc Biệt',
    '924053001': 'MP40 - Huyền Thoại',
    '924051001': 'MP40 - Màu Đặc Biệt',

    # === PET ===
    '1300000127': 'Panda - Huyền Thoại',
    '1300000071': 'Panda',
    '1300000001': 'Robo',
    '1300000002': 'Kitty',
    '1300000003': 'Night Owl',
    '1300000004': 'Ottero',
    '1300000005': 'Mr. Waggor',
    '1300000006': 'Falcon',
    '1300000007': 'Beaston',
    '1300000008': 'Detective Panda',
    '1300000009': 'Moony',
    '1300000010': 'Spirit Fox',
    '1300000011': 'Shiba',
    '1300000012': 'Dreki',
    '1300000013': 'Poring',
    '1300000014': 'Mechanical Panda',

    # === PET SKIN ===
    '1310000074': 'Skin Panda Vàng',
    '1310000001': 'Skin Robo Đặc Biệt',
    '1310000050': 'Skin Panda Huyền Thoại',

    # === AVATAR ===
    '102000038': 'Avatar Harold',
    '102000001': 'Avatar Mặc Định',
    '102000010': 'Avatar Đặc Biệt',
    '102000020': 'Avatar Sự Kiện',

    # === HUY HIỆU (Badge) ===
    '1001000097': 'Huy Hiệu Chiến Binh Huyền Thoại',
    '1001000001': 'Huy Hiệu Mới Bắt Đầu',
    '1001000050': 'Huy Hiệu Đặc Biệt',
    '1001000080': 'Huy Hiệu Grandmaster',

    # === DANH HIỆU (Title) ===
    '904990070': 'Chiến Binh Không Thể Ngăn Cản',
    '904090026': 'Thợ Săn Quái Vật',
    '904000001': 'Người Mới',
    '904000010': 'Xạ Thủ',
    '904000020': 'Sát Thủ',
    '904000030': 'Chiến Binh',
    '904010001': 'Grandmaster',
    '904020001': 'Booyah King',

    # === BANNER ===
    '901051002': 'Banner Sự Kiện Đặc Biệt',
    '901000001': 'Banner Mặc Định',
    '901051001': 'Banner Huyền Thoại',
    '901050001': 'Banner Cao Cấp',

    # === HEAD PIC (Khung ảnh) ===
    '902051015': 'Khung Ảnh Đặc Biệt',
    '902000001': 'Khung Ảnh Mặc Định',
    '902051001': 'Khung Ảnh Huyền Thoại',
    '902050001': 'Khung Ảnh Cao Cấp',

    # === PIN ===
    '910040001': 'Pin Đặc Biệt',
    '910000001': 'Pin Mặc Định',
    '910050001': 'Pin Huyền Thoại',
    '910020001': 'Pin Biểu Cảm',
}

# Bảng phân loại ID theo prefix
ID_CATEGORY_MAP = {
    '203': ('Quần', 'Quần'),
    '204': ('Áo', 'Áo'),
    '205': ('Giày', 'Giày'),
    '206': ('Khẩu Trang / Mặt Nạ', 'Phụ Kiện Mặt'),
    '207': ('Mắt Kính', 'Kính'),
    '208': ('Ba Lô', 'Ba Lô'),
    '209': ('Vòng Cổ', 'Phụ Kiện'),
    '210': ('Vòng Tay', 'Phụ Kiện'),
    '211': ('Mũ', 'Mũ'),
    '212': ('Trang Phục Bộ', 'Bộ Trang Phục'),
    '213': ('Khăn Tay', 'Khăn'),
    '214': ('Quần (Alt)', 'Quần'),
    '215': ('Áo Khoác', 'Áo Khoác'),
    '9': ('Vũ Khí', 'Vũ Khí / Vật Phẩm'),
    '912': ('M4A1', 'Skin M4A1'),
    '914': ('AK47', 'Skin AK47'),
    '907': ('SCAR', 'Skin SCAR'),
    '913': ('AWM', 'Skin AWM'),
    '916': ('M1887', 'Skin M1887'),
    '924': ('MP40', 'Skin MP40'),
    '911': ('Groza', 'Skin Groza'),
    '901': ('Banner', 'Banner'),
    '902': ('Khung Ảnh', 'Khung Ảnh'),
    '904': ('Danh Hiệu', 'Danh Hiệu'),
    '910': ('Pin', 'Pin'),
    '102': ('Avatar', 'Avatar'),
    '1001': ('Huy Hiệu', 'Huy Hiệu'),
    '130': ('Pet', 'Pet'),
    '131': ('Skin Pet', 'Skin Pet'),
}

RARITY_MAP = {
    '050': '🟤 Thường',
    '051': '🟣 Huyền Thoại',
    '052': '🔵 Hiếm',
    '053': '🟡 Đặc Biệt',
    '054': '🔴 Epic',
    '033': '⚫ Độc Quyền',
    '090': '⚪ Cao Cấp',
}

# ==================== BẢNG THÔNG TIN NHÂN VẬT & KỸ NĂNG FF ====================
CHARACTER_INFO = {
    1: ("Olivia", "Hồi Phục Sinh Lực (Healing Touch)"),
    2: ("Kelly", "Vận Động Viên Điền Kinh (Dash)"),
    3: ("Ford", "Ý Chí Sắt Đá (Iron Will)"),
    4: ("Andrew", "Bậc Thầy Giáp (Armor Specialist)"),
    5: ("Nikita", "Chuyên Gia Súng Tiểu Liên (Firearms Expert)"),
    6: ("Misha", "Bùng Nổ (Afterburner)"),
    7: ("Maxim", "Phàm Ăn (Gluttony)"),
    8: ("Kla", "Muay Thái (Muay Thai)"),
    9: ("Paloma", "Nữ Hoàng Đạn Dược (Arms Dealing)"),
    10: ("Miguel", "Kẻ Cuồng Tín (Crazy Slayer)"),
    11: ("Caroline", "Dẻo Dai (Agility)"),
    12: ("Wukong", "Ảo Ảnh (Camouflage)"),
    13: ("Antonio", "Ông Trùm Mafia (Gangster's Spirit)"),
    14: ("Moco", "Kính Công Nghệ (Hacker's Eye)"),
    15: ("Hayato", "Xuyên Giáp (Bushido)"),
    17: ("Laura", "Siêu Xạ Thủ (Sharp Shooter)"),
    18: ("Rafael", "Sự Im Lặng Chết Chóc (Dead Silent)"),
    19: ("A124", "Sức Nóng Chiến Trường (Thrill of Battle)"),
    20: ("Joseph", "Điên Cuồng (Nutty Movement)"),
    21: ("Shani", "Giáp Đột Kích (Gear Recycle)"),
    22: ("Alok", "Giai Điệu Sinh Mệnh (Drop the Beat)"),
    23: ("Alvaro", "Nghệ Sĩ Chất Nổ (Art of Demolition)"),
    24: ("Notora", "Phước Lành Vận Tốc (Thrilling Ride)"),
    25: ("Kelly (Thức Tỉnh)", "Tia Lửa Đạn (Dash - Awaken)"),
    26: ("Steffie", "Không Gian Sắc Màu (Painted Refuge)"),
    27: ("Jota", "Đột Kích Lấy Máu (Sustained Raids)"),
    28: ("Kapella", "Khúc Cao Trào (Healing Song)"),
    29: ("Luqueta", "Phát Súng Quyết Định (Hat-Trick)"),
    30: ("Wolfrahh", "Livestream (Limelight)"),
    31: ("Clu", "Truy Vết (Tracing Steps)"),
    32: ("Hayato (Thức Tỉnh)", "Khiên Đao (Bushido - Awaken)"),
    33: ("Jai", "Nạp Đạn Khẩn Cấp (Raging Reload)"),
    34: ("K", "Bậc Thầy (Master of All)"),
    35: ("Dasha", "Quẩy Lên (Partying On)"),
    38: ("Chrono", "Hào Quang Hộ Mệnh (Time Turner)"),
    40: ("Skyler", "Hủy Diệt Băng Thành (Riptide Rhythm)"),
    41: ("Shirou", "Ăn Miếng Trả Miếng (Damage Delivered)"),
    42: ("Andrew (Thức Tỉnh)", "Cùng Tiến Bộ (Wolfpack)"),
    43: ("Maro", "Ưng Nhãn (Falcon Fervor)"),
    44: ("Xayne", "Cuồng Bạo (Xtreme Encounter)"),
    45: ("D-bee", "Bước Di Chuyển Âm Nhạc (Bullet Beats)"),
    46: ("Thiva", "Giai Điệu Cứu Rỗi (Vital Vibes)"),
    47: ("Dimitri", "Nhịp Điệu Hồi Sinh (Healing Heartbeat)"),
    48: ("Moco (Thức Tỉnh)", "Tia Chớp Công Nghệ (Hacker's Eye - Awaken)"),
    49: ("Leon", "Điểm Đột Phá (Buzzer Beater)"),
    50: ("Otho", "Bí Thuật Tìm Kiếm (Memory Mist)"),
    51: ("Jai (Thức Tỉnh)", "Nạp Đạn Khẩn Cấp (Raging Reload)"),
    52: ("Nairi", "Keo Sắt (Ice Iron)"),
    53: ("Luna", "Nguyệt Ảnh (Fight or Flight)"),
    54: ("Kenta", "Khiên Thịnh Nộ (Swordsman's Wrath)"),
    55: ("Homer", "Bản Năng Sát Thủ (Senses Shockwave)"),
    56: ("Iris", "Xuyên Tường (Wall Brawl)"),
    57: ("J.Biebs", "Hào Quang Phòng Thủ (Silent Sentinel)"),
    58: ("Tatsuya", "Tốc Biến (Rebel Rush)"),
    60: ("Santino", "Phân Thân Vô Ảnh (Shape Splitter)"),
    61: ("J.Biebs (Thức Tỉnh)", "Hào Quang Phòng Thủ (Silent Sentinel - Awaken)"),
    62: ("Orion", "Bóng Đêm Trỗi Dậy (Crimson Crush)"),
    63: ("Alvaro (Thức Tỉnh)", "Nghệ Sĩ Chất Nổ (Art of Demolition - Awaken)"),
    65: ("Sonia", "Lá Chắn Sinh Mệnh (Nano Shield)"),
    66: ("Suzy", "Điểm Thưởng (Money Mark)"),
    67: ("Ignis", "Ranh Giới Lửa (Flame Mirage)"),
    68: ("Ryden", "Mạng Nhện Bẫy Địch (Spider Trap)"),
    69: ("Kairos", "Trạng Thái Xung Kích (Breaker Mode)"),
    70: ("Kassie", "Liên Kết Trị Liệu (Healing Bound)"),
}



def guess_item_name(item_id: str) -> str:
    """Đoán tên item dựa trên cấu trúc ID khi không có trong database"""
    if not item_id or item_id == '0':
        return "Không có"

    # Thử tìm category theo prefix dài nhất trước
    category = None
    for prefix in sorted(ID_CATEGORY_MAP.keys(), key=len, reverse=True):
        if item_id.startswith(prefix):
            category = ID_CATEGORY_MAP[prefix][1]
            break

    # Đoán độ hiếm theo ký tự ở giữa ID
    rarity = ''
    for code, name in RARITY_MAP.items():
        if code in item_id:
            rarity = f' {name}'
            break

    if category:
        return f'{category}{rarity} (#{item_id})'
    return f'Vật Phẩm #{item_id}'


# ==================== LỚP QUẢN LÝ CƠ SỞ DỮ LIỆU ====================
class ItemDatabase:
    def __init__(self):
        self.db_file = "item_database.json"
        self.item_map = {}
        self.rank_map = {}
        self.skill_names = {
            4006: 'Tăng Tốc Độ Di Chuyển',
            6606: 'Hồi Máu Nhanh',
            4806: 'Tăng Sát Thương',
            606: 'Giáp Phòng Thủ',
            2006: 'Kỹ Năng Đặc Biệt',
            2506: 'Kỹ Năng Tấn Công',
            22016: 'Kỹ Năng Phòng Thủ',
            1315000023: 'Khả Năng Tự Hồi Máu (Panda)',
            1315000001: 'Tốc Chạy +5%',
            1315000010: 'Giảm Sát Thương',
        }
        self.load_or_fetch_data()

    def load_or_fetch_data(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.item_map = data.get('items', data)
                        self.rank_map = data.get('ranks', {})
                    else:
                        self.item_map = data
                    # Merge với KNOWN_ITEMS (ưu tiên KNOWN_ITEMS vì có tên tiếng Việt)
                    self.item_map.update(KNOWN_ITEMS)
                    print(f"{Fore.GREEN}✅ Đã tải {len(self.item_map):,} vật phẩm (bao gồm dữ liệu bổ sung).")
                    return
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ Lỗi đọc file: {e}")

        urls = [
            "https://raw.githubusercontent.com/iamaanahmad/FreeFireItems/refs/heads/main/data/OB51-Items.json",
            "https://raw.githubusercontent.com/iamaanahmad/FreeFireItems/refs/heads/main/data/OB53-live-itemData.json",
            "https://raw.githubusercontent.com/iamaanahmad/FreeFireItems/refs/heads/main/data/ItemData.json",
        ]

        for url in urls:
            try:
                print(f"{Fore.YELLOW}🔄 Đang tải từ: {url}")
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        for item in data:
                            if 'id' in item and 'name' in item:
                                self.item_map[str(item['id'])] = item['name']
                            if 'rankId' in item and 'rankName' in item:
                                self.rank_map[str(item['rankId'])] = item['rankName']
                    elif isinstance(data, dict):
                        items_list = data.get('items', data.get('data', []))
                        if isinstance(items_list, list):
                            for item in items_list:
                                if 'id' in item and 'name' in item:
                                    self.item_map[str(item['id'])] = item['name']
                        else:
                            for key, value in data.items():
                                if isinstance(value, dict) and 'id' in value and 'name' in value:
                                    self.item_map[str(value['id'])] = value['name']
                    if self.item_map:
                        self.item_map.update(KNOWN_ITEMS)
                        self._save()
                        print(f"{Fore.GREEN}✅ Đã tải {len(self.item_map):,} vật phẩm.")
                        return
            except Exception as e:
                print(f"{Fore.RED}❌ Lỗi: {e}")

        print(f"{Fore.YELLOW}⚠️ Dùng dữ liệu nội bộ.")
        self.item_map = dict(KNOWN_ITEMS)
        self.load_default_ranks()
        self._save()

    def _save(self):
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump({'items': self.item_map, 'ranks': self.rank_map}, f, indent=2, ensure_ascii=False)
        except:
            pass

    def load_default_ranks(self):
        self.rank_map = {
            '1': 'Bronze I', '2': 'Bronze II', '3': 'Bronze III',
            '4': 'Silver I', '5': 'Silver II', '6': 'Silver III',
            '7': 'Gold I', '8': 'Gold II', '9': 'Gold III', '10': 'Gold IV',
            '11': 'Platinum I', '12': 'Platinum II', '13': 'Platinum III', '14': 'Platinum IV',
            '15': 'Diamond I', '16': 'Diamond II', '17': 'Diamond III', '18': 'Diamond IV',
            '19': 'Heroic', '20': 'Grandmaster', '21': 'Master', '22': 'Legendary',
            '316': 'Platinum IV', '322': 'Diamond IV', '324': 'Diamond II',
            '329': 'Grandmaster', '330': 'Grandmaster I',
        }

    def get_item_name(self, item_id):
        if not item_id:
            return "N/A"
        item_id = str(item_id)
        if item_id in ('0', ''):
            return "Không có"

        # 1. Tìm trong KNOWN_ITEMS (tiếng Việt, ưu tiên cao nhất)
        if item_id in KNOWN_ITEMS:
            return KNOWN_ITEMS[item_id]

        # 2. Tìm trong database tải về
        name = self.item_map.get(item_id)
        if name:
            return name

        # 3. Tìm trong rank_map
        rank_name = self.rank_map.get(item_id)
        if rank_name:
            return rank_name

        # 4. Đoán tên dựa trên cấu trúc ID
        return guess_item_name(item_id)

    def get_rank_name(self, rank_id):
        if not rank_id:
            return "Chưa xếp hạng"
        try:
            rank_id_str = str(rank_id)
            if rank_id_str in self.rank_map:
                return self.rank_map[rank_id_str]
            rank_num = int(rank_id_str)
            if 1 <= rank_num <= 22:
                rank_names = [
                    'Bronze I', 'Bronze II', 'Bronze III',
                    'Silver I', 'Silver II', 'Silver III',
                    'Gold I', 'Gold II', 'Gold III', 'Gold IV',
                    'Platinum I', 'Platinum II', 'Platinum III', 'Platinum IV',
                    'Diamond I', 'Diamond II', 'Diamond III', 'Diamond IV',
                    'Heroic', 'Grandmaster', 'Master', 'Legendary'
                ]
                return rank_names[rank_num - 1]
            # Rank số lớn (API trả về)
            if rank_num >= 300:
                return f'Grandmaster ({rank_num})'
            if rank_num >= 250:
                return f'Heroic ({rank_num})'
            if rank_num >= 200:
                return f'Diamond ({rank_num})'
            if rank_num >= 150:
                return f'Platinum ({rank_num})'
            return f'Rank {rank_id_str}'
        except:
            return str(rank_id)

    def get_skill_name(self, skill_id):
        if not skill_id:
            return "N/A"
        try:
            sid = int(skill_id)
            
            # 1. Tìm trong bảng thông tin kỹ năng nhân vật CHARACTER_INFO
            char_id = None
            if 100 <= sid <= 9999:
                char_id = sid // 100
            elif 10000 <= sid <= 99999:
                prefix_2 = sid // 1000
                if prefix_2 in CHARACTER_INFO:
                    char_id = prefix_2
                else:
                    prefix_3 = sid // 100
                    if prefix_3 in CHARACTER_INFO:
                        char_id = prefix_3
            
            if char_id and char_id in CHARACTER_INFO:
                char_name, skill_name = CHARACTER_INFO[char_id]
                return f"{skill_name} ({char_name})"
            
            # 2. Tìm trong skill_names mặc định
            if sid in self.skill_names:
                return self.skill_names[sid]
            
            # 3. Tìm trong database
            name = self.item_map.get(str(skill_id))
            if name:
                return name
                
            return f'Kỹ Năng #{skill_id}'
        except:
            return str(skill_id)


# ==================== LỚP CHECKER CHÍNH ====================
class FreeFireChecker:
    def __init__(self):
        self.db = ItemDatabase()
        self.token = None  # Sẽ được lấy tự động
        self.session = requests.Session()
        self._initialize_session()

    def _initialize_session(self):
        """Khởi tạo session và lấy token mới"""
        self.session = requests.Session()
        
        # Headers cơ bản
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'vi-VN,vi;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://developers.freefirecommunity.com',
            'referer': 'https://developers.freefirecommunity.com/vi/dashboard/playground',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        
        self.url = 'https://developers.freefirecommunity.com/api/playground'
        
        self.mode_names = {
            1: 'Battle Royale (Xếp Hạng)',
            2: 'Battle Royale (Thường)',
            15: 'Clash Squad (Xếp Hạng)',
            16: 'Clash Squad (Thường)',
            7: 'Lone Wolf',
            8: 'Craftlands',
        }
        self.type_names = {
            2: 'Xạ Thủ 🎯',
            6: 'Chiến Binh ⚔️',
            16: 'Hỗ Trợ 💊',
            1: 'Tấn Công 🔥',
            4: 'Phòng Thủ 🛡️',
        }
        self.rank_colors = {
            'bronze': Fore.LIGHTBLACK_EX,
            'silver': Fore.LIGHTWHITE_EX,
            'gold': Fore.YELLOW,
            'platinum': Fore.CYAN,
            'diamond': Fore.LIGHTBLUE_EX,
            'heroic': Fore.MAGENTA,
            'grandmaster': Fore.RED,
            'master': Fore.LIGHTRED_EX,
            'legendary': Fore.LIGHTYELLOW_EX,
        }

    def _get_token_from_github(self):
        """Hàm lấy token từ GitHub"""
        url = "https://raw.githubusercontent.com/tantinh202408-alt/checker/refs/heads/main/main-token.txt"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text.strip()
        except Exception as e:
            print(f"{Fore.RED}❌ Lỗi lấy token từ GitHub: {e}", file=sys.stderr)
        return None

    def _get_fresh_token(self):
        """Lấy token mới từ file token.txt, GitHub hoặc yêu cầu nhập thủ công"""
        token_file = "token.txt"
        
        # 1. Thử đọc từ file local trước
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
                    if token:
                        self.token = token
                        print(f"{Fore.GREEN}✅ Đã nạp token từ {token_file}", file=sys.stderr)
                        return token
            except Exception as e:
                print(f"{Fore.RED}❌ Lỗi đọc file token.txt: {e}", file=sys.stderr)

        # 2. Thử lấy từ GitHub
        try:
            token = self._get_token_from_github()
            if token:
                self.token = token
                # Lưu vào file token.txt để cache
                with open(token_file, 'w', encoding='utf-8') as f:
                    f.write(token)
                print(f"{Fore.GREEN}✅ Đã nạp token từ GitHub", file=sys.stderr)
                return token
        except Exception as e:
            print(f"{Fore.RED}❌ Lỗi lấy token từ GitHub: {e}", file=sys.stderr)

        # 3. Nếu không có file hoặc đọc lỗi, yêu cầu nhập thủ công từ bàn phím
        # Sử dụng sys.stderr để in thông báo để tránh ảnh hưởng đến stdout của API/CLI
        print(f"\n{Fore.YELLOW}⚠️ Token hết hạn hoặc không tìm thấy!", file=sys.stderr)
        sys.stderr.write(f"{Fore.GREEN}🔑 Vui lòng nhập Token Free Fire mới: {Fore.CYAN}")
        sys.stderr.flush()
        
        try:
            token = sys.__stdin__.readline().strip()
        except Exception:
            token = input().strip()
            
        if token:
            self.token = token
            # Lưu lại vào file cho lần sau
            try:
                with open(token_file, 'w', encoding='utf-8') as f:
                    f.write(token)
                print(f"{Fore.GREEN}✅ Đã lưu token mới vào {token_file}", file=sys.stderr)
            except Exception as e:
                print(f"{Fore.RED}❌ Lỗi lưu token vào file: {e}", file=sys.stderr)
            return token
            
        return None

    def _make_request(self, uid, region='sg'):
        """Thực hiện request với retry khi token hết hạn"""
        max_retries = 2
        
        for attempt in range(max_retries):
            if not self.token:
                self._get_fresh_token()
                if not self.token:
                    return None
            
            # Cập nhật headers với token hiện tại
            headers = {
                'authorization': f'Bearer {self.token}',
            }
            
            json_data = {
                'endpointKey': 'info',
                'region': region,
                'uid': str(uid),
                'mapCode': 'FREEFIRE625B83664022B40F67CBFBFF9CC3C1247490',
                'itemID': '908028011',
                'lang': 'en',
            }
            
            try:
                response = self.session.post(
                    self.url,
                    headers=headers,
                    json=json_data,
                    timeout=15
                )
                
                # Nếu token hết hạn (401)
                if response.status_code == 401:
                    print(f"{Fore.YELLOW}⚠️ Token hết hạn, đang xóa file token cũ và yêu cầu nhập lại...", file=sys.stderr)
                    if os.path.exists("token.txt"):
                        try:
                            os.remove("token.txt")
                        except:
                            pass
                    self.token = None  # Reset token
                    if attempt < max_retries - 1:
                        continue  # Thử lại
                    else:
                        print(f"{Fore.RED}❌ Không thể lấy token mới sau {max_retries} lần thử", file=sys.stderr)
                        return None
                
                # Request thành công
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"{Fore.RED}❌ Lỗi HTTP {response.status_code}")
                    if attempt < max_retries - 1:
                        print(f"{Fore.YELLOW}🔄 Đang thử lại...")
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"{Fore.RED}❌ Quá thời gian chờ!")
                if attempt < max_retries - 1:
                    continue
                return None
            except requests.exceptions.RequestException as e:
                print(f"{Fore.RED}❌ Lỗi kết nối: {e}")
                if attempt < max_retries - 1:
                    continue
                return None
            except json.JSONDecodeError as e:
                print(f"{Fore.RED}❌ Lỗi parse JSON: {e}")
                return None
        
        return None

    # ==================== TIỆN ÍCH ====================
    def get_rank_color(self, rank_name: str):
        rn = rank_name.lower()
        for key, color in self.rank_colors.items():
            if key in rn:
                return color
        return Fore.WHITE

    def format_number(self, num):
        if num is None or num == '':
            return "N/A"
        try:
            n = float(str(num).replace(',', '').strip())
            return f"{int(n):,}" if n == int(n) else f"{n:,.2f}"
        except:
            return str(num)

    def format_date(self, timestamp):
        if not timestamp:
            return "N/A"
        try:
            ts = timestamp if isinstance(timestamp, (int, float)) else int(timestamp)
            return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M:%S")
        except:
            return str(timestamp)

    def bool_str(self, value):
        return "✅" if value else "❌"

    # ==================== HIỂN THỊ ====================
    def print_header(self, title, length=80):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * length}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}{title.center(length)}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * length}")

    def print_section(self, title):
        pad = max(0, 68 - len(title))
        print(f"\n{Fore.GREEN}{Style.BRIGHT}┌─ {title} {'─' * pad}")

    def print_info(self, label, value, color=Fore.WHITE):
        print(f"{Fore.LIGHTBLACK_EX}│  {Fore.LIGHTWHITE_EX}{label}: {color}{value}{Style.RESET_ALL}")

    def print_2_columns(self, title_left, left_items, title_right, right_items, border_color=Fore.CYAN):
        """Hàm phụ trợ in thông tin chia làm 2 cột có độ dài tự động căn chỉnh hoàn hảo"""
        # left_items và right_items là list các tuple: (label, value, value_color)
        left_col = [("header", title_left)] + left_items
        right_col = [("header", title_right)] + right_items
        
        max_visible_left = 0
        for item in left_col:
            if item[0] == "header":
                visible_len = visual_len(item[1])
            else:
                label, value, _ = item
                raw_text = f"{label:<15}: {value}"
                visible_len = visual_len(raw_text)
            if visible_len > max_visible_left:
                max_visible_left = visible_len
                
        max_visible_right = 0
        for item in right_col:
            if item[0] == "header":
                visible_len = visual_len(item[1])
            else:
                label, value, _ = item
                raw_text = f"{label:<15}: {value}"
                visible_len = visual_len(raw_text)
            if visible_len > max_visible_right:
                max_visible_right = visible_len
                
        col_width_left = max_visible_left + 2
        col_width_right = max_visible_right + 2
        
        # In viền trên
        print(f"{border_color}┌{'─' * (col_width_left + 4)}┬{'─' * (col_width_right + 4)}┐")
        
        max_len = max(len(left_col), len(right_col))
        for i in range(max_len):
            left_text = ""
            right_text = ""
            
            if i < len(left_col):
                item = left_col[i]
                if item[0] == "header":
                    left_text = f"{Fore.GREEN}{Style.BRIGHT}{item[1]}"
                else:
                    label, value, color = item
                    left_text = f"{Fore.LIGHTWHITE_EX}{label:<15}: {color}{value}"
                    
            if i < len(right_col):
                item = right_col[i]
                if item[0] == "header":
                    right_text = f"{Fore.GREEN}{Style.BRIGHT}{item[1]}"
                else:
                    label, value, color = item
                    right_text = f"{Fore.LIGHTWHITE_EX}{label:<15}: {color}{value}"
                    
            left_visible_len = visual_len(left_text)
            right_visible_len = visual_len(right_text)
            
            left_pad = col_width_left - left_visible_len
            right_pad = col_width_right - right_visible_len
            
            left_padded = left_text + (' ' * left_pad)
            right_padded = right_text + (' ' * right_pad)
            
            print(f"{border_color}│  {left_padded}  │  {right_padded}  │")
            
            if i == 0:
                print(f"{border_color}├{'─' * (col_width_left + 4)}┼{'─' * (col_width_right + 4)}┤")
                
        print(f"{border_color}└{'─' * (col_width_left + 4)}┴{'─' * (col_width_right + 4)}┘")

    def get_formatted_data(self, data):
        if not data or data.get('status') == 'error':
            return {"status": "error", "message": data.get('message', 'Unknown error') if data else 'Không có dữ liệu'}

        basic = data.get('basicInfo') or {}
        clan = data.get('clanBasicInfo') or {}
        credit = data.get('creditScoreInfo') or {}
        diamond = data.get('diamondCostRes') or {}
        profile = data.get('profileInfo') or {}
        pet = data.get('petInfo') or {}
        captain = data.get('captainBasicInfo') or {}
        social = data.get('socialInfo') or {}
        prime = basic.get('primePrivilegeDetail') or {}

        # Basic Info
        basic_info = {
            "uid": str(basic.get('accountId', 'N/A')),
            "nickname": str(basic.get('nickname', 'N/A')),
            "level": f"Lv.{basic.get('level', 'N/A')}",
            "exp": self.format_number(basic.get('exp')),
            "region": str(basic.get('region', 'N/A')),
            "release_version": str(basic.get('releaseVersion', 'N/A')),
            "season": f"S{basic.get('seasonId', 'N/A')}",
            "liked": f"❤️  {self.format_number(basic.get('liked'))}",
            "account_type": str(basic.get('accountType', 'N/A'))
        }

        # Rank Info
        rid = basic.get('rank')
        rname = self.db.get_rank_name(rid)
        pts = self.format_number(basic.get('rankingPoints'))
        
        rid_max = basic.get('maxRank')
        rname_max = self.db.get_rank_name(rid_max)
        
        rid_cs = basic.get('csRank')
        rname_cs = self.db.get_rank_name(rid_cs)
        pts_cs = self.format_number(basic.get('csRankingPoints'))
        
        rid_cs_max = basic.get('csMaxRank')
        rname_cs_max = self.db.get_rank_name(rid_cs_max)
        
        show_br = self.bool_str(basic.get('showBrRank'))
        show_cs = self.bool_str(basic.get('showCsRank'))
        show_all = self.bool_str(basic.get('showRank'))

        rank_info = {
            "rank_br": f"{rname}  [{pts} điểm]",
            "max_br": rname_max,
            "rank_cs": f"{rname_cs}  [{pts_cs} điểm]",
            "max_cs": rname_cs_max,
            "show_rank": f"BR {show_br}  CS {show_cs}  Chung {show_all}"
        }

        # Clan Info
        clan_info = {}
        if clan:
            clan_info = {
                "clan_name": str(clan.get('clanName', 'N/A')),
                "clan_id": str(clan.get('clanId', 'N/A')),
                "clan_level": f"Lv.{clan.get('clanLevel', 'N/A')}",
                "members": f"{clan.get('memberNum', '?')}/{clan.get('capacity', '?')}"
            }
        else:
            clan_info = {
                "clan_name": "Không có",
                "clan_id": "N/A",
                "clan_level": "N/A",
                "members": "N/A"
            }

        # Time Info
        time_info = {
            "create_at": self.format_date(basic.get('createAt')),
            "last_login_at": self.format_date(basic.get('lastLoginAt'))
        }

        # Credit & Diamond
        credit_info = {}
        if credit:
            score = credit.get('creditScore', 0)
            status = "✅ Đang Hoạt Động" if credit.get('rewardState') == 1 else "❌ Không Hoạt Động"
            credit_info = {
                "credit_score": score,
                "status": status,
                "reward_start_at": self.format_date(credit.get('rewardStartAt')),
                "reward_end_at": self.format_date(credit.get('rewardEndAt'))
            }
        else:
            credit_info = {
                "credit_score": "N/A",
                "status": "N/A",
                "reward_start_at": "N/A",
                "reward_end_at": "N/A"
            }

        diamond_info = {
            "diamond_cost": f"💎 {self.format_number(diamond.get('diamondCost'))}" if diamond else "💎 0"
        }

        # Clothes
        clothes_list = []
        if profile:
            clothes = profile.get('clothes') or []
            if clothes:
                for cloth in clothes:
                    if cloth:
                        cloth_str = str(cloth)
                        name = self.db.get_item_name(cloth_str)
                        label = "Vật Phẩm"
                        for prefix in sorted(ID_CATEGORY_MAP.keys(), key=len, reverse=True):
                            if cloth_str.startswith(prefix):
                                label = ID_CATEGORY_MAP[prefix][0]
                                break
                        clothes_list.append({"category": label, "name": name})
        
        # Accessories
        accessories = {}
        if profile:
            avatar_id = profile.get('avatarId')
            if avatar_id:
                accessories["avatar"] = self.db.get_item_name(str(avatar_id))

        badge_id = basic.get('badgeId')
        if badge_id:
            accessories["badge"] = self.db.get_item_name(str(badge_id))
        accessories["badge_count"] = f"{basic.get('badgeCnt', 'N/A')} huy hiệu"
        
        title_id = basic.get('title')
        if title_id:
            accessories["title"] = self.db.get_item_name(str(title_id))
            
        banner_id = basic.get('bannerId')
        if banner_id:
            accessories["banner"] = self.db.get_item_name(str(banner_id))
            
        head_pic = basic.get('headPic')
        if head_pic:
            accessories["head_pic"] = self.db.get_item_name(str(head_pic))
            
        pin_id = basic.get('pinId')
        if pin_id:
            accessories["pin"] = self.db.get_item_name(str(pin_id))

        # Pet Info
        pet_info = {}
        if pet:
            pet_id = str(pet.get('id', ''))
            pet_name = self.db.get_item_name(pet_id)
            pet_info = {
                "name": f"{pet_name} (Lv.{pet.get('level', 'N/A')})",
                "skin": self.db.get_item_name(str(pet.get('skinId'))) if pet.get('skinId') else None,
                "skill": self.db.get_skill_name(pet.get('selectedSkillId')) if pet.get('selectedSkillId') else None
            }

        # Character & Skills
        character_info = {}
        if profile:
            skills = profile.get('equipedSkills') or []
            active_character = "Chưa xác định"
            if skills:
                main_skill = None
                for skill in skills:
                    slot = skill.get('slotId')
                    if slot is None or slot == 0:
                        main_skill = skill.get('skillId')
                        break
                if not main_skill and len(skills) > 0:
                    main_skill = skills[0].get('skillId')
                
                if main_skill:
                    try:
                        msid = int(main_skill)
                        char_id = None
                        if 100 <= msid <= 9999:
                            char_id = msid // 100
                        elif 10000 <= msid <= 99999:
                            prefix_2 = msid // 1000
                            if prefix_2 in CHARACTER_INFO:
                                char_id = prefix_2
                            else:
                                prefix_3 = msid // 100
                                if prefix_3 in CHARACTER_INFO:
                                    char_id = prefix_3
                        if char_id and char_id in CHARACTER_INFO:
                            active_character = CHARACTER_INFO[char_id][0]
                    except:
                        pass
            
            character_info["name"] = active_character
            character_info["awakened"] = self.bool_str(profile.get('isSelectedAwaken'))

            skills_list = []
            if skills:
                slot_labels = {0: 'Kỹ năng chính', 1: 'Slot 1', 2: 'Slot 2', 3: 'Slot 3'}
                for skill in skills:
                    sid = skill.get('skillId')
                    slot = skill.get('slotId', 0)
                    if slot is None:
                        slot = 0
                    if sid:
                        sname = self.db.get_skill_name(sid)
                        slot_text = slot_labels.get(slot, f'Slot {slot}')
                        skills_list.append({"slot": slot_text, "name": sname})
            character_info["skills"] = skills_list

        # Captain / Prime & Social
        has_captain = captain and str(captain.get('accountId', '')) != str(basic.get('accountId', ''))
        captain_info = {}
        social_info = {}

        if has_captain:
            cap_rname = self.db.get_rank_name(captain.get('rank'))
            cap_cs_rname = self.db.get_rank_name(captain.get('csRank'))
            captain_info = {
                "captain_id": str(captain.get('accountId', 'N/A')),
                "captain_name": str(captain.get('nickname', 'N/A')),
                "captain_level": f"Lv.{captain.get('level', 'N/A')}",
                "captain_rank_br": cap_rname,
                "captain_rank_cs": cap_cs_rname
            }
        else:
            if prime:
                lvl = prime.get('primeLevel', 'N/A')
                social_info["prime_level"] = f"⭐ Level {lvl}"
            else:
                social_info["prime_level"] = "Không tham gia"

            if social:
                sig = social.get('signature', '')
                if sig:
                    social_info["signature"] = sig

        # Weapon Skins
        weapon_skins_list = []
        weapon_skins = basic.get('weaponSkinShows') or []
        if weapon_skins:
            for skin in weapon_skins:
                if skin:
                    weapon_skins_list.append(self.db.get_item_name(str(skin)))

        # Favorite Game Modes
        favorite_modes = []
        select_occ = basic.get('selectOccupations') or []
        if select_occ:
            for occ in select_occ:
                mode_id = occ.get('modeId')
                mode_name = self.mode_names.get(mode_id, f'Chế Độ {mode_id}')
                type_id = occ.get('type')
                type_name = self.type_names.get(type_id, f'Loại {type_id}')
                season = occ.get('seasonId', 'N/A')
                details = occ.get('details') or {}
                
                stats = {}
                if details:
                    d = details
                    if d.get('key2'): stats["matches"] = d['key2']
                    if d.get('key3'): stats["wins"] = d['key3']
                    if d.get('key4'): stats["booyahs"] = d['key4']
                
                favorite_modes.append({
                    "mode": f"{mode_name} (Season S{season})",
                    "role": type_name,
                    "stats": stats
                })

        return {
            "status": "success",
            "basic_info": basic_info,
            "rank_info": rank_info,
            "clan_info": clan_info,
            "time_info": time_info,
            "credit_info": credit_info,
            "diamond_info": diamond_info,
            "clothes": clothes_list,
            "accessories": accessories,
            "pet_info": pet_info,
            "character_info": character_info,
            "captain_info": captain_info if has_captain else None,
            "social_info": social_info if not has_captain else None,
            "weapon_skins": weapon_skins_list,
            "favorite_modes": favorite_modes
        }

    def print_account_info(self, data):
        """Hiển thị thông tin tài khoản với bố cục 2 cột và màu sắc cầu vồng sặc sỡ"""
        if not data or data.get('status') == 'error':
            msg = data.get('message', 'Unknown error') if data else 'Không có dữ liệu'
            print(f"{Fore.RED}❌ Lỗi: {msg}")
            return

        formatted = self.get_formatted_data(data)
        if formatted.get('status') == 'error':
            print(f"{Fore.RED}❌ Lỗi: {formatted.get('message')}")
            return

        self.print_header("📊 THÔNG TIN TÀI KHOẢN FREE FIRE")

        # ======================================================================
        # KHỐI 1: THÔNG TIN CƠ BẢN & CẤP BẬC (Viền Fore.RED)
        # ======================================================================
        b_info = formatted['basic_info']
        left_1 = [
            ("UID", b_info['uid'], Fore.CYAN),
            ("Tên", b_info['nickname'], Fore.YELLOW + Style.BRIGHT),
            ("Cấp độ", b_info['level'], Fore.MAGENTA),
            ("EXP", b_info['exp'], Fore.LIGHTGREEN_EX),
            ("Khu vực", b_info['region'], Fore.CYAN),
            ("Phiên bản", b_info['release_version'], Fore.LIGHTBLUE_EX),
            ("Season", b_info['season'], Fore.LIGHTBLUE_EX),
            ("Lượt thích", b_info['liked'], Fore.LIGHTRED_EX),
            ("Loại TK", b_info['account_type'], Fore.LIGHTWHITE_EX),
        ]

        r_info = formatted['rank_info']
        rcolor = self.get_rank_color(r_info['rank_br'])
        rcolor_max = self.get_rank_color(r_info['max_br'])
        rcolor_cs = self.get_rank_color(r_info['rank_cs'])
        rcolor_cs_max = self.get_rank_color(r_info['max_cs'])

        right_1 = [
            ("Rank BR", r_info['rank_br'], rcolor),
            ("Max BR", r_info['max_br'], rcolor_max),
            ("Rank CS", r_info['rank_cs'], rcolor_cs),
            ("Max CS", r_info['max_cs'], rcolor_cs_max),
            ("Hiển thị rank", r_info['show_rank'], Fore.WHITE),
        ]

        self.print_2_columns("👤 THÔNG TIN CƠ BẢN", left_1, "🏆 CẤP BẬC", right_1, Fore.RED)

        # ======================================================================
        # KHỐI 2: CLAN & CREDIT, DIAMOND (Viền Fore.YELLOW)
        # ======================================================================
        left_2 = []
        clan_f = formatted['clan_info']
        if clan_f.get('clan_name') != "Không có":
            left_2.append(("Tên Clan", clan_f['clan_name'], Fore.YELLOW))
            left_2.append(("ID Clan", clan_f['clan_id'], Fore.CYAN))
            left_2.append(("Cấp độ Clan", clan_f['clan_level'], Fore.MAGENTA))
            left_2.append(("Thành viên", clan_f['members'], Fore.LIGHTGREEN_EX))
        else:
            left_2.append(("Tên Clan", "Không có", Fore.LIGHTBLACK_EX))

        time_f = formatted['time_info']
        left_2.append(("Ngày tạo TK", time_f['create_at'], Fore.LIGHTGREEN_EX))
        left_2.append(("Đăng nhập", time_f['last_login_at'], Fore.LIGHTYELLOW_EX))

        right_2 = []
        credit_f = formatted['credit_info']
        if credit_f.get('credit_score') != "N/A":
            score = credit_f['credit_score']
            score_color = Fore.GREEN if isinstance(score, int) and score >= 80 else Fore.YELLOW if isinstance(score, int) and score >= 50 else Fore.RED
            right_2.append(("Điểm Credit", score, score_color))
            right_2.append(("Trạng thái", credit_f['status'], Fore.LIGHTGREEN_EX))
            right_2.append(("Bắt đầu", credit_f['reward_start_at'], Fore.LIGHTYELLOW_EX))
            right_2.append(("Kết thúc", credit_f['reward_end_at'], Fore.LIGHTYELLOW_EX))
        else:
            right_2.append(("Điểm Credit", "N/A", Fore.LIGHTBLACK_EX))

        right_2.append(("Tổng nạp", formatted['diamond_info']['diamond_cost'], Fore.CYAN))

        self.print_2_columns("🏠 CLAN & THỜI GIAN", left_2, "💳 CREDIT & DIAMOND", right_2, Fore.YELLOW)

        # ======================================================================
        # KHỐI 3: TRANG PHỤC MẶC & PHỤ KIỆN (Viền Fore.GREEN)
        # ======================================================================
        left_3 = []
        clothes_f = formatted['clothes']
        if clothes_f:
            for cloth in clothes_f:
                left_3.append((cloth['category'], cloth['name'], Fore.WHITE))
        else:
            left_3.append(("Trang phục", "Không mặc đồ", Fore.LIGHTBLACK_EX))

        right_3 = []
        acc_f = formatted['accessories']
        if "avatar" in acc_f:
            right_3.append(("Avatar", acc_f['avatar'], Fore.LIGHTBLUE_EX))
        if "badge" in acc_f:
            right_3.append(("Huy hiệu", acc_f['badge'], Fore.LIGHTYELLOW_EX))
        right_3.append(("Số lượng HH", acc_f['badge_count'], Fore.LIGHTBLUE_EX))
        if "title" in acc_f:
            right_3.append(("Danh hiệu", acc_f['title'], Fore.LIGHTRED_EX))
        if "banner" in acc_f:
            right_3.append(("Banner", acc_f['banner'], Fore.LIGHTMAGENTA_EX))
        if "head_pic" in acc_f:
            right_3.append(("Khung ảnh", acc_f['head_pic'], Fore.LIGHTBLUE_EX))
        if "pin" in acc_f:
            right_3.append(("Pin", acc_f['pin'], Fore.LIGHTYELLOW_EX))

        pet_f = formatted['pet_info']
        if pet_f:
            right_3.append(("Pet", pet_f['name'], Fore.YELLOW))
            if pet_f.get('skin'):
                right_3.append(("  └─ Skin", pet_f['skin'], Fore.LIGHTBLUE_EX))
            if pet_f.get('skill'):
                right_3.append(("  └─ Kỹ năng", pet_f['skill'], Fore.LIGHTYELLOW_EX))

        self.print_2_columns("👗 TRANG PHỤC ĐANG MẶC", left_3, "🐾 PHỤ KIỆN & THÚ CƯNG", right_3, Fore.GREEN)

        # ======================================================================
        # KHỐI 4: NHÂN VẬT & KỸ NĂNG (Viền Fore.CYAN)
        # ======================================================================
        left_4 = []
        char_f = formatted['character_info']
        if char_f and "name" in char_f:
            left_4.append(("Nhân vật", char_f['name'], Fore.YELLOW + Style.BRIGHT))
            awakened_val = data.get('profileInfo', {}).get('isSelectedAwaken') if data else False
            left_4.append(("Đã thức tỉnh", char_f['awakened'], Fore.GREEN if awakened_val else Fore.RED))

            skills_f = char_f.get('skills', [])
            if skills_f:
                for skill in skills_f:
                    left_4.append((skill['slot'], skill['name'], Fore.WHITE))
        else:
            left_4.append(("Nhân vật", "N/A", Fore.LIGHTBLACK_EX))

        right_4 = []
        cap_f = formatted.get('captain_info')
        if cap_f:
            right_4.append(("Trưởng nhóm ID", cap_f['captain_id'], Fore.CYAN))
            right_4.append(("Tên Trưởng nhóm", cap_f['captain_name'], Fore.YELLOW))
            right_4.append(("Cấp độ TN", cap_f['captain_level'], Fore.MAGENTA))
            
            cap_rname = cap_f['captain_rank_br']
            right_4.append(("Rank BR TN", cap_rname, self.get_rank_color(cap_rname)))
            cap_cs_rname = cap_f['captain_rank_cs']
            right_4.append(("Rank CS TN", cap_cs_rname, self.get_rank_color(cap_cs_rname)))
        else:
            social_f = formatted.get('social_info') or {}
            right_4.append(("Prime Level", social_f.get('prime_level', 'Không tham gia'), Fore.LIGHTYELLOW_EX))
            if "signature" in social_f:
                right_4.append(("Signature", social_f['signature'], Fore.LIGHTMAGENTA_EX))

        title_right_4 = "👑 THÔNG TIN TRƯỞNG NHÓM" if cap_f else "⭐ PRIME & SOCIAL"
        self.print_2_columns("⚡ NHÂN VẬT & KỸ NĂNG", left_4, title_right_4, right_4, Fore.CYAN)

        # ======================================================================
        # PHẦN VŨ KHÍ SKIN (Khối rộng bên dưới)
        # ======================================================================
        weapon_skins_f = formatted['weapon_skins']
        if weapon_skins_f:
            title = "🔫 VŨ KHÍ SKIN ĐANG SHOW"
            pad = max(0, 68 - len(title))
            print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌─ {title} {'─' * pad}┐")
            for skin_name in weapon_skins_f:
                skin_line = f" 🔫 {skin_name}"
                visible_len = visual_len(skin_line)
                pad_right = max(0, 72 - visible_len)
                print(f"{Fore.MAGENTA}│ {Fore.WHITE}{skin_line}{' ' * pad_right} {Fore.MAGENTA}│")
            print(f"{Fore.MAGENTA}└{'─' * 74}┘")

        # ======================================================================
        # CHẾ ĐỘ CHƠI YÊU THÍCH (Khối rộng bên dưới)
        # ======================================================================
        favorite_modes_f = formatted['favorite_modes']
        if favorite_modes_f:
            title = "🎮 CHẾ ĐỘ CHƠI YÊU THÍCH"
            pad = max(0, 68 - len(title))
            print(f"\n{Fore.BLUE}{Style.BRIGHT}┌─ {title} {'─' * pad}┐")
            for idx, occ in enumerate(favorite_modes_f, 1):
                mode_name_season = occ['mode']
                type_name = occ['role']
                
                header_line = f" #{idx} {mode_name_season}"
                role_line = f"   └─ Vai trò : {type_name}"
                
                stats = []
                stats_dict = occ['stats']
                if stats_dict:
                    if "matches" in stats_dict: stats.append(f"Trận: {stats_dict['matches']}")
                    if "wins" in stats_dict: stats.append(f"Thắng: {stats_dict['wins']}")
                    if "booyahs" in stats_dict: stats.append(f"Booyah: {stats_dict['booyahs']}")
                
                stats_line = f"   └─ Thống kê: {' | '.join(stats)}" if stats else ""

                for line in [header_line, role_line]:
                    visible_len = visual_len(line)
                    pad_right = max(0, 72 - visible_len)
                    print(f"{Fore.BLUE}│ {Fore.YELLOW if line == header_line else Fore.LIGHTWHITE_EX}{line}{' ' * pad_right} {Fore.BLUE}│")
                
                if stats_line:
                    visible_len = visual_len(stats_line)
                    pad_right = max(0, 72 - visible_len)
                    print(f"{Fore.BLUE}│ {Fore.LIGHTMAGENTA_EX}{stats_line}{' ' * pad_right} {Fore.BLUE}│")

            print(f"{Fore.BLUE}└{'─' * 74}┘")

        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 80}{Style.RESET_ALL}\n")


    # ==================== API ====================
    def check_account(self, uid, region='sg'):
        """Kiểm tra tài khoản với retry tự động"""
        print(f"\n{Fore.YELLOW}🔄 Đang kiểm tra UID: {Fore.CYAN}{uid}{Fore.YELLOW}...")
        
        data = self._make_request(uid, region)
        
        if data:
            # Xóa màn hình để tránh log thừa
            os.system('cls' if os.name == 'nt' else 'clear')
            # In lại logo
            print(LOGO)
            self.print_account_info(data)
            return data
        else:
            print(f"{Fore.RED}❌ Không thể lấy thông tin tài khoản")
            return None


class FreeFireApiHandler(BaseHTTPRequestHandler):
    checker = None

    def log_message(self, format, *args):
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        
        if path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return

        uid = None
        # 1. Check query parameter 'uid'
        if 'uid' in query:
            uid = query['uid'][0]
        else:
            # 2. Check path, e.g. /10000001
            parts = path.strip('/').split('/')
            if parts and parts[0].isdigit():
                uid = parts[0]
                
        region = query.get('region', ['sg'])[0]
        
        if not uid:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "error", "message": "Thiếu tham số 'uid'"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
            
        data = self.checker._make_request(uid, region)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if data:
            formatted = self.checker.get_formatted_data(data)
            self.wfile.write(json.dumps(formatted, ensure_ascii=False).encode('utf-8'))
        else:
            response = {"status": "error", "message": "Không thể lấy thông tin tài khoản"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))


# ==================== MAIN ====================
def main():
    # Parse command line arguments
    args = sys.argv[1:]
    mode = 'interactive'
    port = 8080
    uid = None
    region = 'sg'

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '--port' and i + 1 < len(args):
            try:
                port = int(args[i+1])
                i += 2
                continue
            except ValueError:
                pass
        elif arg.startswith('port='):
            try:
                port = int(arg.split('=', 1)[1])
            except ValueError:
                pass
        elif arg.startswith('region='):
            region = arg.split('=', 1)[1]
        elif arg in ['sg', 'vn', 'us', 'in', 'br', 'ru']:
            region = arg
        elif arg in ['api', 'server', 'web']:
            mode = 'api'
        elif arg.isdigit():
            if len(arg) >= 7:
                uid = arg
                mode = 'cli'
            else:
                try:
                    val = int(arg)
                    if 1024 <= val <= 65535:
                        port = val
                    else:
                        uid = arg
                        mode = 'cli'
                except ValueError:
                    uid = arg
                    mode = 'cli'
        else:
            clean_arg = arg
            if clean_arg.startswith('uid='):
                clean_arg = clean_arg[4:]
            elif clean_arg.startswith('='):
                clean_arg = clean_arg[1:]
            
            if clean_arg.isdigit():
                uid = clean_arg
                mode = 'cli'
        i += 1

    if mode == 'api':
        # Khởi động server API
        print(f"{Fore.GREEN}🚀 Đang khởi động Web API Server tại http://0.0.0.0:{port}")
        print(f"{Fore.YELLOW}📌 Các endpoint được hỗ trợ:")
        print(f"  • GET http://localhost:{port}/<uid>")
        print(f"  • GET http://localhost:{port}/api?uid=<uid>&region=<region>")
        print(f"  • GET http://localhost:{port}/?uid=<uid>")
        
        # Để ẩn các log tải dữ liệu/token trên stdout, tạm thời hướng qua stderr
        original_stdout = sys.stdout
        sys.stdout = sys.stderr
        try:
            checker = FreeFireChecker()
            FreeFireApiHandler.checker = checker
        finally:
            sys.stdout = original_stdout

        server = HTTPServer(('0.0.0.0', port), FreeFireApiHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Đang tắt Web API Server...")
            server.server_close()
        return

    if mode == 'cli' and uid:
        # Kiểu 2: In ra JSON dựa trên kết quả đã format của cách 1
        # Chuyển hướng stdout sang stderr trong lúc fetch để tránh các log thừa làm bẩn output JSON
        original_stdout = sys.stdout
        sys.stdout = sys.stderr
        try:
            checker = FreeFireChecker()
            data = checker._make_request(uid, region)
            if data:
                formatted = checker.get_formatted_data(data)
                output = json.dumps(formatted, ensure_ascii=False, indent=2)
            else:
                output = json.dumps({"status": "error", "message": "Không thể lấy thông tin tài khoản"}, ensure_ascii=False, indent=2)
        finally:
            sys.stdout = original_stdout
        
        print(output)
        return

    # Cách 1: Chạy tương tác như cũ
    checker = FreeFireChecker()
    # Xóa màn hình trước khi thực thi nội dung
    os.system('cls' if os.name == 'nt' else 'clear')

    # In logo
    print(LOGO)
    print(f"\n{Fore.WHITE}📌 {Fore.GREEN}Hướng dẫn:")
    print(f"  {Fore.LIGHTBLACK_EX}• {Fore.WHITE}Nhập UID để kiểm tra thông tin tài khoản")
    print(f"  {Fore.LIGHTBLACK_EX}• {Fore.WHITE}Nhập {Fore.YELLOW}'quit'{Fore.WHITE} hoặc {Fore.YELLOW}'exit'{Fore.WHITE} để thoát")
    print(f"  {Fore.LIGHTBLACK_EX}• {Fore.WHITE}Tự động retry khi token hết hạn")
    print(f"{Fore.LIGHTBLACK_EX}{'─' * 80}")

    while True:
        try:
            uid_input = input(f"\n{Fore.GREEN}📝 {Fore.WHITE}Nhập UID: {Fore.CYAN}").strip()
            if uid_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Fore.YELLOW}👋 Tạm biệt!{Style.RESET_ALL}")
                break
            if not uid_input.isdigit():
                print(f"{Fore.RED}⚠️ UID chỉ chứa số!")
                continue
            checker.check_account(uid_input)
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Đã thoát!")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
