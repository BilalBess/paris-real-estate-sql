-- Step 2: price per m2 by arrondissement, with ranking and gap vs the Paris median.

WITH stats AS (
    SELECT
        arrondissement,
        COUNT(*)                         AS n_sales,
        ROUND(MEDIAN(price_m2))          AS median_price_m2,
        ROUND(QUANTILE_CONT(price_m2, 0.25)) AS p25_price_m2,
        ROUND(QUANTILE_CONT(price_m2, 0.75)) AS p75_price_m2,
        ROUND(MEDIAN(surface), 1)        AS median_surface
    FROM sales_clean
    GROUP BY arrondissement
),
paris AS (
    SELECT MEDIAN(price_m2) AS paris_median FROM sales_clean
)
SELECT
    s.arrondissement,
    s.n_sales,
    s.median_price_m2,
    s.p25_price_m2,
    s.p75_price_m2,
    s.median_surface,
    RANK() OVER (ORDER BY s.median_price_m2 DESC)           AS rank_expensive,
    ROUND(100.0 * (s.median_price_m2 / p.paris_median - 1), 1) AS pct_vs_paris
FROM stats s
CROSS JOIN paris p
ORDER BY rank_expensive;
