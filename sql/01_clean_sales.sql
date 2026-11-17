-- Step 1: build a clean table with ONE row per apartment sale.
-- In the raw DVF file, a sale (id_mutation) can have several rows
-- (one per lot / parcel) and the total price is repeated on each row.
-- So I only keep sales that contain exactly one apartment row and nothing else
-- built (no house, no commercial local), otherwise the price per m2 is wrong.

CREATE OR REPLACE TABLE sales_clean AS
WITH raw AS (
    SELECT
        id_mutation,
        CAST(date_mutation AS DATE)                    AS sale_date,
        valeur_fonciere                                AS price,
        code_postal,
        type_local,
        surface_reelle_bati                            AS surface,
        nombre_pieces_principales                      AS rooms,
        longitude,
        latitude
    FROM read_csv_auto('data/dvf_paris_2023.csv')
    WHERE nature_mutation = 'Vente'
      AND valeur_fonciere IS NOT NULL
      AND type_local IS NOT NULL
),
per_sale AS (
    SELECT
        id_mutation,
        COUNT(*)                                       AS n_built_rows,
        SUM(CASE WHEN type_local = 'Appartement' THEN 1 ELSE 0 END) AS n_apartments
    FROM raw
    WHERE type_local IN ('Appartement', 'Maison', 'Local industriel. commercial ou assimilé')
    GROUP BY id_mutation
)
SELECT
    r.id_mutation,
    r.sale_date,
    r.price,
    r.code_postal,
    CAST(r.code_postal AS INTEGER) - 75000             AS arrondissement,
    r.surface,
    r.rooms,
    r.price / r.surface                                AS price_m2,
    r.longitude,
    r.latitude
FROM raw r
JOIN per_sale p USING (id_mutation)
WHERE p.n_built_rows = 1
  AND p.n_apartments = 1
  AND r.type_local = 'Appartement'
  AND r.surface BETWEEN 9 AND 300
  AND r.price BETWEEN 30000 AND 15000000
  AND r.price / r.surface BETWEEN 2000 AND 30000       -- remove obvious errors / non-market sales
  AND r.code_postal BETWEEN '75001' AND '75020';
