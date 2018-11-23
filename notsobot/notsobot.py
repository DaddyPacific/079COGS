# https://github.com/NotSoSuper/NotSoBot

import asyncio, aiohttp, discord
import os, sys, linecache, traceback, glob
import re, json, random, math, html
import wand, wand.color, wand.drawing
import PIL, PIL.Image, PIL.ImageFont, PIL.ImageOps, PIL.ImageDraw
import numpy as np
import cairosvg, jpglitch
import hashlib, base64
from .pixelsort import sorter, sorting, interval
from .pixelsort import util as ps_util
from .vw import macintoshplus
from urllib.parse import parse_qs
from lxml import etree
from imgurpython import ImgurClient
from io import BytesIO, StringIO
from redbot.core import commands
from redbot.core import checks
from pyfiglet import figlet_format
from string import ascii_lowercase as alphabet
from urllib.parse import quote
from concurrent.futures._base import CancelledError
import random, uuid

from redbot.core.data_manager import bundled_data_path

try:
    import aalib
    AALIB_INSTALLED = True
except:
    AALIB_INSTALLED = False

code = "```py\n{0}\n```"

#http://stackoverflow.com/a/34084933
#for google_scrap
def get_deep_text(element):
    try:
        text = element.text or ''
        for subelement in element:
          text += get_deep_text(subelement)
        text += element.tail or ''
        return text
    except:
        return ''

def posnum(num): 
    if num < 0 : 
        return - (num)
    else:
        return num

def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
    A = np.matrix(matrix, dtype=np.float)
    B = np.array(pb).reshape(8)
    res = np.dot(np.linalg.inv(A.T*A)*A.T, B)
    return np.array(res).reshape(8)

class DataProtocol(asyncio.SubprocessProtocol):
    def __init__(self, exit_future):
        self.exit_future = exit_future
        self.output = bytearray()

    def pipe_data_received(self, fd, data):
        self.output.extend(data)

    def process_exited(self):
        try:
            self.exit_future.set_result(True)
        except:
            pass

    def pipe_connection_lost(self, fd, exc):
        try:
            self.exit_future.set_result(True)
        except:
            pass
    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        try:
            self.exit_future.set_result(True)
        except:
            pass

