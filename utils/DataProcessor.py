import pandas as pd


def load_data(csv_file):
    return pd.read_csv(csv_file, dtype={"聯絡方式": str})


def save_data(data, csv_file):
    data.to_csv(csv_file, index=False)
