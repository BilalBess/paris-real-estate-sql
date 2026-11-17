"""Tests for the SQL pipeline. A tiny fake DVF file is built so the tests run in a second."""
import os

import duckdb
import pandas as pd
import pytest

import run_analysis

COLUMNS = ["id_mutation", "date_mutation", "nature_mutation", "valeur_fonciere", "code_postal",
           "type_local", "surface_reelle_bati", "nombre_pieces_principales", "longitude", "latitude"]


def row(id_, price, postcode, type_local, surface, nature="Vente", date="2023-03-01"):
    return [id_, date, nature, price, postcode, type_local, surface, 2, 2.3, 48.8]


@pytest.fixture()
def con(tmp_path):
    rows = [
        row("ok1", 500000, "75006", "Appartement", 50),                 # valid, 10,000 EUR/m2
        row("ok2", 300000, "75006", "Appartement", 30),                 # valid, 10,000 EUR/m2
        row("ok3", 400000, "75019", "Appartement", 50),                 # valid, 8,000 EUR/m2
        row("house", 800000, "75016", "Appartement", 60),               # sale that also has a house -> removed
        row("house", 800000, "75016", "Maison", 80),
        row("tiny", 100000, "75010", "Appartement", 5),                 # surface < 9 m2
        row("cheap", 30000, "75010", "Appartement", 100),               # 300 EUR/m2 -> removed
        row("swap", 500000, "75006", "Appartement", 50, nature="Echange"),
        row("two", 900000, "75007", "Appartement", 40),                 # two apartments in one sale -> removed
        row("two", 900000, "75007", "Appartement", 40),
        row("suburb", 500000, "75116", "Appartement", 50),              # postcode outside 75001-75020
        row("nolocal", 500000, "75006", None, None),                    # land only
    ]
    data = tmp_path / "data"
    data.mkdir()
    pd.DataFrame(rows, columns=COLUMNS).to_csv(data / "dvf_paris_2023.csv", index=False)
    old = os.getcwd()
    os.chdir(tmp_path)
    c = duckdb.connect()
    run_analysis.run_file(c, "01_clean_sales.sql")
    yield c
    os.chdir(old)


def test_cleaning_keeps_only_valid_sales(con):
    ids = sorted(r[0] for r in con.execute("SELECT id_mutation FROM sales_clean").fetchall())
    assert ids == ["ok1", "ok2", "ok3"]


def test_one_row_per_sale(con):
    n, n_unique = con.execute("SELECT COUNT(*), COUNT(DISTINCT id_mutation) FROM sales_clean").fetchone()
    assert n == n_unique


def test_price_per_m2_and_arrondissement(con):
    r = con.execute("SELECT price_m2, arrondissement FROM sales_clean WHERE id_mutation = 'ok3'").fetchone()
    assert r == (8000.0, 19)


def test_arrondissement_ranking(con):
    df = run_analysis.run_file(con, "02_price_by_arrondissement.sql").df()
    assert df.iloc[0]["arrondissement"] == 6          # most expensive first
    assert df.iloc[0]["rank_expensive"] == 1
    assert df.iloc[0]["median_price_m2"] == 10000
    assert df.iloc[0]["n_sales"] == 2
    assert df.iloc[0]["pct_vs_paris"] == 0                 # in this toy data the 6th is exactly the Paris median
    assert df.iloc[1]["arrondissement"] == 19 and df.iloc[1]["pct_vs_paris"] < 0


def test_monthly_trend_first_month_has_no_change(con):
    df = run_analysis.run_file(con, "03_monthly_trend.sql").df()
    assert len(df) == 1
    assert pd.isna(df.iloc[0]["pct_change_vs_prev_month"])
