# Your converted Python script from the Jupyter Notebook
# All markdown cells are preserved as comments for context

# --- Imports & Configuration ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pvlib import solarposition
from pathlib import Path
from datetime import timedelta
import pytz
from scipy.stats import spearmanr

# Configuration
DATA_PATH = Path("data/PLRT.xlsx")  # Change to your file path
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

SITE_LAT = -7.00589
SITE_LON = 106.562
SITE_ALT = 49
TIMEZONE = "Asia/Jakarta"
EXPECTED_FREQ = "10min"
RESAMPLE_FREQ = "H"

NEON_PALETTE = ["#39FF14", "#FF007F", "#00FFFF", "#FFDD00", "#7CFC00", "#FF6EC7"]
sns.set(style="whitegrid")

SELECTED_COLUMNS = [
    'Time', 'rr', 'ws_avg', 'ws_max', 'wd_avg',
    'tt_air_max', 'tt_air_avg', 'tt_air_min',
    'rh_avg', 'pp_air', 'sr_avg', 'sr_max'
]

# --- Data Loading & Inspection ---
# Load dataset
# Inspect structure

df = pd.read_excel(DATA_PATH)
df['Time'] = pd.to_datetime(df['Time'], format="%d/%m/%Y %H:%M:%S", errors="coerce")
df = df[SELECTED_COLUMNS]

# --- Handle Missing Timestamps ---
full_index = pd.date_range(start=df['Time'].min(), end=df['Time'].max(), freq=EXPECTED_FREQ)
df = df.set_index('Time').reindex(full_index).rename_axis('Time').reset_index()

# Interpolate missing values
df.interpolate(method='linear', limit_direction='both', inplace=True)

# --- Solar Geometry & Temporal Features ---
df['WIB'] = df['Time'] + pd.Timedelta(hours=7)
sp = solarposition.get_solarposition(
    df['WIB'].dt.tz_localize(TIMEZONE),
    SITE_LAT, SITE_LON, altitude=SITE_ALT
)
df['Sun_Altitude'] = sp['elevation']
df['Sun_Azimuth'] = sp['azimuth']
df['Sun_Zenith_Angle'] = sp['zenith']

df['Hour'] = df['WIB'].dt.hour
df['DOY'] = df['WIB'].dt.dayofyear
df['Month'] = df['WIB'].dt.month
df['Year'] = df['WIB'].dt.year
df['Day'] = df['WIB'].dt.day

# --- Resample to Hourly ---
df_hourly = df.set_index('WIB').resample(RESAMPLE_FREQ).first().reset_index()
df_hourly['Date'] = pd.to_datetime(df_hourly['WIB']).dt.date

# --- Visualization 1: Standard Line Graph ---
exclude_cols = ['Time', 'WIB', 'Date']
line_columns = [col for col in df_hourly.columns if col not in exclude_cols]
for idx, col in enumerate(line_columns):
    plt.figure(figsize=(14, 2.5))
    plt.plot(df_hourly['WIB'], df_hourly[col], color=NEON_PALETTE[idx % len(NEON_PALETTE)], linewidth=0.9)
    plt.title(col)
    plt.tight_layout()
    plt.show()

# --- Visualization 2: Monthly Faceted Line Plots (Raw Hourly) ---
exclude_cols = ['WIB', 'Date', 'Time', 'Hour', 'DOY', 'Month']
plot_columns = [col for col in df_hourly.columns if col not in exclude_cols]

df_hourly['Year'] = pd.to_datetime(df_hourly['Date']).dt.year
df_hourly['Month'] = pd.to_datetime(df_hourly['Date']).dt.month
df_hourly['Day'] = pd.to_datetime(df_hourly['Date']).dt.day

years_sorted = [2022, 2023]
colors = plt.cm.tab10.colors
for idx, col in enumerate(plot_columns):
    fig, axes = plt.subplots(nrows=4, ncols=6, figsize=(20, 12), sharey=False)
    fig.suptitle(f"{col} — Monthly Plots Jan 2022 to Dec 2023", fontsize=18, y=1.02, fontweight='semibold')
    month_idx = 0
    for year in years_sorted:
        for month in range(1, 13):
            r = month_idx // 6
            c = month_idx % 6
            ax = axes[r, c]
            subset = df_hourly[(df_hourly['Year'] == year) & (df_hourly['Month'] == month)]
            if not subset.empty:
                sns.lineplot(
                    data=subset,
                    x=subset['WIB'].dt.day,
                    y=col,
                    ax=ax,
                    color=colors[idx % len(colors)],
                    estimator=None,
                    errorbar=None
                )
            ax.set_title(f"{year}-{month:02d}", fontsize=10)
            ax.set_xticks(range(1, 32, 5))
            ax.set_xlabel("")
            ax.set_ylabel("")
            month_idx += 1
    plt.tight_layout()
    plt.show()

