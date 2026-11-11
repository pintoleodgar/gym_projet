# gym_projet

Análise exploratória do dataset `gym_members_exercise_tracking.csv` (973 membros de ginásio, Kaggle): tempo de treino e calorias por género, idade, peso e nível de experiência.

**O dataset é sintético.** As relações encontradas são regras de geração e não se generalizam a ginásios reais.

## Conclusões

- **Tempo no ginásio:** igual nos dois géneros (1,26 h por sessão nas mulheres, 1,25 h nos homens; p = 0,70).
- **Calorias:** são uma fórmula exata, `cal = dur * avgb * k`, com `k = 5,0` (mulheres) ou `5,5` (homens), multiplicado por 0,9 acima dos 40 anos. Erro máximo de 0,5 kcal.
- **Género e idade:** só entram pelo fator `k`. Homens queimam 10% mais por hora; acima dos 40 queima-se 10% menos.
- **Peso:** sem efeito nas calorias. A correlação global (0,10) desaparece dentro de cada género.
- **Nível de experiência:** define faixas fixas de duração, frequência e gordura. É o único preditor útil da duração antes da sessão (R² = 0,62). Dentro de cada nível a duração é aleatória, por isso não se passa daí.
- **Clustering:** resultado negativo. O K-Means (k = 2, silhueta 0,27) reencontra o nível 3 contra os restantes (ARI = 0,87) e não gera segmentos novos.
- **Tipo de treino:** não distingue nenhuma outra variável.
- **Robustez:** 126 linhas (13%) são fisicamente implausíveis. Excluí-las não altera nenhuma conclusão.

## Estrutura

```
data/      CSV original
src/       scripts e gym_utils.py (carregamento e funções comuns)
outputs/   figuras e CSV com clusters, gerados pelos scripts
docs/      entidades, métricas e dicionário de colunas
```

## Como correr

```bash
pip install -r requirements.txt
```

```bash
python src/gym_calorias.py
```

```bash
python src/gym_clusters.py
```

```bash
python src/gym_duracao.py
```

Todos aceitam `--csv` e `--out`; por omissão leem de `data/` e gravam em `outputs/`.

| Script | Faz | Saída |
|---|---|---|
| `gym_calorias.py` | Calorias vs género, idade e peso; regressão log-log | `gym_calorias.png` |
| `gym_clusters.py` | Tempo por género, previsão da duração, K-Means | `gym_clusters.png`, `gym_com_clusters.csv` |
| `gym_duracao.py` | Duração prevista a partir das calorias | `gym_duracao.png` |

## O que cada termo significa

**Uma linha é um membro**, com o perfil físico e os valores de uma sessão típica. Não há ID, datas nem várias sessões por membro.

| Termo | Definição |
|---|---|
| Duração da sessão | `dur`, em horas |
| Horas por semana | `dur * freq`; assume sessões todas iguais |
| Calorias por sessão | `cal` |
| Calorias por hora | `cal / dur`; usar esta para comparar pessoas |
| Mais de 40 | `age > 40`; o corte é em 41 |
| Linha plausível | `avgb < maxb` e IMC entre 16 e 40 (847 de 973) |

Os nomes curtos das colunas estão em `src/gym_utils.py` e descritos em [docs/membros.md](docs/membros.md).

## Erros a evitar

- **Concluir que um género treina mais tempo:** só as calorias diferem, e apenas pelo fator `k`.
- **Ler correlações globais com peso, altura ou água:** dependem do género. Calcular dentro de cada género.
- **Ajustar uma reta a idade vs calorias:** o efeito é um degrau aos 40 anos.
- **Apresentar R² ≈ 1 nas calorias como bom modelo:** é a fórmula recuperada.
- **Prever a duração com as calorias:** as calorias só existem depois da sessão e são calculadas a partir da duração.
- **Tratar o nível de experiência como numérico:** os degraus não são iguais (1,01, 1,25 e 1,76 h). Usar dummies.
- **Juntar frequência e nível no mesmo modelo:** são quase a mesma variável (r = 0,84).

Mais detalhe em [docs/metricas.md](docs/metricas.md) e [docs/entidades.md](docs/entidades.md).