class NotSoBot(getattr(commands, "Cog", object)):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.imgur_client = ImgurClient("", "")
        except:
            bot.remove_command('imgur')
        self.image_cache = {}
        self.search_cache = {}
        self.youtube_cache = {}
        self.twitch_cache = []
        self.api_count = 0
        self.emojis = {"soccer": "⚽", "basketball": "🏀", "football": "🏈", "baseball": "⚾", "tennis": "🎾", "volleyball": "🏐", "rugby_football": "🏉", "8ball": "🎱", "golf": "⛳", "golfer": "🏌", "ping_pong": "🏓", "badminton": "🏸", "hockey": "🏒", "field_hockey": "🏑", "cricket": "🏏", "ski": "🎿", "skier": "⛷", "snowboarder": "🏂", "ice_skate": "⛸", "bow_and_arrow": "🏹", "fishing_pole_and_fish": "🎣", "rowboat": "🚣", "swimmer": "🏊", "surfer": "🏄", "bath": "🛀", "basketball_player": "⛹", "lifter": "🏋", "bicyclist": "🚴", "mountain_bicyclist": "🚵", "horse_racing": "🏇", "levitate": "🕴", "trophy": "🏆", "running_shirt_with_sash": "🎽", "medal": "🏅", "military_medal": "🎖", "reminder_ribbon": "🎗", "rosette": "🏵", "ticket": "🎫", "tickets": "🎟", "performing_arts": "🎭", "art": "🎨", "circus_tent": "🎪", "microphone": "🎤", "headphones": "🎧", "musical_score": "🎼", "musical_keyboard": "🎹", "saxophone": "🎷", "trumpet": "🎺", "guitar": "🎸", "violin": "🎻", "clapper": "🎬", "video_game": "🎮", "space_invader": "👾", "dart": "🎯", "game_die": "🎲", "slot_machine": "🎰", "bowling": "🎳", "♡": "heart", "green_apple": "🍏", "apple": "🍎", "pear": "🍐", "tangerine": "🍊", "lemon": "🍋", "banana": "🍌", "watermelon": "🍉", "grapes": "🍇", "strawberry": "🍓", "melon": "🍈", "cherries": "🍒", "peach": "🍑", "pineapple": "🍍", "tomato": "🍅", "eggplant": "🍆", "hot_pepper": "🌶", "corn": "🌽", "sweet_potato": "🍠", "honey_pot": "🍯", "bread": "🍞", "cheese": "🧀", "poultry_leg": "🍗", "meat_on_bone": "🍖", "fried_shrimp": "🍤", "egg": "🍳", "cooking": "🍳", "hamburger": "🍔", "fries": "🍟", "hotdog": "🌭", "pizza": "🍕", "spaghetti": "🍝", "taco": "🌮", "burrito": "🌯", "ramen": "🍜", "stew": "🍲", "fish_cake": "🍥", "sushi": "🍣", "bento": "🍱", "curry": "🍛", "rice_ball": "🍙", "rice": "🍚", "rice_cracker": "🍘", "oden": "🍢", "dango": "🍡", "shaved_ice": "🍧", "ice_cream": "🍨", "icecream": "🍦", "cake": "🍰", "birthday": "🎂", "custard": "🍮", "candy": "🍬", "lollipop": "🍭", "chocolate_bar": "🍫", "popcorn": "🍿", "doughnut": "🍩", "cookie": "🍪", "beer": "🍺", "beers": "🍻", "wine_glass": "🍷", "cocktail": "🍸", "tropical_drink": "🍹", "champagne": "🍾", "sake": "🍶", "tea": "🍵", "coffee": "☕", "baby_bottle": "🍼", "fork_and_knife": "🍴", "fork_knife_plate": "🍽", "dog": "🐶", "cat": "🐱", "mouse": "🐭", "hamster": "🐹", "rabbit": "🐰", "bear": "🐻", "panda_face": "🐼", "koala": "🐨", "tiger": "🐯", "lion_face": "🦁", "cow": "🐮", "pig": "🐷", "pig_nose": "🐽", "frog": "🐸", "octopus": "🐙", "monkey_face": "🐵", "see_no_evil": "🙈", "hear_no_evil": "🙉", "speak_no_evil": "🙊", "monkey": "🐒", "chicken": "🐔", "penguin": "🐧", "bird": "🐦", "baby_chick": "🐤", "hatching_chick": "🐣", "hatched_chick": "🐥", "wolf": "🐺", "boar": "🐗", "horse": "🐴", "unicorn": "🦄", "bee": "🐝", "honeybee": "🐝", "bug": "🐛", "snail": "🐌", "beetle": "🐞", "ant": "🐜", "spider": "🕷", "scorpion": "🦂", "crab": "🦀", "snake": "🐍", "turtle": "🐢", "tropical_fish": "🐠", "fish": "🐟", "blowfish": "🐡", "dolphin": "🐬", "flipper": "🐬", "whale": "🐳", "whale2": "🐋", "crocodile": "🐊", "leopard": "🐆", "tiger2": "🐅", "water_buffalo": "🐃", "ox": "🐂", "cow2": "🐄", "dromedary_camel": "🐪", "camel": "🐫", "elephant": "🐘", "goat": "🐐", "ram": "🐏", "sheep": "🐑", "racehorse": "🐎", "pig2": "🐖", "rat": "🐀", "mouse2": "🐁", "rooster": "🐓", "turkey": "🦃", "dove": "🕊", "dog2": "🐕", "poodle": "🐩", "cat2": "🐈", "rabbit2": "🐇", "chipmunk": "🐿", "feet": "🐾", "paw_prints": "🐾", "dragon": "🐉", "dragon_face": "🐲", "cactus": "🌵", "christmas_tree": "🎄", "evergreen_tree": "🌲", "deciduous_tree": "🌳", "palm_tree": "🌴", "seedling": "🌱", "herb": "🌿", "shamrock": "☘", "four_leaf_clover": "🍀", "bamboo": "🎍", "tanabata_tree": "🎋", "leaves": "🍃", "fallen_leaf": "🍂", "maple_leaf": "🍁", "ear_of_rice": "🌾", "hibiscus": "🌺", "sunflower": "🌻", "rose": "🌹", "tulip": "🌷", "blossom": "🌼", "cherry_blossom": "🌸", "bouquet": "💐", "mushroom": "🍄", "chestnut": "🌰", "jack_o_lantern": "🎃", "shell": "🐚", "spider_web": "🕸", "earth_americas": "🌎", "earth_africa": "🌍", "earth_asia": "🌏", "full_moon": "🌕", "waning_gibbous_moon": "🌖", "last_quarter_moon": "🌗", "waning_crescent_moon": "🌘", "new_moon": "🌑", "waxing_crescent_moon": "🌒", "first_quarter_moon": "🌓", "waxing_gibbous_moon": "🌔", "moon": "🌔", "new_moon_with_face": "🌚", "full_moon_with_face": "🌝", "first_quarter_moon_with_face": "🌛", "last_quarter_moon_with_face": "🌜", "sun_with_face": "🌞", "crescent_moon": "🌙", "star": "⭐", "star2": "🌟", "dizzy": "💫", "sparkles": "✨", "comet": "☄", "sunny": "☀", "white_sun_small_cloud": "🌤", "partly_sunny": "⛅", "white_sun_cloud": "🌥", "white_sun_rain_cloud": "🌦", "cloud": "☁", "cloud_rain": "🌧", "thunder_cloud_rain": "⛈", "cloud_lightning": "🌩", "zap": "⚡", "fire": "🔥", "boom": "💥", "collision": "💥", "snowflake": "❄", "cloud_snow": "🌨", "snowman2": "☃", "snowman": "⛄", "wind_blowing_face": "🌬", "dash": "💨", "cloud_tornado": "🌪", "fog": "🌫", "umbrella2": "☂", "umbrella": "☔", "droplet": "💧", "sweat_drops": "💦", "ocean": "🌊", "watch": "⌚", "iphone": "📱", "calling": "📲", "computer": "💻", "keyboard": "⌨", "desktop": "🖥", "printer": "🖨", "mouse_three_button": "🖱", "trackball": "🖲", "joystick": "🕹", "compression": "🗜", "minidisc": "💽", "floppy_disk": "💾", "cd": "💿", "dvd": "📀", "vhs": "📼", "camera": "📷", "camera_with_flash": "📸", "video_camera": "📹", "movie_camera": "🎥", "projector": "📽", "film_frames": "🎞", "telephone_receiver": "📞", "telephone": "☎", "phone": "☎", "pager": "📟", "fax": "📠", "tv": "📺", "radio": "📻", "microphone2": "🎙", "level_slider": "🎚", "control_knobs": "🎛", "stopwatch": "⏱", "timer": "⏲", "alarm_clock": "⏰", "clock": "🕰", "hourglass_flowing_sand": "⏳", "hourglass": "⌛", "satellite": "📡", "battery": "🔋", "electric_plug": "🔌", "bulb": "💡", "flashlight": "🔦", "candle": "🕯", "wastebasket": "🗑", "oil": "🛢", "money_with_wings": "💸", "dollar": "💵", "yen": "💴", "euro": "💶", "pound": "💷", "moneybag": "💰", "credit_card": "💳", "gem": "💎", "scales": "⚖", "wrench": "🔧", "hammer": "🔨", "hammer_pick": "⚒", "tools": "🛠", "pick": "⛏", "nut_and_bolt": "🔩", "gear": "⚙", "chains": "⛓", "gun": "🔫", "bomb": "💣", "knife": "🔪", "hocho": "🔪", "dagger": "🗡", "crossed_swords": "⚔", "shield": "🛡", "smoking": "🚬", "skull_crossbones": "☠", "coffin": "⚰", "urn": "⚱", "amphora": "🏺", "crystal_ball": "🔮", "prayer_beads": "📿", "barber": "💈", "alembic": "⚗", "telescope": "🔭", "microscope": "🔬", "hole": "🕳", "pill": "💊", "syringe": "💉", "thermometer": "🌡", "label": "🏷", "bookmark": "🔖", "toilet": "🚽", "shower": "🚿", "bathtub": "🛁", "key": "🔑", "key2": "🗝", "couch": "🛋", "sleeping_accommodation": "🛌", "bed": "🛏", "door": "🚪", "bellhop": "🛎", "frame_photo": "🖼", "map": "🗺", "beach_umbrella": "⛱", "moyai": "🗿", "shopping_bags": "🛍", "balloon": "🎈", "flags": "🎏", "ribbon": "🎀", "gift": "🎁", "confetti_ball": "🎊", "tada": "🎉", "dolls": "🎎", "wind_chime": "🎐", "crossed_flags": "🎌", "izakaya_lantern": "🏮", "lantern": "🏮", "envelope": "✉", "email": "📧", "envelope_with_arrow": "📩", "incoming_envelope": "📨", "love_letter": "💌", "postbox": "📮", "mailbox_closed": "📪", "mailbox": "📫", "mailbox_with_mail": "📬", "mailbox_with_no_mail": "📭", "package": "📦", "postal_horn": "📯", "inbox_tray": "📥", "outbox_tray": "📤", "scroll": "📜", "page_with_curl": "📃", "bookmark_tabs": "📑", "bar_chart": "📊", "chart_with_upwards_trend": "📈", "chart_with_downwards_trend": "📉", "page_facing_up": "📄", "date": "📅", "calendar": "📆", "calendar_spiral": "🗓", "card_index": "📇", "card_box": "🗃", "ballot_box": "🗳", "file_cabinet": "🗄", "clipboard": "📋", "notepad_spiral": "🗒", "file_folder": "📁", "open_file_folder": "📂", "dividers": "🗂", "newspaper2": "🗞", "newspaper": "📰", "notebook": "📓", "closed_book": "📕", "green_book": "📗", "blue_book": "📘", "orange_book": "📙", "notebook_with_decorative_cover": "📔", "ledger": "📒", "books": "📚", "book": "📖", "open_book": "📖", "link": "🔗", "paperclip": "📎", "paperclips": "🖇", "scissors": "✂", "triangular_ruler": "📐", "straight_ruler": "📏", "pushpin": "📌", "round_pushpin": "📍", "triangular_flag_on_post": "🚩", "flag_white": "🏳", "flag_black": "🏴", "closed_lock_with_key": "🔐", "lock": "🔒", "unlock": "🔓", "lock_with_ink_pen": "🔏", "pen_ballpoint": "🖊", "pen_fountain": "🖋", "black_nib": "✒", "pencil": "📝", "memo": "📝", "pencil2": "✏", "crayon": "🖍", "paintbrush": "🖌", "mag": "🔍", "mag_right": "🔎", "grinning": "😀", "grimacing": "😬", "grin": "😁", "joy": "😂", "smiley": "😃", "smile": "😄", "sweat_smile": "😅", "laughing": "😆", "satisfied": "😆", "innocent": "😇", "wink": "😉", "blush": "😊", "slight_smile": "🙂", "upside_down": "🙃", "relaxed": "☺", "yum": "😋", "relieved": "😌", "heart_eyes": "😍", "kissing_heart": "😘", "kissing": "😗", "kissing_smiling_eyes": "😙", "kissing_closed_eyes": "😚", "stuck_out_tongue_winking_eye": "😜", "stuck_out_tongue_closed_eyes": "😝", "stuck_out_tongue": "😛", "money_mouth": "🤑", "nerd": "🤓", "sunglasses": "😎", "hugging": "🤗", "smirk": "😏", "no_mouth": "😶", "neutral_face": "😐", "expressionless": "😑", "unamused": "😒", "rolling_eyes": "🙄", "thinking": "🤔", "flushed": "😳", "disappointed": "😞", "worried": "😟", "angry": "😠", "rage": "😡", "pensive": "😔", "confused": "😕", "slight_frown": "🙁", "frowning2": "☹", "persevere": "😣", "confounded": "😖", "tired_face": "😫", "weary": "😩", "triumph": "😤", "open_mouth": "😮", "scream": "😱", "fearful": "😨", "cold_sweat": "😰", "hushed": "😯", "frowning": "😦", "anguished": "😧", "cry": "😢", "disappointed_relieved": "😥", "sleepy": "😪", "sweat": "😓", "sob": "😭", "dizzy_face": "😵", "astonished": "😲", "zipper_mouth": "🤐", "mask": "😷", "thermometer_face": "🤒", "head_bandage": "🤕", "sleeping": "😴", "zzz": "💤", "poop": "💩", "shit": "💩", "smiling_imp": "😈", "imp": "👿", "japanese_ogre": "👹", "japanese_goblin": "👺", "skull": "💀", "ghost": "👻", "alien": "👽", "robot": "🤖", "smiley_cat": "😺", "smile_cat": "😸", "joy_cat": "😹", "heart_eyes_cat": "😻", "smirk_cat": "😼", "kissing_cat": "😽", "scream_cat": "🙀", "crying_cat_face": "😿", "pouting_cat": "😾", "raised_hands": "🙌", "clap": "👏", "wave": "👋", "thumbsup": "👍", "+1": "👍", "thumbsdown": "👎", "-1": "👎", "punch": "👊", "facepunch": "👊", "fist": "✊", "v": "✌", "ok_hand": "👌", "raised_hand": "✋", "hand": "✋", "open_hands": "👐", "muscle": "💪", "pray": "🙏", "point_up": "☝", "point_up_2": "👆", "point_down": "👇", "point_left": "👈", "point_right": "👉", "middle_finger": "🖕", "hand_splayed": "🖐", "metal": "🤘", "vulcan": "🖖", "writing_hand": "✍", "nail_care": "💅", "lips": "👄", "tongue": "👅", "ear": "👂", "nose": "👃", "eye": "👁", "eyes": "👀", "bust_in_silhouette": "👤", "busts_in_silhouette": "👥", "speaking_head": "🗣", "baby": "👶", "boy": "👦", "girl": "👧", "man": "👨", "woman": "👩", "person_with_blond_hair": "👱", "older_man": "👴", "older_woman": "👵", "man_with_gua_pi_mao": "👲", "man_with_turban": "👳", "cop": "👮", "construction_worker": "👷", "guardsman": "💂", "spy": "🕵", "santa": "🎅", "angel": "👼", "princess": "👸", "bride_with_veil": "👰", "walking": "🚶", "runner": "🏃", "running": "🏃", "dancer": "💃", "dancers": "👯", "couple": "👫", "two_men_holding_hands": "👬", "two_women_holding_hands": "👭", "bow": "🙇", "information_desk_person": "💁", "no_good": "🙅", "ok_woman": "🙆", "raising_hand": "🙋", "person_with_pouting_face": "🙎", "person_frowning": "🙍", "haircut": "💇", "massage": "💆", "couple_with_heart": "💑", "couple_ww": "👩‍❤️‍👩", "couple_mm": "👨‍❤️‍👨", "couplekiss": "💏", "kiss_ww": "👩‍❤️‍💋‍👩", "kiss_mm": "👨‍❤️‍💋‍👨", "family": "👪", "family_mwg": "👨‍👩‍👧", "family_mwgb": "👨‍👩‍👧‍👦", "family_mwbb": "👨‍👩‍👦‍👦", "family_mwgg": "👨‍👩‍👧‍👧", "family_wwb": "👩‍👩‍👦", "family_wwg": "👩‍👩‍👧", "family_wwgb": "👩‍👩‍👧‍👦", "family_wwbb": "👩‍👩‍👦‍👦", "family_wwgg": "👩‍👩‍👧‍👧", "family_mmb": "👨‍👨‍👦", "family_mmg": "👨‍👨‍👧", "family_mmgb": "👨‍👨‍👧‍👦", "family_mmbb": "👨‍👨‍👦‍👦", "family_mmgg": "👨‍👨‍👧‍👧", "womans_clothes": "👚", "shirt": "👕", "tshirt": "👕", "jeans": "👖", "necktie": "👔", "dress": "👗", "bikini": "👙", "kimono": "👘", "lipstick": "💄", "kiss": "💋", "footprints": "👣", "high_heel": "👠", "sandal": "👡", "boot": "👢", "mans_shoe": "👞", "shoe": "👞", "athletic_shoe": "👟", "womans_hat": "👒", "tophat": "🎩", "helmet_with_cross": "⛑", "mortar_board": "🎓", "crown": "👑", "school_satchel": "🎒", "pouch": "👝", "purse": "👛", "handbag": "👜", "briefcase": "💼", "eyeglasses": "👓", "dark_sunglasses": "🕶", "ring": "💍", "closed_umbrella": "🌂", "100": "💯", "1234": "🔢", "heart": "❤", "yellow_heart": "💛", "green_heart": "💚", "blue_heart": "💙", "purple_heart": "💜", "broken_heart": "💔", "heart_exclamation": "❣", "two_hearts": "💕", "revolving_hearts": "💞", "heartbeat": "💓", "heartpulse": "💗", "sparkling_heart": "💖", "cupid": "💘", "gift_heart": "💝", "heart_decoration": "💟", "peace": "☮", "cross": "✝", "star_and_crescent": "☪", "om_symbol": "🕉", "wheel_of_dharma": "☸", "star_of_david": "✡", "six_pointed_star": "🔯", "menorah": "🕎", "yin_yang": "☯", "orthodox_cross": "☦", "place_of_worship": "🛐", "ophiuchus": "⛎", "aries": "♈", "taurus": "♉", "gemini": "♊", "cancer": "♋", "leo": "♌", "virgo": "♍", "libra": "♎", "scorpius": "♏", "sagittarius": "♐", "capricorn": "♑", "aquarius": "♒", "pisces": "♓", "id": "🆔", "atom": "⚛", "u7a7a": "🈳", "u5272": "🈹", "radioactive": "☢", "biohazard": "☣", "mobile_phone_off": "📴", "vibration_mode": "📳", "u6709": "🈶", "u7121": "🈚", "u7533": "🈸", "u55b6": "🈺", "u6708": "🈷", "eight_pointed_black_star": "✴", "vs": "🆚", "accept": "🉑", "white_flower": "💮", "ideograph_advantage": "🉐", "secret": "㊙", "congratulations": "㊗", "u5408": "🈴", "u6e80": "🈵", "u7981": "🈲", "a": "🅰", "b": "🅱", "ab": "🆎", "cl": "🆑", "o2": "🅾", "sos": "🆘", "no_entry": "⛔", "name_badge": "📛", "no_entry_sign": "🚫", "x": "❌", "o": "⭕", "anger": "💢", "hotsprings": "♨", "no_pedestrians": "🚷", "do_not_litter": "🚯", "no_bicycles": "🚳", "non_potable_water": "🚱", "underage": "🔞", "no_mobile_phones": "📵", "exclamation": "❗", "heavy_exclamation_mark": "❗", "grey_exclamation": "❕", "question": "❓", "grey_question": "❔", "bangbang": "‼", "interrobang": "⁉", "low_brightness": "🔅", "high_brightness": "🔆", "trident": "🔱", "fleur_de_lis": "⚜", "part_alternation_mark": "〽", "warning": "⚠", "children_crossing": "🚸", "beginner": "🔰", "recycle": "♻", "u6307": "🈯", "chart": "💹", "sparkle": "❇", "eight_spoked_asterisk": "✳", "negative_squared_cross_mark": "❎", "white_check_mark": "✅", "diamond_shape_with_a_dot_inside": "💠", "cyclone": "🌀", "loop": "➿", "globe_with_meridians": "🌐", "m": "Ⓜ", "atm": "🏧", "sa": "🈂", "passport_control": "🛂", "customs": "🛃", "baggage_claim": "🛄", "left_luggage": "🛅", "wheelchair": "♿", "no_smoking": "🚭", "wc": "🚾", "parking": "🅿", "potable_water": "🚰", "mens": "🚹", "womens": "🚺", "baby_symbol": "🚼", "restroom": "🚻", "put_litter_in_its_place": "🚮", "cinema": "🎦", "signal_strength": "📶", "koko": "🈁", "ng": "🆖", "ok": "🆗", "up": "🆙", "cool": "🆒", "new": "🆕", "free": "🆓", "zero": "0⃣", "one": "1⃣", "two": "2⃣", "three": "3⃣", "four": "4⃣", "five": "5⃣", "six": "6⃣", "seven": "7⃣", "eight": "8⃣", "nine": "9⃣", "ten": "🔟","zero": "0⃣", "1": "1⃣", "2": "2⃣", "3": "3⃣", "4": "4⃣", "5": "5⃣", "6": "6⃣", "7": "7⃣", "8": "8⃣", "9": "9⃣", "10": "🔟", "keycap_ten": "🔟", "arrow_forward": "▶", "pause_button": "⏸", "play_pause": "⏯", "stop_button": "⏹", "record_button": "⏺", "track_next": "⏭", "track_previous": "⏮", "fast_forward": "⏩", "rewind": "⏪", "twisted_rightwards_arrows": "🔀", "repeat": "🔁", "repeat_one": "🔂", "arrow_backward": "◀", "arrow_up_small": "🔼", "arrow_down_small": "🔽", "arrow_double_up": "⏫", "arrow_double_down": "⏬", "arrow_right": "➡", "arrow_left": "⬅", "arrow_up": "⬆", "arrow_down": "⬇", "arrow_upper_right": "↗", "arrow_lower_right": "↘", "arrow_lower_left": "↙", "arrow_upper_left": "↖", "arrow_up_down": "↕", "left_right_arrow": "↔", "arrows_counterclockwise": "🔄", "arrow_right_hook": "↪", "leftwards_arrow_with_hook": "↩", "arrow_heading_up": "⤴", "arrow_heading_down": "⤵", "hash": "#⃣", "asterisk": "*⃣", "information_source": "ℹ", "abc": "🔤", "abcd": "🔡", "capital_abcd": "🔠", "symbols": "🔣", "musical_note": "🎵", "notes": "🎶", "wavy_dash": "〰", "curly_loop": "➰", "heavy_check_mark": "✔", "arrows_clockwise": "🔃", "heavy_plus_sign": "➕", "heavy_minus_sign": "➖", "heavy_division_sign": "➗", "heavy_multiplication_x": "✖", "heavy_dollar_sign": "💲", "currency_exchange": "💱", "copyright": "©", "registered": "®", "tm": "™", "end": "🔚", "back": "🔙", "on": "🔛", "top": "🔝", "soon": "🔜", "ballot_box_with_check": "☑", "radio_button": "🔘", "white_circle": "⚪", "black_circle": "⚫", "red_circle": "🔴", "large_blue_circle": "🔵", "small_orange_diamond": "🔸", "small_blue_diamond": "🔹", "large_orange_diamond": "🔶", "large_blue_diamond": "🔷", "small_red_triangle": "🔺", "black_small_square": "▪", "white_small_square": "▫", "black_large_square": "⬛", "white_large_square": "⬜", "small_red_triangle_down": "🔻", "black_medium_square": "◼", "white_medium_square": "◻", "black_medium_small_square": "◾", "white_medium_small_square": "◽", "black_square_button": "🔲", "white_square_button": "🔳", "speaker": "🔈", "sound": "🔉", "loud_sound": "🔊", "mute": "🔇", "mega": "📣", "loudspeaker": "📢", "bell": "🔔", "no_bell": "🔕", "black_joker": "🃏", "mahjong": "🀄", "spades": "♠", "clubs": "♣", "hearts": "♥", "diamonds": "♦", "flower_playing_cards": "🎴", "thought_balloon": "💭", "anger_right": "🗯", "speech_balloon": "💬", "clock1": "🕐", "clock2": "🕑", "clock3": "🕒", "clock4": "🕓", "clock5": "🕔", "clock6": "🕕", "clock7": "🕖", "clock8": "🕗", "clock9": "🕘", "clock10": "🕙", "clock11": "🕚", "clock12": "🕛", "clock130": "🕜", "clock230": "🕝", "clock330": "🕞", "clock430": "🕟", "clock530": "🕠", "clock630": "🕡", "clock730": "🕢", "clock830": "🕣", "clock930": "🕤", "clock1030": "🕥", "clock1130": "🕦", "clock1230": "🕧", "eye_in_speech_bubble": "👁‍🗨", "speech_left": "🗨", "eject": "⏏", "red_car": "🚗", "car": "🚗", "taxi": "🚕", "blue_car": "🚙", "bus": "🚌", "trolleybus": "🚎", "race_car": "🏎", "police_car": "🚓", "ambulance": "🚑", "fire_engine": "🚒", "minibus": "🚐", "truck": "🚚", "articulated_lorry": "🚛", "tractor": "🚜", "motorcycle": "🏍", "bike": "🚲", "rotating_light": "🚨", "oncoming_police_car": "🚔", "oncoming_bus": "🚍", "oncoming_automobile": "🚘", "oncoming_taxi": "🚖", "aerial_tramway": "🚡", "mountain_cableway": "🚠", "suspension_railway": "🚟", "railway_car": "🚃", "train": "🚋", "monorail": "🚝", "bullettrain_side": "🚄", "bullettrain_front": "🚅", "light_rail": "🚈", "mountain_railway": "🚞", "steam_locomotive": "🚂", "train2": "🚆", "metro": "🚇", "tram": "🚊", "station": "🚉", "helicopter": "🚁", "airplane_small": "🛩", "airplane": "✈", "airplane_departure": "🛫", "airplane_arriving": "🛬", "sailboat": "⛵", "boat": "⛵", "motorboat": "🛥", "speedboat": "🚤", "ferry": "⛴", "cruise_ship": "🛳", "rocket": "🚀", "satellite_orbital": "🛰", "seat": "💺", "anchor": "⚓", "construction": "🚧", "fuelpump": "⛽", "busstop": "🚏", "vertical_traffic_light": "🚦", "traffic_light": "🚥", "checkered_flag": "🏁", "ship": "🚢", "ferris_wheel": "🎡", "roller_coaster": "🎢", "carousel_horse": "🎠", "construction_site": "🏗", "foggy": "🌁", "tokyo_tower": "🗼", "factory": "🏭", "fountain": "⛲", "rice_scene": "🎑", "mountain": "⛰", "mountain_snow": "🏔", "mount_fuji": "🗻", "volcano": "🌋", "japan": "🗾", "camping": "🏕", "tent": "⛺", "park": "🏞", "motorway": "🛣", "railway_track": "🛤", "sunrise": "🌅", "sunrise_over_mountains": "🌄", "desert": "🏜", "beach": "🏖", "island": "🏝", "city_sunset": "🌇", "city_sunrise": "🌇", "city_dusk": "🌆", "cityscape": "🏙", "night_with_stars": "🌃", "bridge_at_night": "🌉", "milky_way": "🌌", "stars": "🌠", "sparkler": "🎇", "fireworks": "🎆", "rainbow": "🌈", "homes": "🏘", "european_castle": "🏰", "japanese_castle": "🏯", "stadium": "🏟", "statue_of_liberty": "🗽", "house": "🏠", "house_with_garden": "🏡", "house_abandoned": "🏚", "office": "🏢", "department_store": "🏬", "post_office": "🏣", "european_post_office": "🏤", "hospital": "🏥", "bank": "🏦", "hotel": "🏨", "convenience_store": "🏪", "school": "🏫", "love_hotel": "🏩", "wedding": "💒", "classical_building": "🏛", "church": "⛪", "mosque": "🕌", "synagogue": "🕍", "kaaba": "🕋", "shinto_shrine": "⛩"}
        self.emoji_map = {"a": "", "b": "", "c": "©", "d": "↩", "e": "", "f": "", "g": "⛽", "h": "♓", "i": "ℹ", "j": "" or "", "k": "", "l": "", "m": "Ⓜ", "n": "♑", "o": "⭕" or "", "p": "", "q": "", "r": "®", "s": "" or "⚡", "t": "", "u": "⛎", "v": "" or "♈", "w": "〰" or "", "x": "❌" or "⚔", "y": "✌", "z": "Ⓩ", "1": "1⃣", "2": "2⃣", "3": "3⃣", "4": "4⃣", "5": "5⃣", "6": "6⃣", "7": "7⃣", "8": "8⃣", "9": "9⃣", "0": "0⃣", "$": "", "!": "❗", "?": "❓", " ": "　"}
        self.regional_map = {"z": "🇿", "y": "🇾", "x": "🇽", "w": "🇼", "v": "🇻", "u": "🇺", "t": "🇹", "s": "🇸", "r": "🇷", "q": "🇶", "p": "🇵", "o": "🇴", "n": "🇳", "m": "🇲", "l": "🇱", "k": "🇰", "j": "🇯", "i": "🇮", "h": "🇭", "g": "🇬", "f": "🇫", "e": "🇪", "d": "🇩", "c": "🇨", "b": "🇧", "a": "🇦"}
        self.emote_regex = re.compile(r'<:.*:(?P<id>\d*)>')
        self.retro_regex = re.compile(r"((https)(\:\/\/|)?u3\.photofunia\.com\/.\/results\/.\/.\/.*(\.jpg\?download))")
        self.voice_list = ['`Allison - English/US (Expressive)`', '`Michael - English/US`', '`Lisa - English/US`', '`Kate - English/UK`', '`Renee - French/FR`', '`Birgit - German/DE`', '`Dieter - German/DE`', '`Francesca - Italian/IT`', '`Emi - Japanese/JP`', '`Isabela - Portuguese/BR`', '`Enrique - Spanish`', '`Laura - Spanish`', '`Sofia - Spanish/NA`']
        self.scrap_regex = re.compile(",\"ou\":\"([^`]*?)\"")
        # self.google_keys = bot.google_keys
        self.interval_functions = {"random": interval.random, "threshold": interval.threshold, "edges": interval.edge, "waves": interval.waves, "file": interval.file_mask, "file-edges": interval.file_edges, "none": interval.none}
        self.s_functions =  {"lightness": sorting.lightness, "intensity": sorting.intensity, "maximum": sorting.maximum, "minimum": sorting.minimum}
        self.webmd_responses = ['redacted']
        self.webmd_count = random.randint(0, len(self.webmd_responses)-1)
        self.color_combinations = [[150, 50, -25], [135, 30, -10], [100, 50, -15], [75, 25, -15], [35, 20, -25], [0, 20, 0], [-25, 45, 35], [-25, 45, 65], [-45, 70, 75], [-65, 100, 135], [-45, 90, 100], [-10, 40, 70], [25, 25, 50], [65, 10, 10], [100, 25, 0], [135, 35, -10]]
        # self.fp_dir = os.listdir(str(bundled_data_path(self)/'fp/'))
        self.more_cache = {}
        self.mention_regex = re.compile(r"<@!?(?P<id>\d+)>")
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.image_mimes = ['image/png', 'image/pjpeg', 'image/jpeg', 'image/x-icon']

    async def is_nsfw(self, message):
        channel = message.channel
        if channel.is_private:
            return True
        name = channel.name.lower()
        if name == 'nsfw' or name == '[nsfw]':
            return True
        elif name == 'no-nsfw' or name == 'sfw':
            return False
        split = name.split()
        if 'nsfw' in name:
            try:
                i = split.index('nsfw')
            except:
                i = None
            if len(split) > 1 and i != None and split[i-1] != 'no':
                return True
            elif i is None:
                split = name.split('-')
                try:
                    i = split.index('nsfw')
                except:
                    i = None
                if len(split) > 1 and i != None and split[i-1] != 'no':
                    return True
        if channel.topic != None:
            topic = channel.topic.lower()
            split = topic.split()
            if '{nsfw}' in topic or '[nsfw]' in topic or topic == 'nsfw':
                return True
            elif 'nsfw' in topic and 'sfw' not in split:
                try:
                    i = split.index('nsfw')
                except:
                    i = None
                if len(split) > 1 and i != None and split[i-1] != 'no':
                    return True
                elif i is None:
                    split = topic.split('-')
                    try:
                        i = split.index('nsfw')
                    except:
                        i = None
                    if len(split) > 1 and i != None and split[i-1] != 'no':
                        return True
        return False

    def random(self, image=False, ext:str=False):
        h = str(uuid.uuid4().hex)
        if image:
            return '{0}.{1}'.format(h, ext) if ext else h+'.png'
        return h

    async def get_text(self, url:str):
        try:
            async with self.session.get(url) as resp:
                try:
                    text = await resp.text()
                    return text
                except:
                    return False
        except asyncio.TimeoutError:
            return False

    async def replace_mentions(self, txt:str):
        match = self.mention_regex.findall(txt)
        if match:
            for i in match:
                user = discord.utils.get(self.bot.get_all_members(), id=str(i))
                if user is None:
                    user = await self.bot.get_user_info(i)
                txt = re.sub(re.compile('(<@\!?{0}>)'.format(user.id)), '@{0}'.format(user), txt)
        return txt

    async def get_attachment_images(self, ctx, check_func):
        last_attachment = None
        img_urls = []
        async for m in ctx.channel.history(before=ctx.message, limit=25):
            check = False
            if m.attachments:
                last_attachment = m.attachments[0].url
                check = await check_func(last_attachment)
            elif m.embeds:
                last_attachment = m.embeds[0].url
                check = await check_func(last_attachment)
            if check:
                img_urls.append(last_attachment)
                break
        return img_urls

    def find_member(self, guild, name, steps=2):
        member = None
        match = self.mention_regex.search(name)
        if match:
            member = guild.get_member(match.group('id'))
        if not member:
            name = name.lower()
            checks = [lambda m: m.name.lower() == name or m.display_name.lower() == name, lambda m: m.name.lower().startswith(name) or m.display_name.lower().startswith(name) or m.id == name, lambda m: name in m.display_name.lower() or name in m.name.lower()]
            for i in range(steps if steps <= len(checks) else len(checks)):
                if i == 3:
                    member = discord.utils.find(checks[1], self.bot.get_all_members())
                else:
                    member = discord.utils.find(checks[i], guild.members)
                if member:
                    break
        return member

    async def get_images(self, ctx, **kwargs):
        try:
            message = ctx.message
            channel = ctx.message.channel
            attachments = ctx.message.attachments
            mentions = ctx.message.mentions
            limit = kwargs.pop('limit', 8)
            urls = kwargs.pop('urls', [])
            gif = kwargs.pop('gif', False)
            msg = kwargs.pop('msg', True)
            if gif:
                check_func = self.isgif
            else:
                check_func = self.isimage
            if urls is None:
                urls = []
            elif type(urls) != tuple:
                urls = [urls]
            else:
                urls = list(urls)
            scale = kwargs.pop('scale', None)
            scale_msg = None
            int_scale = None
            if gif is False:
                for user in mentions:
                    if user.avatar:
                        urls.append(user.avatar_url_as(static_format="png"))
                    else:
                        urls.append(user.default_avatar_url)
                    limit += 1
            for attachment in attachments:
                urls.append(attachment.url)
            if scale:
                scale_limit = scale
                limit += 1
            if urls and len(urls) > limit:
                await channel.send(':no_entry: `Max image limit (<= {0})`'.format(limit))
                ctx.command.reset_cooldown(ctx)
                return False
            img_urls = []
            count = 1
            for url in urls:
                user = None
                if url.startswith('<@'):
                    continue
                if not url.startswith('http'):
                    url = 'http://'+url
                try:
                    if scale:
                        s_url = url[8:] if url.startswith('https://') else url[7:]
                        if str(math.floor(float(s_url))).isdigit():
                            int_scale = int(math.floor(float(s_url)))
                            scale_msg = '`Scale: {0}`\n'.format(int_scale)
                            if int_scale > scale_limit and ctx.message.author.id != self.bot.owner.id:
                                int_scale = scale_limit
                                scale_msg = '`Scale: {0} (Limit: <= {1})`\n'.format(int_scale, scale_limit)
                            continue
                except Exception as e:
                    pass
                check = await check_func(url)
                if check is False and gif is False:
                    check = await self.isgif(url)
                    if check:
                        if msg:
                            await channel.send(":warning: This command is for images, not gifs (use `gmagik` or `gascii`)!")
                        ctx.command.reset_cooldown(ctx)
                        return False
                    elif len(img_urls) == 0:
                        name = url[8:] if url.startswith('https://') else url[7:]
                        member = self.find_member(message.guild, name, 2)
                        if member:
                            img_urls.append(member.avatar_url_as(static_format="png") if member.avatar else member.default_avatar_url)
                            count += 1
                            continue
                        if msg:
                            await channel.send(':warning: Unable to download or verify URL is valid.')
                        ctx.command.reset_cooldown(ctx)
                        return False
                    else:
                        if msg:
                            await channel.send(':warning: Image `{0}` is Invalid!'.format(count))
                        continue
                elif gif and check is False:
                    check = await self.isimage(url)
                    if check:
                        if msg:
                            await channel.send(":warning: This command is for gifs, not images (use `magik`)!")
                        ctx.command.reset_cooldown(ctx)
                        return False
                    elif len(img_urls) == 0:
                        name = url[8:] if url.startswith('https://') else url[7:]
                        member = self.find_member(message.guild, name, 2)
                        if member:
                            img_urls.append(member.avatar_url_as(static_format="png") if member.avatar else member.default_avatar_url)
                            count += 1
                            continue
                        if msg:
                            await channel.send(':warning: Unable to download or verify URL is valid.')
                        ctx.command.reset_cooldown(ctx)
                        return False
                    else:
                        if msg:
                            await channel.send(':warning: Gif `{0}` is Invalid!'.format(count))
                        continue
                img_urls.append(url)
                count += 1
            else:
                if len(img_urls) == 0:
                    attachment_images = await self.get_attachment_images(ctx, check_func)
                    if attachment_images:
                        img_urls.extend([*attachment_images])
                    else:
                        if msg:
                            await channel.send(":no_entry: Please input url(s){0}or attachment(s).".format(', mention(s) ' if not gif else ' '))
                        ctx.command.reset_cooldown(ctx)
                        return False
            if scale:
                if len(img_urls) == 0:
                    attachment_images = await self.get_attachment_images(ctx, check_func)
                    if attachment_images:
                        img_urls.extend([*attachment_images])
                    else:
                        if msg:
                            await channel.send(":no_entry: Please input url(s){0}or attachment(s).".format(', mention(s) ' if not gif else ' '))
                        ctx.command.reset_cooldown(ctx)
                        return False
                return img_urls, int_scale, scale_msg
            if img_urls:
                return img_urls
            return False
        except Exception as e:
            print(e)

    async def truncate(self, channel, msg):
        if len(msg) == 0:
            return
        split = [msg[i:i + 1999] for i in range(0, len(msg), 1999)]
        try:
            for s in split:
                await channel.send(s)
                await asyncio.sleep(0.21)
        except Exception as e:
            await channel.send(e)

    async def get_json(self, url:str):
        try:
            async with self.session.get(url) as resp:
                try:
                    load = await resp.json()
                    return load
                except:
                    return {}
        except asyncio.TimeoutError:
            return {}

    async def isimage(self, url:str):
        try:
            async with self.session.head(url) as resp:
                if resp.status == 200:
                    mime = resp.headers.get('Content-type', '').lower()
                    if any([mime == x for x in self.image_mimes]):
                        return True
                    else:
                        return False
        except:
            return False

    async def isgif(self, url:str):
        try:
            async with self.session.head(url) as resp:
                if resp.status == 200:
                    mime = resp.headers.get('Content-type', '').lower()
                    if mime == "image/gif":
                        return True
                    else:
                        return False
        except:
            return False

    async def download(self, url:str, path:str):
        try:
            async with self.session.get(url) as resp:
                data = await resp.read()
                with open(path, "wb") as f:
                    f.write(data)
        except asyncio.TimeoutError:
            return False

    async def bytes_download(self, url:str):
        try:
            async with self.session.get(url) as resp:
                data = await resp.read()
                b = BytesIO(data)
                b.seek(0)
                return b
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            print(e)
            return False

    async def run_process(self, code, response=False):
        try:
            loop = self.bot.loop
            exit_future = asyncio.Future(loop=loop)
            create = loop.subprocess_exec(lambda: DataProtocol(exit_future),
                                                                        *code, stdin=None, stderr=None)
            transport, protocol = await asyncio.wait_for(create, timeout=30)
            await exit_future
            if response:
                data = bytes(protocol.output)
                return data.decode('ascii').rstrip()
            return True
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            print(e)
        finally:
            transport.close()

    async def gist(self, ctx, idk, content:str):
        payload = {
            'name': 'NotSoBot - By: {0}.'.format(ctx.message.author),
            'title': 'ASCII for text: "{0}"'.format(idk),
            'text': content,
            'private': '1',
            'lang': 'python',
            'expire': '0'
        }
        with aiohttp.ClientSession() as session:
            async with session.post('https://spit.mixtape.moe/api/create', data=payload) as r:
                url = await r.text()
                await ctx.send('Uploaded to paste, URL: <{0}>'.format(url))

    def do_magik(self, scale, *imgs):
        try:
            list_imgs = []
            exif = {}
            exif_msg = ''
            count = 0
            for img in imgs:
                i = wand.image.Image(file=img)
                i.format = 'jpg'
                i.alpha_channel = True
                if i.size >= (3000, 3000):
                    return ':warning: `Image exceeds maximum resolution >= (3000, 3000).`', None
                exif.update({count:(k[5:], v) for k, v in i.metadata.items() if k.startswith('exif:')})
                count += 1
                i.transform(resize='800x800>')
                i.liquid_rescale(width=int(i.width * 0.5), height=int(i.height * 0.5), delta_x=int(0.5 * scale) if scale else 1, rigidity=0)
                i.liquid_rescale(width=int(i.width * 1.5), height=int(i.height * 1.5), delta_x=scale if scale else 2, rigidity=0)
                magikd = BytesIO()
                i.save(file=magikd)
                magikd.seek(0)
                list_imgs.append(magikd)
            if len(list_imgs) > 1:
                imgs = [PIL.Image.open(i).convert('RGBA') for i in list_imgs]
                min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
                imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
                imgs_comb = PIL.Image.fromarray(imgs_comb)
                ya = BytesIO()
                imgs_comb.save(ya, 'png')
                ya.seek(0)
            elif not len(list_imgs):
                return ':warning: **Command download function failed...**', None
            else:
                ya = list_imgs[0]
            for x in exif:
                if len(exif[x]) >= 2000:
                    continue
                exif_msg += '**Exif data for image #{0}**\n'.format(str(x+1))+code.format(exif[x])
            else:
                if len(exif_msg) == 0:
                    exif_msg = None
            return ya, exif_msg
        except Exception as e:
            return str(e), None

    @commands.command(pass_context=True, aliases=['imagemagic', 'imagemagick', 'magic', 'magick', 'cas', 'liquid'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def magik(self, ctx, *urls:str):
        """Apply magik to Image(s)\n .magik image_url or .magik image_url image_url_2"""
        try:
            get_images = await self.get_images(ctx, urls=urls, limit=6, scale=5)
            if not get_images:
                return
            img_urls = get_images[0]
            scale = get_images[1]
            scale_msg = get_images[2]
            if scale_msg is None:
                scale_msg = ''
            msg = await ctx.message.channel.send( "ok, processing")
            list_imgs = []
            for url in img_urls:
                b = await self.bytes_download(url)
                if b is False:
                    if len(img_urls) > 1:
                        await ctx.send(':warning: **Command download function failed...**')
                        return
                    continue
                list_imgs.append(b)
            final, content_msg = await self.bot.loop.run_in_executor(None, self.do_magik, scale, *list_imgs)
            if type(final) == str:
                await ctx.send(final)
                return
            if content_msg is None:
                content_msg = scale_msg
            else:
                content_msg = scale_msg+content_msg
            await msg.delete()
            file = discord.File(final, filename='magik.png')
            await ctx.send(content_msg, file=file)
        except discord.errors.Forbidden:
            await ctx.send(":warning: **I do not have permission to send files!**")
        except Exception as e:
            await ctx.send(e)

    def do_gmagik(self, ctx, gif, gif_dir, rand):
        try:
            try:
                frame = PIL.Image.open(gif)
            except:
                return ':warning: Invalid Gif.'
            if frame.size >= (3000, 3000):
                os.remove(gif)
                return ':warning: `GIF resolution exceeds maximum >= (3000, 3000).`'
            nframes = 0
            while frame:
                frame.save('{0}/{1}_{2}.png'.format(gif_dir, nframes, rand), 'GIF')
                nframes += 1
                try:
                    frame.seek(nframes)
                except EOFError:
                    break
            imgs = glob.glob(gif_dir+"*_{0}.png".format(rand))
            if len(imgs) > 150 and ctx.message.author.id != self.bot.owner.id:
                for image in imgs:
                    os.remove(image)
                os.remove(gif)
                return ":warning: `GIF has too many frames (>= 150 Frames).`"
            for image in imgs:
                try:
                    im = wand.image.Image(filename=image)
                except Exception as e:
                    print(e)
                    continue
                i = im.clone()
                i.transform(resize='800x800>')
                i.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
                i.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=2, rigidity=0)
                i.resize(i.width, i.height)
                i.save(filename=image)
            return True
        except Exception as e:
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

    @commands.command(pass_context=True)
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def gmagik(self, ctx, url:str=None, framerate:str=None):
        try:
            url = await self.get_images(ctx, urls=url, gif=True, limit=2)
            if url:
                url = url[0]
            else:
                return
            gif_dir = str(bundled_data_path(self))+'/gif/'
            if not os.path.exists(gif_dir):
                os.makedirs(gif_dir)
            check = await self.isgif(url)
            if check is False:
                await ctx.send("Invalid or Non-GIF!")
                ctx.command.reset_cooldown(ctx)
                return
            x = await ctx.message.channel.send( "ok, processing (this might take a while for big gifs)")
            rand = self.random()
            gifin = gif_dir+'1_{0}.gif'.format(rand)
            gifout = gif_dir+'2_{0}.gif'.format(rand)
            print(url)
            await self.download(url, gifin)
            if os.path.getsize(gifin) > 5000000 and ctx.message.author.id != self.bot.owner.id:
                await ctx.send(":no_entry: `GIF Too Large (>= 5 mb).`")
                os.remove(gifin)
                return
            try:
                result = await self.bot.loop.run_in_executor(None, self.do_gmagik, ctx, gifin, gif_dir, rand)
            except Exception as e:
                print("Failing here")
                print(e)
                await ctx.send(':warning: Gmagik failed...')
                return
            if type(result) == str:
                await ctx.send(result)
                return
            try:
                if framerate != None:
                    args = ['ffmpeg', '-y', '-nostats', '-loglevel', '0', '-i', gif_dir+'%d_{0}.png'.format(rand), '-r', framerate, gifout]
                else:
                    args = ['ffmpeg', '-y', '-nostats', '-loglevel', '0', '-i', gif_dir+'%d_{0}.png'.format(rand), gifout]
            except Exception as e:
                print("Some error has occured:"+e)
            print(gifout)
            await self.run_process(args, True)
            file = discord.File(gifout, filename='gmagik.gif')
            await ctx.send(file=file)
            for image in glob.glob(gif_dir+"*_{0}.png".format(rand)):
                os.remove(image)
            os.remove(gifin)
            os.remove(gifout)
            await x.delete()
        except Exception as e:
            print(e)

    @commands.command(pass_context=True)
    async def caption(self, ctx, url:str=None, text:str=None, color=None, size=None, x:int=None, y:int=None):
        """Add caption to an image\n .caption text image_url"""
        try:
            if url is None:
                await ctx.send("Error: Invalid Syntax\n`.caption <image_url> <text>** <color>* <size>* <x>* <y>*`\n`* = Optional`\n`** = Wrap text in quotes`")
                return
            check = await self.isimage(url)
            if check == False:
                await ctx.send("Invalid or Non-Image!")
                return
            xx = await ctx.message.channel.send( "ok, processing")
            b = await self.bytes_download(url)
            img = wand.image.Image(file=b)
            i = img.clone()
            font_path = str(bundled_data_path(self))+'/impact.ttf'
            if size != None:
                color = wand.color.Color('{0}'.format(color))
                font = wand.font.Font(path=font_path, size=int(size), color=color)
            elif color != None:
                color = wand.color.Color('{0}'.format(color))
                font = wand.font.Font(path=font_path, size=40, color=color)
            else:
                color = wand.color.Color('red')
                font = wand.font.Font(path=font_path, size=40, color=color)
            if x is None:
                x = None
                y = int(i.height/10)
            if x != None and x > 250:
                x = x/2
            if y != None and y > 250:
                y = y/2
            if x != None and x > 500:
                x = x/4
            if y != None and y > 500:
                y = y/4
            if x != None:
                i.caption(str(text), left=x, top=y, font=font, gravity='center')
            else:
                i.caption(str(text), top=y, font=font, gravity='center')
            final = BytesIO()
            i.save(file=final)
            final.seek(0)
            await xx.delete()
            file = discord.File(final, filename='caption.png')
            await ctx.send(file=file)
        except Exception as e:
            await ctx.send("Error: Invalid Syntax\n `.caption <image_url> <text>** <color>* <size>* <x>* <y>*`\n`* = Optional`\n`** = Wrap text in quotes`")
            print(e)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5)
    async def triggered(self, ctx, user:str=None):
        """Generate a Triggered Gif for a User or Image"""
        try:
            url = None
            if user is None:
                user = ctx.message.author
            elif len(ctx.message.mentions):
                user = ctx.message.mentions[0]
            else:
                url = user
            if type(user) == discord.User or type(user) == discord.Member:
                if user.avatar:
                    avatar = user.avatar_url_as(static_format="png")
                else:
                    avatar = user.default_avatar_url
            if url:
                get_images = await self.get_images(ctx, urls=url, limit=1)
                if not get_images:
                    return
                avatar = get_images[0]
            path = str(bundled_data_path(self))+"/"+self.random(True)
            path2 = path[:-3]+'gif'
            await self.download(avatar, path)
            t_path = str(bundled_data_path(self))+'/triggered.jpg'
            print(t_path)
            await self.run_process(['convert',
                'canvas:none',
                '-size', '512x680!',
                '-resize', '512x680!',
                '-draw', 'image over -60,-60 640,640 "{0}"'.format(path),
                '-draw', 'image over 0,586 0,0 "{0}"'.format(t_path),
                '(',
                    'canvas:none',
                    '-size', '512x680!',
                    '-draw', 'image over -45,-50 640,640 "{0}"'.format(path),
                    '-draw', 'image over 0,586 0,0 "{0}"'.format(t_path),
                ')',
                '(',
                    'canvas:none',
                    '-size', '512x680!',
                    '-draw', 'image over -50,-45 640,640 "{0}"'.format(path),
                    '-draw', 'image over 0,586 0,0 "{0}"'.format(t_path),
                ')',
                '(',
                    'canvas:none',
                    '-size', '512x680!',
                    '-draw', 'image over -45,-65 640,640 "{0}"'.format(path),
                    '-draw', 'image over 0,586 0,0 "{0}"'.format(t_path),
                ')',
                '-layers', 'Optimize',
                '-set', 'delay', '2',
            path2])
            file = discord.File(path2, filename='/triggered.gif')
            await ctx.send(file=file)
            os.remove(path)
            os.remove(path2)
        except Exception as e:
            await ctx.send(e)
            try:
                os.remove(path)
                os.remove(path2)
            except:
                pass

    async def do_triggered(self, ctx, user, url, t_path):
        try:
            if user is None:
                user = ctx.message.author
            elif len(ctx.message.mentions):
                user = ctx.message.mentions[0]
            else:
                url = user
            if type(user) == discord.User or type(user) == discord.Member:
                if user.avatar:
                    avatar = user.avatar_url_as(static_format="png")
                else:
                    avatar = user.default_avatar_url
            if url:
                get_images = await self.get_images(ctx, urls=url, limit=1)
                if not get_images:
                    return
                avatar = get_images[0]
            path = str(bundled_data_path(self))+"/"+self.random(True)
            await self.download(avatar, path)
            await self.run_process(['convert',
                '(',
                    path,
                    '-resize', '256', 
                ')',
                t_path,
                '-append', path
            ])
            return path
        except Exception as e:
            print(e)
            return False

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5)
    async def triggered2(self, ctx, user:str=None, url:str=None):
        """Generate a Triggered Image for a User or Image"""
        t_path = str(bundled_data_path(self))+'/triggered.jpeg'
        path = await self.do_triggered(ctx, user, url, t_path)
        if path is False:
            await ctx.send(':warning: **Command Failed.**')
            try:
                os.remove(path)
            except:
                pass
            return
        file = discord.File(path, filename='triggered3.png')
        await ctx.send(file=file)
        os.remove(path)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5)
    async def triggered3(self, ctx, user:str=None, url:str=None):
        """Generate a Triggered2 Image for a User or Image"""
        t_path = str(bundled_data_path(self))+'/triggered2.png'
        path = await self.do_triggered(ctx, user, url, t_path)
        if path is False:
            await ctx.send(':warning: **Command Failed.**')
            try:
                os.remove(path)
            except:
                pass
            return
        file = discord.File(path, filename='triggered3.png')
        await ctx.send(file=file)
        os.remove(path)

    @commands.command(pass_context=True, aliases=['aes'])
    async def aesthetics(self, ctx, *, text:str):
        """Returns inputed text in aesthetics"""
        final = ""
        pre = ' '.join(text)
        for char in pre:
            if not ord(char) in range(33, 127):
                final += char
                continue
            final += chr(ord(char) + 65248)
        await self.truncate(ctx.message.channel, final)

    def do_ascii(self, text):
        try:
            i = PIL.Image.new('RGB', (2000, 1000))
            img = PIL.ImageDraw.Draw(i)
            txt = figlet_format(text, font='starwars')
            img.text((20, 20), figlet_format(text, font='starwars'), fill=(0, 255, 0))
            text_width, text_height = img.textsize(figlet_format(text, font='starwars'))
            imgs = PIL.Image.new('RGB', (text_width + 30, text_height))
            ii = PIL.ImageDraw.Draw(imgs)
            ii.text((20, 20), figlet_format(text, font='starwars'), fill=(0, 255, 0))
            text_width, text_height = ii.textsize(figlet_format(text, font='starwars'))
            final = BytesIO()
            imgs.save(final, 'png')
            final.seek(0)
            return final, txt
        except:
            return False, False

    @commands.command(pass_context=True, aliases=['expand'])
    @commands.cooldown(1, 5)
    async def ascii(self, ctx, *, text:str):
        """Convert text into ASCII"""
        if len(text) > 1000:
            await ctx.send("Text is too long!")
            return
        if text == 'donger' or text == 'dong':
            text = "8====D"
        final, txt = await self.bot.loop.run_in_executor(None, self.do_ascii, text)
        if final is False:
            await ctx.send(':no_entry: go away with your invalid characters.')
            return
        if len(txt) >= 1999:
            await self.gist(ctx, text, txt)
            msg = None
        elif len(txt) <= 600:
            msg = "```fix\n{0}```".format(txt)
        else:
            msg = None
        file = discord.File(final, filename='ascii.png')
        await ctx.send(msg, file=file)

    def generate_ascii(self, image):
        font = PIL.ImageFont.truetype(str(bundled_data_path(self))+'/FreeMonoBold.ttf', 15, encoding="unic")
        image_width, image_height = image.size
        aalib_screen_width= int(image_width/24.9)*10
        aalib_screen_height= int(image_height/41.39)*10
        screen = aalib.AsciiScreen(width=aalib_screen_width, height=aalib_screen_height)
        im = image.convert("L").resize(screen.virtual_size)
        screen.put_image((0,0), im)
        y = 0
        how_many_rows = len(screen.render().splitlines()) 
        new_img_width, font_size = font.getsize(screen.render().splitlines()[0])
        img = PIL.Image.new("RGBA", (new_img_width, how_many_rows*15), (255,255,255))
        draw = PIL.ImageDraw.Draw(img)
        for lines in screen.render().splitlines():
            draw.text((0,y), lines, (0,0,0), font=font)
            y = y + 15
        imagefit = PIL.ImageOps.fit(img, (image_width, image_height), PIL.Image.ANTIALIAS)
        return imagefit

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def iascii(self, ctx, url:str=None):
        if not AALIB_INSTALLED:
            await ctx.send("aalib couldn't be found on this machine!")
            return
        try:
            get_images = await self.get_images(ctx, urls=url, limit=5)
            if not get_images:
                return
            for url in get_images:
                x = await ctx.send("ok, processing")
                b = await self.bytes_download(url)
                if b is False:
                    if len(get_images) == 1:
                        await ctx.send(':warning: **Command download function failed...**')
                        return
                    continue
                im = PIL.Image.open(b)
                img = await self.bot.loop.run_in_executor(None, self.generate_ascii, im)
                final = BytesIO()
                img.save(final, 'png')
                final.seek(0)
                await x.delete()
                file = discord.File(final, filename='iascii.png')
                await ctx.send(file=file)
        except Exception as e:
            await ctx.send(e)

    def do_gascii(self, b, rand, gif_dir):
        try:
            try:
                im = PIL.Image.open(b)
            except IOError:
                return ':warning: Cannot load gif.'
            count = 0
            mypalette = im.getpalette()
            try:
                while True:
                    im.putpalette(mypalette)
                    new_im = PIL.Image.new("RGBA", im.size)
                    new_im.paste(im)
                    new_im = self.generate_ascii(new_im)
                    new_im.save('{0}/{1}_{2}.png'.format(gif_dir, count, rand))
                    count += 1
                    im.seek(im.tell() + 1)
                return True
            except EOFError:
                pass
        except Exception as e:
            print(e)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def gascii(self, ctx, url:str=None):
        """Gif to ASCII"""
        if not AALIB_INSTALLED:
            await ctx.send("aalib couldn't be found on this machine!")
            return
        try:
            get_images = await self.get_images(ctx, urls=url, gif=True, limit=2)
            if not get_images:
                await ctx.send("Error: Invalid Syntax\n`.gascii <gif_url> <liquid_rescale>*`\n`* = Optional`")
                return
            for url in get_images:
                rand = self.random()
                gif_dir = str(bundled_data_path(self)) + '/gascii/'
                if not os.path.os.path.exists(gif_dir):
                    os.makedirs(gif_dir)
                location = gif_dir+'1_{0}.gif'.format(rand)
                location2 = gif_dir+'2_{0}.gif'.format(rand)
                x = await ctx.message.channel.send( "ok, processing")
                await self.download(url, location)
                if os.path.getsize(location) > 3000000 and ctx.message.author.id != self.bot.owner.id:
                    await ctx.send("Sorry, GIF Too Large!")
                    os.remove(location)
                    return
                result = await self.bot.loop.run_in_executor(None, self.do_gascii, location, rand, gif_dir)
                if type(result) == str:
                    await ctx.send(result)
                    return
                list_imgs = glob.glob(gif_dir+"*_{0}.png".format(rand))
                if len(list_imgs) > 120 and ctx.message.author.id != self.bot.owner.id:
                    await ctx.send("Sorry, GIF has too many frames!")
                    for image in list_imgs:
                        os.remove(image)
                    os.remove(location)
                    return
                await self.run_process(['ffmpeg', '-y', '-nostats', '-loglevel', '0', '-i', gif_dir+'%d_{0}.png'.format(rand), location2])
                await x.delete()
                print("it gets here")
                file = discord.File(location2, filename='gascii.gif')
                await ctx.send(file=file)
                for image in list_imgs:
                    os.remove(image)
                os.remove(location)
                os.remove(location2)
        except Exception as e:
            print(e)
            await ctx.send("Whoops something went wrong!")

    @commands.command(pass_context=True)
    async def rip(self, ctx, name:str=None, *, text:str=None):
        if name is None:
            name = ctx.message.author.name
        if len(ctx.message.mentions) >= 1:
            name = ctx.message.mentions[0].name
        if text != None:
            if len(text) > 22:
                one = text[:22]
                two = text[22:]
                url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}&top4={1}&top5={2}".format(name, one, two).replace(" ", "%20")
            else:
                url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}&top4={1}".format(name, text).replace(" ", "%20")
        else:
            if name[-1].lower() != 's':
                name += "'s"
            url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}&top4=Hopes and Dreams".format(name).replace(" ", "%20")
        b = await self.bytes_download(url)
        file = discord.File(b, filename='rip.png')
        await ctx.send(file=file)

    async def add_cache(self, search, result, t=0, level=1):
        try:
            try:
                if result['error']:
                    return
            except KeyError:
                pass
            if t == 0:
                self.image_cache[search] = [result, level]
            elif t == 1:
                self.search_cache[search] = [result, level]
            elif t == 2:
                self.youtube_cache[search] = [result, level]
        except Exception as e:
            print(e)

    async def google_scrap(self, search:str, safe=True, image=False):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
        search = quote(search)
        try:
            if image:
                api = 'https://www.google.com/search?tbm=isch&gs_l=img&safe={0}&q={1}'.format('on' if safe else 'off', search)
                with aiohttp.ClientSession() as session:
                    async with session.get(api, headers=headers) as r:
                        assert r.status == 200
                        txt = await r.text()
                match = self.scrap_regex.findall(txt)
                assert match
                image = random.choice(match[:10])
                check = await self.isimage(image)
                i = 0
                if not check:
                    while not check and i != 10:
                        image = match[:10][i]
                        check = await self.isimage(image)
                        i += 1
                assert check
                return image
            else:
                api = 'https://www.google.com/search?safe={0}&q={1}'.format('on' if safe else 'off', search)
                #why are you so good danny, my old method was using regex so, not so good.....
                entries = {}
                with aiohttp.ClientSession() as session:
                    async with session.get(api, headers=headers) as r:
                        assert r.status == 200
                        txt = await r.text()
                root = etree.fromstring(txt, etree.HTMLParser())
                search_nodes = root.findall(".//div[@class='g']")
                result = False
                for node in search_nodes:
                    if result != False:
                        break
                    try:
                        url_node = node.find('.//h3/a')
                        if url_node is None:
                            continue
                        desc = get_deep_text(node.find(".//div[@class='s']/div/span[@class='st']"))
                        title = get_deep_text(node.find(".//h3[@class='r']"))
                        url = url_node.attrib['href']
                        if url.startswith('/url?'):
                            url = parse_qs(url[5:])['q'][0]
                        result = [title, desc, url]
                    except:
                        continue
                return result
        except AssertionError:
            return False
        except Exception as e:
            print(e)
            return False

    @commands.command(pass_context=True, aliases=['w2x', 'waifu2x', 'enlarge', 'upscale'])
    @commands.cooldown(1, 15)
    async def resize(self, ctx, *urls):
        try:
            get_images = await self.get_images(ctx, urls=urls, scale=10, limit=1)
            if not get_images:
                return
            url = get_images[0][0]
            size = get_images[1]
            if size is None:
                size = 3
            scale_msg = get_images[2]
            if scale_msg is None:
                scale_msg = ''
            else:
                scale_msg = '\n'+scale_msg
            do_2 = False
            rand = self.random()
            x = await ctx.message.channel.send( "ok, resizing `{0}` by `{1}`".format(url, str(size)))
            b = await self.bytes_download(url)
            if sys.getsizeof(b) > 3000000:
                await ctx.send("Sorry, image too large for waifu2x guilds!")
                return
            await x.edit("25%, resizing")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
            payload = aiohttp.FormData()
            payload.add_field('url', url)
            payload.add_field('scale', str(size))
            payload.add_field('style', 'art')
            payload.add_field('noise', '3')
            payload.add_field('comp', '10')
            await x.edit("50%, w2x")
            try:
                with aiohttp.ClientSession() as session:
                    async with session.post('http://waifu2x.me/convert', data=payload, headers=headers) as r:
                        txt = await r.text()
                download_url = 'http://waifu2x.me/{0}'.format(txt)
                final = None
            except asyncio.TimeoutError:
                do_2 = True
            if do_2:
                idk = []
                if size == 1:
                    idk.append(2)
                if size == 2:
                    idk.append(2)
                if size == 3:
                    idk.append(1.6)
                    idk.append(2)
                if size == 4:
                    idk.append(2)
                    idk.append(2)
                if size == 5:
                    idk.append(1.6)
                    idk.append(2)
                    idk.append(2)
                if size == 6:
                    for i in range(3):
                        idk.append(2)
                if size == 7:
                    for i in range(3):
                        idk.append(2)
                    idk.append(1.6)
                if size == 8:
                    for i in range(4):
                        idk.append(2)
                if size == 9:
                    for i in range(4):
                        idk.append(2)
                    idk.append(1.6)
                if size == 10:
                    for i in range(5):
                        idk.append(2)
                for s in idk:
                    if final:
                        b = final
                    if s == 2:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
                        payload = aiohttp.FormData()
                        payload.add_field('scale', '2')
                        payload.add_field('style', 'art')
                        payload.add_field('noise', '1')
                        payload.add_field('url', url)
                        with aiohttp.ClientSession() as session:
                            async with session.post('http://waifu2x.udp.jp/api', data=payload, headers=headers) as r:
                                raw = await r.read()
                    elif s == 1.6:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
                        payload = aiohttp.FormData()
                        payload.add_field('scale', '1.6')
                        payload.add_field('style', 'art')
                        payload.add_field('noise', '1')
                        payload.add_field('url', url)
                        with aiohttp.ClientSession() as session:
                            async with session.post('http://waifu2x.udp.jp/api', data=payload, headers=headers) as r:
                                raw = await r.read()
                    final = BytesIO(raw)
                    final.seek(0)
            if final is None:
                final = await self.bytes_download(download_url)
            if sys.getsizeof(final) > 8388608:
                await ctx.send("Sorry, image too large for discord!")
                return
            await x.edit("100%, uploading")
            i = 0
            while sys.getsizeof(final) == 88 and i < 5:
                final = await self.bytes_download(download_url)
                await asyncio.sleep(0.3)
                if sys.getsizeof(final) != 0:
                    i = 5
                else:
                    i += 1
            file = discord.File(final, filename='enlarge.png')
            await ctx.send('Visit image link for accurate resize visual.'+scale_msg if size > 3 else scale_msg if scale_msg != '' else None, file=file)
            await asyncio.sleep(3)
            await x.delete()
        except Exception as e:
            await ctx.send(code.format(e))
            await ctx.send("Error: Failed\n `Discord Failed To Upload or Waifu2x guilds Failed`")


    @commands.command()
    async def reverse(self, ctx, *, text:str):
        """Reverse Text\n.revese <text>"""
        text = text.replace('\u202E', '')
        s = text.split('\n')
        kek = ''
        for x in s:
            kek += u"\u202E " + x + '\n'
        kek = kek
        await ctx.send(kek)

    async def png_svg(self, path, size):
        with open(path, 'rb') as f:
            path = f.read()
        s = bytes(str(size), encoding="utf-8")
        b = path.replace(b"<svg ", b"<svg width=\"" + s + b"px\" height=\"" + s + b"px\" ")
        path = BytesIO(cairosvg.svg2png(b))
        return path

    fp_emotes = {
        #redacted spam
    }

    @commands.command(pass_context=True)
    @commands.cooldown(3, 5)
    async def b1(self, ctx):
        """cool"""
        file = discord.File(str(bundled_data_path(self))+'/b1.png')
        await ctx.send(file=file)

    @commands.group(pass_context=True, invoke_without_command=True)
    @commands.cooldown(1, 5)
    async def merge(self, ctx, *urls:str):
        """Merge/Combine Two Photos"""
        try:
            if urls and 'vertical' in urls:
                vertical = True
            else:
                vertical = False
            get_images = await self.get_images(ctx, urls=urls, limit=20)
            if get_images and len(get_images) == 1:
                await ctx.send('You gonna merge one image?')
                return
            elif not get_images:
                return
            xx = await ctx.message.channel.send( "ok, processing")
            count = 0
            list_im = []
            for url in get_images:
                count += 1
                b = await self.bytes_download(url)
                if sys.getsizeof(b) == 215:
                    await ctx.send(":no_entry: Image `{0}` is invalid!".format(str(count)))
                    continue
                list_im.append(b)
            imgs = [PIL.Image.open(i).convert('RGBA') for i in list_im]
            if vertical:
                max_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[1][1]
                imgs_comb = np.vstack((np.asarray(i.resize(max_shape)) for i in imgs))
            else:
                min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
                imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
            imgs_comb = PIL.Image.fromarray(imgs_comb)
            final = BytesIO()
            imgs_comb.save(final, 'png')
            final.seek(0)
            await xx.delete()
            file = discord.File(final, filename='merge.png')
            await ctx.send(file=file)
        except Exception as e:
            await ctx.send(code.format(e))

    @commands.command(pass_context=True, aliases=['cancerify', 'em'])
    async def emojify(self, ctx, *, txt:str):
        txt = txt.lower()
        msg = ""
        for s in txt:
            if s in self.emoji_map:
                msg += "{0}".format(self.emoji_map[s])
            else:
                msg += s
        await ctx.send(msg)

    @commands.command(pass_context=True, aliases=['toe', 'analyze'])
    async def tone(self, ctx, *, text:str):
        """Analyze Tone in Text"""
        payload = {'text':text}
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0.2 Waterfox/46.0.2'}
        async with self.session.post('https://tone-analyzer-demo.mybluemix.net/api/tone', data=payload, headers=headers) as r:
            load = await r.json()
        anger = load['document_tone']['tone_categories'][0]['tones'][0]['score']
        disgust = load['document_tone']['tone_categories'][0]['tones'][1]['score']
        fear = load['document_tone']['tone_categories'][0]['tones'][2]['score']
        joy = load['document_tone']['tone_categories'][0]['tones'][3]['score']
        sadness = load['document_tone']['tone_categories'][0]['tones'][4]['score']
        emotions_msg = "Anger: {0}\nDisgust: {1}\nFear: {2}\nJoy: {3}\nSadness: {4}".format(anger, disgust, fear, joy, sadness)
        analytical = load['document_tone']['tone_categories'][1]['tones'][0]['score']
        confident = load['document_tone']['tone_categories'][1]['tones'][1]['score']
        tentative = load['document_tone']['tone_categories'][1]['tones'][2]['score']
        language_msg = "Analytical: {0}\nConfidence: {1}\nTentitive: {2}".format(analytical, confident, tentative)
        openness = load['document_tone']['tone_categories'][2]['tones'][0]['score']
        conscientiousness = load['document_tone']['tone_categories'][2]['tones'][1]['score']
        extraversion = load['document_tone']['tone_categories'][2]['tones'][2]['score']
        agreeableness = load['document_tone']['tone_categories'][2]['tones'][3]['score']
        emotional_range = load['document_tone']['tone_categories'][2]['tones'][4]['score']
        social_msg = "Openness: {0}\nConscientiousness: {1}\nExtraversion (Stimulation): {2}\nAgreeableness: {3}\nEmotional Range: {4}".format(openness, conscientiousness, extraversion, agreeableness, emotional_range)
        await ctx.send("\n**Emotions**"+code.format(emotions_msg)+"**Language Style**"+code.format(language_msg)+"**Social Tendencies**"+code.format(social_msg))

    @commands.command(pass_context=True, aliases=['text2img', 'texttoimage', 'text2image'])
    async def tti(self, ctx, *, txt:str):
        api = 'http://api.img4me.com/?font=arial&fcolor=FFFFFF&size=35&type=png&text={0}'.format(quote(txt))
        r = await self.get_text(api)
        b = await self.bytes_download(r)
        file = discord.File(b, filename='tti.png')
        await ctx.send(file=file)

    @commands.command(pass_context=True, aliases=['comicsans'])
    async def sans(self, ctx, *, txt:str):
        api = 'http://api.img4me.com/?font=sans&fcolor=000000&size=35&type=png&text={0}'.format(quote(txt))
        r = await self.get_text(api)
        b = await self.bytes_download(r)
        file = discord.File(b, filename='tti.png')
        await ctx.send(file=file)

    @commands.command(pass_context=True, aliases=['needsmorejpeg', 'jpegify', 'magik2'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def jpeg(self, ctx, url:str=None, quality:int=1):
        """Add more JPEG to an Image\nNeeds More JPEG!"""
        if quality > 10:
            quality = 10
        elif quality < 1:
            quality = 1
        get_images = await self.get_images(ctx, urls=url)
        if not get_images:
            return
        for url in get_images:
            b = await self.bytes_download(url)
            if b is False:
                if len(get_images) == 1:
                    await ctx.send(':warning: **Command download function failed...**')
                    return
                continue
            img = PIL.Image.open(b).convert('RGB')
            final = BytesIO()
            img.save(final, 'JPEG', quality=quality)
            final.seek(0)
            file = discord.File(final, filename='needsmorejpeg.jpg')
            await ctx.send(file=file)

    def do_vw(self, b, txt):
        im = PIL.Image.open(b)
        k = random.randint(0, 100)
        im = macintoshplus.draw_method1(k, txt, im)
        final = BytesIO()
        im.save(final, 'png')
        final.seek(0)
        return final

    @commands.command(pass_context=True, aliases=['vaporwave', 'vape', 'vapewave'])
    @commands.cooldown(2, 5)
    async def vw(self, ctx, url:str, *, txt:str=None):
        """Vaporwave an image!"""
        get_images = await self.get_images(ctx, urls=url, limit=1)
        if not get_images:
            return
        for url in get_images:
            if txt is None:
                txt = "vapor wave"
            b = await self.bytes_download(url)
            final = await self.bot.loop.run_in_executor(None, self.do_vw, b, txt)
            file = discord.File(final, filename='vapewave.png')
            await ctx.send(file=file)

    @commands.command(pass_context=True)
    async def jagroshisgay(self, ctx, *, txt:str):
        x = await ctx.message.channel.send( txt, replace_mentions=True)
        txt = u"\u202E " + txt
        await x.edit(txt)

    @commands.command(pass_context=True, aliases=['achievement', 'ach'])
    async def mc(self, ctx, *, txt:str):
        """Generate a Minecraft Achievement"""
        api = "https://mcgen.herokuapp.com/a.php?i=1&h=Achievement-{0}&t={1}".format(ctx.message.author.name, txt)
        b = await self.bytes_download(api)
        i = 0
        while sys.getsizeof(b) == 88 and i != 10:
            b = await self.bytes_download(api)
            if sys.getsizeof(b) != 0:
                i = 10
            else:
                i += 1
        if i == 10 and sys.getsizeof(b) == 88:
            await ctx.send("Minecraft Achievement Generator API is bad, pls try again")
            return
        file = discord.File(b, filename='achievement.png')
        await ctx.send(file=file)

    @commands.command(pass_context=True, aliases=['identify', 'captcha', 'whatis'])
    async def i(self, ctx, *, url:str):
        """Identify an image/gif using Microsofts Captionbot API"""
        with aiohttp.ClientSession() as session:
            async with session.post("https://www.captionbot.ai/api/message", data={"conversationId": "FPrBPK2gAJj","waterMark": "","userMessage": url}) as r:
                pass
        load = await self.get_json("https://www.captionbot.ai/api/message?waterMark=&conversationId=FPrBPK2gAJj")
        msg = '`{0}`'.format(json.loads(load)['BotMessages'][-1])
        await ctx.send(msg)

    @commands.command(pass_context=True, aliases=['wm'])
    async def watermark(self, ctx, url:str, mark:str=None):
        try:
            check = await self.isimage(url)
            if check == False:
                await ctx.send("Invalid or Non-Image!")
                return
            b = await self.bytes_download(url)
            if mark == 'brazzers' or mark is None:
                wmm = str(bundled_data_path(self))+'/brazzers.png'
            else:
                check = await self.isimage(mark)
                if check == False:
                    await ctx.send("Invalid or Non-Image for Watermark!")
                    return
                wmm = await self.bytes_download(mark)
            final = BytesIO()
            with wand.image.Image(file=b) as img:
                if mark:
                    with wand.image.Image(file=wmm) as wm:
                        img.watermark(image=wm, left=int(img.width/15), top=int(img.height/10))
                else:
                    with wand.image.Image(filename=wmm) as wm:
                        img.watermark(image=wm, left=int(img.width/15), top=int(img.height/10))          
                img.save(file=final)
            final.seek(0)
            file = discord.File(final, filename='watermark.png')
            await ctx.send(file=file)
        except Exception as e:
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            await ctx.send(code.format('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)))

    def do_glitch(self, b, amount, seed, iterations):
        b.seek(0)
        img = jpglitch.Jpeg(bytearray(b.getvalue()), amount, seed, iterations)
        final = BytesIO()
        img.save_image(final)
        final.seek(0)
        return final

    def do_gglitch(self, b):
        b = bytearray(b.getvalue())
        for x in range(0, sys.getsizeof(b)):
            if b[x] == 33:
                if b[x + 1] == 255:
                    end = x
                    break
                elif b[x + 1] == 249:
                    end = x
                    break
        for x in range(13, end):
            b[x] = random.randint(0, 255)
        return BytesIO(b)

    @commands.command(aliases=['jpglitch'], pass_context=True)
    @commands.cooldown(2, 5)
    async def glitch(self, ctx, url:str=None, iterations:int=None, amount:int=None, seed:int=None):
        """Glitch a gif or image"""
        try:
            if iterations is None:
                iterations = random.randint(1, 30)
            if amount is None:
                amount = random.randint(1, 20)
            elif amount > 99:
                amount = 99
            if seed is None:
                seed = random.randint(1, 20)
            get_images = await self.get_images(ctx, urls=url, msg=False)
            gif = False
            if not get_images:
                get_images = await self.get_images(ctx, urls=url, gif=True)
                if get_images:
                    gif = True
                else:
                    return
            for url in get_images:
                b = await self.bytes_download(url)
                if not gif:
                    img = PIL.Image.open(b)
                    b = BytesIO()
                    img.save(b, format='JPEG')
                    final = await self.bot.loop.run_in_executor(None, self.do_glitch, b, amount, seed, iterations)
                    file = discord.File(final, filename='glitch.jpeg')
                    await ctx.send('Iterations: `{0}` | Amount: `{1}` | Seed: `{2}`'.format(iterations, amount, seed), file=file)
                else:
                    final = await self.bot.loop.run_in_executor(None, self.do_gglitch, b)
                    file = discord.File(final, filename='glitch.gif')
                    await ctx.send(file=file)
        except:
            await ctx.send("sorry, can't reglitch an image.")
            raise

    @commands.command(pass_context=True)
    async def glitch2(self, ctx, *urls:str):

        try:
            get_images = await self.get_images(ctx, urls=urls)
            if not get_images:
                return
            for url in get_images:
                path = str(bundled_data_path(self))+"/"+self.random(True)
                await self.download(url, path)
                args = ['convert', '(', path, '-resize', '1024x1024>', ')', '-alpha', 'on', '(', '-clone', '0', '-channel', 'RGB', '-separate', '-channel', 'A', '-fx', '0', '-compose', 'CopyOpacity', '-composite', ')', '(', '-clone', '0', '-roll', '+5', '-channel', 'R', '-fx', '0', '-channel', 'A', '-evaluate', 'multiply', '.3', ')', '(', '-clone', '0', '-roll', '-5', '-channel', 'G', '-fx', '0', '-channel', 'A', '-evaluate', 'multiply', '.3', ')', '(', '-clone', '0', '-roll', '+0+5', '-channel', 'B', '-fx', '0', '-channel', 'A', '-evaluate', 'multiply', '.3', ')', '(', '-clone', '0', '-channel', 'A', '-fx', '0', ')', '-delete', '0', '-background', 'none', '-compose', 'SrcOver', '-layers', 'merge', '-rotate', '90', '-wave', '1x5', '-rotate', '-90', path]
                await self.run_process(args)
                file = discord.File(path, filename='glitch2.png')
                await ctx.send(file=file)
                os.remove(path)
        except Exception as e:
            print(e)
            try:
                os.remove(path)
            except:
                pass
            raise

    @commands.command()
    async def bean(self, ctx, url:str):
        """You got BEANED"""
        try:
            check = await self.isimage(url)
            if check is False:
                await ctx.send('Invalid or Non-Image!')
                return
            b = await self.bytes_download(url)
            bean_path = str(bundled_data_path(self))+'/bean.png'
            bean = PIL.Image.open(bean_path)
            img = PIL.Image.open(b)
            width, height = bean.size
            bean.resize((int(width/50), int(height/50)))
            img.paste(bean, (math.floor(width/2), math.floor(height/2)))
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            file = discord.File(final, filename='beaned.png')
            await ctx.send(file=file)
        except Exception as e:
            await ctx.send(e)

    @commands.command(aliases=['pixel'], pass_context=True)
    async def pixelate(self, ctx, *urls):
        try:
            get_images = await self.get_images(ctx, urls=urls, limit=6, scale=3000)
            if not get_images:
                return
            img_urls = get_images[0]
            pixels = get_images[1]
            if pixels is None:
                pixels = 9
            scale_msg = get_images[2]
            if scale_msg is None:
                scale_msg = ''
            for url in img_urls:
                b = await self.bytes_download(url)
                if b is False:
                    if len(img_urls) > 1:
                        await ctx.send(':warning: **Command download function failed...**')
                        return
                    continue
                bg = (0, 0, 0)
                img = PIL.Image.open(b)
                img = img.resize((int(img.size[0]/pixels), int(img.size[1]/pixels)), PIL.Image.NEAREST)
                img = img.resize((int(img.size[0]*pixels), int(img.size[1]*pixels)), PIL.Image.NEAREST)
                load = img.load()
                for i in range(0, img.size[0], pixels):
                    for j in range(0, img.size[1], pixels):
                        for r in range(pixels):
                            load[i+r, j] = bg
                            load[i, j+r] = bg
                final = BytesIO()
                img.save(final, 'png')
                final.seek(0)
                file = discord.File(final, filename='pixelated.png')
                await ctx.send(scale_msg, file=file)
                await asyncio.sleep(0.21)
        except Exception as e:
            print(e)
            await ctx.send(':warning: `Too many pixels.`')

    async def do_retro(self, text, bcg):
        if '|' not in text:
            if len(text) >= 15:
                text = [text[i:i + 15] for i in range(0, len(text), 15)]
            else:
                split = text.split()
                if len(split) == 1:
                    text = [x for x in text]
                    if len(text) == 4:
                        text[2] = text[2]+text[-1]
                        del text[3]
                else:
                    text = split
        else:
            text = text.split('|')
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
        payload = aiohttp.FormData()
        payload.add_field('current-category', 'all_effects')
        payload.add_field('bcg', bcg)
        payload.add_field('txt', '4')
        count = 1
        for s in text:
            if count > 3:
                break
            payload.add_field('text'+str(count), s.replace("'", "\'"))
            count += 1
        try:
            async with self.session.post('https://photofunia.com/effects/retro-wave?guild=3', data=payload, headers=headers) as r:
                txt = await r.text()
        except asyncio.TimeoutError:
            return
        match = self.retro_regex.findall(txt)
        if match:
            download_url = match[0][0]
            b = await self.bytes_download(download_url)
            return b
        return False

    @commands.command()
    async def retro(self, ctx, *, text:str):
        retro_result = await self.do_retro(text, '5')
        if retro_result is False:
            await ctx.send(':warning: This text contains unsupported characters')
        else:
            file = discord.File(retro_result, filename='retro.png')
            await ctx.send(file=file)

    @commands.command()
    async def retro2(self, ctx, *, text:str):
        retro_result = await self.do_retro(text, '2')
        if retro_result is False:
            await ctx.send(':warning: This text contains unsupported characters')
        else:
            file = discord.File(retro_result, filename='retro.png')
            await ctx.send(file=file)

    @commands.command()
    async def retro3(self, ctx, *, text:str):
        retro_result = await self.do_retro(text, '4')
        if retro_result is False:
            await ctx.send(':warning: This text contains unsupported characters')
        else:
            file = discord.File(retro_result, filename='retro.png')
            await ctx.send(file=file)

    def do_waaw(self, b):
        f = BytesIO()
        f2 = BytesIO()
        with wand.image.Image(file=b, format='png') as img:
            h1 = img.clone()
            width = int(img.width/2) if int(img.width/2) > 0 else 1
            h1.crop(width=width, height=int(img.height), gravity='east')
            h2 = h1.clone()
            h1.rotate(degree=180)
            h1.flip()
            h1.save(file=f)
            h2.save(file=f2)
        f.seek(0)
        f2.seek(0)
        list_im = [f2, f]
        imgs = [PIL.ImageOps.mirror(PIL.Image.open(i).convert('RGBA')) for i in list_im]
        min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
        imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
        imgs_comb = PIL.Image.fromarray(imgs_comb)
        final = BytesIO()
        imgs_comb.save(final, 'png')
        final.seek(0)
        return final

    #Thanks to Iguniisu#9746 for the idea
    @commands.command(pass_context=True, aliases=['magik3', 'mirror'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def waaw(self, ctx, *urls:str):
        get_images = await self.get_images(ctx, urls=urls, limit=5)
        if not get_images:
            return
        for url in get_images:
            b = await self.bytes_download(url)
            if b is False:
                if len(get_images) == 1:
                    await ctx.send(':warning: **Command download function failed...**')
                    return
                continue
            final = await self.bot.loop.run_in_executor(None, self.do_waaw, b)
            file = discord.File(final, filename='waaw.png')
            await ctx.send(file=file)

    def do_haah(self, b):
        f = BytesIO()
        f2 = BytesIO()
        with wand.image.Image(file=b, format='png') as img:
            h1 = img.clone()
            h1.transform('50%x100%')
            h2 = h1.clone()
            h2.rotate(degree=180)
            h2.flip()
            h1.save(file=f)
            h2.save(file=f2)
        f.seek(0)
        f2.seek(0)
        list_im = [f2, f]
        imgs = [PIL.ImageOps.mirror(PIL.Image.open(i).convert('RGBA')) for i in list_im]
        min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
        imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
        imgs_comb = PIL.Image.fromarray(imgs_comb)
        final = BytesIO()
        imgs_comb.save(final, 'png')
        final.seek(0)
        return final

    @commands.command(pass_context=True, aliases=['magik4', 'mirror2'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def haah(self, ctx, *urls:str):
        get_images = await self.get_images(ctx, urls=urls, limit=5)
        if not get_images:
            return
        for url in get_images:
            b = await self.bytes_download(url)
            if b is False:
                if len(get_images) == 1:
                    await ctx.send(':warning: **Command download function failed...**')
                    return
                continue
            final = await self.bot.loop.run_in_executor(None, self.do_haah, b)
            file = discord.File(final, filename='haah.png')
            await ctx.send(file=file)

    def do_woow(self, b):
        f = BytesIO()
        f2 = BytesIO()
        with wand.image.Image(file=b, format='png') as img:
            h1 = img.clone()
            width = int(img.width) if int(img.width) > 0 else 1
            h1.crop(width=width, height=int(img.height/2), gravity='north')
            h2 = h1.clone()
            h2.rotate(degree=180)
            h2.flop()
            h1.save(file=f)
            h2.save(file=f2)
        f.seek(0)
        f2.seek(0)
        list_im = [f, f2]
        imgs = [PIL.Image.open(i).convert('RGBA') for i in list_im]
        min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
        imgs_comb = np.vstack((np.asarray(i.resize(min_shape)) for i in imgs))
        imgs_comb = PIL.Image.fromarray(imgs_comb)
        final = BytesIO()
        imgs_comb.save(final, 'png')
        final.seek(0)
        return final

    @commands.command(pass_context=True, aliases=['magik5', 'mirror3'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def woow(self, ctx, *urls:str):
        get_images = await self.get_images(ctx, urls=urls, limit=5)
        if not get_images:
            return
        for url in get_images:
            b = await self.bytes_download(url)
            if b is False:
                if len(get_images) == 1:
                    await ctx.send(':warning: **Command download function failed...**')
                    return
                continue
            final = await self.bot.loop.run_in_executor(None, self.do_woow, b)
            file = discord.File(final, filename='woow.png')
            await ctx.send(file=file)

    def do_hooh(self, b):
        f = BytesIO()
        f2 = BytesIO()
        with wand.image.Image(file=b, format='png') as img:
            h1 = img.clone()
            width = int(img.width) if int(img.width) > 0 else 1
            h1.crop(width=width, height=int(img.height/2), gravity='south')
            h2 = h1.clone()
            h1.rotate(degree=180)
            h2.flop()
            h1.save(file=f)
            h2.save(file=f2)
        f.seek(0)
        f2.seek(0)
        list_im = [f, f2]
        imgs = [PIL.Image.open(i).convert('RGBA') for i in list_im]
        min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
        imgs_comb = np.vstack((np.asarray(i.resize(min_shape)) for i in imgs))
        imgs_comb = PIL.Image.fromarray(imgs_comb)
        final = BytesIO()
        imgs_comb.save(final, 'png')
        final.seek(0)
        return final

    @commands.command(pass_context=True, aliases=['magik6', 'mirror4'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def hooh(self, ctx, *urls:str):
        get_images = await self.get_images(ctx, urls=urls, limit=5)
        if not get_images:
            return
        for url in get_images:
            b = await self.bytes_download(url)
            if b is False:
                if len(get_images) == 1:
                    await ctx.send(':warning: **Command download function failed...**')
                    return
                continue
            final = await self.bot.loop.run_in_executor(None, self.do_hooh, b)
            file = discord.File(final, filename='hooh.png')
            await ctx.send(file=file)

    @commands.command(pass_context=True)
    async def flipimg(self, ctx, *urls:str):
        get_images = await self.get_images(ctx, urls=urls, limit=5)
        if not get_images:
            return
        for url in get_images:      
            b = await self.bytes_download(url)
            img = PIL.Image.open(b)
            img = PIL.ImageOps.flip(img)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            file = discord.File(final, filename='flip.png')
            await ctx.send(file=file)

    @commands.command(pass_context=True)
    async def flop(self, ctx, *urls:str):
        get_images = await self.get_images(ctx, urls=urls, limit=5)
        if not get_images:
            return
        for url in get_images:      
            b = await self.bytes_download(url)
            img = PIL.Image.open(b)
            img = PIL.ImageOps.mirror(img)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            file = discord.File(final, filename='flop.png')
            await ctx.send(file=file)

    @commands.command(pass_context=True, aliases=['inverse', 'negate'])
    async def invert(self, ctx, url:str="None"):
        get_images = await self.get_images(ctx, urls=url, limit=3)
        if not get_images:
            return
        for url in get_images:      
            b = await self.bytes_download(url)
            img = PIL.Image.open(b).convert('RGBA')
            img = PIL.ImageOps.invert(img)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            file = discord.File(final, filename='flop.png')
            await ctx.send(file=file)

    @commands.command(pass_context=True)
    async def rotate(self, ctx, *urls:str):
        """Rotate image X degrees"""
        get_images = await self.get_images(ctx, urls=urls, limit=3, scale=360)
        if not get_images:
            return
        img_urls = get_images[0]
        scale = get_images[1] if get_images[1] else random.choice([90, 180, 50, 45, 270, 120, 80])
        for url in img_urls:
            b = await self.bytes_download(url)
            img = PIL.Image.open(b).convert('RGBA')
            img = img.rotate(int(scale))
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            file = discord.File(final, filename='rotate.png')
            await ctx.send('Rotated: `{0}°`'.format(scale), file=file)

    def __unload(self):
        self.bot.loop.create_task(self.session.close())

    __del__ = __unload
