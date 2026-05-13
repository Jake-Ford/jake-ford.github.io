#!/usr/bin/env python3
"""Generate NBA contracts interactive charts.
Run: python3 make_nba.py
Outputs to static/nba/
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
OUT  = ROOT / "static" / "nba"
OUT.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Historical + projected NBA salary caps (fiscal year → cap in dollars)
# Sources: basketball-reference, spotrac, NBA CBA
SAL_CAP_DATA = [
    (1985, 3_600_000), (1986, 4_233_000), (1987, 4_945_000), (1988, 7_232_000),
    (1989, 7_232_000), (1990, 9_802_000), (1991, 11_871_000), (1992, 12_500_000),
    (1993, 14_000_000), (1994, 15_175_000), (1995, 15_964_000), (1996, 23_000_000),
    (1997, 26_900_000), (1998, 30_000_000), (1999, 30_000_000), (2000, 34_000_000),
    (2001, 35_500_000), (2002, 40_271_000), (2003, 43_840_000), (2004, 43_870_000),
    (2005, 43_870_000), (2006, 49_500_000), (2007, 53_135_000), (2008, 55_630_000),
    (2009, 57_700_000), (2010, 57_700_000), (2011, 58_044_000), (2012, 58_044_000),
    (2013, 58_679_000), (2014, 58_679_000), (2015, 63_065_000), (2016, 70_000_000),
    (2017, 99_093_000), (2018, 102_005_000), (2019, 109_140_000), (2020, 109_140_000),
    (2021, 112_414_000), (2022, 112_414_000), (2023, 123_655_000), (2024, 136_021_000),
    (2025, 140_588_000), (2026, 153_938_000), (2027, 162_186_000), (2028, 170_700_000),
    (2029, 179_600_000),
]


def get_sal_cap_df():
    df = pd.DataFrame(SAL_CAP_DATA, columns=["fiscal_year_int", "Salary Cap"])
    df["Fiscal_Year"] = df["fiscal_year_int"].astype(str)
    return df


# ── Scrape player contracts ────────────────────────────────────────────────────
def fetch_player_contracts():
    url = "https://www.basketball-reference.com/contracts/players.html"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find("table", {"id": "player-contracts"}) or soup.find("table")

    headers_row = table.find("thead").find_all("tr")[-1]
    cols = [th.get_text(strip=True) for th in headers_row.find_all("th")]

    rows = []
    for tr in table.find("tbody").find_all("tr"):
        if "thead" in tr.get("class", []):
            continue
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if cells and cells[0].isdigit():
            rows.append(cells[:len(cols)])

    return pd.DataFrame(rows, columns=cols)


# ── Chart 1: Salary cap trajectory ────────────────────────────────────────────
def chart_salary_cap(sal_cap):
    df = sal_cap.copy()
    df["Cap_M"] = df["Salary Cap"] / 1e6

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Fiscal_Year"],
        y=df["Cap_M"],
        mode="lines+markers",
        line=dict(color="#d35400", width=2),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Cap: $%{y:.1f}M<extra></extra>",
    ))
    fig.update_layout(
        title="NBA Salary Cap Over Fiscal Years",
        xaxis_title="Fiscal Year",
        yaxis_title="Salary Cap ($M)",
        xaxis=dict(tickangle=45, nticks=20),
        font=dict(family="ui-monospace, monospace", size=12),
        paper_bgcolor="#f8f7f2",
        plot_bgcolor="#f8f7f2",
        margin=dict(t=60, l=60, r=20, b=80),
        height=460,
    )
    fig.update_yaxes(gridcolor="#d8d8d0")
    fig.update_xaxes(gridcolor="#d8d8d0")
    fig.write_html(str(OUT / "cap_trajectory.html"), full_html=True, include_plotlyjs="cdn")
    print("  wrote static/nba/cap_trajectory.html")


# ── Chart 2: YoY % change ──────────────────────────────────────────────────────
def chart_pct_change(sal_cap):
    df = sal_cap.sort_values("fiscal_year_int").copy()
    df["Pct_Change"] = df["Salary Cap"].pct_change() * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Fiscal_Year"],
        y=df["Pct_Change"],
        mode="lines+markers",
        line=dict(color="#0066cc", width=2),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Change: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="#999", line_width=1)
    fig.update_layout(
        title="Year-Over-Year % Change in NBA Salary Cap",
        xaxis_title="Fiscal Year",
        yaxis_title="% Change",
        xaxis=dict(tickangle=45, nticks=20),
        font=dict(family="ui-monospace, monospace", size=12),
        paper_bgcolor="#f8f7f2",
        plot_bgcolor="#f8f7f2",
        margin=dict(t=60, l=60, r=20, b=80),
        height=460,
    )
    fig.update_yaxes(gridcolor="#d8d8d0")
    fig.update_xaxes(gridcolor="#d8d8d0")
    fig.write_html(str(OUT / "cap_pct_change.html"), full_html=True, include_plotlyjs="cdn")
    print("  wrote static/nba/cap_pct_change.html")


# ── Chart 3: Player salary % of cap ───────────────────────────────────────────
def chart_player_pct(contracts_df, sal_cap):
    def get_cap(yr):
        row = sal_cap[sal_cap["fiscal_year_int"] == yr]
        if not row.empty:
            return row.iloc[0]["Salary Cap"]
        # Extrapolate using last 3 years avg growth
        last = sal_cap.tail(3)
        avg_growth = last["Salary Cap"].pct_change().mean()
        base = sal_cap.iloc[-1]["Salary Cap"]
        steps = yr - sal_cap.iloc[-1]["fiscal_year_int"]
        return base * ((1 + avg_growth) ** steps)

    # Detect available contract year columns
    all_year_cols = [c for c in contracts_df.columns
                     if len(c) == 7 and c[4] == "-" and c[:4].isdigit()]

    # Map column label → fiscal year int (e.g. "2025-26" → 2026)
    year_map = {}
    for col in all_year_cols:
        fy = int(col[:4]) + 1
        year_map[col] = fy

    # Use up to 5 years starting from current
    year_cols = sorted(year_map.keys())[:5]

    df = contracts_df.copy()

    # Parse salary columns to numeric, compute % of cap
    for col in year_cols:
        yr = year_map[col]
        cap = get_cap(yr)
        num_col = col + "_num"
        df[num_col] = pd.to_numeric(
            df[col].str.replace(r"[\$,]", "", regex=True), errors="coerce"
        )
        df[f"pct_{yr}"] = df[num_col] / cap

    # Sort by first year pct, take top 25
    first_pct = f"pct_{year_map[year_cols[0]]}"
    df_sorted = df.sort_values(first_pct, ascending=False).head(25).copy()

    # Ensure Jaylen Brown is in the set
    jb_all = df[df["Player"].str.contains("Jaylen Brown", na=False)]
    if not jb_all.empty and "Jaylen Brown" not in df_sorted["Player"].values:
        df_sorted = pd.concat([df_sorted, jb_all.iloc[[0]]], ignore_index=True)

    # Sort players by first year pct for display
    df_sorted = df_sorted.sort_values(first_pct, ascending=True)

    colors = ["#d35400", "#0066cc", "#27ae60", "#8e44ad", "#e67e22"]

    fig = go.Figure()
    for i, col in enumerate(year_cols):
        yr = year_map[col]
        pct_col = f"pct_{yr}"
        season_label = col
        fig.add_trace(go.Bar(
            y=df_sorted["Player"],
            x=df_sorted[pct_col],
            name=season_label,
            orientation="h",
            marker_color=colors[i % len(colors)],
            opacity=0.85,
            hovertemplate=f"<b>%{{y}}</b><br>{season_label}: %{{x:.1%}}<extra></extra>",
        ))

    # Dotted reference lines for Jaylen Brown's pct each year
    jb_mask = df_sorted["Player"].str.contains("Jaylen Brown", na=False)
    if jb_mask.any():
        jb_row = df_sorted[jb_mask].iloc[0]
        for i, col in enumerate(year_cols):
            yr = year_map[col]
            val = jb_row.get(f"pct_{yr}", None)
            if pd.notna(val) and val > 0:
                fig.add_vline(
                    x=val,
                    line_dash="dot",
                    line_color=colors[i % len(colors)],
                    line_width=1.5,
                )

    fig.update_layout(
        title="Top Player Salaries as % of NBA Salary Cap",
        xaxis_title="% of Salary Cap",
        xaxis=dict(tickformat=".0%"),
        barmode="group",
        font=dict(family="ui-monospace, monospace", size=11),
        paper_bgcolor="#f8f7f2",
        plot_bgcolor="#f8f7f2",
        margin=dict(t=60, l=180, r=20, b=60),
        height=700,
        legend=dict(orientation="h", y=1.06),
    )
    fig.update_xaxes(gridcolor="#d8d8d0")
    fig.write_html(str(OUT / "player_pct.html"), full_html=True, include_plotlyjs="cdn")
    print("  wrote static/nba/player_pct.html")


def main():
    sal_cap = get_sal_cap_df()
    print(f"Salary cap: {len(sal_cap)} seasons")

    print("Fetching player contracts from basketball-reference...")
    contracts = fetch_player_contracts()
    print(f"  {len(contracts)} players, columns: {list(contracts.columns)}")

    chart_salary_cap(sal_cap)
    chart_pct_change(sal_cap)
    chart_player_pct(contracts, sal_cap)
    print("Done.")


if __name__ == "__main__":
    main()
