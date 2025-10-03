import pandas as pd
import statsmodels.api as sm

# --- Lecture
ocde = pd.read_csv(
    r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\ICT_OCDE.csv",
    sep=';',
    skiprows=1
)

# --- Renommer la 1re colonne (pays) en 'Country'
ocde = ocde.rename(columns={"Time period Employment size class: 10 or more": "Country"})

# --- Supprimer la colonne 'Time period' si présente
if "Time period" in ocde.columns:
    ocde = ocde.drop(columns=["Time period"])

# --- Détecter les colonnes d'années (ex: '2012', '2013', ...)
year_cols = [c for c in ocde.columns if str(c).isdigit()]

# --- Large -> Long
ocde_long = ocde.melt(id_vars="Country", value_vars=year_cols,
                      var_name="Year", value_name="WebCompanies")

# --- Nettoyage des valeurs (remplacer virgule, retirer lettres/fanions, convertir)
ocde_long["WebCompanies"] = (
    ocde_long["WebCompanies"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.extract(r"(\d+(?:\.\d+)?)")[0]
)
ocde_long["WebCompanies"] = pd.to_numeric(ocde_long["WebCompanies"], errors="coerce")
ocde_long["Year"] = pd.to_numeric(ocde_long["Year"], errors="coerce")

# --- Nettoyage des pays (retirer puces '·', espaces) et lignes agrégées
ocde_long["Country"] = ocde_long["Country"].str.replace(r"^[\s·]+", "", regex=True).str.strip()
ocde_long = ocde_long[~ocde_long["Country"].str.contains("OECD|European Union|Non-OECD", na=False)]

# --- Supprimer lignes vides
ocde_long = ocde_long.dropna(subset=["WebCompanies", "Year"])

print(ocde_long.head(10))
print("✅ Format long créé :", ocde_long.shape)

ocde_long.to_csv(
    r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\ocde_long.csv",
    sep=';'
)


print("🚀 Début du script de fusion et d'analyse...\n")

# === 1. Satisfaction (Cantril ladder) ===
print("📘 Lecture du fichier Satisfaction...")
satisfaction = pd.read_csv(
    r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\Satisfaction.csv",
    sep=';'
)
print("Colonnes détectées :", satisfaction.columns.tolist())

# Renommage
satisfaction = satisfaction.rename(columns={
    "Entity": "Country",
    "Year": "Year",
    "Cantril ladder score": "WellBeing"
})
satisfaction["Country"] = satisfaction["Country"].str.strip()
satisfaction["Year"] = pd.to_numeric(satisfaction["Year"], errors="coerce")

print("✅ Satisfaction : OK —", satisfaction.shape, "lignes\n")


# === 2. Robots ===
print("🤖 Lecture du fichier Robots...")
robots = pd.read_csv(
    r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\annual-industrial-robots-installed.csv",
    sep=';'
)
print("Colonnes détectées :", robots.columns.tolist())

robots = robots.rename(columns={
    "Entity": "Country",
    "Year": "Year",
    "installations": "RobotsInstalled"
})
robots["Country"] = robots["Country"].str.strip()
robots["Year"] = pd.to_numeric(robots["Year"], errors="coerce")
robots["RobotsInstalled"] = pd.to_numeric(robots["RobotsInstalled"], errors="coerce")

print("✅ Robots : OK —", robots.shape, "lignes\n")


# === 3. Publications IA ===
print("🧠 Lecture du fichier Publications IA...")


ai_pub = pd.read_excel(
    r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\publications.sur.IA.xlsx",
    engine="openpyxl"
)

# On prend le nom lisible (Country_label) et pas le code ISO
ai_pub = ai_pub[["Country_label", "year", "publications"]].rename(columns={
    "Country_label": "Country",
    "year": "Year",
    "publications": "AIPublications"
})

# Nettoyage pays + décimales avec virgule
ai_pub["Country"] = ai_pub["Country"].astype(str).str.strip()

ai_pub["AIPublications"] = (
    ai_pub["AIPublications"].astype(str)
    .str.replace(",", ".", regex=False)
)
ai_pub["AIPublications"] = pd.to_numeric(ai_pub["AIPublications"], errors="coerce")
ai_pub["Year"] = pd.to_numeric(ai_pub["Year"], errors="coerce", downcast="integer")

# Harmonisation des noms pour matcher Satisfaction/OCDE/Robots
mapping_pays = {
    "United States": "United States of America",
    "China (People's Republic of)": "China",
    "Czech Republic": "Czechia",
    "Slovak Republic": "Slovakia",
    "Viet Nam": "Vietnam",
    "Russian Federation": "Russia",
    "Korea, Republic of": "South Korea",  # si présent
    "Korea": "South Korea",               # fallback
}
ai_pub["Country"] = ai_pub["Country"].replace(mapping_pays)

# Retirer les agrégats/régions (EU27, etc.) qui ne matchent aucun pays
bad_regions = {"EU27", "European Union", "World", "OECD", "Non-OECD economies"}
ai_pub = ai_pub[~ai_pub["Country"].isin(bad_regions)]

print("✅ Publications IA (corrigé) :", ai_pub.shape)
print(ai_pub.head())



# === 4. OCDE (WebCompanies) ===
print("🌐 Lecture du fichier OCDE (WebCompanies)...")
ocde_long = pd.read_csv(
    r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\ocde_long.csv" , sep=';'
)
ocde_long["Country"] = ocde_long["Country"].str.strip()
ocde_long["Year"] = pd.to_numeric(ocde_long["Year"], errors="coerce")
ocde_long["WebCompanies"] = pd.to_numeric(ocde_long["WebCompanies"], errors="coerce")

print("✅ OCDE WebCompanies : OK —", ocde_long.shape, "lignes\n")


# === 5. Fusion des bases ===
print("🔗 Fusion des différentes bases...")
merged = satisfaction.merge(robots, on=["Country", "Year"], how="left")
merged = merged.merge(ai_pub, on=["Country", "Year"], how="left")
merged = merged.merge(ocde_long, on=["Country", "Year"], how="left")

# Nettoyage
merged = merged.dropna(subset=["WellBeing"])
numeric_cols = ["RobotsInstalled", "AIPublications", "WebCompanies"]
for col in numeric_cols:
    if col in merged.columns:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")

print("✅ Fusion complète :", merged.shape, "observations\n")
print(merged.head(10))


# === 6. Sauvegarde ===
output_path = r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\merged_IA_BienEtre.csv"
merged.to_csv(output_path, index=False)
print(f"💾 Fichier fusionné enregistré avec succès : {output_path}\n")






