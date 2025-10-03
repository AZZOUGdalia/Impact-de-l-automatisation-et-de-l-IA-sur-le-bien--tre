import pandas as pd
import statsmodels.api as sm

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
ai_pub = ai_pub[["Country", "year", "publications"]].rename(columns={
    "Country": "Country",
    "year": "Year",
    "publications": "AIPublications"
})
ai_pub["Country"] = ai_pub["Country"].str.strip()
ai_pub["Year"] = pd.to_numeric(ai_pub["Year"], errors="coerce")
ai_pub["AIPublications"] = pd.to_numeric(ai_pub["AIPublications"], errors="coerce")

print("✅ Publications IA : OK —", ai_pub.shape, "lignes\n")


# === 4. OCDE (WebCompanies) ===
print("🌐 Lecture du fichier OCDE (WebCompanies)...")
ocde_long = pd.read_csv(
    r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\ocde_long.csv"
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




