-- ============================================================
-- artist_tier_analysis.sql
-- Project: Streaming vs Artist Pay Disparities
-- Author:  Paz Gimenez | github.com/pazgimenezl
-- Description: Analyzes how streaming earnings scale
--              (or fail to scale) across artist tiers.
--              Quantifies the winner-take-all nature of
--              the streaming economy.
-- ============================================================


-- ============================================================
-- QUERY 1: Earnings summary by artist tier
-- ============================================================

SELECT
    artist_tier,
    COUNT(*)                                            AS artist_count,
    ROUND(AVG(total_annual_streams), 0)                 AS avg_annual_streams,
    ROUND(MIN(total_annual_streams), 0)                 AS min_annual_streams,
    ROUND(MAX(total_annual_streams), 0)                 AS max_annual_streams,
    ROUND(AVG(total_annual_streams * 0.004
          * artist_share_pct), 2)                       AS avg_net_earnings_usd,
    ROUND(MIN(total_annual_streams * 0.004
          * artist_share_pct), 2)                       AS min_net_earnings_usd,
    ROUND(MAX(total_annual_streams * 0.004
          * artist_share_pct), 2)                       AS max_net_earnings_usd,
    ROUND(AVG(total_annual_streams * 0.004
          * artist_share_pct) / 12, 2)                  AS avg_monthly_net_usd

FROM artist_streaming_data
GROUP BY artist_tier
ORDER BY
    CASE artist_tier
        WHEN 'Superstar'   THEN 1
        WHEN 'Established' THEN 2
        WHEN 'Mid-Tier'    THEN 3
        WHEN 'Rising'      THEN 4
        WHEN 'Emerging'    THEN 5
    END;


-- ============================================================
-- QUERY 2: The disparity ratio
-- How much more does a Superstar earn vs an Emerging artist?
-- ============================================================

SELECT
    MAX(CASE WHEN artist_tier = 'Superstar'
        THEN avg_net END)                               AS superstar_avg_net,
    MAX(CASE WHEN artist_tier = 'Emerging'
        THEN avg_net END)                               AS emerging_avg_net,
    ROUND(
        MAX(CASE WHEN artist_tier = 'Superstar'
            THEN avg_net END) /
        NULLIF(MAX(CASE WHEN artist_tier = 'Emerging'
            THEN avg_net END), 0)
    , 0)                                                AS disparity_ratio

FROM (
    SELECT
        artist_tier,
        AVG(total_annual_streams * 0.004 * artist_share_pct) AS avg_net
    FROM artist_streaming_data
    GROUP BY artist_tier
) tier_averages;


-- ============================================================
-- QUERY 3: Survival analysis — which tiers can live on streams?
-- Compares each tier's avg earnings to real benchmarks
-- ============================================================

SELECT
    artist_tier,
    COUNT(*)                                            AS total_artists,
    SUM(CASE WHEN total_annual_streams * 0.004
             * artist_share_pct >= 19488
        THEN 1 ELSE 0 END)                              AS artists_above_min_wage,
    SUM(CASE WHEN total_annual_streams * 0.004
             * artist_share_pct < 19488
        THEN 1 ELSE 0 END)                              AS artists_below_min_wage,
    ROUND(
        100.0 * SUM(CASE WHEN total_annual_streams * 0.004
                        * artist_share_pct >= 19488
                   THEN 1 ELSE 0 END) / COUNT(*), 1
    )                                                   AS pct_above_min_wage

FROM artist_streaming_data
GROUP BY artist_tier
ORDER BY
    CASE artist_tier
        WHEN 'Superstar'   THEN 1
        WHEN 'Established' THEN 2
        WHEN 'Mid-Tier'    THEN 3
        WHEN 'Rising'      THEN 4
        WHEN 'Emerging'    THEN 5
    END;


-- ============================================================
-- QUERY 4: Stream concentration — winner-take-all analysis
-- What % of total streams do the top 10% of artists capture?
-- ============================================================

WITH ranked AS (
    SELECT
        artist_name,
        artist_tier,
        total_annual_streams,
        NTILE(10) OVER (ORDER BY total_annual_streams DESC) AS decile
    FROM artist_streaming_data
),
totals AS (
    SELECT SUM(total_annual_streams) AS total_streams FROM artist_streaming_data
)
SELECT
    decile,
    COUNT(*)                                            AS artist_count,
    SUM(r.total_annual_streams)                         AS decile_streams,
    ROUND(100.0 * SUM(r.total_annual_streams)
          / t.total_streams, 2)                         AS pct_of_total_streams
FROM ranked r, totals t
GROUP BY decile, t.total_streams
ORDER BY decile;


-- ============================================================
-- QUERY 5: Top 10 and bottom 10 artists by net earnings
-- Side by side to illustrate the extremes
-- ============================================================

SELECT 'Top 10' AS group_label, artist_name, artist_tier, label_status,
    ROUND(total_annual_streams * 0.004 * artist_share_pct, 2) AS net_earnings_usd
FROM artist_streaming_data
ORDER BY net_earnings_usd DESC
LIMIT 10

UNION ALL

SELECT 'Bottom 10' AS group_label, artist_name, artist_tier, label_status,
    ROUND(total_annual_streams * 0.004 * artist_share_pct, 2) AS net_earnings_usd
FROM artist_streaming_data
ORDER BY net_earnings_usd ASC
LIMIT 10;
