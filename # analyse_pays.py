# ==========================================================
# Impact automatisation (RobotsInstalled) & ICT sur le bien-être
# Analyse par pays + graphique combiné des effets estimés
# ==========================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

# ---------- 0) PARAMÈTRES ----------

INPUT_CSV = r"C:\Users\dalia\OneDrive\Bureau\CM M2\digital economy and technicale change\Munier francis\projet\merged_IA_BienEtre.csv"
# Le fichier doit avoir au minimum ces colonnes (casse indifférente) :
# Country | Year | WellBeing | RobotsInstalled | ICT

# ---------- 1) LECTURE & NETTOYAGE ----------
# Lecture tolérante au séparateur
try:
    df = pd.read_csv(INPUT_CSV, sep=";")
    if df.shape[1] == 1:
        df = pd.read_csv(INPUT_CSV, sep=",")
except Exception:
    df = pd.read_csv(INPUT_CSV)

# Normalise noms colonnes
df.columns = [c.strip() for c in df.columns]
# Essaie d’identifier les colonnes clés même si noms varient un peu
colmap = {}
lower = {c.lower(): c for c in df.columns}
for want in ["country", "year", "wellbeing", "robotsinstalled", "ict"]:
    # variantes possibles
    candidates = [
        want,
        want.replace("_", ""),
        want.replace("robotsinstalled", "robotsinst"),
        want.replace("wellbeing", "wellbeing"),
    ]
    found = None
    for cand in candidates:
        if cand in lower:
            found = lower[cand]
            break
    if found is None:
        # essaie quelques alias courants
        aliases = {
            "wellbeing": ["cantril ladder score", "cantril_ladder_score", "well_being"],
            "robotsinstalled": ["robots", "installations", "robots_installed"],
            "ict": ["webcompanies", "ict_share", "ict_index"],
        }
        for a in aliases.get(want, []):
            if a.lower() in lower:
                found = lower[a.lower()]
                break
    if found is None:
        raise ValueError(f"Colonne '{want}' introuvable dans le fichier : {df.columns.tolist()}")
    colmap[found] = want.capitalize() if want != "robotsinstalled" else "RobotsInstalled"

df = df.rename(columns=colmap)

# Nettoie types
for c in ["Wellbeing", "RobotsInstalled", "Ict", "Year"]:
    if c in df.columns:
        df[c] = (
            df[c]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.extract(r"(-?\d+(?:\.\d+)?)")[0]
        )
        df[c] = pd.to_numeric(df[c], errors="coerce")

df["Country"] = df["Country"].astype(str).str.strip()
df = df.dropna(subset=["Country", "Year", "Wellbeing"])
df = df.sort_values(["Country", "Year"]).reset_index(drop=True)

# Liste des pays présents (ex : France, China, Germany, Japan, Spain, etc.)
countries = df["Country"].dropna().unique().tolist()

# ---------- 2) OUTILS GRAPHIQUES ----------
def plot_timeseries(sub, country):
    """Séries temporelles : WellBeing, RobotsInstalled, ICT (normalisés pour être sur une même échelle)."""
    sub = sub.sort_values("Year")
    plt.figure(figsize=(8,4.6))
    # Normalisation z-score pour comparer les dynamiques
    def z(x):
        x = x.dropna()
        if len(x) < 2:
            return None
        m, s = x.mean(), x.std(ddof=0)
        return (x - m) / (s if s != 0 else 1)
    # Traces
    plt.plot(sub["Year"], sub["Wellbeing"], marker="o", label="WellBeing")
    if sub["RobotsInstalled"].notna().any():
        zrob = z(sub["RobotsInstalled"])
        if zrob is not None:
            plt.plot(sub.loc[zrob.index, "Year"], zrob, marker="o", label="Robots (z-score)")
    if sub["Ict"].notna().any():
        zict = z(sub["Ict"])
        if zict is not None:
            plt.plot(sub.loc[zict.index, "Year"], zict, marker="o", label="ICT (z-score)")
    plt.title(f"{country} — Évolution (WB, Robots z, ICT z)")
    plt.xlabel("Année"); plt.grid(True, alpha=0.3); plt.legend()
    plt.tight_layout()
    plt.show()

