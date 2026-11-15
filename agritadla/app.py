
from __future__ import annotations

import base64
import io
from pathlib import Path

import folium
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from streamlit_folium import st_folium

import data_loader as dl
import scoring_engine as se

# -----------------------------------------------------------------------------
# Configuration de la page
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BladiNova",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Gestion du Logo BladiNova & Encodage Base64
# -----------------------------------------------------------------------------
LOGO_PATH = Path(__file__).parent / "image.png"

@st.cache_data
def get_logo_base64() -> str:
    """Charge le logo image.png et le convertit en base64 pour affichage inline."""
    if LOGO_PATH.exists():
        try:
            with open(LOGO_PATH, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""

# -----------------------------------------------------------------------------
# Initialisation de st.session_state (State Management & Arrière-Plan)
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "parcel_selected" not in st.session_state:
    st.session_state.parcel_selected = False

if "service_chosen" not in st.session_state:
    st.session_state.service_chosen = None

if "bg_theme" not in st.session_state:
    st.session_state.bg_theme = "agri_vert"

if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "email": "ahmed.tadlaoui@agri.ma",
        "name": "Ahmed El Mansouri",
        "commune": "Fquih Ben Salah (Tadla)",
        "superficie": 12.0,
        "id_agriculteur": "TADLA-AGRI-084",
    }

if "parcel_coords" not in st.session_state:
    st.session_state.parcel_coords = {
        "lat": 32.4500,
        "lon": -6.5250,
        "zone": "Périmètre central ORMVAT (Tadla)",
    }

# -----------------------------------------------------------------------------
# Styles CSS Personnalisés & Thèmes d'Arrière-Plan (BladiNova)
# -----------------------------------------------------------------------------
def get_theme_css(theme: str) -> str:
    if theme == "agri_solaire":
        return """
        .stApp {
            background-color: #fdfcf7 !important;
            background-image: 
                radial-gradient(circle at 15% 10%, rgba(217, 119, 6, 0.10) 0%, transparent 45%),
                radial-gradient(circle at 85% 25%, rgba(34, 197, 94, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 50% 90%, rgba(245, 158, 11, 0.06) 0%, transparent 50%),
                linear-gradient(175deg, #fefdf7 0%, #fef8eb 45%, #f6faf5 100%) !important;
            background-attachment: fixed !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #fefbf2 0%, #fcf4de 50%, #fbf0d4 100%) !important;
            border-right: 1px solid #fde68a !important;
        }
        """
    elif theme == "agri_douceur":
        return """
        .stApp {
            background-color: #f4fbf7 !important;
            background-image: 
                radial-gradient(circle at 20% 15%, rgba(5, 150, 105, 0.09) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(16, 185, 129, 0.07) 0%, transparent 50%),
                linear-gradient(180deg, #f0fdf4 0%, #e6f7ec 45%, #f8fafc 100%) !important;
            background-attachment: fixed !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ecfdf5 0%, #d1fae5 50%, #a7f3d0 100%) !important;
            border-right: 1px solid #a7f3d0 !important;
        }
        """
    elif theme == "agri_dark":
        return """
        .stApp {
            background-color: #111713 !important;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(212, 175, 55, 0.12) 0%, transparent 45%),
                radial-gradient(circle at 85% 85%, rgba(46, 125, 50, 0.15) 0%, transparent 50%),
                linear-gradient(165deg, #101511 0%, #162018 45%, #0d120f 100%) !important;
            background-attachment: fixed !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #141c16 0%, #0d130e 100%) !important;
            border-right: 1px solid rgba(212, 175, 55, 0.3) !important;
        }
        .main-title {
            color: #d4af37 !important;
        }
        .sub-title {
            color: #86efac !important;
        }
        """
    else:  # agri_vert (Défaut élégant)
        return """
        .stApp {
            background-color: #f7faf7 !important;
            background-image: 
                radial-gradient(circle at 10% 12%, rgba(46, 125, 50, 0.09) 0%, transparent 45%),
                radial-gradient(circle at 90% 18%, rgba(202, 138, 4, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 50% 95%, rgba(46, 125, 50, 0.06) 0%, transparent 50%),
                linear-gradient(175deg, #f8faf8 0%, #edf5ef 40%, #f4f8f4 100%) !important;
            background-attachment: fixed !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f2f8f3 0%, #e8f4eb 50%, #e0efe4 100%) !important;
            border-right: 1px solid #c8e6c9 !important;
            box-shadow: 2px 0 16px rgba(46, 125, 50, 0.06) !important;
        }
        """

