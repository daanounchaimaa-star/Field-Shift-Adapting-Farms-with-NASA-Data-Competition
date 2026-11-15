"""Moteur multicritère (MCDA) : climat + traits agronomiques + labo + NDVI.

Tous les scores sont sur 10. Les règles sont volontairement simples et
transparentes pour pouvoir être expliquées (XAI) et recalibrées.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations_with_replacement

import numpy as np
import pandas as pd

# Plages de pH tolérées — HYPOTHÈSES agronomiques génériques
# Sols du Tadla : généralement calcaires/tirs (pH 7.5 - 8.2).
PH_RANGE = {
    "blé": (6.0, 8.2),
    "betterave": (6.5, 8.5),
    "oignon": (6.0, 7.8),
    "carotte": (6.0, 7.8),
    "fève": (6.0, 8.2),
}
N_LEVELS = {"Faible": 1.0, "Moyen": 0.5, "Élevé": 0.0}   # déficit en azote

PRESET_ROTATIONS = {
    "Enrichissement": ["blé", "fève", "betterave"],
    "Maraîchère diversifiée": ["fève", "carotte", "blé"],
    "Économe en eau": ["blé", "fève", "oignon"],
    "Monoculture (témoin)": ["blé", "blé", "blé"],
}


@dataclass
class Lab:
    ph: float = 7.8
    azote: str = "Moyen"          # Faible / Moyen / Élevé
    phosphore: str = "Moyen"      # Faible / Moyen / Élevé
    potassium: str = "Moyen"      # Faible / Moyen / Élevé
    matiere_organique: float = 1.5  # %
    texture: str = "Argilo-limoneux / Tirs"
    is_lab_mode: bool = True       # True if Service A, False if Service B (IA & Datasets)
    service_label: str = "Service A (Phygital Labo)"


@dataclass
class Result:
    rotation: list
    name: str
    s_eau: float
    s_sol: float
    score: float
    details: dict = field(default_factory=dict)


def _clip(x, lo=0.0, hi=1.0):
    return float(min(hi, max(lo, x)))


def dryness_index(clim: dict) -> float:
    """0 = climat humide, 1 = très sec (précipitations + humidité racinaire)."""
    p_dry = _clip((500 - clim["precip_mean"]) / 300)
    g_dry = _clip((0.5 - clim["gwetroot_mean"]) / 0.3)
    return 0.7 * p_dry + 0.3 * g_dry


def frost_index(clim: dict) -> float:
    return _clip(clim["frost_days_mean"] / 15)


def crop_water_score(c: pd.Series, clim: dict) -> float:
    """Résilience hydro-climatique d'une culture (0-10)."""
    dry = dryness_index(clim)
    a = 0.3 + 0.5 * dry                       # poids du besoin en eau
    eau = (1 - a) * c.tolerance_secheresse / 5 + a * (5 - c.besoin_eau) / 5
    gel = 1 - frost_index(clim) * (1 - c.tolerance_gel / 5)
    return 10 * (0.75 * eau + 0.25 * gel)


def _ph_fit(crop: str, ph: float) -> float:
    lo, hi = PH_RANGE.get(crop, (6.0, 8.0))
    if lo <= ph <= hi:
        return 1.0
    return _clip(1 - 0.5 * (lo - ph if ph < lo else ph - hi))


