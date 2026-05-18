"""
EDA + aggregation for EMBER site.

Reads raw JSON from ArcGIS HBB feature service + BOM region time-series txt,
writes clean CSV inputs for Vega-Lite.

Run from repo root:
    python scripts/eda.py
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "site" / "data" / "raw"
OUT = ROOT / "site" / "data"

STATE_NAME = {
    "WA (Western Australia)": "Western Australia",
    "NT (Northern Territory)": "Northern Territory",
    "QLD (Queensland)": "Queensland",
    "NSW (New South Wales)": "New South Wales",
    "VIC (Victoria)": "Victoria",
    "SA (South Australia)": "South Australia",
    "TAS (Tasmania)": "Tasmania",
    "ACT (Australian Capital Territory)": "Australian Capital Territory",
}
STATE_SHORT = {
    "Western Australia": "WA",
    "Northern Territory": "NT",
    "Queensland": "QLD",
    "New South Wales": "NSW",
    "Victoria": "VIC",
    "South Australia": "SA",
    "Tasmania": "TAS",
    "Australian Capital Territory": "ACT",
}

BOM_REGIONS = ["aus", "nsw", "vic", "qld", "wa", "sa", "tas", "nt"]


# ---------- helpers ----------
def load_arcgis(path: Path) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = [f["attributes"] for f in payload.get("features", [])]
    return pd.DataFrame(rows)


def load_bom(path: Path) -> pd.DataFrame:
    """BOM raw txt: each line 'YYYYMMYYYYMM value'. Returns year, value."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or not line[0].isdigit():
            continue
        parts = re.split(r"\s+", line)
        if len(parts) < 2:
            continue
        period, val = parts[0], parts[1]
        year = int(period[:4])
        # season 1202 (DJF) -> start year is the December year, so DJF labelled by Jan year
        if period[4:6] == "12":
            year += 1
        try:
            v = float(val)
        except ValueError:
            continue
        rows.append({"year": year, "value": v})
    return pd.DataFrame(rows).drop_duplicates("year").sort_values("year").reset_index(drop=True)


# ---------- 1. Fires by state since 2000 (choropleth + rank) ----------
def fires_state():
    df = load_arcgis(RAW / "hbb_by_state_since2000.json")
    df["state"] = df["state"].map(STATE_NAME).fillna(df["state"])
    df["burnt_area_km2"] = (df["sum_ha"] / 100).round(0).astype(int)
    df = df[["state", "burnt_area_km2", "n_fires"]].sort_values("burnt_area_km2", ascending=False)
    df.to_csv(OUT / "fires_state.csv", index=False)
    print("fires_state.csv", df.shape)
    return df


# ---------- 2. Annual burnt area 1950-2024 ----------
def fires_annual():
    df = load_arcgis(RAW / "hbb_annual.json")
    df = df.rename(columns={"EXPR_1": "year"})
    df["burnt_area_km2"] = (df["sum_ha"] / 100).round(0).astype(int)
    df = df[df["year"].between(1950, 2024)].sort_values("year")
    out = df[["year", "burnt_area_km2", "n_fires"]]
    out.to_csv(OUT / "fires_annual.csv", index=False)
    print("fires_annual.csv", out.shape)
    return out


# ---------- 3. Fires per month ----------
def fires_month():
    """Use area_ha (not count) — count is biased by data-entry artifacts on quarter boundaries."""
    df = load_arcgis(RAW / "hbb_month.json")
    df = df.rename(columns={"EXPR_1": "month_num"})
    df = df[df["month_num"].between(1, 12)].copy()
    df["month"] = pd.to_datetime(df["month_num"].astype(str) + "-01-2020", format="%m-%d-%Y").dt.strftime("%b")
    df["burnt_area_km2"] = (df["sum_ha"] / 100).round(0).astype(int)
    df = df[["month_num", "month", "burnt_area_km2", "n_fires"]].sort_values("month_num")
    df.to_csv(OUT / "fires_month.csv", index=False)
    print("fires_month.csv", df.shape)
    return df


