"""Chargement et nettoyage des données AgriTadla-DSS (100 % local)."""
from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent

TRAITS = ["besoin_eau", "tolerance_secheresse", "fixe_azote",
          "racines_profondes", "tolerance_gel"]
NDVI_COL = "MOD13Q1_061__250m_16_days_NDVI"
NDVI_FILL_BELOW = -0.2          # MODIS fill = -3000 * 0.0001 = -0.3
SEASONS = {12: "Hiver", 1: "Hiver", 2: "Hiver", 3: "Printemps", 4: "Printemps",
           5: "Printemps", 6: "Été", 7: "Été", 8: "Été", 9: "Automne",
           10: "Automne", 11: "Automne"}


def _find(pattern: str) -> Path:
    hits = sorted(ROOT.glob(pattern))
    if not hits:
        raise FileNotFoundError(f"Fichier introuvable dans {ROOT} : {pattern}")
    return hits[0]


# ----------------------------------------------------------------- NASA POWER
def load_power(source=None) -> pd.DataFrame:
    """Lit le CSV NASA POWER. L'en-tête (jusqu'à -END HEADER-) est détecté
    automatiquement (17 lignes dans votre fichier) puis ignoré."""
    if source is None:
        source = _find("POWER_Point_Daily_*.csv")
    if hasattr(source, "read"):
        raw = source.read()
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    else:
        text = Path(source).read_text(encoding="utf-8")
    lines = text.splitlines()
    skip = next((i + 1 for i, l in enumerate(lines) if "-END HEADER-" in l), 0)
    df = pd.read_csv(io.StringIO("\n".join(lines[skip:])))
    df = df.replace(-999, np.nan)
    df["DATE"] = pd.to_datetime(df["YEAR"].astype(str), format="%Y") + \
        pd.to_timedelta(df["DOY"] - 1, unit="D")
    df["MONTH"] = df["DATE"].dt.month
    df["SEASON"] = df["MONTH"].map(SEASONS)
    return df.sort_values("DATE").reset_index(drop=True)


# ---------------------------------------------------------------------- CROPS
def load_crops(source=None) -> pd.DataFrame:
    """Lit crops.xlsx. Gère le cas où toute la ligne est dans une seule
    colonne séparée par des virgules (cas de votre fichier)."""
    if source is None:
        source = _find("crops.xlsx")
    raw = pd.read_excel(source, header=None, dtype=str)
    if raw.shape[1] == 1:
        parts = raw.iloc[:, 0].str.split(",", expand=True)
        parts.columns = [c.strip() for c in parts.iloc[0]]
        df = parts.iloc[1:].reset_index(drop=True)
    else:
        df = raw.iloc[1:].copy()
        df.columns = [str(c).strip() for c in raw.iloc[0]]
        df = df.reset_index(drop=True)
    for c in TRAITS:
        df[c] = df[c].astype(int)
    df["culture"] = df["culture"].str.strip()
    return df


# ----------------------------------------------------------------------- NDVI
def load_ndvi(source=None) -> pd.DataFrame | None:
    """CSV AppEEARS MOD13Q1 -> colonnes Date, NDVI (fill values retirés)."""
    if source is None:
        hits = sorted(ROOT.glob("*MOD13Q1*results.csv"))
        if not hits:
            return None
        source = hits[0]
    df = pd.read_csv(source)
    col = NDVI_COL if NDVI_COL in df.columns else next(
        (c for c in df.columns if c.endswith("NDVI")), None)
    if col is None or "Date" not in df.columns:
        raise ValueError("Le CSV NDVI doit contenir 'Date' et une colonne *_NDVI.")
    out = pd.DataFrame({"Date": pd.to_datetime(df["Date"]),
                        "NDVI": pd.to_numeric(df[col], errors="coerce")})
    out.loc[out["NDVI"] < NDVI_FILL_BELOW, "NDVI"] = np.nan
    return out.dropna().sort_values("Date").reset_index(drop=True)


def bare_soil_months(ndvi: pd.DataFrame | None, threshold: float = 0.2) -> float:
    """Nombre moyen de mois/an où NDVI < seuil (fraction de composites ×12,
    moyennée sur les années complètes)."""
    if ndvi is None or ndvi.empty:
        return 0.0
    d = ndvi.assign(year=ndvi["Date"].dt.year, bare=ndvi["NDVI"] < threshold)
    full = d.groupby("year").filter(lambda g: len(g) >= 20)
    if full.empty:
        full = d
    return float(full.groupby("year")["bare"].mean().mean() * 12)


# ------------------------------------------------------------ INDICATEURS CLIMAT
def annual_climate(power: pd.DataFrame) -> pd.DataFrame:
    """Indicateurs par année civile COMPLÈTE (2014 et 2026 sont partielles)."""
    d = power.assign(year=power["YEAR"])
    g = d.groupby("year")
    cols = {
        "n_jours": g.size(),
        "precip_mm": g["PRECTOTCORR"].sum(),
        "gwetroot": g["GWETROOT"].mean(),
        "jours_chaleur_35": g["T2M_MAX"].apply(lambda s: int((s > 35).sum())),
        "jours_gel": g["T2M_MIN"].apply(lambda s: int((s < 0).sum())),
    }
    if "T2M" in power.columns:
        cols["t2m_moy"] = g["T2M"].mean()
    if "ALLSKY_SFC_SW_DWN" in power.columns:
        cols["irradiance"] = g["ALLSKY_SFC_SW_DWN"].mean()
    out = pd.DataFrame(cols)
    out["complete"] = out["n_jours"] >= 360
    return out


def climate_summary(power: pd.DataFrame, thr_dry: float = 350.0) -> dict:
    ann = annual_climate(power)
    full = ann[ann["complete"]]
    seas = power.groupby("SEASON")["GWETROOT"].mean()
    irr = float(power["ALLSKY_SFC_SW_DWN"].mean()) if "ALLSKY_SFC_SW_DWN" in power.columns else 0.0
    return {
        "annual": ann,
        "precip_mean": float(full["precip_mm"].mean()),
        "precip_min": float(full["precip_mm"].min()),
        "precip_min_year": int(full["precip_mm"].idxmin()),
        "dry_years": [int(y) for y in full.index[full["precip_mm"] < thr_dry]],
        "n_full_years": int(len(full)),
        "gwetroot_mean": float(power["GWETROOT"].mean()),
        "gwetroot_season": seas.to_dict(),
        "heat_days_mean": float(full["jours_chaleur_35"].mean()),
        "frost_days_mean": float(full["jours_gel"].mean()),
        "tmax_abs": float(power["T2M_MAX"].max()),
        "tmin_abs": float(power["T2M_MIN"].min()),
        "t2m_mean": float(power["T2M"].mean()),
        "irradiance_mean": irr,
    }