def evaluate(rotation: list, crops: pd.DataFrame, clim: dict, lab: Lab,
             bare_months: float, w_eau: float = 0.5, name: str = "",
             priorite: str = "Économie d'eau") -> Result:
    cs = crops.set_index("culture")
    rows = [cs.loc[c].rename(c) for c in rotation]
    n_def = N_LEVELS.get(lab.azote, 0.5)

    # ---- Axe 1 : eau & climat
    per_crop_eau = [crop_water_score(r, clim) for r in rows]
    s_eau = float(np.mean(per_crop_eau))

    # ---- Axe 2 : sol
    fix_total = sum(r.fixe_azote for r in rows)
    n_term = _clip(fix_total / 5)                       # une fève = 100 %
    n_score = 10 * (n_term * (0.5 + 0.5 * n_def)
                    + (1 - n_term) * 0.3 * (1 - n_def))
    roots = np.mean([r.racines_profondes for r in rows]) / 5
    if "tirs" in lab.texture.lower() or "argil" in lab.texture.lower():
        roots = _clip(roots * 1.15)                      # sols lourds : bonus
    roots_score = 10 * roots

    fams = [r.famille for r in rows]
    n_distinct = len(set(fams))
    div_score = 10 * (n_distinct - 1) / 2
    consecutive = sum(1 for a, b in zip(fams, fams[1:]) if a == b)
    div_score = max(0.0, div_score - 2.5 * consecutive)

    ph_score = 10 * np.mean([_ph_fit(c, lab.ph) for c in rotation])
    mo_bonus = 0.0
    if lab.matiere_organique < 1.5:  # sol pauvre en MO -> légumineuses/racines utiles
        mo_bonus = 1.0 * n_term + 0.5 * roots

    # Pondération spécifique selon le service choisi
    if lab.is_lab_mode:
        # Service A : Analyse labo in-situ certifiée
        s_sol_raw = (0.35 * n_score + 0.25 * roots_score + 0.25 * div_score
                     + 0.15 * ph_score + mo_bonus)
        ndvi_malus = min(2.0, bare_months * 0.5)
    else:
        # Service B : IA & Datasets historiques (poids renforcé sur le NDVI et la structure)
        s_sol_raw = (0.30 * n_score + 0.30 * roots_score + 0.25 * div_score
                     + 0.15 * ph_score + mo_bonus)
        ndvi_malus = min(2.5, bare_months * 0.6)

    s_sol = float(_clip(min(s_sol_raw, 10.0) - ndvi_malus, 0, 10))

    # Bonus de productivité si "Priorité au rendement"
    yield_bonus = 0.0
    if priorite == "Priorité au rendement":
        if "betterave" in rotation:
            yield_bonus += 0.6  # culture industrielle phare à très haute biomasse / marge
        if "carotte" in rotation:
            yield_bonus += 0.4  # valorisation maraîchère à fort rendement
        if "fève" in rotation and "betterave" in rotation:
            yield_bonus += 0.4  # synergie fertilisation azotée -> booster de rendement betterave

    # pénalité sanitaire globale : même famille deux années de suite
    rep_penalty = 1.5 * consecutive
    score = float(_clip(w_eau * s_eau + (1 - w_eau) * s_sol - rep_penalty + yield_bonus, 0.0, 10.0))
    return Result(
        rotation=rotation, name=name or " → ".join(rotation),
        s_eau=round(s_eau, 2), s_sol=round(s_sol, 2), score=round(score, 2),
        details=dict(n_score=n_score, roots_score=roots_score,
                     div_score=div_score, ph_score=ph_score, mo_bonus=mo_bonus,
                     ndvi_malus=ndvi_malus, fix_total=fix_total,
                     yield_bonus=yield_bonus,
                     per_crop_eau=dict(zip(rotation, per_crop_eau)),
                     n_distinct=n_distinct, consecutive=consecutive, rep_penalty=rep_penalty,
                     dryness=dryness_index(clim), frost=frost_index(clim),
                     is_lab_mode=lab.is_lab_mode, priorite=priorite),
    )


