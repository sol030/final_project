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
    "user_id",
    "event_date",
    "event_type",
    "category_code",
]

cohort_rows = []
category_top_rows = []
buyer_compare_rows = []

for month, path in RAW_FILES.items():
    print(f"\n===== {month} 리텐션 상세 요약 처리 시작 =====")

    max_day = 31 if month == "10월" else 30

    # user_id별 활동일 저장
    user_days = defaultdict(set)

    # 구매자 집합
    purchase_users = set()

    # 스마트폰 구매자 집합
    smartphone_purchase_users = set()

    # 카테고리별 구매자 집합
    category_purchase_users = defaultdict(set)

    for i, chunk in enumerate(pd.read_csv(path, usecols=usecols, chunksize=CHUNKSIZE)):
        print(f"{month} chunk {i + 1} 처리 중...")

        chunk = chunk.dropna(subset=["user_id", "event_date"]).copy()

        # event_date에서 일(day) 추출
        chunk["day"] = chunk["event_date"].astype(str).str[-2:].astype("int16")

        # 유저별 활동일 저장
        user_day_pairs = chunk[["user_id", "day"]].drop_duplicates()
        grouped_days = user_day_pairs.groupby("user_id")["day"].unique()

        for user_id, days in grouped_days.items():
            user_days[user_id].update(days.tolist())

        # 구매 이벤트만 추출
        purchase_df = chunk[chunk["event_type"] == "purchase"].copy()

        if purchase_df.empty:
            continue

        purchase_df["category_code"] = purchase_df["category_code"].fillna("unknown_category")

        # 전체 구매자
        purchase_users.update(purchase_df["user_id"].dropna().unique())

        # 스마트폰 구매자
        smartphone_users = purchase_df.loc[
            purchase_df["category_code"] == SMARTPHONE_CATEGORY,
            "user_id"
        ].dropna().unique()

        smartphone_purchase_users.update(smartphone_users)

        # 카테고리별 구매자
        category_user_pairs = purchase_df[["category_code", "user_id"]].drop_duplicates()

        for category_code, group in category_user_pairs.groupby("category_code"):
            category_purchase_users[category_code].update(group["user_id"].dropna().unique())

    print(f"{month} user_days 생성 완료. 사용자 수: {len(user_days):,}")
    print(f"{month} 전체 구매자 수: {len(purchase_users):,}")
    print(f"{month} 스마트폰 구매자 수: {len(smartphone_purchase_users):,}")

    # 재방문 유저 판별
    revisit_users = {
        user_id
        for user_id, days in user_days.items()
        if len(days) >= 2
    }

    # =========================
    # 1) 코호트 요약
    # =========================
    # first_day 기준으로 코호트 구성
    cohort_users = defaultdict(set)

    for user_id, days in user_days.items():
        first_day = min(days)
        cohort_users[first_day].add(user_id)

    # cohort_day별 day_n 리텐션 계산
    for cohort_day, users in cohort_users.items():
        cohort_user_count = len(users)

        max_day_n = max_day - cohort_day

        for day_n in range(0, max_day_n + 1):
            target_day = cohort_day + day_n

            if day_n == 0:
                retained_user_count = cohort_user_count
            else:
                retained_user_count = sum(
                    1
                    for user_id in users
                    if target_day in user_days[user_id]
                )

            retention_rate = (
                retained_user_count / cohort_user_count * 100
                if cohort_user_count > 0
                else 0
            )

            cohort_rows.append({
                "month": month,
                "cohort_day": cohort_day,
                "day_n": day_n,
                "target_day": target_day,
                "cohort_user_count": cohort_user_count,
                "retained_user_count": retained_user_count,
                "retention_rate": round(retention_rate, 2),
            })

    # =========================
    # 2) 카테고리별 구매자 재방문율 TOP5
    # =========================
    category_rows = []

    for category_code, users in category_purchase_users.items():
        buyer_count = len(users)

        # 너무 작은 카테고리가 TOP에 뜨는 것을 막기 위한 기준
        if buyer_count < 1000:
            continue

        revisit_buyer_count = len(users & revisit_users)

        revisit_rate = (
            revisit_buyer_count / buyer_count * 100
            if buyer_count > 0
            else 0
        )

        category_rows.append({
            "month": month,
            "category_code": category_code,
            "buyer_count": buyer_count,
            "revisit_buyer_count": revisit_buyer_count,
            "revisit_rate": round(revisit_rate, 2),
        })

    category_df = pd.DataFrame(category_rows)

    if not category_df.empty:
        category_df = (
            category_df
            .sort_values(["revisit_rate", "buyer_count"], ascending=[False, False])
            .head(5)
            .copy()
        )

        category_df["rank"] = range(1, len(category_df) + 1)

        category_top_rows.extend(category_df.to_dict("records"))

    # =========================
    # 3) 전체 구매자 vs 스마트폰 구매자 재방문 비교
    # =========================
    purchase_revisit_users = purchase_users & revisit_users
    smartphone_revisit_users = smartphone_purchase_users & revisit_users

    purchase_revisit_rate = (
        len(purchase_revisit_users) / len(purchase_users) * 100
        if len(purchase_users) > 0
        else 0
    )

    smartphone_revisit_rate = (
        len(smartphone_revisit_users) / len(smartphone_purchase_users) * 100
        if len(smartphone_purchase_users) > 0
        else 0
    )

    buyer_compare_rows.append({
        "month": month,
        "group": "전체 구매자",
        "buyer_count": len(purchase_users),
        "revisit_buyer_count": len(purchase_revisit_users),
        "revisit_rate": round(purchase_revisit_rate, 2),
    })

    buyer_compare_rows.append({
        "month": month,
        "group": "스마트폰 구매자",
        "buyer_count": len(smartphone_purchase_users),
        "revisit_buyer_count": len(smartphone_revisit_users),
        "revisit_rate": round(smartphone_revisit_rate, 2),
    })


# DataFrame 변환
cohort_df = pd.DataFrame(cohort_rows)
category_top_df = pd.DataFrame(category_top_rows)
buyer_compare_df = pd.DataFrame(buyer_compare_rows)

# 정렬
cohort_df = cohort_df.sort_values(["month", "cohort_day", "day_n"])

if not category_top_df.empty:
    category_top_df = category_top_df.sort_values(["month", "rank"])

buyer_compare_df = buyer_compare_df.sort_values(["month", "group"])

# 저장
cohort_path = f"{OUTPUT_DIR}/02_retention_cohort_summary.csv"
category_top_path = f"{OUTPUT_DIR}/02_retention_category_top5.csv"
buyer_compare_path = f"{OUTPUT_DIR}/02_retention_buyer_vs_smartphone.csv"

cohort_df.to_csv(cohort_path, index=False, encoding="utf-8-sig")
category_top_df.to_csv(category_top_path, index=False, encoding="utf-8-sig")
buyer_compare_df.to_csv(buyer_compare_path, index=False, encoding="utf-8-sig")

print("\n===== 02_retention_cohort_summary.csv 저장 완료 =====")
print(cohort_df.head(40))

print("\n===== 02_retention_category_top5.csv 저장 완료 =====")
print(category_top_df)

print("\n===== 02_retention_buyer_vs_smartphone.csv 저장 완료 =====")
print(buyer_compare_df)