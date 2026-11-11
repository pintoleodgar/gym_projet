# Métricas

## Definições

| Métrica | Definição | Fórmula | Notas |
|---|---|---|---|
| Calorias por sessão | Energia gasta no treino | `cal` = `dur * avgb * k` | Determinística, erro máximo 0,5 kcal |
| Fator de calorias | kcal por batimento-hora | `k = (5.5 se Male, 5.0 se Female) * (0.9 se age > 40)` | Único sítio onde género e idade entram |
| Calorias por hora | Intensidade energética | `cal / dur` | Igual a `avgb * k` |
| Duração da sessão | Tempo de um treino, em horas | `dur` | Faixa fixa por nível de experiência |
| Horas por semana | Tempo semanal estimado | `dur * freq` | Assume sessões todas iguais |
| IMC | Índice de massa corporal | `w / h**2` | Já vem na coluna `bmi` |
| Reserva cardíaca usada | Intensidade relativa | `(avgb - restb) / (maxb - restb)` | Chega ou passa de 1 nas 28 linhas com `avgb >= maxb` |

## Valores de referência

### Por género
| | Mulheres | Homens | Diferença | Significância |
|---|---|---|---|---|
| Horas por sessão | 1,26 | 1,25 | −0,01 | p = 0,70 |
| Dias por semana | 3,34 | 3,31 | — | — |
| Horas por semana | 4,41 | 4,35 | −0,06 | p = 0,68 |
| Calorias por sessão | 862 | 944 | +82 | p < 0,001, d = 0,31 |
| Calorias por hora | 684 | 753 | +69 | p < 0,001, d = 0,86 |
| % de gordura | 27,7 | 22,6 | — | — |
| Água (L/dia) | 2,21 | 3,01 | — | — |

### Por nível de experiência
| Nível | n | Duração (h) | Dias/semana | % gordura | Calorias |
|---|---|---|---|---|---|
| 1 | 376 | 0,5–1,5 (média 1,01) | 2–3 | 20–35 (média 27,6) | 726 |
| 2 | 406 | 1,0–1,5 (média 1,25) | 3–4 | 20–35 (média 27,3) | 902 |
| 3 | 191 | 1,5–2,0 (média 1,76) | 4–5 | 10–20 (média 14,8) | 1265 |

### Por faixa etária
| Faixa | n | Calorias por sessão | Calorias por hora |
|---|---|---|---|
| 18–29 | 276 | 950 | 753 |
| 30–40 | 234 | 941 | 752 |
| 41–49 | 220 | 893 | 691 |
| 50–59 | 243 | 832 | 680 |

## Resultados de modelos já validados (validação cruzada, 5 folds)

### Prever a duração da sessão
| Variáveis | R² | Erro médio |
|---|---|---|
| Só género | ≈ 0 | 16 min |
| Género + nível como número | 0,58 | 11 min |
| Género + nível em dummies | 0,62 | 10 min |
| Calorias | 0,82 | 7 min |
| Calorias + género + mais de 40 | 0,87 | 6 min |
| `cal / (k * avgb)` | 1,00 | 0 min |

As calorias só existem depois da sessão. Para prever com antecedência, o limite é R² ≈ 0,62: dentro de cada nível a duração é aleatória (R² do perfil físico entre −0,03 e −0,10). A frequência não acrescenta nada ao nível (r = 0,84 entre as duas).

### Prever as calorias
| Variáveis | R² |
|---|---|
| Género + mais de 40 + peso | 0,05 |
| Duração | 0,82 |
| Duração + BPM médio | 0,93 |
| Duração + BPM médio + idade + género (linear) | 0,98 |
| Log-log: `log(cal) ~ log(dur) + log(avgb) + homem + mais40` | 1,00 |

No modelo log-log os expoentes de `dur` e `avgb` são 1,00, e os fatores são ×1,10 (homem) e ×0,90 (mais de 40). O peso não é significativo (p = 0,28). Como o alvo é um produto, o modelo aditivo é o errado; usar sempre o log-log.

## Robustez (973 linhas contra as 847 plausíveis)

| Resultado | Todas | Plausíveis |
|---|---|---|
| Calorias, homens − mulheres | +82 | +89 |
| Calorias, até 40 − mais de 40 | +85 | +73 |
| Horas por sessão, homens − mulheres | −0,01 | 0,00 |
| R² da duração com o nível em dummies | 0,62 | 0,63 |
| Silhueta do K-Means (k = 2) | 0,27 | 0,28 |
| ARI dos clusters contra o nível 3 | 0,87 | 0,91 |

Nenhuma conclusão muda.

## Cuidados
- **Correlações globais com peso, altura ou água:** são efeito do género. Calcular dentro de cada género.
- **Correlações globais com duração, frequência ou gordura:** são efeito do nível. Dentro de cada nível, duração vs gordura fica entre −0,05 e 0,14.
- **Significância com n = 973:** efeitos pequenos dão p baixo. Reportar sempre o tamanho do efeito.
