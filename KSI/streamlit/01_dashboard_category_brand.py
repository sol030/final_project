import os
import pandas as pd

RAW_FILES = {
    "10월": "data/raw/mart_total_final_oct.csv",
    "11월": "data/raw/mart_total_final_nov.csv",
}

OUTPUT_DIR = "data/summary"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHUNKSIZE = 500_000

usecols = [
    "event_type",
    "category_code",
    "brand",
    "price",
]

# 카테고리별 매출 저장용
category_stats = {}

# 카테고리-브랜드별 매출 저장용
category_brand_stats = {}

for month, path in RAW_FILES.items():
    print(f"\n===== {month} 카테고리/브랜드 요약 처리 시작 =====")

    for i, chunk in enumerate(pd.read_csv(path, usecols=usecols, chunksize=CHUNKSIZE)):
        print(f"{month} chunk {i + 1} 처리 중...")

        # 구매 이벤트만 매출 계산에 사용
        purchase_df = chunk[chunk["event_type"] == "purchase"].copy()

        if purchase_df.empty:
            continue

        purchase_df["category_code"] = purchase_df["category_code"].fillna("unknown_category")
        purchase_df["brand"] = purchase_df["brand"].fillna("unknown_brand")
        purchase_df["price"] = purchase_df["price"].fillna(0)

        # 1) 카테고리별 매출/구매수
        grouped_category = purchase_df.groupby("category_code").agg(
            purchase_count=("event_type", "count"),
            revenue=("price", "sum")
        ).reset_index()

        for _, row in grouped_category.iterrows():
            key = (month, row["category_code"])

            if key not in category_stats:
                category_stats[key] = {
                    "purchase_count": 0,
                    "revenue": 0.0,
                }

            category_stats[key]["purchase_count"] += int(row["purchase_count"])
            category_stats[key]["revenue"] += float(row["revenue"])

        # 2) 카테고리-브랜드별 매출/구매수
        grouped_category_brand = purchase_df.groupby(["category_code", "brand"]).agg(
            purchase_count=("event_type", "count"),
            revenue=("price", "sum")
        ).reset_index()

        for _, row in grouped_category_brand.iterrows():
            key = (month, row["category_code"], row["brand"])

            if key not in category_brand_stats:
                category_brand_stats[key] = {
                    "purchase_count": 0,
                    "revenue": 0.0,
                }

            category_brand_stats[key]["purchase_count"] += int(row["purchase_count"])
            category_brand_stats[key]["revenue"] += float(row["revenue"])


# =========================
# 1) 카테고리 TOP5 만들기
# =========================
category_rows = []

for (month, category_code), stats in category_stats.items():
    category_rows.append({
        "month": month,
        "category_code": category_code,
        "purchase_count": stats["purchase_count"],
        "revenue": round(stats["revenue"], 2),
    })

category_df = pd.DataFrame(category_rows)

category_top5_df = (
    category_df
    .sort_values(["month", "revenue"], ascending=[True, False])
    .groupby("month")
    .head(5)
    .copy()
)

category_top5_df["rank"] = (
    category_top5_df
    .groupby("month")["revenue"]
    .rank(method="first", ascending=False)
    .astype(int)
)

category_top5_df = category_top5_df.sort_values(["month", "rank"])


# =========================
# 2) 카테고리별 대표 브랜드 만들기
# =========================
category_brand_rows = []

for (month, category_code, brand), stats in category_brand_stats.items():
    category_brand_rows.append({
        "month": month,
        "category_code": category_code,
        "brand": brand,
        "purchase_count": stats["purchase_count"],
        "revenue": round(stats["revenue"], 2),
    })

category_brand_df = pd.DataFrame(category_brand_rows)

# 전체를 다 저장하면 커질 수 있어서
# 월별-카테고리별 매출 상위 브랜드 3개만 저장
category_brand_top_df = (
    category_brand_df
    .sort_values(["month", "category_code", "revenue"], ascending=[True, True, False])
    .groupby(["month", "category_code"])
    .head(3)
    .copy()
)

category_brand_top_df["brand_rank_in_category"] = (
    category_brand_top_df
    .groupby(["month", "category_code"])["revenue"]
    .rank(method="first", ascending=False)
    .astype(int)
)

# 저장
category_top5_path = f"{OUTPUT_DIR}/01_overview_category_top5.csv"
category_brand_path = f"{OUTPUT_DIR}/01_overview_category_brand_summary.csv"

category_top5_df.to_csv(category_top5_path, index=False, encoding="utf-8-sig")
category_brand_top_df.to_csv(category_brand_path, index=False, encoding="utf-8-sig")

print("\n===== 01_overview_category_top5.csv 저장 완료 =====")
print(category_top5_df)

print("\n===== 01_overview_category_brand_summary.csv 저장 완료 =====")
print(category_brand_top_df.head(30))