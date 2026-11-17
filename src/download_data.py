"""Download the DVF 2023 file (property sales) for Paris (department 75).

Source: data.gouv.fr "Demandes de valeurs foncieres geolocalisees".
"""
import gzip
import shutil
from pathlib import Path

import requests

URL = "https://files.data.gouv.fr/geo-dvf/latest/csv/2023/departements/75.csv.gz"
RAW = Path(__file__).resolve().parents[1] / "data" / "dvf_paris_2023.csv"


def main():
    if RAW.exists():
        print(f"{RAW.name} already there, skipping download")
        return
    RAW.parent.mkdir(exist_ok=True)
    gz_path = RAW.with_suffix(".csv.gz")
    with requests.get(URL, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(gz_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    with gzip.open(gz_path, "rb") as f_in, open(RAW, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    gz_path.unlink()
    print(f"saved {RAW}")


if __name__ == "__main__":
    main()
