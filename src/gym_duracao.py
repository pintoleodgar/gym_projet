"""Prever a duração da sessão a partir das calorias, por género."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_predict
from gym_utils import argumentos, carregar, amostras, COR, ROTULO

csv, out = argumentos(__doc__)
df = carregar(csv)
df["cal_k"] = df.cal / df.k                    # calorias corrigidas de género e idade
df["cal_k_bpm"] = df.cal / (df.k * df.avgb)    # fórmula invertida: é a própria duração
cv = KFold(5, shuffle=True, random_state=0)
BASE = ["cal", "male", "mais40"]

def prever(d, cols):
    p = pd.Series(cross_val_predict(LinearRegression(), d[cols], d.dur, cv=cv), index=d.index)
    r2 = 1 - ((p - d.dur) ** 2).sum() / ((d.dur - d.dur.mean()) ** 2).sum()
    return p, r2, (p - d.dur).abs() * 60

# 1. Modelos (as calorias só existem depois da sessão: isto reconstrói a fórmula, não antecipa)
print("== 1. Previsão da duração (validação cruzada, 5 folds) ==")
sets = {"só género": ["male"], "calorias": ["cal"], "calorias + género": ["cal", "male"],
        "calorias + género + idade>40": BASE, "calorias / fator (género, idade)": ["cal_k"],
        "calorias / (fator x BPM médio)": ["cal_k_bpm"]}
for nome, cols in sets.items():
    _, r2, e = prever(df, cols)
    print(f"{nome:34s} R² = {r2:6.3f} | MAE = {e.mean():4.1f} min "
          f"(mulheres {e[df.male == 0].mean():4.1f}, homens {e[df.male == 1].mean():4.1f})")

# 2. Duração prevista por género: média e para as mesmas calorias
print("\n== 2. Duração prevista por género ==")
p, _, _ = prever(df, BASE)
print(pd.DataFrame({"real": df.groupby("gender").dur.mean(), "prevista": p.groupby(df.gender).mean()}).round(3))
m = LinearRegression().fit(df[BASE], df.dur)
print("Modelo: duração = %.3f + %.5f x calorias %+.3f x homem %+.3f x mais de 40" % (m.intercept_, *m.coef_))
bpm = df.avgb.mean()
print(f"\nMinutos para queimar X kcal a {bpm:.0f} BPM (fórmula invertida):")
print(pd.DataFrame({f"{g}, {i}": [c / (bpm * kg * ki) * 60 for c in (600, 900, 1200)]
                    for g, kg in (("Mulher", 5.0), ("Homem", 5.5)) for i, ki in (("até 40", 1.0), ("mais de 40", 0.9))},
                   index=["600 kcal", "900 kcal", "1200 kcal"]).round(0).astype(int))

# 3. Robustez: com e sem as linhas implausíveis
print("\n== 3. Robustez ==")
for nome, d in amostras(df).items():
    _, r2, e = prever(d, BASE)
    mm = LinearRegression().fit(d[BASE], d.dur)
    print(f"{nome}: R² = {r2:.3f}, MAE = {e.mean():.1f} min, efeito de ser homem = {mm.coef_[1]*60:+.1f} min")

# Figura
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
xs = np.array([df.cal.min(), df.cal.max()])
for g, s in df.groupby("gender"):
    ax[0].scatter(s.cal, s.dur, s=10, alpha=.3, color=COR[g])
    b1, b0 = np.polyfit(s.cal, s.dur, 1)
    ax[0].plot(xs, b0 + b1 * xs, color=COR[g], lw=2.5, label=ROTULO[g])
    ax[1].scatter(s.dur, p[s.index], s=10, alpha=.35, color=COR[g], label=ROTULO[g])
ax[0].set(title="Para as mesmas calorias, as mulheres ficam mais tempo",
          xlabel="Calorias queimadas (kcal)", ylabel="Duração da sessão (h)")
ax[1].plot([.5, 2], [.5, 2], color="gray", ls="--", lw=1)
ax[1].set(title="Duração real vs prevista (calorias + género + idade>40)",
          xlabel="Duração real (h)", ylabel="Duração prevista (h)")
for a in ax: a.legend(frameon=False); a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(out / "gym_duracao.png", dpi=130)
