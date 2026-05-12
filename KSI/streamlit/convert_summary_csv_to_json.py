import os
import pandas as pd

csv_dir = "data/summary"
json_dir = "data/summary_json"

os.makedirs(json_dir, exist_ok=True)

for file in os.listdir(csv_dir):
    if file.endswith(".csv"):
        csv_path = os.path.join(csv_dir, file)
        json_path = os.path.join(json_dir, file.replace(".csv", ".json"))

        df = pd.read_csv(csv_path)
        df.to_json(
            json_path,
            orient="records",
            force_ascii=False,
            indent=2
        )

        print(f"변환 완료: {csv_path} -> {json_path}")