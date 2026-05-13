#!/usr/bin/env python3
"""Generate Eras Tour interactive table + chart.
Run: python3 make_eras.py
Outputs to static/eras/
"""
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).parent
OUT  = ROOT / "static" / "eras"
OUT.mkdir(parents=True, exist_ok=True)

# ── Load & clean ──────────────────────────────────────────────────────────────
df = pd.read_excel(ROOT / "content" / "data" / "tay_tay_data.xlsx")
df["Title"] = df["Title"].ffill()
df = df.dropna(subset=["Notes"])

rows = []
for _, r in df.iterrows():
    for note in str(r["Notes"]).split("\n"):
        note = note.strip()
        if not note:
            continue
        date_match = re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", note)
        if not date_match:
            continue
        date_str = date_match.group()
        location = re.sub(r"^\d{1,2}/\d{1,2}/\d{2,4}\s*-?\s*", "", note)
        location = re.sub(r"\s*\(.*?\)\s*$", "", location).strip()
        mashup_m = re.search(r"\(mashup with (.+?)\)", note)
        mashup = mashup_m.group(1) if mashup_m else ""
        try:
            parsed = pd.to_datetime(date_str, dayfirst=False)
        except Exception:
            continue
        rows.append({"Title": r["Title"], "Date": parsed,
                     "Location": location, "Mashup": mashup})

tay = pd.DataFrame(rows)
tay["Month_Year"] = tay["Date"].dt.to_period("M").dt.to_timestamp()
tay = tay.sort_values("Date")


# ── 1. Searchable table ───────────────────────────────────────────────────────
tbl = tay[["Title", "Date", "Location", "Mashup"]].copy()
tbl["Date"] = tbl["Date"].dt.strftime("%Y-%m-%d")
tbl["Mashup"] = tbl["Mashup"].fillna("")

rows_html = ""
for _, r in tbl.iterrows():
    mashup = f'<span class="mashup">{r["Mashup"]}</span>' if r["Mashup"] else ""
    rows_html += (
        f"<tr><td>{r['Title']}</td><td>{r['Date']}</td>"
        f"<td>{r['Location']}</td><td>{mashup}</td></tr>\n"
    )

table_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
<style>
  body {{ font-family: ui-monospace, monospace; font-size: 12px; margin: 0; padding: 8px; background: #f8f7f2; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ background: #d35400; color: white; }}
  td, th {{ padding: 5px 8px; }}
  tr:nth-child(even) {{ background: #f0efe8; }}
  .mashup {{ color: #666; font-style: italic; }}
  .dataTables_wrapper .dataTables_filter input {{ border: 1px solid #d8d8d0; padding: 3px 6px; }}
</style>
</head>
<body>
<table id="eras-table" class="display">
  <thead><tr><th>Song</th><th>Date</th><th>Location</th><th>Mashup</th></tr></thead>
  <tbody>{rows_html}</tbody>
</table>
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script>
  $(document).ready(function() {{
    $('#eras-table').DataTable({{
      pageLength: 15,
      order: [[1, 'asc']],
      columnDefs: [{{ targets: [1], type: 'date' }}]
    }});
  }});
</script>
</body>
</html>"""

(OUT / "table.html").write_text(table_html)
print("  wrote static/eras/table.html")


# ── 2. Frequency chart ────────────────────────────────────────────────────────
agg = (
    tay.groupby(["Title", "Month_Year", "Location"])
       .size().reset_index(name="Frequency")
)
agg["Month_Year_str"] = agg["Month_Year"].dt.strftime("%b %Y")
agg = agg.sort_values("Month_Year")

all_months = sorted(agg["Month_Year"].unique())
month_labels = [pd.Timestamp(m).strftime("%b %Y") for m in all_months]

songs = sorted(agg["Title"].unique())
fig = go.Figure()

for song in songs:
    d = agg[agg["Title"] == song]
    fig.add_trace(go.Scatter(
        x=d["Month_Year_str"],
        y=d["Frequency"],
        mode="lines+markers",
        name=song,
        text=d["Location"],
        hovertemplate="<b>%{fullData.name}</b><br>%{x}<br>Freq: %{y}<br>%{text}<extra></extra>",
        visible=(song == songs[0]),
    ))

buttons = [
    dict(label=s,
         method="update",
         args=[{"visible": [s2 == s for s2 in songs]},
               {"title": f"<b>{s}</b> — play frequency over time"}])
    for s in songs
]

fig.update_layout(
    title=f"<b>{songs[0]}</b> — play frequency over time",
    xaxis_title="Month",
    yaxis_title="Times played",
    font=dict(family="ui-monospace, monospace", size=12),
    paper_bgcolor="#f8f7f2",
    plot_bgcolor="#f8f7f2",
    updatemenus=[dict(
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0.01, xanchor="left",
        y=1.15, yanchor="top",
        bgcolor="#f0efe8",
        bordercolor="#d8d8d0",
    )],
    margin=dict(t=100, l=50, r=20, b=60),
    height=460,
)

fig.write_html(str(OUT / "chart.html"), full_html=True, include_plotlyjs="cdn")
print("  wrote static/eras/chart.html")
print("Done.")


if __name__ == "__main__":
    pass
