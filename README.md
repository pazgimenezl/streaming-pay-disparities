# Streaming vs Artist Pay Disparities
### A data analytics project by Paz | Business Intelligence & Data Analytics

---

## The Question

Spotify reported over $4 billion paid to rights holders in 2023. So why are most artists still struggling to make a living from streams?

This project breaks down the economics of music streaming — where the money actually goes, which artists are hit hardest, and what the data reveals about the gap between platform revenue and artist earnings.

---

## What I Found

- The average per-stream payout across major platforms ranges from **$0.003 to $0.005**
- An independent artist needs roughly **250,000 streams per month** just to earn minimum wage
- Major label artists receive a fraction of already-low royalty rates due to label contract splits
- Genre and audience size create dramatic disparities — artists in niche genres face compounding disadvantages
- The top 1% of artists on Spotify account for over 90% of total streams

---

## Project Structure

```
streaming-pay-disparities/
│
├── data/
│   ├── raw/                        # Original datasets (unmodified)
│   └── cleaned/
│       └── streaming_payouts.xlsx  # Cleaned dataset with artist tier, genre, label status
│
├── sql/
│   ├── avg_payout_by_genre.sql
│   ├── indie_vs_label_comparison.sql
│   └── artist_tier_analysis.sql
│
├── python/
│   └── data_cleaning.py            # Data cleaning and exploratory analysis
│
├── tableau/
│   └── dashboard_link.md           # Link to live Tableau Public dashboard
│
└── README.md
```

---

## Tools Used

| Tool | Purpose |
|------|---------|
| **Excel** | Data cleaning, pivot tables, initial exploration |
| **SQL** | Querying and aggregating payout data by genre, label status, and artist tier |
| **Tableau** | Interactive dashboard visualizing pay disparities |
| **Python** | Data cleaning automation and exploratory analysis |

---

## Data Sources

- [Spotify Loud & Clear Report](https://loudandclear.byspotify.com/) — official Spotify royalty transparency data
- [Bureau of Labor Statistics](https://www.bls.gov/) — minimum wage benchmarks for context
- [Water & Music Research](https://www.waterandmusic.com/) — music industry economics research
- Supplementary data compiled manually from public artist interviews and industry reports

---

## Key Visualizations

*(Tableau Public dashboard — link coming soon)*

1. **Platform Payout Comparison** — per-stream rates across Spotify, Apple Music, Tidal, YouTube Music
2. **Artist Tier Breakdown** — how stream count tier affects effective payout rate
3. **Genre Disparity Map** — average streams and earnings by genre
4. **Indie vs Label Split** — how label contracts affect what artists actually take home
5. **Streams to Minimum Wage Calculator** — how many streams an artist needs to survive, by country

---

## Why This Matters

The music industry conversation is often dominated by platform vs. label debates. But the data tells a more nuanced story — one where the structure of streaming economics systematically disadvantages independent and emerging artists regardless of platform. Understanding these patterns is essential for anyone working in music analytics, artist development, or music tech.

---

## About Me

I'm a data analytics student (graduating April 2027) with a focus on the music industry. I'm interested in the intersection of data, streaming economics, and artist success — building toward a career in music analytics at companies like Spotify, Apple Music, or major labels.

📎 [[LinkedIn](https://www.linkedin.com/in/maria-paz-gimenez-lopez-a9a068367/)](#) | 📊 [[Tableau Public](https://public.tableau.com/app/profile/maria.gimenez.lopez/vizzes)](#) | 🐙 [GitHub](https://github.com)
