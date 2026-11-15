# 🌾 BladiNova
### Phygital Agricultural Decision Support System for the Tadla Plain, Morocco

**NASA Space Apps Challenge 2026 — Field Shift: Adapting Farms with NASA Data**

BladiNova is a phygital agricultural Decision Support System (DSS) designed to help farmers in Morocco's Tadla Plain explore more informed crop rotation strategies by combining NASA Earth observation data, agronomic crop characteristics, and soil information.

The platform transforms environmental and agricultural data into understandable indicators and compares three-year crop rotation scenarios according to the farmer's priorities.

> **Our vision:** Turn Earth observation data into practical insights for more informed agricultural decisions.

---

## 🌱 1. The Problem

Farmers must make crop selection and rotation decisions in an increasingly challenging agricultural environment.

Several factors make these decisions complex:

- **Water availability:** Rainfall variability and irrigation requirements.
- **Climate pressure:** High temperatures, drought periods, and frost events.
- **Soil health:** Maintaining fertility, organic matter, and soil structure.
- **Crop succession:** Avoiding excessive repetition of the same botanical families.
- **Decision complexity:** Balancing water requirements, soil health, climate resilience, and production objectives.

Traditional crop selection does not always provide an integrated view of these different factors.

BladiNova aims to make relevant environmental and agronomic information more accessible to farmers.

---

## 🎯 2. Our Solution

BladiNova is an interactive decision-support platform that helps farmers compare alternative crop rotations over a three-year period.

It combines:

- NASA POWER climate and soil-moisture indicators.
- MODIS NDVI vegetation observations.
- Agronomic characteristics of five crops.
- Soil information and optional laboratory analysis.
- Farmer-defined strategic priorities.

The platform generates three crop rotation proposals and presents their comparative evaluation.

**BladiNova supports farmers' decisions; it does not replace farmers or agricultural experts.**

---

## 📍 3. Study Area

<image_placeholder>

**Study area:** Tadla irrigated plain, around Beni Mellal, Morocco.

- Reference coordinates: 32.45° N, -6.525° W.
- Geographic focus: Tadla agricultural region.
- Climate analysis: historical NASA POWER observations.
- Local context: irrigated agricultural systems and argilo-limoneux / Tirs soils.

The application uses the selected parcel location to associate the available environmental information with the farmer's area of interest.

---

## 🔄 4. How BladiNova Works

The application follows four main steps.

### Step 1 — Login

The farmer accesses the application through an authentication interface.

### Step 2 — Parcel Geolocation

The farmer selects or adjusts the geographical location of the agricultural parcel using an interactive map.

### Step 3 — Phygital Service Selection

The farmer chooses between two service options:

**Service A — Phygital Labo**

A field-service option involving soil sampling and physico-chemical laboratory analysis. Available laboratory results can then be entered into the application.

**Service B — AI & Datasets**

An automated assessment based on available historical climate, satellite and regional agronomic information, without requiring a laboratory analysis.

### Step 4 — Dashboard & Decision

BladiNova displays the parcel diagnosis, climate indicators, crop rotation proposals, interactive visualizations, and an agronomic explanation of the results.

---

## 🛰️ 5. Data Sources

BladiNova combines several sources of environmental and agricultural information.

### NASA POWER

Used for historical agro-climatic analysis.

Variables include:

| Variable | Description |
|---|---|
| PRECTOTCORR | Corrected precipitation |
| T2M | Mean air temperature |
| T2M_MAX | Maximum air temperature |
| T2M_MIN | Minimum air temperature |
| GWETROOT | Root-zone soil wetness |
| GWETTOP | Surface soil wetness |
| GWETPROF | Profile soil wetness |
| RH2M | Relative humidity at 2 meters |
| ALLSKY_SFC_SW_DWN | Solar radiation |

These variables support the calculation of indicators such as annual rainfall, hot days, frost days, and root-zone wetness.

### MODIS NDVI

The MODIS vegetation index is used to explore vegetation dynamics over time.

It supports:

- Vegetation monitoring.
- Identification of periods of low vegetation cover.
- Indicative detection of potentially bare-soil periods.

