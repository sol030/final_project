import os
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
]

brand_stats = {}

for month, path in RAW_FILES.items():
    print(f"\n===== {month} 스마트폰 브랜드 KPI 처리 시작 =====")

    for i, chunk in enumerate(pd.read_csv(path, usecols=usecols, chunksize=CHUNKSIZE)):
        print(f"{month} chunk {i + 1} 처리 중...")

        smartphone_df = chunk[chunk["category_code"] == SMARTPHONE_CATEGORY].copy()

        if smartphone_df.empty:
            continue

        smartphone_df["brand"] = smartphone_df["brand"].fillna("unknown_brand")
        smartphone_df["price"] = smartphone_df["price"].fillna(0)

        for brand, group in smartphone_df.groupby("brand"):
            key = (month, brand)

            if key not in brand_stats:
                brand_stats[key] = {
                    "view_count": 0,
                    "cart_count": 0,
                    "purchase_count": 0,
                    "remove_from_cart_count": 0,
                    "revenue": 0.0,
                    "total_users": set(),
                    "purchase_users": set(),
                    "total_sessions": set(),
                    "purchase_sessions": set(),
                }

            view_mask = group["event_type"] == "view"
            cart_mask = group["event_type"] == "cart"
            purchase_mask = group["event_type"] == "purchase"
            remove_mask = group["event_type"] == "remove_from_cart"

            brand_stats[key]["view_count"] += int(view_mask.sum())
            brand_stats[key]["cart_count"] += int(cart_mask.sum())
            brand_stats[key]["purchase_count"] += int(purchase_mask.sum())
            brand_stats[key]["remove_from_cart_count"] += int(remove_mask.sum())

            brand_stats[key]["revenue"] += group.loc[purchase_mask, "price"].sum()

            brand_stats[key]["total_users"].update(group["user_id"].dropna().unique())
            brand_stats[key]["purchase_users"].update(
                group.loc[purchase_mask, "user_id"].dropna().unique()
            )

            brand_stats[key]["total_sessions"].update(group["user_session"].dropna().unique())
            brand_stats[key]["purchase_sessions"].update(
                group.loc[purchase_mask, "user_session"].dropna().unique()
            )

summary_rows = []
funnel_rows = []

for (month, brand), stats in brand_stats.items():
    view_count = stats["view_count"]
    cart_count = stats["cart_count"]
    purchase_count = stats["purchase_count"]
    remove_count = stats["remove_from_cart_count"]
    revenue = stats["revenue"]

    total_user_count = len(stats["total_users"])
    purchase_user_count = len(stats["purchase_users"])
    total_session_count = len(stats["total_sessions"])
    purchase_session_count = len(stats["purchase_sessions"])

    view_to_cart_rate = cart_count / view_count * 100 if view_count > 0 else 0
    cart_to_purchase_rate = purchase_count / cart_count * 100 if cart_count > 0 else 0
    view_to_purchase_rate = purchase_count / view_count * 100 if view_count > 0 else 0
    purchase_user_rate = purchase_user_count / total_user_count * 100 if total_user_count > 0 else 0
    revenue_per_purchase_user = revenue / purchase_user_count if purchase_user_count > 0 else 0

    summary_rows.append({
        "month": month,
        "brand": brand,
        "view_count": view_count,
        "cart_count": cart_count,
        "purchase_count": purchase_count,
        "remove_from_cart_count": remove_count,
        "revenue": round(revenue, 2),
        "total_user_count": total_user_count,
        "purchase_user_count": purchase_user_count,
        "total_session_count": total_session_count,
        "purchase_session_count": purchase_session_count,
        "view_to_cart_rate": round(view_to_cart_rate, 2),
        "cart_to_purchase_rate": round(cart_to_purchase_rate, 2),
        "view_to_purchase_rate": round(view_to_purchase_rate, 2),
        "purchase_user_rate": round(purchase_user_rate, 2),
        "revenue_per_purchase_user": round(revenue_per_purchase_user, 2),
    })

    funnel_rows.extend([
        {
            "month": month,
            "brand": brand,
            "stage": "view",
            "count": view_count,
        },
        {
            "month": month,
            "brand": brand,
            "stage": "cart",
            "count": cart_count,
        },
        {
            "month": month,
            "brand": brand,
            "stage": "purchase",
            "count": purchase_count,
        },
    ])

summary_df = pd.DataFrame(summary_rows)
funnel_df = pd.DataFrame(funnel_rows)

summary_df = summary_df.sort_values(["month", "revenue"], ascending=[True, False])
funnel_df = funnel_df.sort_values(["month", "brand", "stage"])

summary_path = f"{OUTPUT_DIR}/03_smartphone_brand_summary.csv"
funnel_path = f"{OUTPUT_DIR}/03_smartphone_funnel_summary.csv"

summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
funnel_df.to_csv(funnel_path, index=False, encoding="utf-8-sig")

print("\n===== 03_smartphone_brand_summary.csv 저장 완료 =====")
print(summary_df.head(30))

print("\n===== 03_smartphone_funnel_summary.csv 저장 완료 =====")
print(funnel_df.head(60))