-- Step 4: does the price per m2 change with the size of the flat?
-- I expected small flats to be more expensive per m2. The result is more
-- interesting: it is flat between 20 and 70 m2, then goes up for big flats.

SELECT
    CASE
        WHEN surface < 20 THEN '1) < 20 m2'
        WHEN surface < 40 THEN '2) 20-39 m2'
        WHEN surface < 70 THEN '3) 40-69 m2'
        WHEN surface < 100 THEN '4) 70-99 m2'
        ELSE '5) 100+ m2'
    END                                  AS size_bucket,
    COUNT(*)                             AS n_sales,
    ROUND(MEDIAN(price_m2))              AS median_price_m2,
    ROUND(MEDIAN(price))                 AS median_total_price
FROM sales_clean
GROUP BY 1
ORDER BY 1;
