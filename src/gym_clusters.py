"""Tempo no ginásio por género, previsão da duração e clustering (resultado negativo)."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from gym_utils import argumentos, carregar, amostras, welch, COR, ROTULO

csv, out = argumentos(__doc__)
df = carregar(csv)
df = df.join(pd.get_dummies(df.exp, prefix="exp", drop_first=True, dtype=int))   # exp_2, exp_3
M, F = df[df.male == 1], df[df.male == 0]
cv = KFold(5, shuffle=True, random_state=0)
FISICO = ["male", "age", "w", "h", "fat", "water", "avgb", "restb"]

def r2_mae(d, cols):
    r2 = cross_val_score(LinearRegression(), d[cols], d.dur, cv=cv, scoring="r2").mean()
    mae = -cross_val_score(LinearRegression(), d[cols], d.dur, cv=cv, scoring="neg_mean_absolute_error").mean()
    return r2, mae * 60

# 1. Diferença entre géneros
print("== 1. Tempo por género ==")
print(df.groupby("gender")[["dur", "freq", "week"]].mean().round(3))
welch(M.dur, F.dur, "Horas por sessão (H - M)")
welch(M.week, F.week, "Horas por semana (H - M)")
print(df.pivot_table(index="exp", columns="gender", values="dur").round(3))

# 2. Previsão da duração (sem calorias: são calculadas a partir da duração;
#    sem frequência: é quase a mesma variável que o nível)
print("\n== 2. Previsão da duração (validação cruzada, 5 folds) ==")
print("r(freq, exp) = %.2f" % df.freq.corr(df.exp))
sets = {"género": ["male"],
        "género + perfil físico": FISICO,
        "género + nível (numérico)": ["male", "exp"],
        "género + nível (dummies)": ["male", "exp_2", "exp_3"],
        "género + nível (dummies) + freq": ["male", "exp_2", "exp_3", "freq"],
        "perfil físico + nível (dummies)": FISICO + ["exp_2", "exp_3"]}
for nome, cols in sets.items():
    print("%-34s R² = %6.3f   MAE = %4.1f min" % (nome, *r2_mae(df, cols)))
print("Porque o teto é ~0,6: dentro de cada nível a duração não se prevê com mais nada.")
for e, g in df.groupby("exp"):
    print("  nível %d (n=%d): R² do perfil físico = %+.3f | duração %.2f-%.2f h, desvio-padrão %.2f"
          % (e, len(g), r2_mae(g, FISICO)[0], g.dur.min(), g.dur.max(), g.dur.std()))

# 3. Clustering (sem género, calorias e nível, para os cruzar depois)
print("\n== 3. K-Means (variáveis estandardizadas) ==")
feats = ["dur", "freq", "fat", "water", "bmi", "age", "avgb"]
X = StandardScaler().fit_transform(df[feats])
ks = range(1, 9)
fits = {k: KMeans(k, n_init=20, random_state=0).fit(X) for k in ks}
inercia = {k: fits[k].inertia_ for k in ks}
sil = {k: silhouette_score(X, fits[k].labels_) for k in ks if k > 1}
print(pd.DataFrame({"inércia": inercia, "queda_%": pd.Series(inercia).pct_change().mul(-100), "silhueta": sil}).round(3))
k = max(sil, key=sil.get)
lab = fits[k].labels_
order = df.assign(c=lab).groupby("c").dur.mean().sort_values().index      # 1 = sessões mais curtas
df["cluster"] = pd.Series(lab).map({c: i + 1 for i, c in enumerate(order)}).values
print(f"k = {k} (silhueta {sil[k]:.2f}: estrutura fraca, abaixo de 0,5)")
print("Estabilidade entre sementes (ARI): %.3f" % np.mean(
    [adjusted_rand_score(lab, KMeans(k, n_init=20, random_state=s).fit_predict(X)) for s in range(1, 6)]))
print("ARI contra 'nível 3 vs resto': %.2f" % adjusted_rand_score(df.exp == 3, df.cluster))
print(pd.crosstab(df.cluster, df.exp))
print(df.groupby("cluster").agg(n=("dur", "size"), dur=("dur", "mean"), freq=("freq", "mean"), fat=("fat", "mean"),
                                water=("water", "mean"), pct_homens=("male", "mean")).round(2))
print("Conclusão: resultado negativo. O clustering reencontra o nível 3 e não gera segmentos novos.")
df.drop(columns=["exp_2", "exp_3"]).to_csv(out / "gym_com_clusters.csv", index=False)

# 4. Robustez: com e sem as linhas implausíveis
print("\n== 4. Robustez ==")
for nome, d in amostras(df).items():
    Xd = StandardScaler().fit_transform(d[feats])
    ld = KMeans(k, n_init=20, random_state=0).fit_predict(Xd)
    print(f"{nome}: horas/sessão H-M = {d.dur[d.male == 1].mean()-d.dur[d.male == 0].mean():+.3f} | "
          f"R² nível (dummies) = {r2_mae(d, ['male', 'exp_2', 'exp_3'])[0]:.3f} | "
          f"silhueta = {silhouette_score(Xd, ld):.2f} | ARI vs nível 3 = {adjusted_rand_score(d.exp == 3, ld):.2f}")

# Figura
fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
bins = np.arange(0.5, 2.05, 0.1)
for g, s in df.groupby("gender"):
    ax[0].hist(s.dur, bins=bins, histtype="step", lw=2, color=COR[g], label=f"{ROTULO[g]} (média {s.dur.mean():.2f} h)")
ax[0].set(title="Duração da sessão por género", xlabel="Horas por sessão", ylabel="Membros"); ax[0].legend(frameon=False)
ax[1].plot(list(ks), [inercia[i] for i in ks], "o-", color="#444444")
ax[1].set(title="Cotovelo e silhueta", xlabel="Número de clusters (k)", ylabel="Inércia")
a2 = ax[1].twinx(); a2.plot(list(sil), list(sil.values()), "s--", color="#d55e00")
a2.set_ylabel("Silhueta", color="#d55e00"); a2.set_ylim(0, .5); a2.spines["top"].set_visible(False)
P = PCA(2).fit(X); Z = P.transform(X)
for c, cor in zip(sorted(df.cluster.unique()), ["#e69f00", "#0072b2", "#009e73", "#cc79a7", "#56b4e9", "#d55e00", "#f0e442", "#999999"]):
    i = (df.cluster == c).values
    ax[2].scatter(Z[i, 0], Z[i, 1], s=12, alpha=.7, color=cor, label=f"Cluster {c} (n={i.sum()})")
ax[2].set(title="Clusters: o cluster 2 é o nível 3", xlabel=f"CP1 ({P.explained_variance_ratio_[0]:.0%})",
          ylabel=f"CP2 ({P.explained_variance_ratio_[1]:.0%})"); ax[2].legend(frameon=False)
for a in ax: a.spines[["top"]].set_visible(False)
ax[0].spines["right"].set_visible(False); ax[2].spines["right"].set_visible(False)
fig.tight_layout(); fig.savefig(out / "gym_clusters.png", dpi=130)
