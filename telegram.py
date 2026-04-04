import requests
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ============================================================
# 텔레그램 설정
# ============================================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS  = os.getenv("CHAT_IDS", "").split(",")
# ============================================================

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def send_telegram(message: str) -> bool:
    success = True
    for chat_id in CHAT_IDS:
        res = requests.post(
            BASE_URL,
            json={"chat_id": chat_id, "text": message},
            timeout=10
        )
        if res.status_code == 200:
            print(f"[텔레그램] {chat_id} 전송 완료")
        else:
            print(f"[텔레그램] {chat_id} 전송 실패: {res.text}")
            success = False
    return success