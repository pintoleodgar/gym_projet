# Entidades

## Membro
- **Definição:** uma pessoa inscrita no ginásio, com o seu perfil físico e os valores de uma sessão de treino típica.
- **Tabela:** `membros` (o CSV completo).
- **Identificador:** não existe. Usar o índice da linha se for preciso um ID (`df.reset_index(names="id")`).
- **Contagem:** 973 (511 homens, 462 mulheres).
- **Filtros habituais:** nenhum obrigatório. Para testar a robustez, usar a coluna `plausivel` criada por `gym_utils.carregar()` (847 de 973 linhas).

## Sessão
- **Definição:** o treino descrito em cada linha (duração, BPM, calorias, tipo).
- **Relação com o membro:** 1 para 1. Não há várias sessões por membro.
- **O que isto impede:** histórico, evolução, retenção, assiduidade real, comparação entre sessões do mesmo membro.

## Agrupamentos usados nas análises

| Agrupamento | Como obter | Notas |
|---|---|---|
| Género | `gender` (`Male`, `Female`) | Determina os intervalos de peso, altura e água |
| Nível de experiência | `exp` (1, 2, 3) | 376, 406 e 191 membros |
| Tipo de treino | `type` | 258 Strength, 255 Cardio, 239 Yoga, 221 HIIT |
| Faixa etária | `pd.cut(age, [17, 29, 40, 49, 59])` | Cortar em 40/41 para respeitar o degrau das calorias |
| Classe de IMC | `pd.cut(bmi, [0, 18.5, 25, 30, 100])` | 17% abaixo do peso, 38% normal, 25% excesso, 20% obesidade |
| Cluster | K-Means com k = 2 em `dur, freq, fat, water, bmi, age, avgb` estandardizadas | Resultado negativo: coincide com `exp == 3` (ARI 0,87); guardado em `outputs/gym_com_clusters.csv` |

## Relações entre agrupamentos
- **Género × nível, género × tipo, tipo × nível:** independentes (qui-quadrado p > 0,4).
- **Nível × frequência:** nível 1 treina 2–3 dias, nível 2 treina 3–4, nível 3 treina 4–5. Não há exceções.
- **Género × classe de IMC:** 33% dos homens estão em obesidade contra 5% das mulheres, porque o peso dos homens vai até 130 kg.
