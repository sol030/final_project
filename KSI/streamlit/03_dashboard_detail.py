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

SMARTPHONE_CATEGORY = "electronics.smartphone"

usecols = [
    "event_type",
    "category_code",
    "brand",
    "price",
    "user_id",
    "user_session",
    "hour",
    "time_segment",
    "price_tier",
    "time_to_purchase_sec",
    "consider_purchase_tier",
    "decision_tier",
]

# 1) 시간대별 스마트폰 구매 패턴
time_stats = {}

# 2) 가격대별 구매 소요시간
price_tier_stats = {}

# 3) 함께 구매/관심 카테고리 TOP3용
# 스마트폰 구매 유저 집합
smartphone_purchase_users_by_month = defaultdict(set)

# 스마트폰 구매 유저가 구매한 다른 카테고리
bundle_category_stats = {}

for month, path in RAW_FILES.items():
    print(f"\n===== {month} 스마트폰 상세 요약 처리 시작 =====")

    # 1차: 스마트폰 구매 유저 수집 + 시간/가격대 요약
    for i, chunk in enumerate(pd.read_csv(path, usecols=usecols, chunksize=CHUNKSIZE)):
        print(f"{month} 1차 chunk {i + 1} 처리 중...")

        chunk["category_code"] = chunk["category_code"].fillna("unknown_category")
        chunk["brand"] = chunk["brand"].fillna("unknown_brand")
        chunk["price"] = chunk["price"].fillna(0)

        smartphone_df = chunk[chunk["category_code"] == SMARTPHONE_CATEGORY].copy()

        if smartphone_df.empty:
            continue

        smartphone_purchase = smartphone_df[
            smartphone_df["event_type"] == "purchase"
        ].copy()

        if smartphone_purchase.empty:
            continue

        # 스마트폰 구매 유저 저장
        smartphone_purchase_users_by_month[month].update(
            smartphone_purchase["user_id"].dropna().unique()
        )

        # =========================
        # 1) 시간대별 구매 패턴
        # =========================
        smartphone_purchase["hour"] = smartphone_purchase["hour"].fillna(-1).astype(int)
        smartphone_purchase["time_segment"] = smartphone_purchase["time_segment"].fillna("unknown_time")

        grouped_time = smartphone_purchase.groupby(
            ["brand", "hour", "time_segment"]
        ).agg(
            purchase_count=("event_type", "count"),
            revenue=("price", "sum"),
            purchase_user_count=("user_id", pd.Series.nunique),
        ).reset_index()

        for _, row in grouped_time.iterrows():
            key = (
                month,
                row["brand"],
                int(row["hour"]),
                row["time_segment"],
            )

            if key not in time_stats:
                time_stats[key] = {
                    "purchase_count": 0,
                    "revenue": 0.0,
                    "purchase_users": set(),
                }

            time_stats[key]["purchase_count"] += int(row["purchase_count"])
            time_stats[key]["revenue"] += float(row["revenue"])

            users = smartphone_purchase[
                (smartphone_purchase["brand"] == row["brand"])
                & (smartphone_purchase["hour"] == row["hour"])
                & (smartphone_purchase["time_segment"] == row["time_segment"])
            ]["user_id"].dropna().unique()

            time_stats[key]["purchase_users"].update(users)

        # =========================
        # 2) 가격대별 구매 소요시간
        # =========================
        smartphone_purchase["price_tier"] = smartphone_purchase["price_tier"].fillna("unknown_price_tier")
        smartphone_purchase["consider_purchase_tier"] = smartphone_purchase["consider_purchase_tier"].fillna("unknown_consider_tier")
        smartphone_purchase["decision_tier"] = smartphone_purchase["decision_tier"].fillna("unknown_decision_tier")

        grouped_price = smartphone_purchase.groupby(
            ["brand", "price_tier", "consider_purchase_tier", "decision_tier"]
        ).agg(
            purchase_count=("event_type", "count"),
            revenue=("price", "sum"),
            avg_time_to_purchase_sec=("time_to_purchase_sec", "mean"),
            median_time_to_purchase_sec=("time_to_purchase_sec", "median"),
            purchase_user_count=("user_id", pd.Series.nunique),
        ).reset_index()

        for _, row in grouped_price.iterrows():
            key = (
                month,
                row["brand"],
                row["price_tier"],
                row["consider_purchase_tier"],
                row["decision_tier"],
            )

            if key not in price_tier_stats:
                price_tier_stats[key] = {
                    "purchase_count": 0,
                    "revenue": 0.0,
                    "time_sum": 0.0,
                    "time_count": 0,
                    "median_values": [],
                    "purchase_users": set(),
                }

            purchase_count = int(row["purchase_count"])
            avg_time = row["avg_time_to_purchase_sec"]

            price_tier_stats[key]["purchase_count"] += purchase_count
            price_tier_stats[key]["revenue"] += float(row["revenue"])

            if pd.notna(avg_time):
                price_tier_stats[key]["time_sum"] += float(avg_time) * purchase_count
                price_tier_stats[key]["time_count"] += purchase_count

            if pd.notna(row["median_time_to_purchase_sec"]):
                price_tier_stats[key]["median_values"].append(float(row["median_time_to_purchase_sec"]))

            users = smartphone_purchase[
                (smartphone_purchase["brand"] == row["brand"])
                & (smartphone_purchase["price_tier"] == row["price_tier"])
                & (smartphone_purchase["consider_purchase_tier"] == row["consider_purchase_tier"])
                & (smartphone_purchase["decision_tier"] == row["decision_tier"])
            ]["user_id"].dropna().unique()

            price_tier_stats[key]["purchase_users"].update(users)

    print(f"{month} 스마트폰 구매 유저 수집 완료: {len(smartphone_purchase_users_by_month[month]):,}")

    # 2차: 스마트폰 구매 유저가 함께 구매한 카테고리 집계
    # 원본이 크기 때문에 다시 한 번 읽지만, 필요한 기준을 명확히 하기 위함
    smartphone_users = smartphone_purchase_users_by_month[month]

    for i, chunk in enumerate(pd.read_csv(path, usecols=["event_type", "category_code", "price", "user_id"], chunksize=CHUNKSIZE)):
        print(f"{month} 2차 chunk {i + 1} 처리 중...")

        purchase_df = chunk[
            (chunk["event_type"] == "purchase")
            & (chunk["user_id"].isin(smartphone_users))
        ].copy()

        if purchase_df.empty:
            continue

        purchase_df["category_code"] = purchase_df["category_code"].fillna("unknown_category")
        purchase_df["price"] = purchase_df["price"].fillna(0)

        # 스마트폰 자체는 제외하고 함께 구매한 카테고리만 보기
        purchase_df = purchase_df[purchase_df["category_code"] != SMARTPHONE_CATEGORY]

        if purchase_df.empty:
            continue

        grouped_bundle = purchase_df.groupby("category_code").agg(
            purchase_count=("event_type", "count"),
            revenue=("price", "sum"),
            buyer_count=("user_id", pd.Series.nunique),
        ).reset_index()

        for _, row in grouped_bundle.iterrows():
            key = (month, row["category_code"])

            if key not in bundle_category_stats:
                bundle_category_stats[key] = {
                    "purchase_count": 0,
                    "revenue": 0.0,
                    "buyers": set(),
                }

            bundle_category_stats[key]["purchase_count"] += int(row["purchase_count"])
            bundle_category_stats[key]["revenue"] += float(row["revenue"])

            users = purchase_df[
                purchase_df["category_code"] == row["category_code"]
            ]["user_id"].dropna().unique()

            bundle_category_stats[key]["buyers"].update(users)


