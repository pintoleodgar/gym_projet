# Tabela `membros`

## Referência rápida

**Localização:** `data/gym_members_exercise_tracking.csv`
**Descrição:** um membro por linha, com perfil físico e uma sessão típica. Dataset sintético do Kaggle.
**Chave primária:** não tem; usar o índice da linha.
**Atualização:** ficheiro estático, sem datas.
**Dimensão:** 973 linhas, 15 colunas, sem nulos, sem duplicados.

## Colunas

| Nome curto | Coluna original | Tipo | Intervalo | Notas |
|---|---|---|---|---|
| **age** | Age | int | 18–59 | Aproximadamente uniforme; degrau nas calorias em `age > 40` |
| **gender** | Gender | texto | Male, Female | 511 e 462 |
| **w** | Weight (kg) | float | 40–129,9 | Mulheres 40–79,9; homens 45–129,9 |
| **h** | Height (m) | float | 1,50–2,00 | Mulheres 1,5–1,8; homens 1,6–2,0 |
| **maxb** | Max_BPM | int | 160–199 | Sem relação com a idade |
| **avgb** | Avg_BPM | int | 120–169 | Entra na fórmula das calorias; 28 linhas com `avgb >= maxb` |
| **restb** | Resting_BPM | int | 50–74 | Independente de tudo |
| **dur** | Session_Duration (hours) | float | 0,5–2,0 | Faixa fixa por nível |
| **cal** | Calories_Burned | float | 303–1783 | Calculada: `dur * avgb * k` |
| **type** | Workout_Type | texto | 4 categorias | Independente de tudo |
| **fat** | Fat_Percentage | float | 10–35 | Nível 3: 10–20; níveis 1 e 2: 20–35; mulheres ~5 pontos acima |
| **water** | Water_Intake (liters) | float | 1,5–3,7 | Mulheres 1,5–2,7; homens 2,0–3,7; mais alta no nível 3 |
| **freq** | Workout_Frequency (days/week) | int | 2–5 | Presa ao nível |
| **exp** | Experience_Level | int | 1–3 | Ordinal |
| **bmi** | BMI | float | 12,3–49,8 | `w / h**2`; 68 linhas abaixo de 16, 34 acima de 40 |

## O que determina o quê

- **Género →** intervalos de peso, altura e água; nível base de gordura; fator de calorias.
- **Nível →** faixas de duração, frequência e gordura; água mais alta no nível 3.
- **Idade →** só o fator de calorias (×0,9 acima dos 40).
- **Sem efeito em nada:** tipo de treino, BPM máximo, BPM em repouso.

## Consultas de exemplo

Para SQL, carregar o CSV em SQLite em memória (a correr a partir de `src/`):

```python
import sqlite3
from gym_utils import carregar
df = carregar()
con = sqlite3.connect(":memory:")
df.to_sql("membros", con, index=False)
```

### Duração e calorias por género e nível
```sql
SELECT gender, exp, COUNT(*) AS n,
       ROUND(AVG(dur), 2) AS horas_sessao,
       ROUND(AVG(cal), 0) AS cal_sessao,
       ROUND(AVG(fat), 1) AS gordura
FROM membros
GROUP BY gender, exp
ORDER BY gender, exp;
```

### Calorias por faixa etária, com o corte certo aos 40
```sql
SELECT CASE WHEN age <= 29 THEN '18-29'
            WHEN age <= 40 THEN '30-40'
            WHEN age <= 49 THEN '41-49'
            ELSE '50-59' END AS faixa,
       COUNT(*) AS n,
       ROUND(AVG(cal), 0) AS cal_sessao,
       ROUND(AVG(cal / dur), 0) AS cal_hora
FROM membros
GROUP BY faixa
ORDER BY faixa;
```

### Contar linhas implausíveis
```sql
SELECT SUM(avgb >= maxb) AS bpm_medio_acima_do_maximo,
       SUM(bmi < 16)     AS imc_abaixo_de_16,
       SUM(bmi > 40)     AS imc_acima_de_40,
       SUM(avgb >= maxb OR bmi < 16 OR bmi > 40) AS total_implausiveis
FROM membros;
```

### Verificar a fórmula das calorias em SQL
```sql
WITH f AS (
    SELECT cal,
           dur * avgb
           * (CASE WHEN gender = 'Male' THEN 5.5 ELSE 5.0 END)
           * (CASE WHEN age > 40 THEN 0.9 ELSE 1.0 END) AS cal_formula
    FROM membros
)
SELECT ROUND(MAX(ABS(cal - cal_formula)), 2) AS erro_maximo FROM f;
```

### Tempo para queimar um objetivo de calorias
```python
def minutos(calorias, bpm, homem, mais40):
    k = (5.5 if homem else 5.0) * (0.9 if mais40 else 1.0)
    return calorias / (bpm * k) * 60

minutos(900, 144, homem=False, mais40=False)   # 75
```

## Armadilhas

1. **Peso vs calorias:** a correlação global engana.
   - Errado: `df.w.corr(df.cal)` (0,10)
   - Certo: `df.groupby("gender").apply(lambda g: g.w.corr(g.cal))` (≈ 0)

2. **Clustering com água, peso ou altura:** estas variáveis são um substituto do género e puxam mais homens para o cluster intensivo sem diferença real de comportamento.

3. **Calorias como preditor da duração:** fuga de informação, porque as calorias são calculadas a partir da duração.

4. **Divisão em SQLite:** `cal / dur` funciona porque são reais; com `freq` ou `exp` (inteiros) multiplicar por `1.0`.

## Scripts relacionados

| Script | Faz |
|---|---|
| `gym_calorias.py` | Calorias vs género, idade e peso |
| `gym_clusters.py` | Tempo por género, previsão da duração, K-Means |
| `gym_duracao.py` | Duração prevista a partir das calorias |
