from fractions import Fraction
from math import lcm

# Cálculo de costos y beneficio de cada agente de la red
def preparar_datos(red):
    costos = [agente.costo_moderacion() for agente in red.agentes]

    beneficios = []
    for agente in red.agentes:
        beneficios.append(Fraction(agente.opinion) ** 2 * agente.influencia)

    return costos, beneficios

# Algoritmo por fuerza bruta:
# - Genera todas las estrategias posibles
# - Determina aquellas que son viable
# - Escoge la que maximiza la reducción en extremismo (beneficio)
def modexFB(red, callback_progreso=None):
    costos, beneficios = preparar_datos(red)
    n = len(red.agentes)
    total = 2 ** n # Número máximo de estrategias

    # Valores iniciales de comparación
    mejor_estrategia = None
    mejor_beneficio = -1

    # Ciclo principal para recorrer todas las estrategias posibles
    for i in range(total):
        # Separar los e_i de la estrategia
        estrategia = [(i >> j) & 1 for j in range(n)]

        # Cálculo del costo total de la estrategia
        esfuerzo = sum(
            costos[j] for j in range(n) if estrategia[j] == 1
        )
        
        if esfuerzo <= red.presupuesto_maximo:
            # Cálculo del beneficio
            beneficio = sum(
                beneficios[j] for j in range(n) if estrategia[j] == 1
            )

            # Comparación con la mejor hasta ahora
            if beneficio > mejor_beneficio:
                mejor_beneficio = beneficio
                mejor_estrategia = estrategia

        if callback_progreso is not None:
            if i % int(total/10) == 0 or i == total - 1:
                callback_progreso((i + 1) / total * 100)

    return (
        mejor_estrategia,
        red.calcular_esfuerzo(mejor_estrategia),
        red.calcular_extremismo(mejor_estrategia)
    )


def modexV(red):
    costos, beneficios = preparar_datos(red)
    n = len(red.agentes)

    estrategia = [0] * n

    # Primero se toman los agentes que no requieren esfuerzo
    for i in range(n):
        if costos[i] == 0 and beneficios[i] > 0:
            estrategia[i] = 1

    # Se ordenan los demás según su beneficio por unidad de esfuerzo
    candidatos = [
        i for i in range(n)
        if costos[i] > 0 and beneficios[i] > 0
    ]

    candidatos.sort(
        key=lambda i: Fraction(beneficios[i], costos[i]),
        reverse=True
    )

    esfuerzo = sum(
        costos[i] for i in range(n) if estrategia[i] == 1
    )

    for i in candidatos:
        if esfuerzo + costos[i] <= red.presupuesto_maximo:
            estrategia[i] = 1
            esfuerzo += costos[i]

    return (
        estrategia,
        red.calcular_esfuerzo(estrategia),
        red.calcular_extremismo(estrategia)
    )


def modexPD(red):
    costos, beneficios = preparar_datos(red)
    n = len(red.agentes)
    R = red.presupuesto_maximo

    estrategia = [0] * n

    # Los agentes con costo cero siempre se pueden moderar
    for i in range(n):
        if costos[i] == 0 and beneficios[i] > 0:
            estrategia[i] = 1

    candidatos = [
        i for i in range(n)
        if costos[i] > 0 and beneficios[i] > 0
    ]

    valor = [0] * (R + 1)
    decisiones = []

    for i in candidatos:
        costo = costos[i]
        beneficio = beneficios[i]
        tomado = bytearray(R + 1)

        # Se recorre w de mayor a menor para no usar dos veces el mismo candidato
        for w in range(R, costo - 1, -1):
            if valor[w - costo] + beneficio > valor[w]:
                valor[w] = valor[w - costo] + beneficio
                tomado[w] = 1

        decisiones.append(tomado)

    # Se reconstruye la estrategia a partir de las decisiones guardadas
    w = R

    for k in range(len(candidatos) - 1, -1, -1):
        if decisiones[k][w]:
            i = candidatos[k]
            estrategia[i] = 1
            w -= costos[i]

    return (
        estrategia,
        red.calcular_esfuerzo(estrategia),
        red.calcular_extremismo(estrategia)
    )