# =========================
# 1) 시간대별 구매 패턴 저장
# =========================
time_rows = []

for (month, brand, hour, time_segment), stats in time_stats.items():
    time_rows.append({
        "month": month,
        "brand": brand,
        "hour": hour,
        "time_segment": time_segment,
        "purchase_count": stats["purchase_count"],
        "revenue": round(stats["revenue"], 2),
        "purchase_user_count": len(stats["purchase_users"]),
    })

time_df = pd.DataFrame(time_rows)

if not time_df.empty:
    time_df = time_df.sort_values(["month", "brand", "hour"])


# =========================
# 2) 가격대별 구매 소요시간 저장
# =========================
price_rows = []

for (month, brand, price_tier, consider_tier, decision_tier), stats in price_tier_stats.items():
    avg_time = (
        stats["time_sum"] / stats["time_count"]
        if stats["time_count"] > 0
        else None
    )

    # 여러 chunk의 median을 다시 정확히 계산한 것은 아니고,
    # chunk별 median의 중앙값으로 근사
    median_time = (
        pd.Series(stats["median_values"]).median()
        if len(stats["median_values"]) > 0
        else None
    )

    price_rows.append({
        "month": month,
        "brand": brand,
        "price_tier": price_tier,
        "consider_purchase_tier": consider_tier,
        "decision_tier": decision_tier,
        "purchase_count": stats["purchase_count"],
        "revenue": round(stats["revenue"], 2),
        "purchase_user_count": len(stats["purchase_users"]),
        "avg_time_to_purchase_sec": round(avg_time, 2) if avg_time is not None else None,
        "median_time_to_purchase_sec_approx": round(median_time, 2) if median_time is not None else None,
    })

price_df = pd.DataFrame(price_rows)

if not price_df.empty:
    price_df = price_df.sort_values(["month", "brand", "price_tier"])


# =========================
# 3) 함께 구매한 카테고리 TOP3 저장
# =========================
bundle_rows = []

for (month, category_code), stats in bundle_category_stats.items():
    bundle_rows.append({
        "month": month,
        "category_code": category_code,
        "purchase_count": stats["purchase_count"],
        "revenue": round(stats["revenue"], 2),
        "buyer_count": len(stats["buyers"]),
    })

bundle_df = pd.DataFrame(bundle_rows)

if not bundle_df.empty:
    bundle_df = (
        bundle_df
        .sort_values(["month", "purchase_count", "revenue"], ascending=[True, False, False])
        .groupby("month")
        .head(3)
        .copy()
    )

    bundle_df["rank"] = (
        bundle_df
        .groupby("month")["purchase_count"]
        .rank(method="first", ascending=False)
        .astype(int)
    )

    bundle_df = bundle_df.sort_values(["month", "rank"])


# 저장
time_path = f"{OUTPUT_DIR}/03_smartphone_time_summary.csv"
price_path = f"{OUTPUT_DIR}/03_smartphone_price_tier_summary.csv"
bundle_path = f"{OUTPUT_DIR}/03_smartphone_bundle_top3.csv"

time_df.to_csv(time_path, index=False, encoding="utf-8-sig")
price_df.to_csv(price_path, index=False, encoding="utf-8-sig")
bundle_df.to_csv(bundle_path, index=False, encoding="utf-8-sig")

print("\n===== 03_smartphone_time_summary.csv 저장 완료 =====")
print(time_df.head(30))

print("\n===== 03_smartphone_price_tier_summary.csv 저장 완료 =====")
print(price_df.head(30))

print("\n===== 03_smartphone_bundle_top3.csv 저장 완료 =====")
print(bundle_df)