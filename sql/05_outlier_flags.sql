-- Step 5: flag sales that are unusually cheap or expensive FOR THEIR arrondissement
-- (z-score computed with window functions, partitioned by arrondissement).
-- Useful to spot deals, data errors, or special sales (family sale, viager...).

WITH scored AS (
    SELECT
        id_mutation,
        sale_date,
        arrondissement,
        surface,
        price,
        ROUND(price_m2) AS price_m2,
        (price_m2 - AVG(price_m2) OVER (PARTITION BY arrondissement))
            / NULLIF(STDDEV_SAMP(price_m2) OVER (PARTITION BY arrondissement), 0) AS z_score
    FROM sales_clean
)
SELECT *, ROUND(z_score, 2) AS z
FROM scored
WHERE ABS(z_score) > 3
ORDER BY ABS(z_score) DESC
LIMIT 20;