# ---------- 4. Cause split ----------
def fires_cause():
    df = load_arcgis(RAW / "hbb_cause.json")
    df = df.rename(columns={"ignition_cause": "cause", "n_fires": "count"})
    # collapse to 4 buckets
    def bucket(c):
        if not isinstance(c, str):
            return "Unknown"
        s = c.strip().lower()
        if s == "" or "undetermined" in s or "unknown" in s or "not determined" in s or s == "other":
            return "Unknown"
        if "lightning" in s or "natural" in s:
            return "Lightning"
        if "prescribed" in s or "planned" in s or "fuel reduction" in s or "burn-off" in s or "burnoff" in s:
            return "Prescribed"
        # Incendiary (arson), Accidental, Escape, Re-ignition → Human
        return "Human"
    df["cause_bucket"] = df["cause"].apply(bucket)
    agg = df.groupby("cause_bucket", as_index=False)["count"].sum()
    agg = agg.rename(columns={"cause_bucket": "cause"})
    total = agg["count"].sum()
    agg["share"] = (agg["count"] / total).round(4)
    order = {"Lightning": 0, "Human": 1, "Prescribed": 2, "Unknown": 3}
    agg["sort"] = agg["cause"].map(order)
    agg = agg.sort_values("sort").drop(columns="sort")
    agg.to_csv(OUT / "fires_cause.csv", index=False)
    print("fires_cause.csv", agg.shape)
    return agg


# ---------- 5. Cause over time (stacked area) ----------
def cause_yearly():
    df = load_arcgis(RAW / "hbb_cause_year.json")
    df = df.rename(columns={"ignition_cause": "cause", "EXPR_1": "year", "n_fires": "count"})
    def bucket(c):
        if not isinstance(c, str):
            return "Unknown"
        s = c.strip().lower()
        if s == "" or "undetermined" in s or "unknown" in s or "not determined" in s or s == "other":
            return "Unknown"
        if "lightning" in s or "natural" in s:
            return "Lightning"
        if "prescribed" in s or "planned" in s or "fuel reduction" in s or "burn-off" in s or "burnoff" in s:
            return "Prescribed"
        # Incendiary (arson), Accidental, Escape, Re-ignition → Human
        return "Human"
    df["cause"] = df["cause"].apply(bucket)
    agg = df.groupby(["year", "cause"], as_index=False)["count"].sum()
    agg = agg[agg["year"].between(1990, 2024)]
    agg.to_csv(OUT / "cause_yearly.csv", index=False)
    print("cause_yearly.csv", agg.shape)
    return agg


