-- Step 3: monthly trend with window functions (3-month moving median is not
-- available directly, so I use a 3-month moving average of the monthly median).

WITH monthly AS (
    SELECT
        DATE_TRUNC('month', sale_date)   AS month,
        COUNT(*)                         AS n_sales,
        MEDIAN(price_m2)                 AS median_price_m2
    FROM sales_clean
    GROUP BY 1
)
SELECT
    month,
    n_sales,
    ROUND(median_price_m2)                                             AS median_price_m2,
    ROUND(AVG(median_price_m2) OVER (ORDER BY month
          ROWS BETWEEN 2 PRECEDING AND CURRENT ROW))                   AS moving_avg_3m,
    ROUND(100.0 * (median_price_m2 / LAG(median_price_m2) OVER (ORDER BY month) - 1), 1)
                                                                       AS pct_change_vs_prev_month
FROM monthly
ORDER BY month;
