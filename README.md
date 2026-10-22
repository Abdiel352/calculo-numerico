# Raízes pelo método da bissecção

Este projeto contém um programa Python que recebe uma função de `x`, procura automaticamente um intervalo adequado e calcula uma raiz real pelo método da bissecção.

## Como executar

É necessário ter Python 3.10 ou mais recente instalado. Abra o PowerShell nesta pasta e execute:

```powershell
python .\bisseccao.py
```

Quando o programa pedir `f(x)`, digite uma expressão. Exemplos:

```text
x**2 - 2
x^2 - 5x + 4
cos(x) - x
exp(x) - 5
x^3 + x - 1
```

O operador de potência pode ser escrito como `**` ou `^`. Use ponto para casas decimais, por exemplo `0.25`.

O programa também entende multiplicação implícita da forma usada em matemática. Por exemplo, `5x`, `2(x + 1)`, `(x + 1)(x - 1)` e `3sin(x)` são convertidos automaticamente para a sintaxe do Python.

## Como o programa funciona

### 1. Leitura segura da função

A função é transformada em uma árvore sintática com o módulo `ast`. O programa aceita apenas números, `x`, operadores aritméticos, constantes matemáticas e funções da lista permitida. Isso evita executar comandos arbitrários digitados na entrada.

Constantes disponíveis: `pi`, `e` e `tau`.

Funções disponíveis: `abs`, `acos`, `asin`, `atan`, `ceil`, `cos`, `cosh`, `exp`, `floor`, `log`, `log10`, `sen`, `sin`, `sinh`, `sqrt`, `tan` e `tanh`.

### 2. Busca automática do intervalo

O método da bissecção precisa de dois pontos `a` e `b` nos quais os valores da função tenham sinais opostos. Pelo Teorema do Valor Intermediário, uma função contínua que troca de sinal nesse intervalo possui pelo menos uma raiz nele.

O programa começa examinando `[-10, 10]`. Se não encontrar uma raiz ou troca de sinal, expande a busca em blocos de 10 unidades, examinando os dois lados da reta, até chegar a `-1000` e `1000`.

Cada bloco é amostrado a cada `0.5` unidade. Essa amostragem é importante: testar somente os extremos de `[-10, 10]` não encontraria, por exemplo, as duas raízes de `x² - 4`, pois a função é positiva nos dois extremos.

### 3. Bissecção

Depois de obter `[a, b]`, o programa calcula o ponto médio:

```text
m = (a + b) / 2
```

Em seguida, mantém a metade em que ocorre a troca de sinal e descarta a outra metade. Esse processo é repetido até uma destas condições ser satisfeita:

- o erro relativo aproximado entre dois pontos médios consecutivos ser menor ou igual a `0.00005`;
- o ponto médio ser uma raiz exata;
- atingir o limite de `10.000` iterações.

Assim, `0.00005` é usado como tolerância para o erro relativo aproximado: `abs((x_atual - x_anterior) / x_atual)`. Esse valor equivale a `0,005%`. O programa também mostra `|f(x)|` como informação adicional; ele é o resíduo absoluto da função, não o erro relativo. Se a aproximação estiver muito próxima de zero, o programa usa a diferença absoluta entre os pontos médios para evitar divisão por zero.

Na prática, para um intervalo de tamanho moderado, a bissecção converge muito antes de 10.000 iterações.

## Organização das principais partes

- `criar_funcao`: valida e compila a expressão digitada.
- `avaliar`: avalia um ponto e ignora valores fora do domínio durante a busca.
- `examinar_trecho`: procura uma raiz aproximada ou uma troca de sinal em um bloco.
- `encontrar_intervalo`: amplia a busca de ±10 até ±1000.
- `bisseccao`: reduz o intervalo repetidamente até atingir a precisão pedida.
- `main`: conversa com o usuário e mostra o resultado.

## Limitações matemáticas

Nenhum método numérico consegue garantir que encontrará uma raiz de absolutamente qualquer função sem hipóteses adicionais.

- A bissecção pressupõe continuidade no intervalo escolhido. Uma descontinuidade como a de `1/x` pode parecer uma troca de sinal sem existir raiz.
- Uma raiz que apenas toca o eixo, sem trocar de sinal, pode não ser detectada se não estiver perto de um dos pontos amostrados. Exemplo: `(x - 0.123456)**2`.
- Oscilações muito rápidas podem ocorrer entre os pontos da malha de `0.5` e passar despercebidas.
- O programa procura somente no intervalo de `-1000` a `1000` e retorna a primeira raiz detectada na busca do centro para fora.

Para aumentar a sensibilidade, diminua `PASSO_AMOSTRAGEM`. Isso fará mais avaliações e poderá tornar a busca mais lenta.
