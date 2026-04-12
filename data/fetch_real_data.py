
import requests
import pandas as pd

API_KEY = "YOUR_API_KEY"

url = "https://api.electricitymap.org/v4/carbon-intensity/history"

def fetch_data(zone="IN"):
    headers = {
        "auth-token": API_KEY
    }

    params = {
        "zone": zone
    }

    response = requests.get(URL, headers=headers, params=params)

    if response.status_code != 200:
        print(response.text)  # DEBUG
        raise Exception(f"API Error: {response.status_code}")

    data = response.json()
    return data


def prepare_dataset():
    df = fetch_data()

    # add workload (needed for your model)
    import numpy as np

    df["workload"] = (
        df["carbon_intensity"].rolling(3).mean()
        + np.random.normal(0, 20, len(df))
    )

    # fill gaps
    df = df.set_index("timestamp").resample("1H").mean().interpolate().reset_index()

    return df


if __name__ == "__main__":
    df = prepare_dataset()

    df.to_csv("data/real_dataset.csv", index=False)

    print("Saved to data/real_dataset.csv")