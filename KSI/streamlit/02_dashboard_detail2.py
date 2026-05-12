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
    "user_id",
    "event_date",
    "event_type",
    "category_code",
]

# 결과 저장용
first_purchase_cohort_rows = []
buyer_vs_nonbuyer_rows = []

# 카테고리 비교는 너무 많은 카테고리를 전부 저장하면 커질 수 있어서 상위 N개만 저장
TOP_CATEGORY_N = 20
MIN_CATEGORY_BUYER_COUNT = 1000

for month, path in RAW_FILES.items():
    print(f"\n===== {month} 리텐션 대시보드 기준 보완 처리 시작 =====")

    max_day = 31 if month == "10월" else 30

    # user_id별 활동일
    user_days = defaultdict(set)

    # user_id별 첫 구매일
    user_first_purchase_day = {}

    # 전체 유저
    all_users = set()

    # 전체 재방문 유저
    revisit_users = set()

    # 카테고리별 구매 유저
    category_purchase_users = defaultdict(set)

    # =========================
    # 1차 pass
    # - 유저별 활동일
    # - 유저별 첫 구매일
    # - 카테고리별 구매자 수집
    # =========================
    for i, chunk in enumerate(pd.read_csv(path, usecols=usecols, chunksize=CHUNKSIZE)):
        print(f"{month} chunk {i + 1} 처리 중...")

        chunk = chunk.dropna(subset=["user_id", "event_date"]).copy()

        chunk["event_date"] = chunk["event_date"].astype(str)
        chunk["day"] = chunk["event_date"].str[-2:].astype("int16")
        chunk["event_type"] = chunk["event_type"].astype(str)
        chunk["category_code"] = chunk["category_code"].fillna("unknown")

        # 전체 유저 저장
        all_users.update(chunk["user_id"].dropna().unique())

        # 유저별 활동일 저장
        user_day_pairs = chunk[["user_id", "day"]].drop_duplicates()
        grouped_days = user_day_pairs.groupby("user_id")["day"].unique()

        for user_id, days in grouped_days.items():
            user_days[user_id].update(days.tolist())

        # 구매 이벤트만 추출
        purchase_df = chunk[chunk["event_type"] == "purchase"].copy()

        if purchase_df.empty:
            continue

        # 유저별 첫 구매일 저장
        user_purchase_min_day = purchase_df.groupby("user_id")["day"].min()

        for user_id, purchase_day in user_purchase_min_day.items():
            purchase_day = int(purchase_day)

            if user_id not in user_first_purchase_day:
                user_first_purchase_day[user_id] = purchase_day
            else:
                if purchase_day < user_first_purchase_day[user_id]:
                    user_first_purchase_day[user_id] = purchase_day

        # 카테고리별 구매자 저장
        category_user_pairs = purchase_df[["category_code", "user_id"]].drop_duplicates()

        for category_code, group in category_user_pairs.groupby("category_code"):
            category_purchase_users[category_code].update(
                group["user_id"].dropna().unique()
            )

    print(f"{month} 전체 유저 수: {len(all_users):,}")
    print(f"{month} 첫 구매 유저 수: {len(user_first_purchase_day):,}")
    print(f"{month} 카테고리 수: {len(category_purchase_users):,}")

    # 전체 재방문 유저 계산
    revisit_users = {
        user_id
        for user_id, days in user_days.items()
        if len(days) >= 2
    }

    print(f"{month} 재방문 유저 수: {len(revisit_users):,}")

    # =========================
    # 1) 첫 구매일 기준 코호트 생성
    # =========================
    first_purchase_cohort_users = defaultdict(set)

    for user_id, first_purchase_day in user_first_purchase_day.items():
        first_purchase_cohort_users[first_purchase_day].add(user_id)

    for cohort_day, users in first_purchase_cohort_users.items():
        cohort_user_count = len(users)

        # 첫 구매일 이후 월 범위 안에서만 계산
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

            first_purchase_cohort_rows.append({
                "month": month,
                "first_purchase_day": cohort_day,
                "day_n": day_n,
                "target_day": target_day,
                "cohort_user_count": cohort_user_count,
                "retained_user_count": retained_user_count,
                "retention_rate": round(retention_rate, 2),
            })

    # =========================
    # 2) 구매자 vs 비구매자 카테고리 재방문율
    # =========================
    category_base_rows = []

    for category_code, buyers in category_purchase_users.items():
        buyer_count = len(buyers)

        if buyer_count < MIN_CATEGORY_BUYER_COUNT:
            continue

        category_base_rows.append({
            "category_code": category_code,
            "buyer_count": buyer_count,
        })

    category_base_df = pd.DataFrame(category_base_rows)

    if category_base_df.empty:
        print(f"{month} 구매자 수 기준을 만족하는 카테고리가 없습니다.")
        continue

    # 구매자 수 기준 상위 카테고리만 저장
    selected_categories = (
        category_base_df
        .sort_values("buyer_count", ascending=False)
        .head(TOP_CATEGORY_N)["category_code"]
        .tolist()
    )

    print(f"{month} 구매자 vs 비구매자 비교 대상 카테고리 수: {len(selected_categories)}")

    for category_code in selected_categories:
        buyers = category_purchase_users[category_code]
        nonbuyers = all_users - buyers

        buyer_count = len(buyers)
        nonbuyer_count = len(nonbuyers)

        buyer_revisit_count = len(buyers & revisit_users)
        nonbuyer_revisit_count = len(nonbuyers & revisit_users)

        buyer_revisit_rate = (
            buyer_revisit_count / buyer_count * 100
            if buyer_count > 0
            else 0
        )

        nonbuyer_revisit_rate = (
            nonbuyer_revisit_count / nonbuyer_count * 100
            if nonbuyer_count > 0
            else 0
        )

        buyer_vs_nonbuyer_rows.append({
            "month": month,
            "category_code": category_code,
            "group": "구매자",
            "user_count": buyer_count,
            "revisit_user_count": buyer_revisit_count,
            "revisit_rate": round(buyer_revisit_rate, 2),
        })

        buyer_vs_nonbuyer_rows.append({
            "month": month,
            "category_code": category_code,
            "group": "비구매자",
            "user_count": nonbuyer_count,
            "revisit_user_count": nonbuyer_revisit_count,
            "revisit_rate": round(nonbuyer_revisit_rate, 2),
        })


