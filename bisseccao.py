"""Encontra uma raiz real usando busca automática e método da bissecção."""

from __future__ import annotations

import ast
import math
import re
from collections.abc import Callable



ERRO_ACEITAVEL = 0.0000000005
MAX_ITERACOES = 10_000
LIMITE_BUSCA = 10_000 
INCREMENTO_BUSCA = 10
PASSO_AMOSTRAGEM = 0.5


FUNCOES_PERMITIDAS: dict[str, Callable[..., float]] = {
    "abs": abs,
    "acos": math.acos,
    "asin": math.asin,
    "atan": math.atan,
    "ceil": math.ceil,
    "cos": math.cos,
    "cosh": math.cosh,
    "exp": math.exp,
    "floor": math.floor,
    "log": math.log,
    "log10": math.log10,
    "sen": math.sin,
    "sin": math.sin,
    "sinh": math.sinh,
    "sqrt": math.sqrt,
    "tan": math.tan,
    "tanh": math.tanh,
}

CONSTANTES_PERMITIDAS = {"pi": math.pi, "e": math.e, "tau": math.tau}

TIPOS_AST_PERMITIDOS = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.UAdd,
    ast.USub,
)

"""5x(x^3) -- > 5*x*(x**3)"""
def normalizar_expressao(expressao: str) -> str:
    """Converte multiplicações implícitas, como 5x e 2(x+1), em multiplicações explícitas."""
    expressao = expressao.strip().replace("^", "**")
    padrao = re.compile(
        r"(?P<NUMBER>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
        r"|(?P<NAME>[A-Za-z_]\w*)"
        r"|(?P<POW>\*\*)"
        r"|(?P<OP>[+\-*/%(),])"
        r"|(?P<SPACE>\s+)"
        r"|(?P<MISMATCH>.)"
    )
    tokens: list[tuple[str, str]] = []

    for correspondencia in padrao.finditer(expressao):
        tipo = correspondencia.lastgroup
        valor = correspondencia.group()
        if tipo == "SPACE":
            continue
        if tipo == "MISMATCH":
            raise ValueError(f"Caractere não permitido: {valor!r}.")
        if tipo == "OP" and valor == "(":
            tipo = "LPAREN"
        elif tipo == "OP" and valor == ")":
            tipo = "RPAREN"
        tokens.append((tipo or "", valor))

    resultado: list[str] = []
    tipos_finais = {"NUMBER", "NAME", "RPAREN"}
    tipos_iniciais = {"NUMBER", "NAME", "LPAREN"}

    for indice, (tipo, valor) in enumerate(tokens):
        if indice:
            tipo_anterior, valor_anterior = tokens[indice - 1]
            precisa_multiplicar = tipo_anterior in tipos_finais and tipo in tipos_iniciais
            chamada_de_funcao = (
                tipo_anterior == "NAME"
                and tipo == "LPAREN"
                and valor_anterior in FUNCOES_PERMITIDAS
            )
            if precisa_multiplicar and not chamada_de_funcao:
                resultado.append("*")
        resultado.append(valor)

    return "".join(resultado)

"""5y(5x)-- 5*y*5*x"""
def criar_funcao(expressao: str) -> Callable[[float], float]:
    """Converte uma expressão matemática segura em uma função de x."""
    expressao = normalizar_expressao(expressao)
    if not expressao:
        raise ValueError("A expressão não pode estar vazia.")

    try:
        arvore = ast.parse(expressao, mode="eval")
    except SyntaxError as erro:
        raise ValueError("Expressão inválida. Exemplo válido: x**2 - 2") from erro

    nomes_validos = {"x", *FUNCOES_PERMITIDAS, *CONSTANTES_PERMITIDAS}
    for no in ast.walk(arvore):
        if not isinstance(no, TIPOS_AST_PERMITIDOS):
            raise ValueError(f"Operação não permitida: {type(no).__name__}.")
        if isinstance(no, ast.Name) and no.id not in nomes_validos:
            raise ValueError(f"Nome não permitido: {no.id!r}.")
        if isinstance(no, ast.Call):
            if not isinstance(no.func, ast.Name) or no.func.id not in FUNCOES_PERMITIDAS:
                raise ValueError("Use somente as funções matemáticas permitidas.")
            if no.keywords:
                raise ValueError("Argumentos nomeados não são permitidos.")

    codigo = compile(arvore, "<funcao>", "eval")
    ambiente = {**FUNCOES_PERMITIDAS, **CONSTANTES_PERMITIDAS}

    def funcao(x: float) -> float:
        valor = eval(codigo, {"__builtins__": {}}, {**ambiente, "x": x})
        valor = float(valor)
        if not math.isfinite(valor):
            raise ValueError("A função produziu um valor não finito.")
        return valor

    return funcao

