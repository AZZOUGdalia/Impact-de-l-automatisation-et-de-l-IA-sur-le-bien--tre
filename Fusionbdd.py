import pandas as pd


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





# === 1. Satisfaction (Cantril ladder) ===
satisfaction = pd.read_csv(r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\Satisfaction.csv")
satisfaction = satisfaction.rename(columns={
    "country": "Country",
    "year": "Year",
    "cantril_ladder_score": "WellBeing"
})
satisfaction["Country"] = satisfaction["Country"].str.strip()
satisfaction["Year"] = pd.to_numeric(satisfaction["Year"], errors="coerce")

# === 2. Robots ===
robots = pd.read_csv(r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\annual-industrial-robots-installed.csv")
robots = robots.rename(columns={
    "Entity": "Country",
    "Year": "Year",
    "Annual industrial robots installed": "RobotsInstalled"
})
robots["Country"] = robots["Country"].str.strip()

# === 3. Publications IA ===
ai_pub = pd.read_excel(r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\publications.sur.IA.xlsx")
ai_pub = ai_pub.rename(columns={"Country": "Country", "Year": "Year", "Publications": "AIPublications"})
ai_pub["Country"] = ai_pub["Country"].str.strip()
ai_pub["Year"] = pd.to_numeric(ai_pub["Year"], errors="coerce")

# === 4. ICT (usage du numérique / IA / Big Data) ===
ict = pd.read_csv(r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\OECD.STI.DEP,DSD_ICT_B@DF_BUSINESSES,,filtered,2025-09-16 21-04-12.csv")
ict = ict.rename(columns={"COU": "Country", "TIME": "Year", "Value": "ICT_Value", "INDIC_IS": "Indicator"})
ict = ict[ict["Indicator"].isin(["BUS_AI", "BUS_BDANL", "BUS_ROB", "BUS_WEB"])]
ict = ict.pivot_table(index=["Country", "Year"], columns="Indicator", values="ICT_Value").reset_index()

# === 5. OCDE (WebCompanies, ton fichier nettoyé) ===

ocde_long = pd.read_csv(r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\ocde_long.csv")  


#Fusion 
merged = satisfaction.merge(robots, on=["Country", "Year"], how="left")
merged = merged.merge(ai_pub, on=["Country", "Year"], how="left")
merged = merged.merge(ict, on=["Country", "Year"], how="left")
merged = merged.merge(ocde_long, on=["Country", "Year"], how="left")


#Nettoyage des données 
# Supprimer les lignes sans bien-être (Y)
merged = merged.dropna(subset=["WellBeing"])

# Conversion numérique cohérente
numeric_cols = ["RobotsInstalled", "AIPublications", "BUS_AI", "BUS_BDANL", "BUS_ROB", "BUS_WEB", "WebCompanies"]
for col in numeric_cols:
    if col in merged.columns:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")

print("✅ Fusion complète :", merged.shape)
print(merged.head(10))


merged.to_csv(r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\merged_IA_BienEtre.csv", index=False)
print("💾 Fichier fusionné enregistré !")







