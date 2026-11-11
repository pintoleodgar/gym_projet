"""Carregamento, caminhos e funções comuns aos scripts do gym_projet."""
import argparse
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "data" / "gym_members_exercise_tracking.csv"
OUT = RAIZ / "outputs"

NOMES = {"Age": "age", "Gender": "gender", "Weight (kg)": "w", "Height (m)": "h",
         "Max_BPM": "maxb", "Avg_BPM": "avgb", "Resting_BPM": "restb",
         "Session_Duration (hours)": "dur", "Calories_Burned": "cal", "Workout_Type": "type",
         "Fat_Percentage": "fat", "Water_Intake (liters)": "water",
         "Workout_Frequency (days/week)": "freq", "Experience_Level": "exp", "BMI": "bmi"}
COR = {"Female": "#b8336a", "Male": "#1f6f8b"}
ROTULO = {"Female": "Mulheres", "Male": "Homens"}


def argumentos(descricao):
    """CLI comum: --csv e --out, ambos com valor por omissão."""
    p = argparse.ArgumentParser(description=descricao)
    p.add_argument("--csv", type=Path, default=CSV, help="CSV de entrada")
    p.add_argument("--out", type=Path, default=OUT, help="pasta de saída")
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 200)
    return a.csv, a.out


def carregar(csv=CSV):
    """Lê o CSV, renomeia por nome de coluna e acrescenta as variáveis derivadas."""
    df = pd.read_csv(csv)
    falta = set(NOMES) - set(df.columns)
    if falta:
        raise KeyError(f"Colunas em falta no CSV: {sorted(falta)}")
    df = df.rename(columns=NOMES)
    df["male"] = (df.gender == "Male").astype(int)
    df["mais40"] = (df.age > 40).astype(int)
    df["k"] = np.where(df.male == 1, 5.5, 5.0) * np.where(df.mais40 == 1, 0.9, 1.0)  # kcal por batimento-hora
    df["calh"] = df.cal / df.dur                     # calorias por hora
    df["week"] = df.dur * df.freq                    # horas por semana
    df["plausivel"] = (df.avgb < df.maxb) & df.bmi.between(16, 40)
    return df


def amostras(df):
    """Amostra completa e só as linhas fisicamente plausíveis, para testar a robustez."""
    p = df[df.plausivel]
    return {f"todas ({len(df)})": df, f"plausíveis ({len(p)})": p}


def welch(a, b, nome):
    """Diferença de médias a - b com IC 95% de Welch, p e d de Cohen."""
    r = stats.ttest_ind(a, b, equal_var=False)
    ic = r.confidence_interval()
    d = a.mean() - b.mean()
    sp = np.sqrt((a.var() + b.var()) / 2)
    print(f"{nome}: dif = {d:+.3g}, IC95% [{ic.low:+.3g}; {ic.high:+.3g}], p = {r.pvalue:.2g}, d de Cohen = {d/sp:+.2f}")
    return d
