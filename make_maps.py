#!/usr/bin/env python3
"""Generate Folium restaurant maps for Good Eatins posts.
Run: python3 make_maps.py
Outputs to static/maps/  (picked up by build.py via static/ copy)
"""
from pathlib import Path
import pandas as pd
import folium
from folium.plugins import GroupedLayerControl

ROOT = Path(__file__).parent
MAPS_OUT = ROOT / "static" / "maps"
MAPS_OUT.mkdir(parents=True, exist_ok=True)

PALETTE = [
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00",
    "#a65628", "#f781bf", "#999999", "#66c2a5", "#fc8d62",
    "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f", "#b3b3b3",
]


MAP_HEIGHT = 600  # px — iframe CSS should be slightly taller


def make_map(xlsx_path: Path, out_path: Path, center: tuple, zoom: int):
    df = pd.read_excel(xlsx_path)
    df = df.dropna(subset=["Latitutde", "Longitude"])

    genres = df["Genre"].unique().tolist()
    color_map = {g: PALETTE[i % len(PALETTE)] for i, g in enumerate(genres)}

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="CartoDB positron",
        width="100%",
        height=MAP_HEIGHT,
    )

    # One FeatureGroup per genre so layer control works
    groups = {}
    for genre in genres:
        fg = folium.FeatureGroup(name=genre, show=True)
        groups[genre] = fg
        m.add_child(fg)

    for _, row in df.iterrows():
        dont_miss = row["Don't Miss:"]
        popup_html = (
            f"<b>{row['Name']}</b><br>"
            f"{row['Location']}<br>"
            f"<i>{row['Genre']}</i><br>"
            f"<b>Don't miss:</b> {dont_miss}"
        )
        folium.CircleMarker(
            location=[row["Latitutde"], row["Longitude"]],
            radius=8,
            color=color_map[row["Genre"]],
            fill=True,
            fill_color=color_map[row["Genre"]],
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=row["Name"],
        ).add_to(groups[row["Genre"]])

    folium.LayerControl(collapsed=False).add_to(m)
    m.save(str(out_path))
    print(f"  wrote {out_path}")


if __name__ == "__main__":
    make_map(
        ROOT / "_posts" / "2022-05-03-good-eatins" / "Eat_Data.xlsx",
        MAPS_OUT / "good-eatins-durham.html",
        center=(35.99, -78.91),
        zoom=12,
    )
    make_map(
        ROOT / "_posts" / "2023-10-20-good-eatins-toronto" / "Eat_Data.xlsx",
        MAPS_OUT / "good-eatins-toronto.html",
        center=(43.665, -79.365),
        zoom=12,
    )
    print("Done.")
