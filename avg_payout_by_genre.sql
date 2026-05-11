-- ============================================================
-- avg_payout_by_genre.sql
-- Project: Streaming vs Artist Pay Disparities
-- Author:  Paz Gimenez | github.com/pazgimenezl
-- Description: Analyzes estimated gross and net earnings
--              by genre to identify which genres are most
--              and least compensated on Spotify.
-- ============================================================

SELECT
    genre,
    COUNT(*)                                        AS artist_count,
    ROUND(AVG(total_annual_streams), 0)             AS avg_annual_streams,
    ROUND(AVG(total_annual_streams * 0.004), 2)     AS avg_gross_earnings_usd,
    ROUND(AVG(artist_share_pct), 2)                 AS avg_artist_share_pct,
    ROUND(AVG(total_annual_streams * 0.004
          * artist_share_pct), 2)                   AS avg_net_earnings_usd,
    ROUND(AVG(total_annual_streams * 0.004
          * artist_share_pct) / 12, 2)              AS avg_monthly_net_usd,

    -- How many streams does the avg artist in this genre
    -- need per month to reach US minimum wage ($1,624/mo)?
    ROUND(1624.0 / 0.004 / AVG(artist_share_pct), 0)
                                                    AS monthly_streams_for_min_wage

FROM artist_streaming_data
GROUP BY genre
ORDER BY avg_net_earnings_usd DESC;


-- ============================================================
-- FOLLOW-UP: Bottom 10 genres by average net earnings
-- Highlights the genres where artists struggle the most
-- ============================================================

SELECT
    genre,
    COUNT(*)                                        AS artist_count,
    ROUND(AVG(total_annual_streams * 0.004
          * artist_share_pct), 2)                   AS avg_net_earnings_usd,
    ROUND(AVG(total_annual_streams * 0.004
          * artist_share_pct) / 12, 2)              AS avg_monthly_net_usd
FROM artist_streaming_data
GROUP BY genre
HAVING COUNT(*) >= 2
ORDER BY avg_net_earnings_usd ASC
LIMIT 10;


-- ============================================================
-- FOLLOW-UP: Genre earnings vs minimum wage benchmark
-- Flags genres where the average artist earns below
-- the US federal poverty line (~$15,000/year)
-- ============================================================

SELECT
    genre,
    COUNT(*)                                        AS artist_count,
    ROUND(AVG(total_annual_streams * 0.004
          * artist_share_pct), 2)                   AS avg_net_earnings_usd,
    CASE
        WHEN AVG(total_annual_streams * 0.004
             * artist_share_pct) < 15000
        THEN 'Below poverty line'
        WHEN AVG(total_annual_streams * 0.004
             * artist_share_pct) < 19488
        THEN 'Below minimum wage'
        WHEN AVG(total_annual_streams * 0.004
             * artist_share_pct) < 50000
        THEN 'Modest income'
        ELSE 'Sustainable income'
    END                                             AS income_category
FROM artist_streaming_data
GROUP BY genre
ORDER BY avg_net_earnings_usd DESC;
