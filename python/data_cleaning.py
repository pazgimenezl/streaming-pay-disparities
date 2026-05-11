# ============================================================
# data_cleaning.py
# Project: Streaming vs Artist Pay Disparities
# Author:  Paz Gimenez | github.com/pazgimenezl
#
# Description:
#   Loads the raw Kaggle dataset, cleans and enriches it,
#   calculates estimated earnings, and produces exploratory
#   visualizations that support the Tableau dashboard.
#
# Requirements:
#   pip install pandas matplotlib seaborn openpyxl
#
# Usage:
#   python data_cleaning.py
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")

# ── Config ────────────────────────────────────────────────────────
RAW_FILE        = "data/raw/Most Streamed Spotify Songs 2024.csv"
CLEANED_FILE    = "data/cleaned/streaming_pay_disparities_FINAL.xlsx"
OUTPUT_CHARTS   = "output_charts/"
PAYOUT_RATE     = 0.004   # Spotify avg per-stream rate (Loud & Clear 2024)
MIN_WAGE_ANNUAL = 19_488  # US minimum wage annual ($1,624/mo)

os.makedirs(OUTPUT_CHARTS, exist_ok=True)

# ── Color palette (Spotify-inspired) ─────────────────────────────
PALETTE = {
    "green":        "#1DB954",
    "dark":         "#191414",
    "white":        "#FFFFFF",
    "gray":         "#B3B3B3",
    "Superstar":    "#7B1FA2",
    "Established":  "#1565C0",
    "Mid-Tier":     "#2E7D32",
    "Rising":       "#E65100",
    "Emerging":     "#C62828",
}

TIER_ORDER  = ["Superstar", "Established", "Mid-Tier", "Rising", "Emerging"]
TIER_COLORS = [PALETTE[t] for t in TIER_ORDER]

plt.rcParams.update({
    "figure.facecolor":  PALETTE["dark"],
    "axes.facecolor":    "#212121",
    "axes.edgecolor":    PALETTE["gray"],
    "axes.labelcolor":   PALETTE["white"],
    "xtick.color":       PALETTE["gray"],
    "ytick.color":       PALETTE["gray"],
    "text.color":        PALETTE["white"],
    "grid.color":        "#333333",
    "grid.linestyle":    "--",
    "grid.alpha":        0.5,
    "font.family":       "sans-serif",
})


# ════════════════════════════════════════════════════════════════
# STEP 1 — Load & inspect raw data
# ════════════════════════════════════════════════════════════════

print("=" * 60)
print("STEP 1: Loading raw data")
print("=" * 60)

df_raw = pd.read_csv(RAW_FILE, encoding="latin-1")
print(f"  Raw shape: {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns")
print(f"  Columns: {list(df_raw.columns)}")
print(f"  Null counts:\n{df_raw.isnull().sum()[df_raw.isnull().sum() > 0]}")


# ════════════════════════════════════════════════════════════════
# STEP 2 — Clean raw data
# ════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("STEP 2: Cleaning data")
print("=" * 60)

df = df_raw.copy()

# Clean stream columns — remove commas, cast to numeric
stream_cols = ["Spotify Streams", "YouTube Views", "TikTok Views",
               "Pandora Streams", "Soundcloud Streams"]

for col in stream_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "").str.strip(),
            errors="coerce"
        )

# Drop rows with no Spotify stream data
before = len(df)
df = df.dropna(subset=["Spotify Streams"])
print(f"  Dropped {before - len(df)} rows with null Spotify Streams")

# Standardize text columns
df["Artist"] = df["Artist"].str.strip()
df["Track"]  = df["Track"].str.strip()

# Parse release date
df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce")
df["Release Year"]  = df["Release Date"].dt.year

