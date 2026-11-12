# Post LinkedIn: gym_projet

Fui fazer uma análise simples a um dataset de ginásio do Kaggle e acabei a provar que os dados eram inventados.

Era para ser rotina: quem treina mais tempo, o que explica as calorias, que tipos de membros existem. Mas uma regressão deu R² de 1,00, e isso não acontece com pessoas.

Fui ver como os dados tinham sido feitos. Em cinco testes:

1. As calorias são uma conta exata, duração x BPM x um fator fixo. Erro máximo de 0,5 kcal em 973 linhas.
2. A idade entra como um interruptor aos 41 anos. Não há declínio gradual.
3. O nível de experiência define faixas sem uma única exceção.
4. Faltam relações que existem em qualquer amostra real, como o BPM máximo descer com a idade.
5. Uma hora de yoga e uma hora de HIIT queimam o mesmo.

Nada disto serve para gerir um ginásio. Mas serve para uma coisa: antes de construir modelos, testar se o alvo é uma fórmula das outras colunas. Nenhuma métrica de validação apanha isso sozinha.

Código, figuras e os cinco testes no GitHub: github.com/pintoleodgar/gym_projet

#DataScience #Python #Portfolio
