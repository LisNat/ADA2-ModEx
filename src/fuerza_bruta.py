from itertools import product


# Calcula la estrategia optima de ModEx probando las 2^n estrategias posibles.
# Recibe una RedSocial y devuelve (estrategia, esfuerzo, extremismo).
#
# Solo se consideran las estrategias aplicables (esfuerzo <= Rmax) y, entre
# ellas, se queda la de menor extremismo. Se compara la suma exacta
# (suma_extremismo), que da el mismo orden que Ext; la raiz se calcula solo al final.
#
# La estrategia <0,...,0> siempre es aplicable (esfuerzo 0 <= Rmax), asi que
# siempre hay al menos una candidata y mejor_estrategia nunca queda en None.
def modexFB(red):
    mejor_estrategia = None
    mejor_suma = None

    for estrategia in product([0, 1], repeat=len(red.agentes)):
        estrategia = list(estrategia)

        if not red.es_aplicable(estrategia):
            continue

        suma = red.suma_extremismo(estrategia)

        if mejor_suma is None or suma < mejor_suma:
            mejor_suma = suma
            mejor_estrategia = estrategia

    return (
        mejor_estrategia,
        red.calcular_esfuerzo(mejor_estrategia),
        red.calcular_extremismo(mejor_estrategia),
    )
