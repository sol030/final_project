import os
import pandas as pd

# 원본 CSV 경로
RAW_FILES = {
    "10월": "data/raw/mart_total_final_oct.csv",
    "11월": "data/raw/mart_total_final_nov.csv",
}

# 요약 CSV 저장 폴더
OUTPUT_DIR = "data/summary"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHUNKSIZE = 500_000

# 전체 현황 분석 KPI에 필요한 컬럼만 읽기
usecols = [
    "event_type",
    "price",
    "user_id",
    "user_session",
]

summary_rows = []
funnel_rows = []

for month, path in RAW_FILES.items():
    print(f"\n===== {month} 전체 현황 KPI 처리 시작 =====")

    view_count = 0
    cart_count = 0
    purchase_count = 0
    remove_count = 0

    total_revenue = 0.0

    total_users = set()
    purchase_users = set()
    total_sessions = set()
    purchase_sessions = set()

    for i, chunk in enumerate(pd.read_csv(path, usecols=usecols, chunksize=CHUNKSIZE)):
        print(f"{month} chunk {i + 1} 처리 중...")

        chunk["event_type"] = chunk["event_type"].astype(str)

        view_mask = chunk["event_type"] == "view"
        cart_mask = chunk["event_type"] == "cart"
        purchase_mask = chunk["event_type"] == "purchase"
        remove_mask = chunk["event_type"] == "remove_from_cart"

        # 이벤트 수
        view_count += int(view_mask.sum())
        cart_count += int(cart_mask.sum())
        purchase_count += int(purchase_mask.sum())
        remove_count += int(remove_mask.sum())

        # 구매 매출: purchase 이벤트의 price 합계
        total_revenue += chunk.loc[purchase_mask, "price"].fillna(0).sum()

        # 유저 수
        total_users.update(chunk["user_id"].dropna().unique())
        purchase_users.update(chunk.loc[purchase_mask, "user_id"].dropna().unique())

        # 세션 수
        total_sessions.update(chunk["user_session"].dropna().unique())
        purchase_sessions.update(chunk.loc[purchase_mask, "user_session"].dropna().unique())

    # 전환율 계산
    view_to_cart_rate = cart_count / view_count * 100 if view_count > 0 else 0
    cart_to_purchase_rate = purchase_count / cart_count * 100 if cart_count > 0 else 0
    view_to_purchase_rate = purchase_count / view_count * 100 if view_count > 0 else 0

    purchase_user_rate = (
        len(purchase_users) / len(total_users) * 100
        if len(total_users) > 0
        else 0
    )

    purchase_session_rate = (
        len(purchase_sessions) / len(total_sessions) * 100
        if len(total_sessions) > 0
        else 0
    )

    # KPI 요약 행
    summary_rows.append({
        "month": month,
        "view_count": view_count,
        "cart_count": cart_count,
        "purchase_count": purchase_count,
        "remove_from_cart_count": remove_count,
        "total_revenue": round(total_revenue, 2),
        "total_user_count": len(total_users),
        "purchase_user_count": len(purchase_users),
        "total_session_count": len(total_sessions),
        "purchase_session_count": len(purchase_sessions),
        "view_to_cart_rate": round(view_to_cart_rate, 2),
        "cart_to_purchase_rate": round(cart_to_purchase_rate, 2),
        "view_to_purchase_rate": round(view_to_purchase_rate, 2),
        "purchase_user_rate": round(purchase_user_rate, 2),
        "purchase_session_rate": round(purchase_session_rate, 2),
    })

    # 퍼널용 요약 행
    funnel_rows.extend([
        {
            "month": month,
            "stage": "view",
            "count": view_count,
        },
        {
            "month": month,
            "stage": "cart",
            "count": cart_count,
        },
        {
            "month": month,
            "stage": "purchase",
            "count": purchase_count,
        },
    ])

# DataFrame 변환
summary_df = pd.DataFrame(summary_rows)
funnel_df = pd.DataFrame(funnel_rows)

# 저장 경로
summary_path = f"{OUTPUT_DIR}/01_overview_kpi_summary.csv"
funnel_path = f"{OUTPUT_DIR}/01_overview_funnel_summary.csv"

# CSV 저장
summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
funnel_df.to_csv(funnel_path, index=False, encoding="utf-8-sig")

print("\n===== 01_overview_kpi_summary.csv 저장 완료 =====")
print(summary_df)

print("\n===== 01_overview_funnel_summary.csv 저장 완료 =====")
print(funnel_df)