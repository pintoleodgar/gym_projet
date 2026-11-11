"""Auditoria: as provas de que o dataset é sintético."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from gym_utils import argumentos, carregar, COR, ROTULO

csv, out = argumentos(__doc__)
df = carregar(csv)
df["k_obs"] = df.cal / (df.dur * df.avgb)          # fator de calorias observado em cada linha
df["formula"] = df.dur * df.avgb * df.k

# 1. As calorias são uma fórmula
print("== 1. Calorias = duração x BPM médio x k ==")
print(df.groupby(["gender", "mais40"]).k_obs.agg(["mean", "std", "min", "max"]).round(4))
print("Erro máximo da fórmula: %.2f kcal em %d linhas (as calorias vêm arredondadas à unidade)" % ((df.formula - df.cal).abs().max(), len(df)))

# 2. O efeito da idade é um degrau aos 40 anos
print("\n== 2. Fator k médio por idade, à volta dos 40 ==")
print(df[df.age.between(37, 44)].pivot_table(index="age", columns="gender", values="k_obs").round(3))

# 3. O nível de experiência define faixas fixas
print("\n== 3. Mínimo e máximo por nível de experiência ==")
print(df.groupby("exp")[["dur", "freq", "fat"]].agg(["min", "max"]))
print("Dentro de cada nível, a duração segue uma distribuição uniforme?")
for e, g in df.groupby("exp"):
    r = stats.kstest(g.dur, stats.uniform(g.dur.min(), g.dur.max() - g.dur.min()).cdf)
    print(f"  Kolmogorov-Smirnov, nível {e}: estatística={r.statistic:.3f}, p-valor={r.pvalue:.2f} | H0: duração uniforme na faixa")

# 4. Relações que existem em pessoas reais e aqui não
print("\n== 4. Correlações que deviam existir ==")
for a, b, esperado in [("age", "maxb", "negativa (o BPM máximo desce com a idade)"),
                       ("bmi", "fat", "positiva (mais IMC, mais gordura)"),
                       ("exp", "restb", "negativa (quem treina mais tem BPM em repouso mais baixo)"),
                       ("age", "fat", "positiva (a gordura corporal sobe com a idade)")]:
    r, p = stats.pearsonr(df[a], df[b])
    print(f"  Pearson {a} x {b}: r={r:+.3f}, p-valor={p:.2f} | H0: r = 0 | esperado: {esperado}")

# 5. O tipo de treino não distingue nada
print("\n== 5. Tipo de treino ==")
for v in ["dur", "cal", "calh", "avgb", "fat", "freq"]:
    r = stats.f_oneway(*[g[v] for _, g in df.groupby("type")])
    print(f"  ANOVA {v} por tipo: F={r.statistic:.2f}, p-valor={r.pvalue:.2f} | H0: médias iguais nos 4 tipos")
for v in ["gender", "exp"]:
    r = stats.chi2_contingency(pd.crosstab(df.type, df[v]))
    print(f"  Qui-quadrado tipo x {v}: chi2={r.statistic:.2f}, p-valor={r.pvalue:.2f} | H0: independentes")

# 6. Linhas fisicamente implausíveis
print("\n== 6. Linhas implausíveis ==")
print(f"BPM médio >= BPM máximo: {(df.avgb >= df.maxb).sum()} | IMC < 16: {(df.bmi < 16).sum()} | "
      f"IMC > 40: {(df.bmi > 40).sum()} | total: {(~df.plausivel).sum()} de {len(df)} ({(~df.plausivel).mean():.0%})")

# Figura
fig, ax = plt.subplots(1, 4, figsize=(21, 4.8))
for g, s in df.groupby("gender"):
    ax[0].scatter(s.formula, s.cal, s=10, alpha=.4, color=COR[g], label=ROTULO[g])
    m = s.groupby("age").k_obs.mean()
    ax[1].plot(m.index, m, "o-", ms=3.5, color=COR[g], label=ROTULO[g])
    ax[3].scatter(s.age, s.maxb, s=10, alpha=.35, color=COR[g])
lim = [df.cal.min(), df.cal.max()]
ax[0].plot(lim, lim, color="gray", ls="--", lw=1)
ax[0].set(title="As calorias são uma fórmula (erro máx. 0,5 kcal)", xlabel="duração x BPM médio x k", ylabel="Calorias no dataset (kcal)")
ax[1].axvline(40.5, color="gray", ls="--", lw=1)
ax[1].set(title="A idade entra como um degrau aos 40", xlabel="Idade (anos)", ylabel="kcal por batimento-hora (k)")
rng = np.random.default_rng(0)
for e, g in df.groupby("exp"):
    ax[2].scatter(e + rng.uniform(-.25, .25, len(g)), g.dur, s=10, alpha=.4, color="#1f3a5f")
ax[2].set(title="Cada nível tem a sua faixa de duração", xlabel="Nível de experiência", ylabel="Horas por sessão", xticks=[1, 2, 3])
ax[3].plot([18, 59], [202, 161], color="gray", ls="--", lw=1.5, label="220 - idade")
ax[3].set(title="BPM máximo sem relação com a idade (r = %+.2f)" % df.age.corr(df.maxb), xlabel="Idade (anos)", ylabel="BPM máximo")
for a in (ax[0], ax[1], ax[3]): a.legend(frameon=False)
for a in ax: a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(out / "gym_auditoria.png", dpi=130)
