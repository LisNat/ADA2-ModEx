from fractions import Fraction
from math import lcm


# Prepara los valores que usan los algoritmos, en enteros, una sola vez por red.
# - costos[i]: esfuerzo de moderar al agente i (ya es entero, ceil exacto).
# - beneficios[i]: o_i^2 * inf_i, multiplicado por D para que sea entero.
#   D es el mcm de los denominadores de las influencias. Al multiplicar todo por
#   D no cambia cual estrategia es mejor, pero la suma queda en enteros y no
#   hay que usar Fraction dentro del ciclo principal (eso lo hace mucho mas rapido).
# Devuelve (costos, beneficios, D).
def _preparar(red):
    costos = [agente.costo_moderacion() for agente in red.agentes]

    D = 1
    for agente in red.agentes:
        D = lcm(D, Fraction(agente.influencia).denominator)

    beneficios = [
        int(Fraction(agente.opinion) ** 2 * agente.influencia * D)
        for agente in red.agentes
    ]

    return costos, beneficios, D


# Fuerza bruta: prueba las 2^n estrategias y se queda con la aplicable de menor extremismo.
#
# Como moderar un agente quita su o_i^2 * inf_i de la suma del extremismo, minimizar
# el extremismo es lo mismo que maximizar el beneficio de los moderados.
#
# Recibe una RedSocial y devuelve (estrategia, esfuerzo, extremismo).
# callback_progreso (opcional) recibe un porcentaje entre 0 y 100 y sirve para la GUI.
#
# La estrategia <0,...,0> siempre es aplicable (esfuerzo 0 <= Rmax), asi que
# siempre hay al menos una candidata.
def modexFB(red, callback_progreso=None):
    costos, beneficios, _ = _preparar(red)
    n = len(red.agentes)
    total = 2 ** n

    mejor_estrategia = None
    mejor_beneficio = -1

    for i in range(total):
        # El bit j de i indica si se modera al agente j.
        estrategia = [(i >> j) & 1 for j in range(n)]

        esfuerzo = sum(costos[j] for j in range(n) if estrategia[j])

        if esfuerzo <= red.presupuesto_maximo:
            beneficio = sum(beneficios[j] for j in range(n) if estrategia[j])

            if beneficio > mejor_beneficio:
                mejor_beneficio = beneficio
                mejor_estrategia = estrategia

        if callback_progreso and (i % 10000 == 0 or i == total - 1):
            callback_progreso((i + 1) / total * 100)

    return (
        mejor_estrategia,
        red.calcular_esfuerzo(mejor_estrategia),
        red.calcular_extremismo(mejor_estrategia),
    )


# Voraz: moderar primero a los agentes con mayor beneficio por unidad de esfuerzo.
#
# 1. Los agentes de costo 0 se moderan siempre: es gratis y reduce el extremismo.
# 2. Los demas se ordenan de mayor a menor beneficio / costo.
# 3. Se recorren en ese orden y se moderan mientras el esfuerzo acumulado no supere Rmax.
#    Si un agente no cabe, se salta y se sigue con el siguiente (no se detiene).
#
# Es rapido, pero NO siempre da el optimo: un agente grande y muy eficiente puede
# dejar sin espacio a una combinacion mejor (ver test_algoritmos.py).
#
# Devuelve (estrategia, esfuerzo, extremismo).
def modexV(red):
    costos, beneficios, _ = _preparar(red)
    n = len(red.agentes)

    estrategia = [0] * n

    for i in range(n):
        if costos[i] == 0 and beneficios[i] > 0:
            estrategia[i] = 1

    candidatos = [i for i in range(n) if costos[i] > 0 and beneficios[i] > 0]
    candidatos.sort(key=lambda i: Fraction(beneficios[i], costos[i]), reverse=True)

    esfuerzo = sum(costos[i] for i in range(n) if estrategia[i])
    for i in candidatos:
        if esfuerzo + costos[i] <= red.presupuesto_maximo:
            estrategia[i] = 1
            esfuerzo += costos[i]

    return (
        estrategia,
        red.calcular_esfuerzo(estrategia),
        red.calcular_extremismo(estrategia),
    )


# Programacion dinamica (mochila 0/1), con la misma idea que el problema de la mochila:
#
# Subproblemas: valor[w] = mejor beneficio con esfuerzo a lo sumo w, usando los
# primeros k candidatos. Para cada candidato i (costo c, beneficio b):
#     nuevo[w] = max(anterior[w], anterior[w - c] + b)   si c <= w
# Para reconstruir la solucion se guarda, por candidato, si se tomo para cada w.
#
# Los agentes de costo 0 no entran a la tabla: se moderan siempre (son gratis).
#
# Tiempo: O(n * Rmax). Espacio: O(n * Rmax) para la tabla de decisiones.
# Devuelve (estrategia, esfuerzo, extremismo).
def modexPD(red):
    costos, beneficios, _ = _preparar(red)
    n = len(red.agentes)
    R = red.presupuesto_maximo

    estrategia = [0] * n

    for i in range(n):
        if costos[i] == 0 and beneficios[i] > 0:
            estrategia[i] = 1

    candidatos = [i for i in range(n) if costos[i] > 0 and beneficios[i] > 0]

    valor = [0] * (R + 1)
    tomado_en = []  # tomado_en[k][w] = 1 si el candidato k se toma con esfuerzo w

    for i in candidatos:
        c = costos[i]
        b = beneficios[i]
        decision = bytearray(R + 1)

        # Se recorre w de mayor a menor para no usar dos veces el mismo candidato.
        for w in range(R, c - 1, -1):
            if valor[w - c] + b > valor[w]:
                valor[w] = valor[w - c] + b
                decision[w] = 1

        tomado_en.append(decision)

    # Reconstruccion: se recorre hacia atras desde el mejor esfuerzo R.
    w = R
    for k in range(len(candidatos) - 1, -1, -1):
        if tomado_en[k][w]:
            i = candidatos[k]
            estrategia[i] = 1
            w -= costos[i]

    return (
        estrategia,
        red.calcular_esfuerzo(estrategia),
        red.calcular_extremismo(estrategia),
    )
