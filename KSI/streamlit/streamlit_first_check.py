import pandas as pd

oct_path = "data/raw/mart_total_final_oct.csv"
nov_path = "data/raw/mart_total_final_nov.csv"

# 큰 CSV 전체를 읽지 않고 앞 5행만 읽기
oct_sample = pd.read_csv(oct_path, nrows=5)
nov_sample = pd.read_csv(nov_path, nrows=5)

print("===== 10월 데이터 샘플 =====")
print(oct_sample.head())

print("\n===== 10월 데이터 shape =====")
print(oct_sample.shape)

print("\n===== 10월 컬럼 목록 =====")
for col in oct_sample.columns:
    print(col)

print("\n\n===== 11월 데이터 샘플 =====")
print(nov_sample.head())

print("\n===== 11월 데이터 shape =====")
print(nov_sample.shape)

print("\n===== 11월 컬럼 목록 =====")
for col in nov_sample.columns:
    print(col)