# =========================
# 저장
# =========================
first_purchase_cohort_df = pd.DataFrame(first_purchase_cohort_rows)
buyer_vs_nonbuyer_df = pd.DataFrame(buyer_vs_nonbuyer_rows)

if not first_purchase_cohort_df.empty:
    first_purchase_cohort_df = first_purchase_cohort_df.sort_values(
        ["month", "first_purchase_day", "day_n"]
    )

if not buyer_vs_nonbuyer_df.empty:
    buyer_vs_nonbuyer_df = buyer_vs_nonbuyer_df.sort_values(
        ["month", "category_code", "group"]
    )

first_purchase_cohort_path = f"{OUTPUT_DIR}/02_retention_first_purchase_cohort_summary.csv"
buyer_vs_nonbuyer_path = f"{OUTPUT_DIR}/02_retention_buyer_vs_nonbuyer.csv"

first_purchase_cohort_df.to_csv(
    first_purchase_cohort_path,
    index=False,
    encoding="utf-8-sig"
)

buyer_vs_nonbuyer_df.to_csv(
    buyer_vs_nonbuyer_path,
    index=False,
    encoding="utf-8-sig"
)

print("\n===== 02_retention_first_purchase_cohort_summary.csv 저장 완료 =====")
print(first_purchase_cohort_df.head(40))

print("\n===== 02_retention_buyer_vs_nonbuyer.csv 저장 완료 =====")
print(buyer_vs_nonbuyer_df.head(60))