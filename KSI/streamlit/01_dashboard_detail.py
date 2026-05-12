import os
from collections import defaultdict

import pandas as pd

RAW_FILES = {
    "10월": "data/raw/mart_total_final_oct.csv",
    "11월": "data/raw/mart_total_final_nov.csv",
}

OUTPUT_DIR = "data/summary"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHUNKSIZE = 500_000

usecols = [
    "event_date",
    "event_type",
    "price",
    "user_id",
    "user_session",
]

daily_stats = {}
first_vs_revisit_stats = {}

for month, path in RAW_FILES.items():
    print(f"\n===== {month} 전체 현황 보완 요약 처리 시작 =====")

    # user_id별 해당 월 첫 활동일 저장
    user_first_date = {}

    # =========================
    # 1차 pass: 일별 요약 + 유저별 첫 활동일 수집
    # =========================
    for i, chunk in enumerate(pd.read_csv(path, usecols=usecols, chunksize=CHUNKSIZE)):
        print(f"{month} 1차 chunk {i + 1} 처리 중...")

        chunk = chunk.dropna(subset=["event_date", "user_id"]).copy()
        chunk["event_date"] = chunk["event_date"].astype(str)
        chunk["event_type"] = chunk["event_type"].astype(str)
        chunk["price"] = chunk["price"].fillna(0)

        # -------------------------
        # user_id별 첫 활동일 저장
        # -------------------------
        user_min_dates = chunk.groupby("user_id")["event_date"].min()

        for user_id, first_date in user_min_dates.items():
            if user_id not in user_first_date:
                user_first_date[user_id] = first_date
            else:
                if first_date < user_first_date[user_id]:
                    user_first_date[user_id] = first_date

        # -------------------------
        # 일별 요약
        # -------------------------
        for event_date, group in chunk.groupby("event_date"):
            key = (month, event_date)

            if key not in daily_stats:
                daily_stats[key] = {
                    "view_count": 0,
                    "cart_count": 0,
                    "purchase_count": 0,
                    "remove_from_cart_count": 0,
                    "revenue": 0.0,
                    "users": set(),
                    "sessions": set(),
                }

            view_mask = group["event_type"] == "view"
            cart_mask = group["event_type"] == "cart"
            purchase_mask = group["event_type"] == "purchase"
            remove_mask = group["event_type"] == "remove_from_cart"

            daily_stats[key]["view_count"] += int(view_mask.sum())
            daily_stats[key]["cart_count"] += int(cart_mask.sum())
            daily_stats[key]["purchase_count"] += int(purchase_mask.sum())
            daily_stats[key]["remove_from_cart_count"] += int(remove_mask.sum())
            daily_stats[key]["revenue"] += group.loc[purchase_mask, "price"].sum()

            daily_stats[key]["users"].update(group["user_id"].dropna().unique())
            daily_stats[key]["sessions"].update(group["user_session"].dropna().unique())

    print(f"{month} user_first_date 생성 완료. 사용자 수: {len(user_first_date):,}")

    # =========================
    # 2차 pass: 첫방문 vs 재방문 요약
    # =========================
    for i, chunk in enumerate(pd.read_csv(path, usecols=usecols, chunksize=CHUNKSIZE)):
        print(f"{month} 2차 chunk {i + 1} 처리 중...")

        chunk = chunk.dropna(subset=["event_date", "user_id"]).copy()
        chunk["event_date"] = chunk["event_date"].astype(str)
        chunk["event_type"] = chunk["event_type"].astype(str)
        chunk["price"] = chunk["price"].fillna(0)

        # 각 row의 user_id에 해당하는 첫 활동일 매핑
        chunk["first_date"] = chunk["user_id"].map(user_first_date)

        # 첫 활동일과 같은 날짜면 첫방문, 이후 날짜면 재방문
        chunk["visit_type"] = chunk.apply(
            lambda row: "첫방문" if row["event_date"] == row["first_date"] else "재방문",
            axis=1
        )

        for visit_type, group in chunk.groupby("visit_type"):
            key = (month, visit_type)

            if key not in first_vs_revisit_stats:
                first_vs_revisit_stats[key] = {
                    "view_count": 0,
                    "cart_count": 0,
                    "purchase_count": 0,
                    "remove_from_cart_count": 0,
                    "revenue": 0.0,
                    "users": set(),
                    "sessions": set(),
                }

            view_mask = group["event_type"] == "view"
            cart_mask = group["event_type"] == "cart"
            purchase_mask = group["event_type"] == "purchase"
            remove_mask = group["event_type"] == "remove_from_cart"

            first_vs_revisit_stats[key]["view_count"] += int(view_mask.sum())
            first_vs_revisit_stats[key]["cart_count"] += int(cart_mask.sum())
            first_vs_revisit_stats[key]["purchase_count"] += int(purchase_mask.sum())
            first_vs_revisit_stats[key]["remove_from_cart_count"] += int(remove_mask.sum())
            first_vs_revisit_stats[key]["revenue"] += group.loc[purchase_mask, "price"].sum()

            first_vs_revisit_stats[key]["users"].update(group["user_id"].dropna().unique())
            first_vs_revisit_stats[key]["sessions"].update(group["user_session"].dropna().unique())