print(f"  Cleaned shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"  Date range: {df['Release Year'].min()} – {df['Release Year'].max()}")


# ════════════════════════════════════════════════════════════════
# STEP 3 — Aggregate by artist & enrich
# ════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("STEP 3: Aggregating by artist & calculating earnings")
print("=" * 60)

artist_df = (
    df.groupby("Artist")
    .agg(
        total_streams    = ("Spotify Streams", "sum"),
        track_count      = ("Track", "count"),
        avg_popularity   = ("Spotify Popularity", "mean"),
        total_yt_views   = ("YouTube Views", "sum"),
        total_tiktok_views = ("TikTok Views", "sum"),
    )
    .reset_index()
    .sort_values("total_streams", ascending=False)
)

# Assign tiers
def assign_tier(streams):
    if streams >= 10_000_000_000: return "Superstar"
    elif streams >= 1_000_000_000: return "Established"
    elif streams >= 100_000_000:   return "Mid-Tier"
    elif streams >= 10_000_000:    return "Rising"
    else:                          return "Emerging"

artist_df["artist_tier"] = artist_df["total_streams"].apply(assign_tier)

# Earnings calculations
artist_df["gross_earnings"]   = artist_df["total_streams"] * PAYOUT_RATE
artist_df["monthly_streams"]  = artist_df["total_streams"] / 12
artist_df["monthly_gross"]    = artist_df["monthly_streams"] * PAYOUT_RATE

print(f"  Total artists: {len(artist_df):,}")
print(f"  Tier breakdown:\n{artist_df['artist_tier'].value_counts()}")
print(f"\n  Top 5 by streams:")
print(artist_df[["Artist","total_streams","gross_earnings"]].head())


# ════════════════════════════════════════════════════════════════
# STEP 4 — Exploratory visualizations
# ════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("STEP 4: Generating charts")
print("=" * 60)


# ── Chart 1: Top 15 artists by total streams ─────────────────────
top15 = artist_df.head(15).copy()
top15_colors = [PALETTE.get(t, PALETTE["green"]) for t in top15["artist_tier"]]

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(top15["Artist"][::-1], top15["total_streams"][::-1] / 1e9,
               color=top15_colors[::-1], edgecolor="none", height=0.7)

ax.set_xlabel("Total Streams (Billions)", fontsize=11)
ax.set_title("Top 15 Most Streamed Artists — Spotify 2024",
             fontsize=14, fontweight="bold", color=PALETTE["green"], pad=15)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}B"))
ax.grid(axis="x")

# Add value labels
for bar, val in zip(bars[::-1], top15["total_streams"] / 1e9):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}B", va="center", fontsize=9, color=PALETTE["gray"])

plt.tight_layout()
plt.savefig(f"{OUTPUT_CHARTS}01_top15_artists_by_streams.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ Chart 1: Top 15 artists by streams")


# ── Chart 2: Estimated gross earnings by tier (box plot) ─────────
fig, ax = plt.subplots(figsize=(11, 6))

tier_data = [
    artist_df[artist_df["artist_tier"] == tier]["gross_earnings"].values / 1e6
    for tier in TIER_ORDER
    if tier in artist_df["artist_tier"].values
]
valid_tiers  = [t for t in TIER_ORDER if t in artist_df["artist_tier"].values]
valid_colors = [PALETTE[t] for t in valid_tiers]

bp = ax.boxplot(tier_data, patch_artist=True, notch=False,
                medianprops=dict(color="white", linewidth=2))

for patch, color in zip(bp["boxes"], valid_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)
for element in ["whiskers", "caps", "fliers"]:
    for item in bp[element]:
        item.set_color(PALETTE["gray"])