def avaliar(funcao: Callable[[float], float], x: float) -> float | None:
    """Avalia a função; pontos fora do domínio são ignorados na busca."""
    try:
        return funcao(x)
    except (ArithmeticError, OverflowError, ValueError):
        return None




def examinar_trecho(
    funcao: Callable[[float], float], inicio: float, fim: float
) -> tuple[float, float] | None:
    """Procura raiz ou troca de sinal em um trecho, usando uma malha fina."""
    quantidade = max(1, math.ceil((fim - inicio) / PASSO_AMOSTRAGEM))
    x_anterior = inicio
    f_anterior = avaliar(funcao, x_anterior)


    if f_anterior == 0:
        return x_anterior, x_anterior

    for indice in range(1, quantidade + 1):
        x_atual = inicio + (fim - inicio) * indice / quantidade
        f_atual = avaliar(funcao, x_atual)

        if f_atual == 0:
            return x_atual, x_atual

        if (
            f_anterior is not None
            and f_atual is not None
            and f_anterior * f_atual < 0
        ):
            return x_anterior, x_atual

        x_anterior, f_anterior = x_atual, f_atual

    return None


def encontrar_intervalo(
    funcao: Callable[[float], float],
) -> tuple[float, float] | None:
    """Busca do centro para fora, ampliando de ±10 até ±10000."""
    intervalo = examinar_trecho(funcao, -INCREMENTO_BUSCA, INCREMENTO_BUSCA)
    if intervalo is not None:
        return intervalo

    limite_anterior = INCREMENTO_BUSCA
    for limite in range(2 * INCREMENTO_BUSCA, LIMITE_BUSCA + 1, INCREMENTO_BUSCA):
        # Examina primeiro o novo trecho negativo e depois o positivo.
        intervalo = examinar_trecho(funcao, -limite, -limite_anterior)
        if intervalo is not None:
            return intervalo

        intervalo = examinar_trecho(funcao, limite_anterior, limite)
        if intervalo is not None:
            return intervalo

        limite_anterior = limite

    return None


def bisseccao(
    funcao: Callable[[float], float], a: float, b: float
) -> tuple[float, int, float, float]:
    """Aplica bissecção e retorna raiz, iterações, resíduo e erro relativo."""
    fa = funcao(a)
    fb = funcao(b)

    if fa == 0:
        return a, 0, abs(fa), 0.0
    if fb == 0:
        return b, 0, abs(fb), 0.0
    if fa * fb > 0:
        raise ValueError("O intervalo não contém uma troca de sinal.")

    meio_anterior: float | None = None
    erro_relativo = math.inf
    for iteracao in range(1, MAX_ITERACOES + 1):
        meio = (a + b) / 2
        fm = funcao(meio)

        if fm == 0:
            return meio, iteracao, abs(fm), 0.0

        if meio_anterior is not None:
            if abs(meio) < 1e-15:
                # Próximo de zero, a divisão tornaria o erro relativo instável.
                erro_relativo = abs(meio - meio_anterior)
            else:
                erro_relativo = abs((meio - meio_anterior) / meio)

            if erro_relativo <= ERRO_ACEITAVEL:
                return meio, iteracao, abs(fm), erro_relativo

        if fa * fm < 0:
            b, fb = meio, fm
        else:
            a, fa = meio, fm
        meio_anterior = meio

    meio = (a + b) / 2
    return meio, MAX_ITERACOES, abs(funcao(meio)), erro_relativo


def main() -> None:
    print("Localizador de raízes pelo método da bissecção")
    print("Exemplos: x**2 - 2 | x^2 - 5x + 4 | cos(x) - x | 2(x + 1)")
    expressao = input("Digite f(x): ")

    try:
        funcao = criar_funcao(expressao)
        intervalo = encontrar_intervalo(funcao)

        if intervalo is None:
            print("\nNenhuma raiz foi detectada entre -10000 e 10000.")
            print("A função pode não ter raiz real, não trocar de sinal ou ter uma raiz muito estreita.")
            return

        a, b = intervalo
        if a == b:
            raiz, iteracoes, residuo, erro_relativo = a, 0, abs(funcao(a)), 0.0
            print(f"\nRaiz detectada durante a busca: x ~= {raiz:.10g}")
        else:
            print(f"\nIntervalo encontrado: [{a:.10g}, {b:.10g}]")
            raiz, iteracoes, residuo, erro_relativo = bisseccao(funcao, a, b)
            print(f"Raiz aproximada: x ~= {raiz:.10g}")

        print(f"f(x) em módulo: {residuo:.10g}")
        print(f"Iterações da bissecção: {iteracoes}")
        print(f"Erro relativo entre iterações: {erro_relativo:.10g}")
        print(f"Tolerância de erro relativo: {ERRO_ACEITAVEL:.10g}")
    except (ValueError, TypeError) as erro:
        print(f"\nErro: {erro}")


if __name__ == "__main__":
    main()
