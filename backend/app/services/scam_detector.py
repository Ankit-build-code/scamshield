import re
import hashlib
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from app.models.scam import ScamNumber, ScamURL, ScamKeyword

SUSPICIOUS_TLDS = (".xyz", ".top", ".click", ".loan", ".work", ".gq", ".tk")
SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "goo.gl", "cutt.ly", "is.gd")

def normalize_number(number: str) -> str:
    digits = re.sub(r"\D", "", number)
    return digits[-10:] if len(digits) >= 10 else digits

def normalize_url(url: str) -> str:
    url = url.strip().lower()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url

def check_number(db: Session, number: str):
    n = normalize_number(number)
    reasons, score = [], 0
    hit = db.query(ScamNumber).filter(ScamNumber.number == n).first()
    if hit:
        score += 90
        reasons.append(f"यह नंबर पहले scam के रूप में report हो चुका है ({hit.report_count} बार)")
    return score, reasons

def check_url(db: Session, url: str):
    u = normalize_url(url)
    reasons, score = [], 0
    h = hashlib.sha256(u.encode()).hexdigest()
    if db.query(ScamURL).filter(ScamURL.url_hash == h).first():
        score += 90
        reasons.append("यह link known scam database में मौजूद है")

    host = urlparse(u).hostname or ""
    if host.endswith(SUSPICIOUS_TLDS):
        score += 30
        reasons.append("Domain का extension अक्सर scam sites में use होता है")
    if host in SHORTENERS:
        score += 25
        reasons.append("Shortened link है, असली destination छिपा हुआ है")
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
        score += 35
        reasons.append("Link में domain की जगह सीधा IP address है")
    if u.startswith("http://"):
        score += 10
        reasons.append("Link secure (HTTPS) नहीं है")
    return score, reasons

URGENCY_PATTERNS = [
    (r"urgent|immediately|right now|last chance|expire|jaldi|turant|abhi|तुरंत|जल्दी|अभी", 20, "Urgency बनाने वाली भाषा"),
    (r"(share|send|tell|reveal|give|batao|bataye|bhej|bhejo|bolo|bolein).{0,20}(otp|pin|cvv|password)|(otp|pin|cvv|password).{0,20}(share|send|batao|bataye|bhej|bhejo|bolo|bolein)|(बताएं|भेजें|शेयर).{0,15}(ओटीपी|पिन)|(ओटीपी|पिन).{0,15}(बताएं|भेजें|शेयर)", 35, "OTP/PIN/password share करने को कहा जा रहा है"),
    (r"kyc|account.*(block|suspend|freeze)|खाता.*(बंद|ब्लॉक)", 30, "Account block/KYC का डर दिखाया जा रहा है"),
    (r"lottery|prize|winner|jackpot|इनाम|लॉटरी", 30, "इनाम/लॉटरी का लालच"),
    (r"arrest|police|cbi|customs|digital arrest|गिरफ्तार", 35, "पुलिस/गिरफ्तारी का डर दिखाया जा रहा है"),
    (r"https?://\S+|www\.\S+", 10, "Message में link मौजूद है"),
    (r"बिजली.*(कट|काट)|बिजली.*बिल|bijli.*(kat|cut)|light.*(kat|cut)|power.*(cut|disconnect)", 30, "बिजली कटने का डर दिखाया जा रहा है"),
    (r"(लिंक|link).*(क्लिक|click|खोल)|(क्लिक|click).*(लिंक|link)", 25, "Link पर click करने को कहा जा रहा है"),
]

NEGATION_WORDS = ("do not", "don't", "never", "mat", "nahi", "ना ", "न ", "मत")

def check_message(db: Session, text: str):
    t = text.lower()
    reasons, score = [], 0
    for pattern, pts, reason in URGENCY_PATTERNS:
        match = re.search(pattern, t)
        if match:
            window = t[max(0, match.start()-15):match.end()+15]
            if "otp" in pattern or "pin" in pattern:
                if any(neg in window for neg in NEGATION_WORDS):
                    continue  # ye "OTP mat batao" jaisa normal warning hai, scam nahi
            score += pts
            reasons.append(reason)
    for kw in db.query(ScamKeyword).all():
        if kw.keyword.lower() in t:
            score += kw.weight * 3
            reasons.append(f"संदिग्ध शब्द: {kw.keyword}")
    for link in re.findall(r"https?://\S+|www\.\S+", text):
        s, r = check_url(db, link)
        score += s
        reasons += r
    return score, reasons

def to_verdict(score: int) -> str:
    if score >= 60:
        return "dangerous"
    if score >= 25:
        return "suspicious"
    return "safe"