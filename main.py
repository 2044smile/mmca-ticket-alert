import requests
import time
from datetime import datetime
from telegram import send_telegram

# ============================================================
# 설정
# ============================================================
TIME_IDS = {
    "10:00~11:00": 186105,
    "11:00~12:00": 186111,
    "12:00~13:00": 186117,
    "13:00~14:00": 186123,
    "14:00~15:00": 186129,
    "15:00~16:00": 186135,
    "16:00~17:00": 186141,
}
CHECK_INTERVAL = 60
# ============================================================

BASE_URL = "https://booking.mmca.go.kr/product/ko/performance/time/{time_id}"
HEADERS  = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://booking.mmca.go.kr/product/ko/performance/490",
}


def check_slot(label: str, time_id: int) -> dict:
    try:
        res = requests.get(BASE_URL.format(time_id=time_id), headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        return {"label": label, "error": str(e)}

    pt    = data.get("PlayTime", {})
    seats = pt.get("Seats", [])

    return {
        "label":     label,
        "time":      pt.get("PlayPeriod", "?"),
        "bookable":  pt.get("IsBookable", False),
        "status":    pt.get("BookableStatusName", "?"),
        "remaining": seats[0].get("BookableCount", 0) if seats else 0,
    }


def main():
    notified = set()
    count = 0

    print(f"모니터링 시작 | 4월 12일 | 주기: {CHECK_INTERVAL}초")
    print("종료하려면 Ctrl+C\n")

    while True:
        count += 1
        print(f"\n[{count}회차] {datetime.now().strftime('%H:%M:%S')} 확인 중...")
        print("=" * 50)

        for label, time_id in TIME_IDS.items():
            result = check_slot(label, time_id)

            if "error" in result:
                print(f"  ❓ [{label}] 오류: {result['error']}")
                continue

            icon = "🟢" if result["bookable"] else "🔴"
            print(f"  {icon} [{result['time']}] {result['status']} | 잔여석: {result['remaining']}석")

            if result["bookable"] and label not in notified:
                msg = (
                    f"🎟 [데이미언 허스트] 4월 12일 예매 가능!\n"
                    f"시간: {result['time']}\n"
                    f"잔여석: {result['remaining']}석\n"
                    f"지금 바로 예매하세요!"
                )
                ok = send_telegram(msg)
                if ok:
                    print(f"  ✅ 텔레그램 알림 전송 완료!")
                    notified.add(label)
                else:
                    print(f"  ⚠️ 텔레그램 전송 실패")

        print("=" * 50)
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()