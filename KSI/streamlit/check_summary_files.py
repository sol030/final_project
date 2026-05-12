import os
import pandas as pd

SUMMARY_DIR = "data/summary"

print("===== summary 폴더 파일 목록 =====")

files = sorted([
    file for file in os.listdir(SUMMARY_DIR)
    if file.endswith(".csv")
])

for file in files:
    path = os.path.join(SUMMARY_DIR, file)
    df = pd.read_csv(path)

    print("\n==============================")
    print(f"파일명: {file}")
    print(f"크기: {df.shape}")
    print("컬럼:")
    print(df.columns.tolist())
    print("\n상위 5행:")
    print(df.head())