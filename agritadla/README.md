# 🌾 BladiNova (Prototype v1 — Flux Phygital Complet)

Système d'Aide à la Décision (DSS) **Phygital** pour l'optimisation agro-climatique des rotations culturales sur 3 ans dans la **plaine du Tadla (Maroc)**.

---

## 🎯 Parcours Utilisateur en 4 Étapes

1. **Écran 1 — Connexion (Login) :** Authentification de l'agriculteur (Email / Identifiant, nom de l'exploitant, commune du Tadla, superficie).
2. **Écran 2 — Sélection Géographique (Carte Folium) :** Carte interactive centrée sur le Tadla (`32.45°N, -6.525°W`) avec marqueur dynamique, secteur d'irrigation ORMVAT (rayon 5 km) et sélection par clic ou coordonnées manuelles.
3. **Écran 3 — Choix du Service Phygital :**
   * **Service A (Phygital Labo) :** Demande de passage d'un agent de terrain pour prélèvement et analyses physico-chimiques certifiées en laboratoire.
   * **Service B (IA & Datasets) :** Génération automatique instantanée basée sur 12 ans d'historique NASA POWER, MODIS NDVI et modèles d'apprentissage régionaux.
4. **Écran 4 — Tableau de Bord & Recommandations :**
   * **3 Propositions de Rotation Optimales sur 3 Ans** (ex: *Blé → Fève → Betterave* en n°1).
   * **Encart Recommandation Explicable (XAI)** justifiant la proposition n°1 selon le climat, le sol et la télédétection.
   * **Barre latérale conditionnelle :** Le formulaire de saisie laboratoire (pH, N, P, K, MO %) ne s'affiche **que pour le Service A** (masqué pour le Service B avec valeurs par défaut robustes).
   * **4 KPIs climatiques et pédologiques** (`st.metric`).
   * **Graphiques interactifs Plotly :** Évolution annuelle pluies/GWETROOT, Radar chart agronomique, Série temporelle NDVI.

---

## 📁 Architecture des Fichiers

* **`app.py`** : Point d'entrée Streamlit avec routeur de navigation séquentiel (`st.session_state`), styling CSS et tableau de bord.
* **`data_loader.py`** : Ingestion et nettoyage robuste 100 % local :
  * `POWER_Point_Daily_20140401_20260211_032d45N_006d53W_LST.csv` (NASA POWER, saut automatique de l'en-tête de 17 lignes).
  * `crops.xlsx` (Séparation de la colonne unifiée et typage des scores agronomiques).
  * `Zonz-NDVI-MOD13Q1-061-results.csv` (Série temporelle NDVI et calcul des mois de sol nu $< 0.2$).
* **`scoring_engine.py`** : Moteur multicritère (MCDA) pondérant l'axe hydro-climatique et l'axe pédologique avec explicabilité XAI en français.
* **`requirements.txt`** : Dépendances (`streamlit`, `pandas`, `numpy`, `plotly`, `openpyxl`, `folium`, `streamlit-folium`).

---

## 🚀 Lancement Rapide (100 % Local)

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement de l'application
streamlit run app.py
```
L'application s'ouvre directement à l'adresse locale `http://localhost:8501`.
