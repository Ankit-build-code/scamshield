import hashlib
from app.db.session import SessionLocal, Base, engine
from app.models.scam import ScamNumber, ScamURL, ScamKeyword
from app.services.scam_detector import normalize_number, normalize_url

Base.metadata.create_all(bind=engine)

# (keyword, weight 1-10, language)
KEYWORDS = [
    ("verify your account", 4, "en"), ("account suspended", 4, "en"),
    ("update your kyc", 5, "en"), ("click the link", 3, "en"),
    ("claim your reward", 4, "en"), ("processing fee", 5, "en"),
    ("refund", 3, "en"), ("electricity bill", 3, "en"),
    ("disconnected tonight", 5, "en"), ("gift card", 4, "en"),
    ("work from home", 3, "en"), ("earn daily", 4, "en"),
    ("investment guaranteed", 5, "en"), ("double your money", 5, "en"),
    ("parcel", 2, "en"), ("courier", 2, "en"), ("anydesk", 6, "en"),
    ("teamviewer", 6, "en"), ("screen share", 5, "en"),
    ("sim block", 5, "en"), ("aadhaar", 3, "en"), ("loan approved", 4, "en"),
    ("वेरिफाई", 4, "hi"), ("केवाईसी अपडेट", 5, "hi"),
    ("बिजली कनेक्शन कट", 5, "hi"), ("रिफंड", 3, "hi"),
    ("इनाम जीता", 4, "hi"), ("प्रोसेसिंग फीस", 5, "hi"),
    ("घर बैठे कमाएं", 4, "hi"), ("आधार", 3, "hi"),
    ("सिम बंद", 5, "hi"), ("लोन मंजूर", 4, "hi"),
    ("किसी को मत बताना", 6, "hi"), ("kisi ko batana mat", 6, "hinglish"),
    ("paise bhej do", 5, "hinglish"), ("jaldi paise", 5, "hinglish"),
]

# Ye sirf DEMO ke fake numbers hain
NUMBERS = [
    ("9999900001", "bank_fraud", 42), ("9999900002", "kyc_scam", 31),
    ("9999900003", "lottery", 18), ("9999900004", "digital_arrest", 57),
    ("9999900005", "electricity_bill", 25),
]

# Ye bhi demo ke fake domains hain
URLS = [
    ("http://sbi-kyc-update.xyz/login", "bank_phishing"),
    ("http://paytm-reward-claim.top/win", "lottery"),
    ("http://electricity-bill-pay.click/now", "utility_scam"),
    ("http://aadhaar-verify-online.tk", "identity_theft"),
]

db = SessionLocal()
added = {"kw": 0, "num": 0, "url": 0}

for kw, w, lang in KEYWORDS:
    if not db.query(ScamKeyword).filter_by(keyword=kw).first():
        db.add(ScamKeyword(keyword=kw, weight=w, language=lang)); added["kw"] += 1

for num, cat, cnt in NUMBERS:
    n = normalize_number(num)
    if not db.query(ScamNumber).filter_by(number=n).first():
        db.add(ScamNumber(number=n, category=cat, report_count=cnt)); added["num"] += 1

for url, cat in URLS:
    u = normalize_url(url)
    h = hashlib.sha256(u.encode()).hexdigest()
    if not db.query(ScamURL).filter_by(url_hash=h).first():
        db.add(ScamURL(url_hash=h, domain=u.split("/")[2], category=cat)); added["url"] += 1

db.commit()
db.close()
print("Added:", added)