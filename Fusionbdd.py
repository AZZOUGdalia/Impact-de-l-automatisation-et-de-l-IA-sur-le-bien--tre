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