The project uses an NDVI threshold of 0.20 as an indicative bare-soil detection parameter.

NDVI alone cannot confirm the actual crop or soil condition of a parcel.

### Agronomic Crop Dataset

The current crop reference includes five crops:

| Crop | Botanical family |
|---|---|
| Wheat | Cereal |
| Sugar beet / beet* | Root crop |
| Onion | Bulb vegetable |
| Carrot | Root crop |
| Faba bean | Legume |

*The original dataset identifies the crop as beet ("betterave"). Its precise type should be confirmed before interpreting it specifically as sugar beet.*

Each crop is described using qualitative agronomic scores, including:

- Water requirement.
- Drought tolerance.
- Nitrogen fixation.
- Root depth.
- Frost tolerance.

Scores use a qualitative scale from 1 to 5 and are based on the project's agronomic reference table. Their reliability depends on the availability and quality of supporting references.

### Soil Information

For the Phygital Labo option, the user can enter available laboratory information:

- Soil pH.
- Available nitrogen (N).
- Assimilable phosphorus (P).
- Exchangeable potassium (K).
- Organic matter percentage.
- Soil texture.

For the automated option, regional reference assumptions are used where parcel-specific laboratory measurements are unavailable. These assumptions must not be interpreted as actual laboratory measurements.

---

## 🧠 6. Decision Engine

BladiNova uses a multi-criteria decision approach to compare three-year crop rotation scenarios.

### Strategic priorities

The farmer can select one of three priorities:

**💧 Water Economy**

Emphasizes water requirements, drought tolerance, and adaptation to water constraints.

**🌱 Soil Regeneration**

Emphasizes nitrogen fixation, root characteristics, soil structure, and botanical diversification.

**🌾 Yield Priority**

Emphasizes the production objective and the agronomic potential represented in the crop reference.

### Evaluation criteria

Each rotation is assessed using four main dimensions:

1. **Water Management:** Compatibility between crop water requirements and available environmental indicators.
2. **Soil Health:** Nitrogen fixation, root characteristics, and available soil information.
3. **Climate Resilience:** Crop tolerance to drought, heat-related conditions, and frost.
4. **Phytosanitary Risk:** Penalties associated with repeated crops from the same botanical family.

The selected priority influences the weighting of the decision criteria.

### Rotation comparison

The system explores three-year sequences, including illustrative scenarios such as:

| Scenario | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Monoculture reference | Wheat | Wheat | Wheat |
| Diversification | Wheat | Faba bean | Carrot |
| Soil enrichment | Wheat | Faba bean | Beet |

These sequences are comparison scenarios, not experimentally validated agronomic recommendations.

### Explainable recommendations

The platform provides an accessible agronomic explanation of the proposed rotations.

It aims to explain:

- Why a rotation receives its evaluation.
- How crop characteristics influence the result.
- How environmental indicators affect the comparison.
- What potential benefits and trade-offs should be considered.

The scores are decision-support indicators, not probabilities of agricultural success.

---

## 📊 7. Main Application Features

| Feature | Description |
|---|---|
| Authentication | Farmer access interface |
| Interactive map | Parcel location selection |
| Phygital services | Laboratory-based or dataset-based assessment |
| Climate dashboard | NASA POWER indicators |
| Vegetation monitoring | MODIS NDVI analysis |
| Soil information | Laboratory data input |
| Crop reference | Five agronomic crop profiles |
| Rotation comparison | Three-year crop rotation scenarios |
| Strategic priorities | Water economy, soil regeneration, yield |
| Agronomic explanation | Understandable justification of results |
| Interactive charts | Climate trends and crop profile comparisons |

---

## 📈 8. Climate Indicators

The project analysis has reported the following historical indicators from the available NASA POWER dataset:

| Indicator | Reported value |
|---|---:|
| Average annual precipitation | Approximately 407.8 mm/year |
| Minimum annual precipitation | Approximately 227.5 mm in 2023 |
| Average root-zone wetness (GWETROOT) | Approximately 0.50 |
| Days with maximum temperature above 35 °C | Approximately 77 days/year |
| Frost days | Approximately 2.4 days/year |
| Average solar radiation | Approximately 20.1 MJ/m²/day |