def plot_scatter(sub, country, xcol):
    """Scatter WellBeing vs une variable, avec droite de tendance."""
    data = sub[[xcol, "Wellbeing"]].dropna()
    if len(data) < 2:
        print(f"• {country}: trop peu de points pour {xcol} (n={len(data)})")
        return None
    plt.figure(figsize=(6,4))
    plt.scatter(data[xcol], data["Wellbeing"], alpha=0.8)
    # droite de tendance
    m, b = np.polyfit(data[xcol].values, data["Wellbeing"].values, 1)
    xs = np.linspace(data[xcol].min(), data[xcol].max(), 100)
    plt.plot(xs, m*xs + b, linestyle="--")
    plt.title(f"{country} — WellBeing vs {xcol}")
    plt.xlabel(xcol); plt.ylabel("WellBeing")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    return m  # pente brute (pour info)

def ols_country(sub, country):
    """Régression OLS WellBeing ~ RobotsInstalled + ICT (selon disponibilité)."""
    y = "Wellbeing"
    X_vars = [v for v in ["RobotsInstalled", "Ict"] if sub[v].notna().sum() >= 6]
    sub = sub.dropna(subset=[y] + X_vars)
    if len(sub) < 8 or not X_vars:
        print(f"⛔ {country}: pas assez de données pour l’OLS ({len(sub)} obs, X={X_vars})")
        return None
    X = sm.add_constant(sub[X_vars])
    model = sm.OLS(sub[y], X).fit()
    print(f"\n📊 {country} — OLS ({len(sub)} obs) — variables: {X_vars}")
    print(model.summary())
    return {
        "Country": country,
        "N": len(sub),
        "R2_adj": model.rsquared_adj,
        **{f"coef_{v}": model.params.get(v, np.nan) for v in X_vars},
        **{f"p_{v}": model.pvalues.get(v, np.nan) for v in X_vars}
    }

# ---------- 3) ANALYSE PAR PAYS ----------
all_results = []
for country in countries:
    sub = df[df["Country"] == country].copy()
    if sub.empty:
        continue
    print("\n" + "="*58)
    print(f"🌍 Analyse du pays : {country} ({len(sub)} lignes)")
    # 1) Séries temporelles
    plot_timeseries(sub, country)
    # 2) Scatter WB vs Robots / ICT
    if sub["RobotsInstalled"].notna().sum() >= 2:
        plot_scatter(sub, country, "RobotsInstalled")
    if sub["Ict"].notna().sum() >= 2:
        plot_scatter(sub, country, "Ict")
    # 3) OLS par pays
    res = ols_country(sub, country)
    if res:
        all_results.append(res)

# ---------- 4) GRAPHIQUE COMBINÉ (comparaison des effets) ----------
# On récupère les coefficients OLS (non standardisés) pour RobotsInstalled et ICT
if all_results:
    res_df = pd.DataFrame(all_results)
    # Pour lisibilité, on normalise les coefficients par l’écart-type de X et de Y (bêta standardisés)
    betas = []
    for _, row in res_df.iterrows():
        ctry = row["Country"]
        sub = df[df["Country"] == ctry].copy()
        # Standardisation
        sub = sub.dropna(subset=["Wellbeing"])
        y_std = sub["Wellbeing"].std(ddof=0)
        for var in ["RobotsInstalled", "Ict"]:
            if f"coef_{var}" in res_df.columns and not pd.isna(row.get(f"coef_{var}", np.nan)):
                x = sub[var].dropna()
                if len(x) >= 2 and y_std not in (0, np.nan):
                    x_std = x.std(ddof=0)
                    if x_std not in (0, np.nan):
                        beta = row[f"coef_{var}"] * (x_std / y_std)
                        betas.append({"Country": ctry, "Variable": var, "BetaStd": beta})
    if betas:
        betas_df = pd.DataFrame(betas)
        # Barres côte à côte par pays
        pivot = betas_df.pivot(index="Country", columns="Variable", values="BetaStd").fillna(0.0)
        plt.figure(figsize=(9.5,4.8))
        width = 0.35
        idx = np.arange(len(pivot.index))
        bar1 = plt.bar(idx - width/2, pivot.get("RobotsInstalled", pd.Series(0, index=pivot.index)), width, label="Robots (β std)")
        bar2 = plt.bar(idx + width/2, pivot.get("Ict", pd.Series(0, index=pivot.index)), width, label="ICT (β std)")
        plt.axhline(0, color="black", linewidth=0.8)
        plt.xticks(idx, pivot.index, rotation=0)
        plt.ylabel("Coefficient standardisé (β)")
        plt.title("Impact estimé (β standardisé) sur le bien-être — comparaison entre pays")
        plt.legend()
        plt.tight_layout()
        plt.show()
    else:
        print("\n⚠️ Impossible de calculer les β standardisés (trop peu de données exploitable).")
else:
    print("\n⚠️ Aucun modèle OLS n’a pu être estimé (données insuffisantes).")
