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
]

retention_kpi_rows = []
retention_day_rows = []

for month, path in RAW_FILES.items():
    print(f"\n===== {month} 리텐션 KPI 처리 시작 =====")

    # user_id별 활동 날짜 저장
    # 예: {12345: {1, 2, 5}, 67890: {3, 10}}
    user_days = defaultdict(set)

    for i, chunk in enumerate(pd.read_csv(path, usecols=usecols, chunksize=CHUNKSIZE)):
        print(f"{month} chunk {i + 1} 처리 중...")

        chunk = chunk.dropna(subset=["user_id", "event_date"]).copy()

        # event_date가 2019-10-01 형태라고 가정하고, 일(day)만 추출
        chunk["day"] = chunk["event_date"].astype(str).str[-2:].astype("int16")

        # 같은 유저가 같은 날짜에 여러 번 행동해도 1번 활동으로 처리
        user_day_pairs = chunk[["user_id", "day"]].drop_duplicates()

        grouped = user_day_pairs.groupby("user_id")["day"].unique()

        for user_id, days in grouped.items():
            user_days[user_id].update(days.tolist())

    print(f"{month} user_days 생성 완료. 사용자 수: {len(user_days):,}")

    total_user_count = len(user_days)

    revisit_user_count = 0
    day1_revisit_user_count = 0
    day7_revisit_user_count = 0

    max_day = 31 if month == "10월" else 30

    # n-day 리텐션 계산용
    day_retention_stats = {
        day_n: {
            "eligible_user_count": 0,
            "retained_user_count": 0,
        }
        for day_n in range(1, max_day)
    }

    for user_id, days in user_days.items():
        days = set(days)

        if len(days) >= 2:
            revisit_user_count += 1

        first_day = min(days)

        # Day1, Day7 재방문 여부
        if first_day + 1 in days:
            day1_revisit_user_count += 1

        if first_day + 7 in days:
            day7_revisit_user_count += 1

        # Day1~Day30 리텐션
        for day_n in range(1, max_day):
            target_day = first_day + day_n

            # 해당 n일 뒤가 월 범위 안에 있는 유저만 분모에 포함
            if target_day <= max_day:
                day_retention_stats[day_n]["eligible_user_count"] += 1

                if target_day in days:
                    day_retention_stats[day_n]["retained_user_count"] += 1

    revisit_rate = (
        revisit_user_count / total_user_count * 100
        if total_user_count > 0
        else 0
    )

    day1_revisit_rate = (
        day1_revisit_user_count / total_user_count * 100
        if total_user_count > 0
        else 0
    )

    day7_revisit_rate = (
        day7_revisit_user_count / total_user_count * 100
        if total_user_count > 0
        else 0
    )

    retention_kpi_rows.append({
        "month": month,
        "total_user_count": total_user_count,
        "revisit_user_count": revisit_user_count,
        "revisit_rate": round(revisit_rate, 2),
        "day1_revisit_user_count": day1_revisit_user_count,
        "day1_revisit_rate": round(day1_revisit_rate, 2),
        "day7_revisit_user_count": day7_revisit_user_count,
        "day7_revisit_rate": round(day7_revisit_rate, 2),
    })

    for day_n, stats in day_retention_stats.items():
        eligible = stats["eligible_user_count"]
        retained = stats["retained_user_count"]

        retention_rate = retained / eligible * 100 if eligible > 0 else 0

        retention_day_rows.append({
            "month": month,
            "day_n": day_n,
            "eligible_user_count": eligible,
            "retained_user_count": retained,
            "retention_rate": round(retention_rate, 2),
        })

retention_kpi_df = pd.DataFrame(retention_kpi_rows)
retention_day_df = pd.DataFrame(retention_day_rows)

kpi_path = f"{OUTPUT_DIR}/02_retention_kpi_summary.csv"
day_path = f"{OUTPUT_DIR}/02_retention_day_summary.csv"

retention_kpi_df.to_csv(kpi_path, index=False, encoding="utf-8-sig")
retention_day_df.to_csv(day_path, index=False, encoding="utf-8-sig")

print("\n===== 02_retention_kpi_summary.csv 저장 완료 =====")
print(retention_kpi_df)

print("\n===== 02_retention_day_summary.csv 저장 완료 =====")
print(retention_day_df.head(40))