st.markdown(f"""
<style>
    /* 1. Arrière-plan global */
    {get_theme_css(st.session_state.bg_theme)}
    
    [data-testid="stAppViewContainer"] {{
        background: transparent !important;
    }}
    
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* 2. Typographie */
    .main-title {{
        color: #1b5e20;
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-weight: 800;
        margin-bottom: 0.2rem;
        letter-spacing: -0.3px;
    }}
    .sub-title {{
        color: #4b6b50;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }}
    
    /* 3. Stepper horizontal épuré */
    .stepper-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.8rem;
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(10px);
        padding: 0.9rem 1.4rem;
        border-radius: 14px;
        border: 1px solid #c8e6c9;
        box-shadow: 0 4px 16px rgba(46, 125, 50, 0.07);
    }}
    .step-item {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.95rem;
        font-weight: 600;
        color: #64748b;
    }}
    .step-item.active {{
        color: #1b5e20;
        font-weight: 700;
    }}
    .step-item.done {{
        color: #2e7d32;
    }}
    .step-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #e2e8f0;
        color: #4a5568;
        font-size: 0.85rem;
        font-weight: 700;
    }}
    .step-item.active .step-badge {{
        background: #2e7d32;
        color: white;
        box-shadow: 0 0 0 4px rgba(46, 125, 50, 0.22);
    }}
    .step-item.done .step-badge {{
        background: #4caf50;
        color: white;
    }}
    .step-arrow {{
        color: #cbd5e1;
        font-size: 1.15rem;
        font-weight: bold;
    }}
    
    /* 4. Cartes de service Phygital A & B */
    .service-card {{
        border-radius: 16px !important;
        padding: 1.8rem !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.07) !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
    }}
    .service-card:hover {{
        transform: translateY(-4px) !important;
    }}
    .service-card-lab {{
        background: linear-gradient(150deg, #ffffff 0%, #f0f9ff 100%) !important;
        border: 2px solid #0284c7 !important;
        box-shadow: 0 8px 24px rgba(2, 132, 199, 0.12) !important;
    }}
    .service-card-lab:hover {{
        border-color: #0369a1 !important;
        box-shadow: 0 12px 32px rgba(2, 132, 199, 0.22) !important;
    }}
    .service-card-ai {{
        background: linear-gradient(150deg, #ffffff 0%, #faf5ff 100%) !important;
        border: 2px solid #7e22ce !important;
        box-shadow: 0 8px 24px rgba(126, 34, 206, 0.12) !important;
    }}
    .service-card-ai:hover {{
        border-color: #6b21a8 !important;
        box-shadow: 0 12px 32px rgba(126, 34, 206, 0.22) !important;
    }}
    .service-card h3 {{
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        margin-top: 0.6rem !important;
        margin-bottom: 0.8rem !important;
        line-height: 1.3 !important;
    }}
    .service-card-lab h3 {{
        color: #0369a1 !important;
    }}
    .service-card-ai h3 {{
        color: #7e22ce !important;
    }}
    .service-card p {{
        font-size: 1.02rem !important;
        line-height: 1.65 !important;
        margin-bottom: 0.65rem !important;
        color: #1e293b !important;
    }}
    .card-badge {{
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 800;
        letter-spacing: 0.3px;
        margin-bottom: 0.5rem;
    }}
    .badge-lab {{
        background: #e0f2fe !important;
        color: #0369a1 !important;
        border: 1px solid #7dd3fc !important;
    }}
    .badge-ai {{
        background: #f3e8ff !important;
        color: #7e22ce !important;
        border: 1px solid #d8b4fe !important;
    }}

    /* 5. Cartes podium */
    .podium-card {{
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .podium-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.12);
    }}
    .podium-card * {{
        color: #0f172a !important;
    }}
    .podium-gold {{
        border: 2px solid #ca8a04 !important;
        background: linear-gradient(135deg, #fef9c3 0%, #fde047 100%) !important;
    }}
    .podium-silver {{
        border: 2px solid #64748b !important;
        background: linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 100%) !important;
    }}
    .podium-bronze {{
        border: 2px solid #ea580c !important;
        background: linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%) !important;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Chargement des données locales en cache
# -----------------------------------------------------------------------------
@st.cache_data
def get_power():
    return dl.load_power()

@st.cache_data
def get_crops():
    return dl.load_crops()

try:
    power = get_power()
    crops = get_crops()
except FileNotFoundError as e:
    st.error(f"❌ {e}\n\nVeuillez vérifier que les fichiers CSV et Excel se trouvent dans le répertoire de l'application.")
    st.stop()

clim = dl.climate_summary(power)

# -----------------------------------------------------------------------------
# Composant En-Tête Marque BladiNova (Logo + Contexte Parcelle)
# -----------------------------------------------------------------------------
def render_brand_header(subtitle: str = ""):
    logo_b64 = get_logo_base64()
    logo_html = (
        f'<div style="background: linear-gradient(145deg, #18201a, #0f1411); padding: 0.35rem 0.8rem; '
        f'border-radius: 12px; border: 1.2px solid rgba(212, 175, 55, 0.45); display: flex; align-items: center; '
        f'box-shadow: 0 4px 12px rgba(0,0,0,0.15); flex-shrink: 0;">'
        f'<img src="data:image/png;base64,{logo_b64}" style="height: 44px; width: auto; object-fit: contain;" alt="BladiNova" />'
        f'</div>'
    ) if logo_b64 else ""

    sub_html = f'<div style="font-size: 0.92rem; color: #4b6b50; margin-top: 0.2rem; font-weight: 500;">{subtitle}</div>' if subtitle else ""
    user_name = st.session_state.user_info.get("name", "Ahmed El Mansouri")
    commune = st.session_state.user_info.get("commune", "Tadla")

    header_html = (
        f'<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; '
        f'margin-bottom: 1.5rem; padding: 0.85rem 1.4rem; background: rgba(255, 255, 255, 0.92); backdrop-filter: blur(10px); '
        f'border-radius: 16px; border: 1px solid #c8e6c9; box-shadow: 0 4px 18px rgba(46, 125, 50, 0.07);">'
        f'<div style="display: flex; align-items: center; gap: 1.2rem;">'
        f'{logo_html}'
        f'<div>'
        f'<div style="display: flex; align-items: center; gap: 0.6rem;">'
        f'<span style="font-size: 1.4rem; font-weight: 800; color: #1b5e20; letter-spacing: 0.3px;">BladiNova</span>'
        f'<span style="font-size: 0.8rem; color: #2e7d32; font-weight: 700; background: #e8f5e9; border: 1px solid #c8e6c9; padding: 0.15rem 0.6rem; border-radius: 10px;">DSS Phygital Tadla</span>'
        f'</div>'
        f'{sub_html}'
        f'</div>'
        f'</div>'
        f'<div style="font-size: 0.9rem; color: #334155; background: #f8fafc; padding: 0.4rem 0.9rem; border-radius: 12px; border: 1px solid #cbd5e1; font-weight: 500;">'
        f'👤 <strong>{user_name}</strong> · <span style="color: #64748b;">{commune}</span>'
        f'</div>'
        f'</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Composant Stepper de Progression
# -----------------------------------------------------------------------------
def render_stepper():
    s1 = "done" if st.session_state.logged_in else "active"
    s2 = "done" if st.session_state.parcel_selected else ("active" if st.session_state.logged_in else "")
    s3 = "done" if st.session_state.service_chosen else ("active" if st.session_state.parcel_selected else "")
    s4 = "active" if (st.session_state.logged_in and st.session_state.parcel_selected and st.session_state.service_chosen) else ""

    badge1 = "✓" if st.session_state.logged_in else "1"
    badge2 = "✓" if st.session_state.parcel_selected else "2"
    badge3 = "✓" if st.session_state.service_chosen else "3"

    html = (
        f'<div class="stepper-container">'
        f'<div class="step-item {s1}"><span class="step-badge">{badge1}</span><span>Connexion</span></div>'
        f'<span class="step-arrow">➔</span>'
        f'<div class="step-item {s2}"><span class="step-badge">{badge2}</span><span>Géolocalisation Parcelle</span></div>'
        f'<span class="step-arrow">➔</span>'
        f'<div class="step-item {s3}"><span class="step-badge">{badge3}</span><span>Choix du Service Phygital</span></div>'
        f'<span class="step-arrow">➔</span>'
        f'<div class="step-item {s4}"><span class="step-badge">4</span><span>Tableau de Bord & Décision</span></div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# =============================================================================
# ÉCRAN 1 : CONNEXION (LOGIN)
# =============================================================================
if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.8, 1])

    with col_login:
        logo_b64 = get_logo_base64()
        if logo_b64:
            login_badge = (
                f'<div style="text-align: center; margin-top: 1rem; margin-bottom: 1.5rem;">'
                f'<div style="display: inline-block; background: linear-gradient(145deg, #19201a 0%, #0e130f 100%); '
                f'padding: 1.2rem 2.4rem; border-radius: 22px; border: 1.5px solid rgba(212, 175, 55, 0.45); '
                f'box-shadow: 0 12px 32px rgba(0,0,0,0.25), 0 0 20px rgba(212, 175, 55, 0.15);">'
                f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 155px; width: auto; object-fit: contain; '
                f'filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3));" alt="BladiNova" />'
                f'</div>'
                f'<div style="margin-top: 1rem;">'
                f'<div style="font-size: 1.2rem; font-weight: 700; color: #1b5e20; letter-spacing: 0.3px;">'
                f'Système d\'Aide à la Décision Phygital'
                f'</div>'
                f'<div style="font-size: 0.92rem; color: #4b6b50; font-weight: 500; margin-top: 0.2rem;">'
                
                f'</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(login_badge, unsafe_allow_html=True)
        else:
            st.markdown('<h1 class="main-title" style="text-align: center; margin-top: 1.5rem; margin-bottom: 2rem;">🌾 BladiNova</h1>', unsafe_allow_html=True)
            
        with st.container(border=True):
            
            
            
            with st.form("login_form"):
                identifiant = st.text_input(
                    "Identifiant Agriculteur / Email",
                    value=st.session_state.user_info["email"],
                    placeholder="ex: ahmed.tadlaoui@agri.ma ou TADLA-042"
                )
                nom_agri = st.text_input(
                    "Nom de l'exploitant / Domaine",
                    value=st.session_state.user_info["name"]
                )
                commune = st.selectbox(
                    "Commune / Zone agricole Tadla",
                    [
                        "Fquih Ben Salah (Tadla)",
                        "Beni Mellal (Périmètre Ouest)",
                        "Oulad Ayad (Zone sucrière)",
                        "Souk Sebt Oulad Nemma",
                        "Kasba Tadla (Bord Oum Er-Rbia)",
                    ]
                )
                password = st.text_input("Mot de passe ou Code PIN", type="password", value="••••••••")
                superficie = st.number_input("Superficie de la parcelle (Hectares)", min_value=0.5, max_value=500.0, value=12.0, step=0.5)
                
                submitted = st.form_submit_button("Se connecter à mon espace", use_container_width=True, type="primary")
                
                if submitted:
                    st.session_state.user_info = {
                        "email": identifiant or "ahmed.tadlaoui@agri.ma",
                        "name": nom_agri or "Ahmed El Mansouri",
                        "commune": commune,
                        "superficie": superficie,
                        "id_agriculteur": "TADLA-AGRI-084",
                    }
                    st.session_state.logged_in = True
                    st.rerun()

# =============================================================================
# ÉCRAN 2 : SÉLECTION GÉOGRAPHIQUE (CARTE FOLIUM)
# =============================================================================
elif not st.session_state.parcel_selected:
    
    render_stepper()
    
    st.markdown('<h2 class="main-title">Sélection et Positionnement de la Parcelle</h2>', unsafe_allow_html=True)
    
    col_map_ctrl, col_map = st.columns([0.9, 1.1], gap="medium")
    
    current_lat = st.session_state.parcel_coords["lat"]
    current_lon = st.session_state.parcel_coords["lon"]
    
    with col_map_ctrl:
        st.subheader("Coordonnées de l'exploitation")
        st.write(f"Agriculteur connecté : **{st.session_state.user_info['name']}** ({st.session_state.user_info['commune']})")
        
        # Préréglages des secteurs agricoles du Tadla
        presets = {
            "Tadla Centre (Béni Mellal / Fquih Ben Salah) [Défaut]": (32.4500, -6.5250),
            "Périmètre irrigué d'Oulad Ayad": (32.4200, -6.6100),
            "Plaine de Souk Sebt Oulad Nemma": (32.2900, -6.7100),
            "Zone Nord Kasba Tadla (Oum Er-Rbia)": (32.5900, -6.2600),
            "Beni Mellal Ouest (Zone Tirs)": (32.3394, -6.3608),
        }
        
        selected_preset = st.selectbox("Choisir un secteur du Tadla :", list(presets.keys()))
        preset_lat, preset_lon = presets[selected_preset]
        
        # Coordonnées personnalisables
        lat_in = st.number_input("Latitude (°N)", min_value=31.5, max_value=33.5, value=float(preset_lat), step=0.001, format="%.4f")
        lon_in = st.number_input("Longitude (°W)", min_value=-7.5, max_value=-5.5, value=float(preset_lon), step=0.001, format="%.4f")
        
        st.session_state.parcel_coords["lat"] = lat_in
        st.session_state.parcel_coords["lon"] = lon_in
        st.session_state.parcel_coords["zone"] = selected_preset
        
        st.write("")
        valider = st.button("Valider la localisation de la parcelle", type="primary", use_container_width=True)
        if valider:
            st.session_state.parcel_selected = True
            st.rerun()
            
        if st.button("Retour à la connexion", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    with col_map:
        st.subheader("Carte Interactive")
        st.caption("Cliquez sur la carte ou utilisez les commandes à gauche pour ajuster l'emplacement.")
        
        # Création de la carte Folium
        m = folium.Map(
            location=[st.session_state.parcel_coords["lat"], st.session_state.parcel_coords["lon"]],
            zoom_start=11,
            tiles="OpenStreetMap"
        )
        
        # Ajout du marqueur de la parcelle
        folium.Marker(
            location=[st.session_state.parcel_coords["lat"], st.session_state.parcel_coords["lon"]],
            popup=f"Parcelle de {st.session_state.user_info['name']}<br>Lat: {st.session_state.parcel_coords['lat']} | Lon: {st.session_state.parcel_coords['lon']}",
            tooltip="Emplacement de votre parcelle",
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(m)
        
        # Zone de commande / périmètre de rayon 5km
        folium.Circle(
            location=[st.session_state.parcel_coords["lat"], st.session_state.parcel_coords["lon"]],
            radius=5000,
            color="#2e7d32",
            fill=True,
            fill_color="#81c784",
            fill_opacity=0.2,
            popup="Périmètre d'irrigation ORMVAT associé (5 km)"
        ).add_to(m)
        
        map_out = st_folium(m, height=430, use_container_width=True, returned_objects=["last_clicked"])
        if map_out and map_out.get("last_clicked"):
            c_lat = round(map_out["last_clicked"]["lat"], 4)
            c_lon = round(map_out["last_clicked"]["lng"], 4)
            if (c_lat != st.session_state.parcel_coords["lat"]) or (c_lon != st.session_state.parcel_coords["lon"]):
                st.session_state.parcel_coords["lat"] = c_lat
                st.session_state.parcel_coords["lon"] = c_lon
                st.toast(f"Coordonnées mises à jour : {c_lat}°N, {c_lon}°W")

# =============================================================================
# ÉCRAN 3 : CHOIX DU SERVICE PHYGITAL (SERVICE A vs SERVICE B)
# =============================================================================
elif st.session_state.service_chosen is None:
    
    render_stepper()
    
    st.markdown('<h2 class="main-title">Choix du Service Phygital</h2>', unsafe_allow_html=True)
    st.caption("Sélectionnez votre modalité d'accompagnement agronomique pour le périmètre du Tadla :")
    
    col_sa, col_sb = st.columns(2, gap="large")
    
    with col_sa:
        card_a = (
            '<div class="service-card service-card-lab">'
            '<div>'
            '<span class="card-badge badge-lab">🧪 Option Terrain et Laboratoire</span>'
            '<h3 style="color: #0369a1; font-size: 1.45rem; font-weight: 800; margin-top: 0.6rem; margin-bottom: 0.8rem;">Service A : Phygital Labo</h3>'
            '<p style="color: #1e293b; font-size: 1.05rem; line-height: 1.6; margin-bottom: 0.65rem;">'
            'Demande de passage d\'un agent de terrain pour prélèvement et analyses physico-chimiques certifiées du sol.'
            '</p>'
            '<p style="color: #1e293b; font-size: 1.05rem; line-height: 1.6; margin-bottom: 0.8rem;">'
            'Recommandation agronomique de haute précision calibrée sur la composition réelle de votre parcelle.'
            '</p>'
            '</div>'
            '<div>'
            '<div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.6rem; margin-bottom: 0.4rem;">'
            '<span style="font-size: 0.82rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 8px; background: rgba(3, 105, 161, 0.08); border: 1px solid rgba(3, 105, 161, 0.25); color: #0369a1;">📍 Prélèvement in situ</span>'
            '<span style="font-size: 0.82rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 8px; background: rgba(3, 105, 161, 0.08); border: 1px solid rgba(3, 105, 161, 0.25); color: #0369a1;">🔬 Analyses certifiées pH & NPK</span>'
            '<span style="font-size: 0.82rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 8px; background: rgba(3, 105, 161, 0.08); border: 1px solid rgba(3, 105, 161, 0.25); color: #0369a1;">🎯 Calibrage parcellaire réel</span>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(card_a, unsafe_allow_html=True)
        st.write("")
        if st.button("Choisir le Service A (Phygital Labo)", type="primary", use_container_width=True):
            st.session_state.service_chosen = "Service A (Phygital Labo)"
            st.rerun()

    with col_sb:
        card_b = (
            '<div class="service-card service-card-ai">'
            '<div>'
            '<span class="card-badge badge-ai">⚡ 100% Numérique et Immédiat</span>'
            '<h3 style="color: #7e22ce; font-size: 1.45rem; font-weight: 800; margin-top: 0.6rem; margin-bottom: 0.8rem;">Service B : IA & Datasets</h3>'
            '<p style="color: #1e293b; font-size: 1.05rem; line-height: 1.6; margin-bottom: 0.65rem;">'
            'Génération automatique instantanée basée sur 12 ans d\'historique agro-climatique NASA POWER et MODIS NDVI.'
            '</p>'
            '<p style="color: #1e293b; font-size: 1.05rem; line-height: 1.6; margin-bottom: 0.8rem;">'
            'Estimation pédologique selon les référentiels régionaux du Tadla, sans déplacement ni attente.'
            '</p>'
            '</div>'
            '<div>'
            '<div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.6rem; margin-bottom: 0.4rem;">'
            '<span style="font-size: 0.82rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 8px; background: rgba(126, 34, 206, 0.08); border: 1px solid rgba(126, 34, 206, 0.25); color: #7e22ce;">⏱️ Immédiat 0s</span>'
            '<span style="font-size: 0.82rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 8px; background: rgba(126, 34, 206, 0.08); border: 1px solid rgba(126, 34, 206, 0.25); color: #7e22ce;">🛰️ 12 ans NASA & MODIS</span>'
            '<span style="font-size: 0.82rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 8px; background: rgba(126, 34, 206, 0.08); border: 1px solid rgba(126, 34, 206, 0.25); color: #7e22ce;">🌐 Zéro déplacement</span>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(card_b, unsafe_allow_html=True)
        st.write("")
        if st.button("Choisir le Service B (IA & Datasets)", type="secondary", use_container_width=True):
            st.session_state.service_chosen = "Service B (IA & Datasets)"
            st.rerun()
            
    st.write("")
    if st.button("Retour à la sélection de la parcelle", use_container_width=False):
        st.session_state.parcel_selected = False
        st.rerun()

# =============================================================================
# ÉCRAN 4 : TABLEAU DE BORD & RECOMMANDATIONS
# =============================================================================
else:
    
    render_stepper()
    
    # -------------------------------------------------------------------------
    # En-tête de Navigation et Récapitulatif
    # -------------------------------------------------------------------------
    with st.container():
        c_top1, c_top2 = st.columns([2.5, 1.5])
        with c_top1:
            is_lab = (st.session_state.service_chosen == "Service A (Phygital Labo)")
            st.markdown(f"### Tableau de Bord : {st.session_state.user_info['name']}")
        with c_top2:
            st.write("")
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("🔄 Changer de Service", use_container_width=True):
                    st.session_state.service_chosen = None
                    st.rerun()
            with c_btn2:
                if st.button("🚪 Déconnexion", use_container_width=True):
                    st.session_state.logged_in = False
                    st.session_state.parcel_selected = False
                    st.session_state.service_chosen = None
                    st.rerun()

    # -------------------------------------------------------------------------
    # BARRE LATÉRALE (SIDEBAR) CONDITIONNELLE
    # -------------------------------------------------------------------------
    sb = st.sidebar
    logo_b64 = get_logo_base64()
    if logo_b64:
        sb_logo = (
            f'<div style="text-align: center; padding: 0.8rem 1rem; margin-bottom: 0.8rem; '
            f'background: linear-gradient(145deg, #18201a 0%, #0d120e 100%); border-radius: 16px; '
            f'border: 1.5px solid rgba(212, 175, 55, 0.4); box-shadow: 0 6px 18px rgba(0,0,0,0.18);">'
            f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 85px; width: auto; object-fit: contain;" alt="BladiNova" />'
            f'</div>'
        )
        sb.markdown(sb_logo, unsafe_allow_html=True)
    else:
        sb.title("🌾 BladiNova")
    sb.caption(f"📍 Tadla ({st.session_state.parcel_coords['lat']}°N, {st.session_state.parcel_coords['lon']}°W)")

    # Badge de service dans la sidebar
    if is_lab:
        sb.info("**Mode Actif : Service A (Phygital Labo)**\n")
    else:
        sb.success("**Mode Actif : Service B (IA & Datasets)**\n")

    # Choix de la Priorité Stratégique (Économie d'eau vs Régénération du sol vs Priorité au rendement)
    sb.subheader("Priorité Stratégique")
    choix_priorite = sb.radio(
        "Priorité Stratégique",
        options=["Économie d'eau", "Régénération du sol", "Priorité au rendement"],
        index=0,
        label_visibility="collapsed"
    )
    if choix_priorite == "Économie d'eau":
        w_eau = 0.75
    elif choix_priorite == "Régénération du sol":
        w_eau = 0.25
    else:  # Priorité au rendement
        w_eau = 0.45

    # AFFICHAGE CONDITIONNEL DES RÉSULTATS DE LABORATOIRE
    # Spécification stricte : Affiché UNIQUEMENT si l'agriculteur a sélectionné le Service A (Labo).
    # S'il a choisi le Service B, ces champs sont masqués et des valeurs par défaut robustes sont appliquées.
    if is_lab:
        sb.subheader("Résultats d'Analyse du Laboratoire")
        sb.caption("Saisie issue du bulletin de prélèvement terrain de l'agent :")
        lab_ph = sb.number_input("pH du sol (extrait 1:2.5)", min_value=4.0, max_value=10.0, value=7.8, step=0.1)
        lab_azote = sb.selectbox("Azote disponible (N)", ["Faible", "Moyen", "Élevé"], index=0)
        lab_phosphore = sb.selectbox("Phosphore assimilable (P)", ["Faible", "Moyen", "Élevé"], index=1)
        lab_potassium = sb.selectbox("Potassium échangeable (K)", ["Faible", "Moyen", "Élevé"], index=1)
        lab_mo = sb.number_input("Taux de Matière Organique (%)", min_value=0.0, max_value=10.0, value=1.5, step=0.1)
        lab_texture = sb.selectbox("Texture du sol", ["Argilo-limoneux / Tirs", "Limoneux", "Sableux"], index=0)

        lab = se.Lab(
            ph=lab_ph,
            azote=lab_azote,
            phosphore=lab_phosphore,
            potassium=lab_potassium,
            matiere_organique=lab_mo,
            texture=lab_texture,
            is_lab_mode=True,
            service_label="Service A (Phygital Labo)"
        )
    else:
        # En mode Service B, les champs sont masqués, valeurs par défaut robustes du Tadla appliquées
        lab = se.Lab(
            ph=7.8,
            azote="Moyen",
            phosphore="Moyen",
            potassium="Moyen",
            matiere_organique=1.5,
            texture="Argilo-limoneux / Tirs",
            is_lab_mode=False,
            service_label="Service B (IA & Datasets)"
        )
        with sb.expander("Paramètres Pédologiques Estimés (IA)", expanded=False):
            st.markdown(
                "* **Texture :** Argilo-limoneux / Tirs\n"
                "* **pH estimé :** 7.8\n"
                "* **Azote (N) :** Moyen\n"
                "* **Phosphore (P) :** Moyen\n"
                "* **Potassium (K) :** Moyen\n"
                "* **Matière Organique :** 1.5 %\n\n"
                "*(Champs de saisie laboratoire masqués en mode Service B).*"
            )

    # -------------------------------------------------------------------------
    # Traitement automatique MODIS NDVI depuis le dataset local (masqué de la sidebar)
    # -------------------------------------------------------------------------
    try:
        ndvi = dl.load_ndvi()
    except Exception:
        ndvi = None

    thr_bare = 0.20
    bare_months = dl.bare_soil_months(ndvi, thr_bare)
    explore_all = False

    # -------------------------------------------------------------------------
    # Exécution du Moteur Multicritère MCDA
    # -------------------------------------------------------------------------
    ranking = se.rank(crops, clim, lab, bare_months, w_eau, explore_all, priorite=choix_priorite)
    best_res = ranking.iloc[0]["_res"]
    worst_res = ranking.iloc[-1]["_res"]

    # -------------------------------------------------------------------------
    # ONGLETS DU TABLEAU DE BORD PRINCIPAL
    # -------------------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs([
        "Recommandations & XAI",
        "Diagnostic de la Parcelle",
        "Visualisations Interactives"
    ])

    # =========================================================================
    # ONGLET 1 : CLASSEMENT & 3 PROPOSITIONS DE ROTATION (OPTIMALES SUR 3 ANS)
    # =========================================================================
    with tab1:
        st.markdown("### Les 3 Propositions de Rotation Culturale Optimales ")
        st.write("Calculées par l'algorithme multicritère intégrant le climat NASA POWER, l'indice de sol nu NDVI et le diagnostic sol :")

        # Extraction des 3 meilleures propositions
        top3 = ranking.head(3)
        cols_podium = st.columns(3)

        podium_styles = ["podium-gold", "podium-silver", "podium-bronze"]
        podium_medals = ["1ère Proposition (Optimale)", "2ème Proposition", "3ème Proposition"]

        for idx, (_, row) in enumerate(top3.iterrows()):
            with cols_podium[idx]:
                r_obj = row["_res"]
                seq_formatted = " ➔ ".join([c.capitalize() for c in r_obj.rotation])
                podium_html = (
                    f'<div class="podium-card {podium_styles[idx]}">'
                    f'<span style="font-size: 1.05rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">{podium_medals[idx]}</span>'
                    f'<h4 style="margin: 0.6rem 0 0.4rem 0; font-size: 1.25rem; font-weight: 700;">{row["Rotation"]}</h4>'
                    f'<p style="font-size: 1.2rem; font-weight: 700; margin-bottom: 0rem;">{seq_formatted}</p>'
                    f'</div>'
                )
                st.markdown(podium_html, unsafe_allow_html=True)

        st.write("")
        logo_b64 = get_logo_base64()
        if logo_b64:
            table_header = (
                f'<div style="display: flex; align-items: center; gap: 14px; margin: 1.2rem 0 0.8rem 0; flex-wrap: wrap;">'
                f'<div style="background: linear-gradient(145deg, #18201a, #0f1411); padding: 0.35rem 0.8rem; border-radius: 12px; border: 1.2px solid rgba(212, 175, 55, 0.45); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">'
                f'<img src="data:image/png;base64,{logo_b64}" style="height: 34px; width: auto; object-fit: contain;" alt="BladiNova" />'
                f'</div>'
                f'<div>'
                f'<h4 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #1b4332;">Tableau Comparatif Détaillé des Rotations</h4>'
                f'<span style="font-size: 0.85rem; color: #555;">Évaluation multicritère et scoring agronomique certifié BladiNova</span>'
                f'</div>'
                f'</div>'
            )
        else:
            table_header = "#### 🌾 Tableau Comparatif Détaillé des Rotations"
        st.markdown(table_header, unsafe_allow_html=True)
        
        pref_cols = ["Rotation", "Séquence (3 ans)", "Séquence", "Score Global /10", "Score Eau /10", "Score Sol /10", "Bénéfice Clé"]
        show_cols = [c for c in pref_cols if c in ranking.columns]
        if not show_cols:
            show_cols = [c for c in ranking.columns if not c.startswith("_")]
        st.dataframe(
            ranking[show_cols],
            width="stretch",
            column_config={
                "Score Global /10": st.column_config.ProgressColumn(
                    "Score Global /10",
                    min_value=0.0,
                    max_value=10.0,
                    format="%.2f"
                ),
                "Score Eau /10": st.column_config.NumberColumn("Score Eau /10", format="%.2f"),
                "Score Sol /10": st.column_config.NumberColumn("Score Sol /10", format="%.2f"),
            }
        )

        st.write("")
        st.markdown("#### Synthèse Agronomique de la Proposition N°1")

        rot_str = " ➔ ".join([c.capitalize() for c in best_res.rotation])
        has_feve = "fève" in best_res.rotation
        has_betterave = "betterave" in best_res.rotation
        has_carotte = "carotte" in best_res.rotation

        sol_points = []
        if has_feve:
            sol_points.append("la **fève** capte l'azote atmosphérique pour enrichir naturellement le sol et réduire les apports en engrais minéraux")
        if has_betterave or has_carotte:
            sol_points.append("l'enracinement profond décompacte et aère naturellement les sols argilo-limoneux (Tirs) du Tadla")
        sol_points.append("l'alternance de trois familles de cultures brise efficacement le cycle des maladies et des ravageurs telluriques")

        if choix_priorite == "Économie d'eau":
            priorite_txt = "Cette rotation a été retenue avec une priorité à la **sobriété en eau**, afin de sécuriser votre récolte face aux années de déficit hydrique."
        elif choix_priorite == "Régénération du sol":
            priorite_txt = "Cette rotation a été retenue avec une priorité à la **régénération du sol**, afin de restaurer durablement la fertilité et la matière organique de votre parcelle."
        else:
            priorite_txt = "Cette rotation a été retenue avec une priorité au **rendement**, pour valoriser au maximum la marge brute et le potentiel de votre terre."

        sol_joined = "; ".join(sol_points)
        pourquoi_html = (
            f'<div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-left: 5px solid #2e7d32; '
            f'border-radius: 8px; padding: 1.2rem; margin-top: 0.5rem; color: #1e293b;">'
            f'<p style="font-size: 1.05rem; line-height: 1.6; margin: 0 0 0.5rem 0; color: #0f172a;">'
            f'<strong>Pourquoi cette rotation ?</strong> La séquence <strong>{best_res.name}</strong> ({rot_str}) offre la meilleure réponse agronomique pour votre exploitation.'
            f'</p>'
            f'<p style="font-size: 1rem; line-height: 1.6; margin: 0 0 0.5rem 0; color: #1e293b;">'
            f'<strong>Bénéfice sol :</strong> {sol_joined}.'
            f'</p>'
            f'<p style="font-size: 1rem; line-height: 1.6; margin: 0; color: #1e293b;">'
            f'<strong>Bénéfice eau et climat :</strong> {priorite_txt}'
            f'</p>'
            f'</div>'
        )
        st.markdown(pourquoi_html, unsafe_allow_html=True)

    # =========================================================================
    # ONGLET 2 : DIAGNOSTIC & KPIS DE LA PARCELLE
    # =========================================================================
    with tab2:
        st.markdown("### Diagnostic Agro-Climatique et Pédologique de la Parcelle")
        st.caption(f"Coordonnées : {st.session_state.parcel_coords['lat']}°N, {st.session_state.parcel_coords['lon']}°W · Période historique : 2014–2026 ({clim['n_full_years']} années complètes)")

        # 4 KPIs clés (st.metric)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        kpi1.metric(
            label="Précipitation Moyenne",
            value=f"{clim['precip_mean']:.1f} mm/an",
            delta=f"Min {clim['precip_min']:.0f} mm ({clim['precip_min_year']})",
            delta_color="off"
        )
        
        kpi2.metric(
            label="Humidité Racines (GWETROOT)",
            value=f"{clim['gwetroot_mean']:.2f}",
            delta="Fraction saturation 0-1",
            delta_color="off"
        )
        
        kpi3.metric(
            label="Jours Chauds (>35°C)",
            value=f"{clim['heat_days_mean']:.0f} j/an",
            delta=f"Gel : {clim['frost_days_mean']:.1f} j/an",
            delta_color="off"
        )
        
        src_label = "Laboratoire" if is_lab else "Estimé IA"
        kpi4.metric(
            label="Statut Chimique du Sol",
            value=f"pH {lab.ph} · N {lab.azote}",
            delta=f"Source : {src_label}",
            delta_color="normal" if is_lab else "off"
        )

        st.write("")
        c_diag_a, c_diag_b = st.columns(2)
        
        with c_diag_a:
            st.subheader("Humidité Racinaire Moyenne par Saison (GWETROOT)")
            s_seas = pd.Series(clim["gwetroot_season"]).reindex(["Hiver", "Printemps", "Été", "Automne"])
            df_seas = pd.DataFrame({
                "Saison": s_seas.index,
                "GWETROOT (0-1)": s_seas.values.round(3),
                "Diagnostic": [
                    "Recharge hivernale",
                    "Stress printanier modéré",
                    "Déficit hydrique estival sévère",
                    "Début des pluies automnales"
                ]
            })
            st.dataframe(df_seas, width="stretch", hide_index=True)
            
            if clim["dry_years"]:
                st.warning(f"⚠️ **Années déficitaires critiques (< 350 mm/an) :** {', '.join(map(str, clim['dry_years']))}")

        with c_diag_b:
            st.subheader("Indicateurs Annuels NASA POWER")
            ann_table = clim["annual"][clim["annual"]["complete"]].copy()
            ann_table = ann_table[["precip_mm", "gwetroot", "jours_chaleur_35", "jours_gel"]]
            ann_table.columns = ["Pluie (mm)", "GWETROOT", "Jours >35°C", "Jours Gel"]
            st.dataframe(ann_table.round(2), width="stretch")

        st.caption(f"🌡️ Température moyenne annuelle : {clim['t2m_mean']:.1f} °C (extrêmes absolus : {clim['tmin_abs']:.1f} °C à {clim['tmax_abs']:.1f} °C) · ☀️ Irradiance solaire moyenne : {clim.get('irradiance_mean', 20.1):.1f} MJ/m²/jour.")

    # =========================================================================
    # ONGLET 3 : VISUALISATIONS INTERACTIVES (PLOTLY)
    # =========================================================================
    with tab3:
        st.markdown("### Visualisations Agro-Climatiques et Comparatives")

        # Graphique 1 : Évolution annuelle des précipitations et de l'humidité des racines
        st.subheader("Graphique 1 : Précipitations Annuelles & Humidité Racinaire (2014–2025)")
        ann_df = clim["annual"][clim["annual"]["complete"]]
        
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig1.add_bar(
            x=ann_df.index,
            y=ann_df["precip_mm"],
            name="Précipitations annuelles (mm)",
            marker_color="#2b6cb0",
            secondary_y=False
        )
        fig1.add_scatter(
            x=ann_df.index,
            y=ann_df["gwetroot"],
            name="Humidité racinaire GWETROOT",
            mode="lines+markers",
            line=dict(color="#2e7d32", width=3),
            marker=dict(size=8),
            secondary_y=True
        )
        fig1.add_hline(
            y=350,
            line_dash="dash",
            line_color="#e53e3e",
            annotation_text="Seuil sécheresse (350 mm)",
            secondary_y=False
        )
        fig1.update_xaxes(title_text="Année")
        fig1.update_yaxes(title_text="Précipitations (mm/an)", secondary_y=False)
        fig1.update_yaxes(title_text="GWETROOT (0–1)", secondary_y=True)
        fig1.update_layout(
            height=400,
            margin=dict(l=40, r=40, t=30, b=40),
            legend=dict(orientation="h", y=-0.2, x=0.2)
        )
        st.plotly_chart(fig1, width="stretch")

        col_g2, col_g3 = st.columns(2)
        
        with col_g2:
            # Graphique 2 : Radar Chart comparant les profils agronomiques
            st.subheader("Graphique 2 : Profils Agronomiques des Cultures")
            traits_labels = [
                "Besoin en eau",
                "Tolérance sécheresse",
                "Fixation azote",
                "Racines profondes",
                "Tolérance gel"
            ]
            fig_radar = go.Figure()
            colors = ["#2b6cb0", "#c53030", "#d69e2e", "#dd6b20", "#38a169"]
            
            for idx, (_, r_crop) in enumerate(crops.iterrows()):
                vals = [r_crop[t] for t in dl.TRAITS]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals + vals[:1],
                    theta=traits_labels + traits_labels[:1],
                    fill="toself",
                    opacity=0.35,
                    name=r_crop["culture"].capitalize(),
                    line=dict(color=colors[idx % len(colors)], width=2)
                ))
                
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                height=450,
                margin=dict(l=50, r=50, t=30, b=30),
                legend=dict(orientation="h", y=-0.15)
            )
            st.plotly_chart(fig_radar, width="stretch")

        with col_g3:
            # Graphique 3 : Comparatif des 3 Rotations Optimales
            st.subheader("Graphique 3 : Comparaison des 3 Rotations Optimales")
            df_top3_plot = top3.copy()
            
            fig_bar = go.Figure(data=[
                go.Bar(name="Score Global", x=df_top3_plot["Rotation"], y=df_top3_plot["Score Global /10"], marker_color="#2e7d32"),
                go.Bar(name="Score Eau", x=df_top3_plot["Rotation"], y=df_top3_plot["Score Eau /10"], marker_color="#3182ce"),
                go.Bar(name="Score Sol", x=df_top3_plot["Rotation"], y=df_top3_plot["Score Sol /10"], marker_color="#d69e2e"),
            ])
            fig_bar.update_layout(
                barmode="group",
                yaxis=dict(title="Score / 10", range=[0, 10]),
                height=450,
                margin=dict(l=40, r=40, t=30, b=30),
                legend=dict(orientation="h", y=-0.15)
            )
            st.plotly_chart(fig_bar, width="stretch")

        # Graphique NDVI Série Temporelle
        if ndvi is not None:
            st.subheader("Graphique 4 : Série Temporelle NDVI MODIS (2000–2026)")
            fig_ndvi = go.Figure()
            fig_ndvi.add_trace(go.Scatter(
                x=ndvi["Date"],
                y=ndvi["NDVI"],
                mode="lines",
                line=dict(color="#38a169", width=1.5),
                name="NDVI 250m (16 jours)"
            ))
            fig_ndvi.add_hline(
                y=thr_bare,
                line_dash="dot",
                line_color="#e53e3e",
                annotation_text=f"Seuil sol nu ({thr_bare})"
            )
            fig_ndvi.update_layout(
                yaxis=dict(title="NDVI"),
                height=350,
                margin=dict(l=40, r=40, t=20, b=40)
            )
            st.plotly_chart(fig_ndvi, width="stretch")