ax.set_xticklabels(valid_tiers, fontsize=10)
ax.set_ylabel("Estimated Gross Earnings (USD Millions)", fontsize=11)
ax.set_title("Earnings Distribution by Artist Tier — Spotify 2024",
             fontsize=14, fontweight="bold", color=PALETTE["green"], pad=15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
ax.grid(axis="y")

plt.tight_layout()
plt.savefig(f"{OUTPUT_CHARTS}02_earnings_by_tier_boxplot.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ Chart 2: Earnings distribution by tier")


# ── Chart 3: Streams needed per month to reach minimum wage ──────
scenarios = {
    "Major Label\n(18% share)":      1624 / (PAYOUT_RATE * 0.18),
    "Major Label\n(25% share)":      1624 / (PAYOUT_RATE * 0.25),
    "Indie\n(65% share)":            1624 / (PAYOUT_RATE * 0.65),
    "Indie\n(80% share)":            1624 / (PAYOUT_RATE * 0.80),
    "Fully Self-Released\n(100%)":   1624 / (PAYOUT_RATE * 1.00),
}

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.bar(scenarios.keys(), [v/1000 for v in scenarios.values()],
              color=[PALETTE["Superstar"], PALETTE["Established"],
                     PALETTE["Mid-Tier"], PALETTE["Rising"], PALETTE["green"]],
              edgecolor="none", width=0.6)

ax.set_ylabel("Monthly Streams Needed (Thousands)", fontsize=11)
ax.set_title("Monthly Streams Needed to Earn US Minimum Wage\nby Deal Type — Spotify @ $0.004/stream",
             fontsize=13, fontweight="bold", color=PALETTE["green"], pad=15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}K"))
ax.axhline(y=250, color=PALETTE["gray"], linestyle="--", alpha=0.6, linewidth=1)
ax.text(4.4, 255, "250K (common\nbenchmark)", fontsize=8, color=PALETTE["gray"])
ax.grid(axis="y")

for bar, val in zip(bars, scenarios.values()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f"{val/1000:,.0f}K", ha="center", fontsize=9, color=PALETTE["white"])

plt.tight_layout()
plt.savefig(f"{OUTPUT_CHARTS}03_streams_for_min_wage_by_deal.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ Chart 3: Streams needed for minimum wage by deal type")


# ── Chart 4: Stream concentration — winner-take-all ──────────────
artist_df_sorted = artist_df.sort_values("total_streams", ascending=False).reset_index(drop=True)
artist_df_sorted["cumulative_pct"] = (
    artist_df_sorted["total_streams"].cumsum() / artist_df_sorted["total_streams"].sum() * 100
)
artist_df_sorted["artist_pct"] = (artist_df_sorted.index + 1) / len(artist_df_sorted) * 100

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(artist_df_sorted["artist_pct"], artist_df_sorted["cumulative_pct"],
        color=PALETTE["green"], linewidth=2.5)
ax.fill_between(artist_df_sorted["artist_pct"], artist_df_sorted["cumulative_pct"],
                alpha=0.15, color=PALETTE["green"])

# Mark the 10% / 50% points
for pct, label in [(10, "Top 10%"), (1, "Top 1%")]:
    idx = artist_df_sorted[artist_df_sorted["artist_pct"] <= pct].index[-1]
    cum = artist_df_sorted.loc[idx, "cumulative_pct"]
    ax.annotate(f"{label}\n→ {cum:.0f}% of streams",
                xy=(pct, cum), xytext=(pct + 8, cum - 15),
                arrowprops=dict(arrowstyle="->", color=PALETTE["gray"]),
                fontsize=9, color=PALETTE["white"])

ax.set_xlabel("% of Artists (ranked by streams)", fontsize=11)
ax.set_ylabel("Cumulative % of Total Streams", fontsize=11)
ax.set_title("Stream Concentration — Winner-Take-All Economy\nSpotify 2024 Dataset",
             fontsize=13, fontweight="bold", color=PALETTE["green"], pad=15)
ax.grid()
plt.tight_layout()
plt.savefig(f"{OUTPUT_CHARTS}04_stream_concentration_curve.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ Chart 4: Stream concentration curve")


# ════════════════════════════════════════════════════════════════
# STEP 5 — Summary stats
# ════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("STEP 5: Summary statistics")
print("=" * 60)

total_streams = artist_df["total_streams"].sum()
print(f"  Total streams in dataset:     {total_streams/1e9:.1f}B")
print(f"  Total artists analyzed:       {len(artist_df):,}")
print(f"  Avg streams per artist:       {artist_df['total_streams'].mean()/1e6:.1f}M")
print(f"  Median streams per artist:    {artist_df['total_streams'].median()/1e6:.1f}M")

top10_pct = artist_df.head(int(len(artist_df)*0.1))["total_streams"].sum() / total_streams * 100
print(f"\n  Top 10% of artists control:   {top10_pct:.1f}% of all streams")

emerging = artist_df[artist_df["artist_tier"] == "Emerging"]
if len(emerging) > 0:
    avg_emerging_monthly = emerging["monthly_gross"].mean()
    print(f"\n  Avg emerging artist monthly gross: ${avg_emerging_monthly:,.2f}")
    print(f"  Streams needed/month for min wage: {1624/PAYOUT_RATE:,.0f}")

print(f"\n  Charts saved to: {OUTPUT_CHARTS}")
print("\n✓ Script complete.")
