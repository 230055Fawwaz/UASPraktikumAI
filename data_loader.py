# data_loader.py
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")

def load_csv(file_name):
    path = DATA_DIR / file_name
    if not path.exists():
        raise FileNotFoundError(f"{file_name} tidak ditemukan di folder data/")
    return pd.read_csv(path)

def load_all_data():
    matkul = load_csv("matkul.csv")
    dosen = load_csv("dosen.csv")
    kelas = load_csv("kelas.csv")
    ruangan = load_csv("ruangan.csv")
    return matkul, dosen, kelas, ruangan

# Fungsi tambahan jika ingin bentuk dictionary
def convert_to_dict(df, key_col):
    return df.set_index(key_col).to_dict(orient="index")