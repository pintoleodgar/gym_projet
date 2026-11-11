"""Calorias vs género, idade e peso."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from scipy import stats
from gym_utils import argumentos, carregar, amostras, welch, COR, ROTULO

csv, out = argumentos(__doc__)
df = carregar(csv)
M, F = df[df.male == 1], df[df.male == 0]

# 1. Calorias vs género
print("== 1. Calorias vs género ==")
print(df.groupby("gender")[["cal", "calh", "dur", "avgb"]].mean().round(2))
welch(M.cal, F.cal, "Calorias por sessão (H - M)")
welch(M.calh, F.calh, "Calorias por hora   (H - M)")

# 2. Idade vs calorias
print("\n== 2. Idade vs calorias ==")
print("Pearson r = %.3f (p = %.2g)" % stats.pearsonr(df.age, df.cal))
df["faixa"] = pd.cut(df.age, [17, 29, 40, 49, 59], labels=["18-29", "30-40", "41-49", "50-59"])
print(df.groupby("faixa", observed=True).agg(n=("cal", "size"), cal=("cal", "mean"), calh=("calh", "mean")).round(1))
welch(df.cal[df.mais40 == 0], df.cal[df.mais40 == 1], "Calorias (<=40 - >40)")
for nome, g in [("<= 40 anos", df[df.mais40 == 0]), ("> 40 anos", df[df.mais40 == 1])]:
    print("Dentro de %s: r(idade, calorias) = %+.3f, p = %.2f" % (nome, *stats.pearsonr(g.age, g.cal)))

# 3. Peso vs calorias
print("\n== 3. Peso vs calorias ==")
print("Global: r = %.3f (p = %.2g)" % stats.pearsonr(df.w, df.cal))
for g, s in df.groupby("gender"):
    print("%s: r = %+.3f, p = %.2f" % (ROTULO[g], *stats.pearsonr(s.w, s.cal)))
df["qpeso"] = pd.qcut(df.w, 4, labels=["Q1 (leves)", "Q2", "Q3", "Q4 (pesados)"])
print(df.groupby("qpeso", observed=True).agg(peso=("w", "mean"), cal=("cal", "mean"), pct_homens=("male", "mean")).round(2))

# 4. Efeitos em conjunto: o alvo é multiplicativo, por isso modelo log-log
print("\n== 4. Regressão log-log: log(cal) ~ log(dur) + log(avgb) + homem + mais40 + log(peso) ==")
m = smf.ols("np.log(cal) ~ np.log(dur) + np.log(avgb) + male + mais40 + np.log(w)", df).fit()
t = pd.concat([m.params, m.conf_int(), m.pvalues], axis=1); t.columns = ["coef", "ic_inf", "ic_sup", "p"]
print(t.round(4)); print("R² = %.5f" % m.rsquared)
print("Fatores multiplicativos: homem x%.3f, mais de 40 x%.3f" % (np.exp(m.params["male"]), np.exp(m.params["mais40"])))
print("Só género + mais40 + peso: R² = %.3f" % smf.ols("np.log(cal) ~ male + mais40 + np.log(w)", df).fit().rsquared)

# 5. Robustez: com e sem as linhas implausíveis
print("\n== 5. Robustez ==")
for nome, d in amostras(df).items():
    h, f = d[d.male == 1], d[d.male == 0]
    print(f"{nome}: calorias H-M = {h.cal.mean()-f.cal.mean():+.0f} | <=40 - >40 = "
          f"{d.cal[d.mais40 == 0].mean()-d.cal[d.mais40 == 1].mean():+.0f} | r(peso, cal) mulheres {f.w.corr(f.cal):+.2f}, "
          f"homens {h.w.corr(h.cal):+.2f} | erro máx. da fórmula = {(d.dur*d.avgb*d.k-d.cal).abs().max():.1f} kcal")

# Figura
fig, ax = plt.subplots(1, 3, figsize=(17, 5))
bp = ax[0].boxplot([F.cal, M.cal], widths=.5, patch_artist=True, medianprops=dict(color="white", lw=2))
for b, g in zip(bp["boxes"], ["Female", "Male"]): b.set(facecolor=COR[g], edgecolor=COR[g])
ax[0].set_xticks([1, 2], [f"Mulheres\nmédia {F.cal.mean():.0f} kcal", f"Homens\nmédia {M.cal.mean():.0f} kcal"])
ax[0].set(title="Calorias por sessão e género", ylabel="Calorias queimadas (kcal)")
for g, s in df.groupby("gender"):
    ax[1].scatter(s.age, s.cal, s=10, alpha=.3, color=COR[g])
    med = s.groupby("age").cal.mean()
    ax[1].plot(med.index, med.rolling(3, center=True, min_periods=1).mean(), color=COR[g], lw=2.5, label=ROTULO[g])
    ax[2].scatter(s.w, s.cal, s=10, alpha=.3, color=COR[g])
    b1, b0 = np.polyfit(s.w, s.cal, 1); xs = np.array([s.w.min(), s.w.max()])
    ax[2].plot(xs, b0 + b1 * xs, color=COR[g], lw=2.5, label=f"{ROTULO[g]} (r = {s.w.corr(s.cal):+.2f})")
ax[1].axvline(40.5, color="gray", ls="--", lw=1); ax[1].text(41, df.cal.max(), "40 anos", color="gray", va="top")
ax[1].set(title="Idade vs calorias (linha: média móvel por idade)", xlabel="Idade (anos)", ylabel="Calorias queimadas (kcal)")
ax[2].set(title="Peso vs calorias", xlabel="Peso (kg)", ylabel="Calorias queimadas (kcal)")
ax[1].legend(frameon=False, loc="lower left"); ax[2].legend(frameon=False, loc="upper right")
for a in ax: a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(out / "gym_calorias.png", dpi=130)