# ---------- 6. State by year (small multiples + state-decade) ----------
def state_year():
    df = load_arcgis(RAW / "hbb_state_year.json")
    df = df.rename(columns={"EXPR_1": "year", "state": "state_long"})
    df["state"] = df["state_long"].map(STATE_NAME).map(STATE_SHORT).fillna(df["state_long"])
    df["burnt_area_km2"] = (df["sum_ha"] / 100).round(0).astype(int)
    df["decade"] = (df["year"] // 10) * 10
    df = df[df["state"].isin(["NSW", "VIC", "QLD", "WA", "SA", "TAS"])]

    state_year_csv = df[["state", "year", "burnt_area_km2"]].sort_values(["state", "year"])
    state_year_csv.to_csv(OUT / "state_year.csv", index=False)

    decade = df.groupby(["state", "decade"], as_index=False)["burnt_area_km2"].sum()
    # add peak flag per state
    decade["is_peak"] = decade.groupby("state")["burnt_area_km2"].transform(lambda s: s == s.max())
    decade.to_csv(OUT / "state_decade.csv", index=False)
    print("state_decade.csv", decade.shape)
    return decade


# ---------- 7. BOM temperatures + rainfall ----------
def bom_climate():
    region_full = {
        "aus": "Australia",
        "nsw": "New South Wales",
        "vic": "Victoria",
        "qld": "Queensland",
        "wa": "Western Australia",
        "sa": "South Australia",
        "tas": "Tasmania",
        "nt": "Northern Territory",
    }
    rows = []
    for r in BOM_REGIONS:
        for var in ["tmean", "rain"]:
            for season, label in [("0112", "annual"), ("1202", "djf")]:
                path = RAW / f"bom_{var}_{r}_{season}.txt"
                if not path.exists():
                    continue
                tmp = load_bom(path)
                tmp["region"] = region_full[r]
                tmp["variable"] = var
                tmp["season"] = label
                rows.append(tmp)
    big = pd.concat(rows, ignore_index=True)
    big.to_csv(OUT / "bom_long.csv", index=False)
    print("bom_long.csv", big.shape)
    return big


# ---------- 8. Summer temp vs annual fires (scatter) ----------
def temp_vs_fires(annual_fires: pd.DataFrame, climate: pd.DataFrame):
    djf_temp = climate[(climate["region"] == "Australia") &
                       (climate["variable"] == "tmean") &
                       (climate["season"] == "djf")].rename(columns={"value": "temp_anom_djf"})
    merged = annual_fires.merge(djf_temp[["year", "temp_anom_djf"]], on="year", how="inner")
    merged["fires"] = merged["n_fires"]
    merged = merged[merged["year"].between(1990, 2024)]
    merged[["year", "temp_anom_djf", "fires", "burnt_area_km2"]].to_csv(OUT / "temp_vs_fires.csv", index=False)
    print("temp_vs_fires.csv", merged.shape)
    return merged


# ---------- 9. Rainfall deficit vs burnt area (connected scatter) ----------
def rain_fires(annual_fires: pd.DataFrame, climate: pd.DataFrame):
    rain = climate[(climate["region"] == "Australia") &
                   (climate["variable"] == "rain") &
                   (climate["season"] == "annual")].copy()
    # deficit vs 30-yr mean (1961-1990)
    base = rain[rain["year"].between(1961, 1990)]["value"].mean()
    rain["rain_deficit_mm"] = (rain["value"] - base).round(1)
    merged = annual_fires.merge(rain[["year", "rain_deficit_mm"]], on="year", how="inner")
    merged = merged[merged["year"].between(1990, 2024)]
    merged["decade"] = (merged["year"] // 10) * 10
    merged[["year", "decade", "rain_deficit_mm", "burnt_area_km2"]].to_csv(OUT / "rain_fires.csv", index=False)
    print("rain_fires.csv", merged.shape)
    return merged


# ---------- 10. Bivariate state map (freq x temp anomaly) ----------
def state_bivariate(state_csv: pd.DataFrame, climate: pd.DataFrame):
    # Use cumulative fires/km2 since 2000 to bin frequency
    s = state_csv.copy()
    s["freq_bin"] = pd.qcut(s["n_fires"], 3, labels=["low", "med", "high"]).astype(str)

    # DJF temp anomaly recent (2000-2024) mean per state
    recent = climate[(climate["variable"] == "tmean") & (climate["season"] == "djf")]
    recent = recent[recent["year"].between(2000, 2024)]
    anom = recent.groupby("region", as_index=False)["value"].mean().rename(columns={"value": "temp_anom_djf"})
    s = s.merge(anom, left_on="state", right_on="region", how="left")
    s["temp_bin"] = pd.qcut(s["temp_anom_djf"].fillna(s["temp_anom_djf"].median()), 3, labels=["cool", "med", "hot"]).astype(str)
    fmap = {"low": 1, "med": 2, "high": 3}
    tmap = {"cool": 1, "med": 2, "hot": 3}
    s["bin"] = s["freq_bin"].map(fmap).astype(str) + "-" + s["temp_bin"].map(tmap).astype(str)
    out = s[["state", "freq_bin", "temp_bin", "bin", "n_fires", "temp_anom_djf"]]
    out.to_csv(OUT / "state_bivariate.csv", index=False)
    print("state_bivariate.csv", out.shape)
    return out


# ---------- 11. Top-10 fires ----------
def top10_fires():
    """Pull a larger pool, dedup by (name, year, state), drop unnamed-no-date rows."""
    df = load_arcgis(RAW / "hbb_top20.json")
    df["state"] = df["state"].map(STATE_NAME).map(STATE_SHORT).fillna(df["state"])
    df["year"] = pd.to_datetime(df["ignition_date"], unit="ms", errors="coerce").dt.year
    df["burnt_area_km2"] = (df["area_ha"] / 100).round(0).astype(int)
    df["name"] = df["fire_name"].fillna("").str.title().str.strip()
    df = df[df["name"] != ""]
    df = df[df["year"].notna()].copy()
    df["year"] = df["year"].astype(int)
    # dedup: same (name, year, state) → keep largest polygon area
    df = df.sort_values("burnt_area_km2", ascending=False).drop_duplicates(["name", "year", "state"])
    out = df.head(10).sort_values("burnt_area_km2", ascending=False)
    out = out[["name", "state", "year", "burnt_area_km2", "ignition_cause"]]
    out.to_csv(OUT / "top10_fires.csv", index=False)
    print("top10_fires.csv", out.shape)
    return out


# ---------- 12. Black Summer daily calendar ----------
def black_summer_daily():
    df = load_arcgis(RAW / "hbb_blacksummer_daily.json")
    df["date"] = pd.to_datetime(df["ignition_date"], unit="ms")
    daily = df.groupby(df["date"].dt.date).agg(count=("n_fires", "sum"), area_ha=("sum_ha", "sum")).reset_index()
    daily.columns = ["date", "count", "area_ha"]
    daily["burnt_area_km2"] = (daily["area_ha"] / 100).round(1)

    # Fill missing days with 0
    full = pd.DataFrame({"date": pd.date_range("2019-07-01", "2020-03-31").date})
    daily = full.merge(daily, on="date", how="left").fillna({"count": 0, "burnt_area_km2": 0})
    daily["date"] = pd.to_datetime(daily["date"])
    daily["weekday"] = daily["date"].dt.day_name().str[:3]
    daily["week"] = ((daily["date"] - pd.Timestamp("2019-07-01")) // pd.Timedelta(days=7)).astype(int) + 1
    daily["month"] = daily["date"].dt.strftime("%b %Y")
    out = daily[["date", "week", "weekday", "month", "count", "burnt_area_km2"]]
    out.to_csv(OUT / "calendar_blacksummer.csv", index=False)
    print("calendar_blacksummer.csv", out.shape)
    return out


# ---------- 13. KPI scalars ----------
def kpis(state_df: pd.DataFrame, annual_df: pd.DataFrame):
    total_km2 = int(state_df["burnt_area_km2"].sum())
    total_fires = int(state_df["n_fires"].sum())
    # Homes destroyed in Black Summer — reference: Royal Commission 2020
    homes = 3094
    payload = {
        "area": f"{total_km2:,}",
        "count": f"{total_fires:,}",
        "homes": f"{homes:,}",
    }
    (OUT / "kpis.json").write_text(json.dumps(payload, indent=2))
    print("kpis.json", payload)


def main():
    state_df = fires_state()
    annual_df = fires_annual()
    fires_month()
    fires_cause()
    cause_yearly()
    state_year()
    climate = bom_climate()
    temp_vs_fires(annual_df, climate)
    rain_fires(annual_df, climate)
    state_bivariate(state_df, climate)
    top10_fires()
    black_summer_daily()
    kpis(state_df, annual_df)
    print("Done.")


if __name__ == "__main__":
    main()