These values are project-reported summaries. They depend on the selected coordinates, data period, and calculation method. They describe the regional data source, not direct measurements on every agricultural parcel.

---

## 🖥️ 9. Application Screenshots

Add screenshots of the actual application in this section.

| Screen | Screenshot |
|---|---|
| Login | `docs/images/login.png` |
| Parcel geolocation | `docs/images/map.png` |
| Phygital service selection | `docs/images/services.png` |
| Dashboard | `docs/images/dashboard.png` |
| Rotation recommendations | `docs/images/recommendations.png` |
| Interactive visualizations | `docs/images/visualizations.png` |

---

## 🛠️ 10. Technology Stack

| Category | Technologies |
|---|---|
| Programming language | Python |
| Web application | Streamlit |
| Data processing | Pandas, NumPy |
| Data visualization | Plotly |
| Interactive mapping | Folium, Streamlit-Folium |
| Excel data handling | OpenPyXL |
| Climate data | NASA POWER |
| Satellite vegetation data | MODIS NDVI |
| Decision approach | Multi-Criteria Decision Analysis (MCDA) |

---

## 📁 11. Project Structure

```text
BladiNova/
│
├── app.py
├── data_loader.py
├── scoring_engine.py
├── requirements.txt
├── README.md
│
├── POWER_Point_Daily_20140401_20260211_032d45N_006d53W_LST.csv
├── crops.xlsx
├── Zonz-NDVI-MOD13Q1-061-results.csv
│
└── docs/
    └── images/
        ├── login.png
        ├── map.png
        ├── services.png
        ├── dashboard.png
        ├── recommendations.png
        └── visualizations.png
```

---

## 🚀 12. Installation and Local Execution

### Prerequisites

- Python 3.10 or later.
- pip.
- The project datasets listed in the project structure.

### Step 1 — Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd BladiNova
```

### Step 2 — Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Launch the application

```bash
streamlit run app.py
```

Open the application in your browser:

```text
http://localhost:8501
```

---

## 🔌 13. API Requirements

**No external API key is required to run the current local prototype**, provided that the required datasets are already available locally.

The application reads the NASA POWER, crop reference, and MODIS NDVI files from the project directory.

An internet connection may be required for external map tiles or other online resources, depending on the map configuration. This does not mean that an external API key is required by the current data-processing workflow.

---

## ⚠️ 14. Limitations and Responsible Use

BladiNova is an experimental decision-support prototype. Its outputs must be interpreted carefully.

Current limitations include:

- NASA POWER has a relatively coarse spatial resolution and does not provide direct field measurements.
- MODIS NDVI is an indirect vegetation indicator.
- Agronomic crop scores are qualitative and have different levels of supporting evidence.
- Regional soil assumptions do not replace parcel-specific laboratory measurements.
- Market prices and detailed economic profitability are not currently integrated.
- The proposed rotations require validation under local agricultural conditions.
- The decision engine requires evaluation with local agronomists and farmers.

**BladiNova is designed to support agricultural judgment, not replace it.**

---

## 🔭 15. Future Improvements

Planned development directions include:

- Expanding the crop database.
- Integrating more detailed soil information through SoilGrids.
- Exploring complementary soil-moisture observations from SMAP.
- Adding local agricultural market prices.
- Improving the agronomic scoring model.
- Validating rotation proposals with local agronomists and farmers.
- Developing Arabic and French interfaces.
- Incorporating field observations and real agricultural feedback.

---

## 👥 16. Team

**TDI — Together Dream Innovate**

NASA Space Apps Challenge 2026

Team members:

- DAANOUN Chaimaa
- RAFIKI Najat
- EL FATHI Saloua
- DIANI Souad

---

## 🌍 17. Final Message

BladiNova connects Earth observation, agronomic knowledge, and farmer priorities to make agricultural decision-making more accessible.

By transforming environmental information into understandable comparisons, the project aims to support more informed crop rotation choices in the Tadla Plain and contribute to the exploration of climate-resilient agricultural practices.

**From satellite observations to informed decisions in the field.**

---

*Developed for the NASA Space Apps Challenge 2026 — Field Shift: Adapting Farms with NASA Data.*
