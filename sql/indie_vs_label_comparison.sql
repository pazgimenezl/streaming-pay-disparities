-- ============================================================
-- indie_vs_label_comparison.sql
-- Project: Streaming vs Artist Pay Disparities
-- Author:  Paz Gimenez | github.com/pazgimenezl
-- Description: Compares streaming earnings between
--              independent and major label artists.
--              Highlights the trade-off between reach
--              (major labels) and share (independents).
-- ============================================================


-- ============================================================
-- QUERY 1: High-level comparison — Major vs Independent
-- ============================================================

SELECT
    label_status,
    COUNT(*)                                            AS artist_count,
    ROUND(AVG(total_annual_streams), 0)                 AS avg_annual_streams,
    ROUND(AVG(total_annual_streams * 0.004), 2)         AS avg_gross_earnings_usd,
    ROUND(AVG(artist_share_pct) * 100, 1)               AS avg_artist_share_pct,
    ROUND(AVG(total_annual_streams * 0.004
          * artist_share_pct), 2)                       AS avg_net_earnings_usd,
    ROUND(AVG(total_annual_streams * 0.004
          * artist_share_pct) / 12, 2)                  AS avg_monthly_net_usd,
    ROUND(MAX(total_annual_streams * 0.004
          * artist_share_pct), 2)                       AS max_net_earnings_usd,
    ROUND(MIN(total_annual_streams * 0.004
          * artist_share_pct), 2)                       AS min_net_earnings_usd

FROM artist_streaming_data
GROUP BY label_status
ORDER BY avg_net_earnings_usd DESC;


-- ============================================================
-- QUERY 2: The trade-off — same streams, different take-home
-- Simulates what an independent artist would earn
-- if they had the same stream count as a major label artist
-- ============================================================

SELECT
    artist_name,
    label_status,
    total_annual_streams,
    artist_share_pct,
    ROUND(total_annual_streams * 0.004, 2)              AS gross_earnings_usd,
    ROUND(total_annual_streams * 0.004
          * artist_share_pct, 2)                        AS actual_net_usd,

    -- What would they earn with an independent 80% share?
    ROUND(total_annual_streams * 0.004 * 0.80, 2)       AS hypothetical_indie_net_usd,

    -- What would they earn with a major 18% share?
    ROUND(total_annual_streams * 0.004 * 0.18, 2)       AS hypothetical_major_net_usd,

    -- Difference: how much more an indie deal would pay
    ROUND((total_annual_streams * 0.004 * 0.80)
        - (total_annual_streams * 0.004 * 0.18), 2)     AS indie_advantage_usd

FROM artist_streaming_data
WHERE total_annual_streams > 500000000  -- focus on artists with meaningful streams
ORDER BY gross_earnings_usd DESC
LIMIT 20;


-- ============================================================
-- QUERY 3: Independent artists ranked by net earnings
-- Shows which indie artists are actually making it work
-- ============================================================

SELECT
    artist_name,
    genre,
    label_name,
    total_annual_streams,
    artist_share_pct,
    ROUND(total_annual_streams * 0.004
          * artist_share_pct, 2)                        AS net_earnings_usd,
    ROUND(total_annual_streams * 0.004
          * artist_share_pct / 12, 2)                   AS monthly_net_usd,
    CASE
        WHEN total_annual_streams * 0.004
             * artist_share_pct >= 100000
        THEN 'Sustainable'
        WHEN total_annual_streams * 0.004
             * artist_share_pct >= 19488
        THEN 'Above min wage'
        WHEN total_annual_streams * 0.004
             * artist_share_pct >= 15000
        THEN 'Near poverty line'
        ELSE 'Below poverty line'
    END                                                 AS financial_status

FROM artist_streaming_data
WHERE label_status = 'Independent'
ORDER BY net_earnings_usd DESC;


-- ============================================================
-- QUERY 4: The real cost of a major label deal
-- For each major label artist, calculates how much money
-- goes to the label vs how much the artist keeps
-- ============================================================

SELECT
    artist_name,
    label_name,
    ROUND(total_annual_streams * 0.004, 2)              AS gross_earnings_usd,
    ROUND(total_annual_streams * 0.004
          * artist_share_pct, 2)                        AS artist_keeps_usd,
    ROUND(total_annual_streams * 0.004
          * (1 - artist_share_pct), 2)                  AS label_takes_usd,
    ROUND((1 - artist_share_pct) * 100, 1)              AS label_cut_pct

FROM artist_streaming_data
WHERE label_status = 'Major'
ORDER BY label_takes_usd DESC
LIMIT 20;
