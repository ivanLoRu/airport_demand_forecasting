from pathlib import Path
import pandas as pd

ROOT = Path.cwd()
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed" / "passenger_volume"

def main():
    db28_list = list(RAW.glob("*.asc"))
    db28 = pd.concat(pd.read_csv(f, delimiter="|",header=None, usecols=[0,1,2,6,13,15]) for f in db28_list)
    db28.columns = ["Year", "Month","Origin Airport", "Destination Airport","Distance","Passengers"]
    db28["Datetime"] = pd.to_datetime(db28["Year"].astype(str)+'-'+db28["Month"].astype(str).str.zfill(2), format="%Y-%m")
    pas_vol = PROCESSED / "db28_general.csv"
    db28.to_csv(pas_vol, index=None)

if __name__ == '__main__':
    main()