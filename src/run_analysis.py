"""Run the SQL files with DuckDB, save result tables (csv) and make the figures."""
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql"
OUT = ROOT / "reports"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def run_file(con, name):
    return con.execute((SQL / name).read_text())


def main():
    con = duckdb.connect()  # in-memory
    import os
    os.chdir(ROOT)  # so the relative path in the SQL file works

    run_file(con, "01_clean_sales.sql")
    n = con.execute("SELECT COUNT(*) FROM sales_clean").fetchone()[0]
    print(f"clean apartment sales: {n}")

    by_arr = run_file(con, "02_price_by_arrondissement.sql").df()
    trend = run_file(con, "03_monthly_trend.sql").df()
    sizes = run_file(con, "04_size_and_rooms.sql").df()
    outliers = run_file(con, "05_outlier_flags.sql").df()

    by_arr.to_csv(OUT / "price_by_arrondissement.csv", index=False)
    trend.to_csv(OUT / "monthly_trend.csv", index=False)
    sizes.to_csv(OUT / "price_by_size.csv", index=False)
    outliers.to_csv(OUT / "outliers_top20.csv", index=False)

    print(by_arr.to_string(index=False))
    print(trend.to_string(index=False))
    print(sizes.to_string(index=False))

    # figure 1: median price per m2 by arrondissement
    d = by_arr.sort_values("median_price_m2")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(d["arrondissement"].astype(str), d["median_price_m2"], color="#2b6cb0")
    ax.axvline(con.execute("SELECT MEDIAN(price_m2) FROM sales_clean").fetchone()[0],
               color="red", linestyle="--", label="Paris median")
    ax.set_xlabel("Median price per m2 (EUR)")
    ax.set_ylabel("Arrondissement")
    ax.set_title("Apartment price per m2 by arrondissement (Paris, 2023)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "price_by_arrondissement.png", dpi=150)
    plt.close(fig)

    # figure 2: monthly trend
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(trend["month"], trend["median_price_m2"], marker="o", label="Monthly median")
    ax.plot(trend["month"], trend["moving_avg_3m"], linestyle="--", label="3-month moving avg")
    ax.set_ylabel("EUR per m2")
    ax.set_title("Paris apartment price per m2, monthly (2023)")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIG / "monthly_trend.png", dpi=150)
    plt.close(fig)

    # figure 3: price per m2 by size bucket
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(sizes["size_bucket"], sizes["median_price_m2"], color="#2f855a")
    ax.set_ylabel("Median price per m2 (EUR)")
    ax.set_title("Price per m2 by flat size (big flats cost more per m2)")
    plt.xticks(rotation=20)
    fig.tight_layout()
    fig.savefig(FIG / "price_by_size.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