def rank(crops: pd.DataFrame, clim: dict, lab: Lab, bare_months: float,
         w_eau: float, explore_all: bool = False,
         priorite: str = "Économie d'eau") -> pd.DataFrame:
    if explore_all:
        names = list(crops["culture"])
        rots = [(" → ".join(r), list(r))
                for r in combinations_with_replacement(names, 3)]
    else:
        rots = [(n, r) for n, r in PRESET_ROTATIONS.items()
                if all(c in set(crops["culture"]) for c in r)]
    res = [evaluate(r, crops, clim, lab, bare_months, w_eau, n, priorite=priorite) for n, r in rots]

    def get_advantage(r: Result) -> str:
        if r.details["consecutive"] > 0:
            return "⚠️ Monoculture (fort risque sanitaire & épuisement)"
        if "fève" in r.rotation and "betterave" in r.rotation:
            return "🌱 Fixation N, Décompactage Tirs & Rendement industriel"
        if "fève" in r.rotation and "carotte" in r.rotation:
            return "🥕 Diversification maraîchère & Rupture cycles ravageurs"
        if "oignon" in r.rotation:
            return "💧 Sobriété hydrique & Haute valeur commerciale"
        return "Équilibre agronomique régional"

    df = pd.DataFrame([{
        "Rotation": r.name,
        "Séquence (3 ans)": " → ".join([c.capitalize() for c in r.rotation]),
        "Score Global /10": r.score,
        "Score Eau /10": r.s_eau,
        "Score Sol /10": r.s_sol,
        "Bénéfice Clé": get_advantage(r),
        "_res": r} for r in res])
    df = df.sort_values("Score Global /10", ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    return df


def explain(best: Result, worst: Result, clim: dict, lab: Lab,
            bare_months: float, w_eau: float,
            priorite: str = "Économie d'eau") -> str:
    d = best.details
    L = []

    # En-tête de recommandation
    if lab.is_lab_mode:
        L.append("🔬 **Service A (Phygital Labo)** : Recommandation calibrée sur vos analyses de sol en laboratoire et le climat local du Tadla.")
    else:
        L.append("🤖 **Service B (IA & Datasets)** : Recommandation générée par les modèles d'apprentissage à partir de 12 ans d'historique NASA POWER, MODIS NDVI et du référentiel pédologique ORMVAT Tadla.")

    L.append(f"### 🏆 Proposition Optimale N°1 : {best.name} ({' → '.join([c.capitalize() for c in best.rotation])})")
    L.append(f"Cette séquence obtient la meilleure note avec un **Score Global de {best.score}/10** (Sous-score Eau : **{best.s_eau}/10**, Sous-score Sol : **{best.s_sol}/10**).")

    # Diagnostic Climat Tadla
    irr_txt = f", irradiance moyenne {clim['irradiance_mean']:.1f} MJ/m²/j" if "irradiance_mean" in clim and clim["irradiance_mean"] > 0 else ""
    L.append(f"**Diagnostic Climatique de la Parcelle :**\n"
             f"- Précipitations annuelles moyennes : **{clim['precip_mean']:.0f} mm/an** ({clim['n_full_years']} années complètes analysées), avec un minimum de **{clim['precip_min']:.0f} mm** enregistré en {clim['precip_min_year']}.\n"
             f"- Humidité racinaire du sol (`GWETROOT`) moyenne : **{clim['gwetroot_mean']:.2f}**.\n"
             f"- Stress thermique : **{clim['heat_days_mean']:.0f} jours/an** avec $T_{{max}} > 35$ °C et **{clim['frost_days_mean']:.1f} jours de gel/an**.\n"
             f"- Indice global de sécheresse calculé : **{d['dryness']:.2f}/1.0**{irr_txt}.")

    if clim["dry_years"]:
        L.append(f"⚠️ **Années déficitaires historiques (< 350 mm)** : {', '.join(map(str, clim['dry_years']))}. La stratégie intègre une résilience face aux sécheresses récurrentes.")

    # Analyse Eau & Tolérance
    thirsty = [c for c in best.rotation if c == "betterave"]
    if thirsty and d["dryness"] > 0.2:
        L.append("💧 **Gestion de l'eau :** La betterave (besoin hydrique 4/5) assure une rentabilité économique élevée mais nécessite de piloter l'irrigation d'appoint en période de déficit printanier.")
    frost_sens = [c for c in best.rotation if c == "oignon"]
    if frost_sens and clim["frost_days_mean"] >= 2:
        L.append(f"❄️ **Tolérance gel :** L'oignon (tolérance gel 1/5) demande une vigilance lors des nuits hivernales froides ({clim['frost_days_mean']:.1f} j de gel en moyenne dans la plaine).")

    # Analyse Sol, Azote et Structure
    if d["fix_total"] > 0:
        if lab.azote == "Faible":
            L.append("🌱 **Fertilité Azotée :** L'azote disponible est **faible**. L'insertion de la fève (légumineuse fixatrice, note 5/5) enrichit le sol en azote symbiotique et réduit significativement les intrants de synthèse.")
        elif lab.azote == "Moyen":
            L.append("🌱 **Fertilité Azotée :** L'azote du sol est **moyen**. La fève stabilise le bilan azoté et améliore la matière organique.")
        else:
            L.append("🌱 **Fertilité Azotée :** L'azote du sol est satisfaisant ; la fève apporte un bénéfice de structuration et de diversification microbiologique.")
    else:
        L.append(f"⚠️ **Attention Azote :** Teneur en azote **{lab.azote.lower()}** sans légumineuse dans la rotation : prévoir une fertilisation organique complémentaire.")

    if d["roots_score"] >= 6.5:
        L.append(f"⛏️ **Enracinement & Sols Lourds :** Le système racinaire profond (score {d['roots_score']:.1f}/10) favorise le décompactage biologique naturel des sols argilo-limoneux / Tirs du Tadla ({lab.texture}).")

    # Rupture sanitaire
    if d["consecutive"] == 0:
        L.append(f"🛡️ **Rupture Sanitaire :** Alternance de {d['n_distinct']} familles botaniques distinctes sans répétition consécutive, ce qui brise le cycle des nématodes et agents pathogènes telluriques.")
    else:
        L.append(f"⚠️ **Risque Sanitaire :** {d['consecutive']} répétition(s) de la même famille consécutive, augmentant la pression des bio-agresseurs.")

    # Couverture végétale NDVI
    if bare_months > 0.5:
        L.append(f"🛰️ **Couverture Végétale (MODIS NDVI) :** {bare_months:.1f} mois/an estimés avec un NDVI < 0,20 (sol nu). Un malus de {d['ndvi_malus']:.1f} pt a été pris en compte pour inciter au maintien d'un couvert protecteur contre l'érosion éolienne et la battance.")

    # Synthèse de pondération
    if priorite == "Priorité au rendement":
        L.append(f"⚖️ **Pondération appliquée :** **Priorité au rendement et à la maximisation économique** (valorisation optimale des parcelles irriguées du Tadla). "
                 f"À titre comparatif, la rotation la moins bien classée est *{worst.name}* avec un score de **{worst.score}/10**.")
    elif priorite == "Régénération du sol":
        L.append(f"⚖️ **Pondération appliquée :** **Priorité à la régénération du sol** ({1 - w_eau:.0%} sol vs {w_eau:.0%} eau). "
                 f"À titre comparatif, la rotation la moins bien classée est *{worst.name}* avec un score de **{worst.score}/10**.")
    else:
        L.append(f"⚖️ **Pondération appliquée :** **Priorité à l'économie d'eau** ({w_eau:.0%} eau vs {1 - w_eau:.0%} sol). "
                 f"À titre comparatif, la rotation la moins bien classée est *{worst.name}* avec un score de **{worst.score}/10**.")

    return "\n\n".join(L)