# --- Visualization 3: Monthly Faceted Line Plots (Daily Aggregated) ---
for idx, col in enumerate(plot_columns):
    fig, axes = plt.subplots(nrows=4, ncols=6, figsize=(20, 12), sharey=False)
    fig.suptitle(f"{col} — Monthly (Daily Aggregated) Plots Jan 2022 to Dec 2023", fontsize=18, y=1.02, fontweight='semibold')
    month_idx = 0
    for year in years_sorted:
        for month in range(1, 13):
            r = month_idx // 6
            c = month_idx % 6
            ax = axes[r, c]
            subset = df_hourly[(df_hourly['Year'] == year) & (df_hourly['Month'] == month)]
            if not subset.empty:
                daily_avg = subset.groupby('Day')[col].mean().reset_index()
                sns.lineplot(
                    data=daily_avg,
                    x='Day',
                    y=col,
                    ax=ax,
                    color=colors[idx % len(colors)]
                )
            ax.set_title(f"{year}-{month:02d}", fontsize=10)
            ax.set_xticks(range(1, 32, 5))
            ax.set_xlabel("")
            ax.set_ylabel("")
            month_idx += 1
    plt.tight_layout()
    plt.show()

# --- Visualization 4: Data Distribution Histograms ---
exclude_cols = ['Time', 'WIB', 'Date']
hist_columns = [col for col in df_hourly.columns if col not in exclude_cols]
colors = sns.color_palette("tab20", len(hist_columns))
n_cols = 3
n_rows = int(np.ceil(len(hist_columns) / n_cols))
plt.figure(figsize=(6 * n_cols, 4 * n_rows))
for idx, col in enumerate(hist_columns, 1):
    ax = plt.subplot(n_rows, n_cols, idx)
    sns.histplot(
        data=df_hourly,
        x=col,
        color=colors[idx % len(colors)],
        bins=30,
        kde=True,
        ax=ax
    )
    ax.set_title(f"Histogram of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Frequency")
plt.tight_layout()
plt.show()

# --- Visualization 5: Spearman Correlation Heatmap ---
selected_corr_columns = [
    'rr', 'ws_avg', 'ws_max', 'wd_avg',
    'tt_air_max', 'tt_air_avg', 'tt_air_min',
    'rh_avg', 'pp_air', 'sr_avg', 'sr_max',
    'Sun_Altitude', 'Sun_Azimuth', 'Sun_Zenith_Angle'
]
plt.figure(figsize=(10, 8))
corr = df_hourly[selected_corr_columns].corr(method='spearman')
sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', center=0)
plt.title("Spearman Correlation Heatmap (Hourly)")
plt.tight_layout()
plt.show()

# --- Visualization 6: Scatter Plot sr_avg vs Other Variables ---
exclude_cols = ['Time', 'WIB', 'sr_avg', 'Date']
plot_columns = [col for col in df_hourly.columns if col not in exclude_cols]
n_cols = 3
n_rows = int(np.ceil(len(plot_columns) / n_cols))
plt.figure(figsize=(4 * n_cols, 3.2 * n_rows))
for idx, col in enumerate(plot_columns, 1):
    ax = plt.subplot(n_rows, n_cols, idx)
    sns.regplot(
        data=df_hourly,
        x='sr_avg',
        y=col,
        scatter_kws={'s': 10, 'alpha': 0.5, 'color': 'darkturquoise'},
        line_kws={'color': 'black', 'lw': 1.5},
        ax=ax
    )
    ax.set_xlim(0, 1200)
    rho, _ = spearmanr(df_hourly['sr_avg'], df_hourly[col], nan_policy='omit')
    ax.text(
        0.05, 0.95,
        f"ρ = {rho:.2f}",
        transform=ax.transAxes,
        ha='left', va='top',
        fontsize=10,
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
    )
    ax.set_title(f"sr_avg vs {col}")
    ax.set_xlabel("sr_avg (W/m²)")
    ax.set_ylabel(col)
plt.tight_layout()
plt.show()