# =========================
# 1) daily summary 저장
# =========================
daily_rows = []

for (month, event_date), stats in daily_stats.items():
    view_count = stats["view_count"]
    cart_count = stats["cart_count"]
    purchase_count = stats["purchase_count"]

    daily_rows.append({
        "month": month,
        "event_date": event_date,
        "view_count": view_count,
        "cart_count": cart_count,
        "purchase_count": purchase_count,
        "remove_from_cart_count": stats["remove_from_cart_count"],
        "revenue": round(stats["revenue"], 2),
        "daily_user_count": len(stats["users"]),
        "daily_session_count": len(stats["sessions"]),
        "view_to_cart_rate": round(cart_count / view_count * 100, 2) if view_count > 0 else 0,
        "cart_to_purchase_rate": round(purchase_count / cart_count * 100, 2) if cart_count > 0 else 0,
        "view_to_purchase_rate": round(purchase_count / view_count * 100, 2) if view_count > 0 else 0,
    })

daily_df = pd.DataFrame(daily_rows)
daily_df = daily_df.sort_values(["month", "event_date"])

daily_path = f"{OUTPUT_DIR}/01_overview_daily_summary.csv"
daily_df.to_csv(daily_path, index=False, encoding="utf-8-sig")


# =========================
# 2) first vs revisit summary 저장
# =========================
first_vs_rows = []

# 월별 전체 revenue 계산용
monthly_revenue = defaultdict(float)

for (month, visit_type), stats in first_vs_revisit_stats.items():
    monthly_revenue[month] += stats["revenue"]

for (month, visit_type), stats in first_vs_revisit_stats.items():
    revenue = stats["revenue"]
    total_month_revenue = monthly_revenue[month]

    view_count = stats["view_count"]
    cart_count = stats["cart_count"]
    purchase_count = stats["purchase_count"]

    first_vs_rows.append({
        "month": month,
        "visit_type": visit_type,
        "user_count": len(stats["users"]),
        "session_count": len(stats["sessions"]),
        "view_count": view_count,
        "cart_count": cart_count,
        "purchase_count": purchase_count,
        "remove_from_cart_count": stats["remove_from_cart_count"],
        "revenue": round(revenue, 2),
        "revenue_ratio": round(revenue / total_month_revenue * 100, 2) if total_month_revenue > 0 else 0,
        "view_to_cart_rate": round(cart_count / view_count * 100, 2) if view_count > 0 else 0,
        "cart_to_purchase_rate": round(purchase_count / cart_count * 100, 2) if cart_count > 0 else 0,
        "view_to_purchase_rate": round(purchase_count / view_count * 100, 2) if view_count > 0 else 0,
    })

first_vs_df = pd.DataFrame(first_vs_rows)

visit_order = {"첫방문": 1, "재방문": 2}
first_vs_df["visit_order"] = first_vs_df["visit_type"].map(visit_order)
first_vs_df = first_vs_df.sort_values(["month", "visit_order"]).drop(columns=["visit_order"])

first_vs_path = f"{OUTPUT_DIR}/01_overview_first_vs_revisit.csv"
first_vs_df.to_csv(first_vs_path, index=False, encoding="utf-8-sig")


print("\n===== 01_overview_daily_summary.csv 저장 완료 =====")
print(daily_df.head(40))

print("\n===== 01_overview_first_vs_revisit.csv 저장 완료 =====")
print(first_vs_df)