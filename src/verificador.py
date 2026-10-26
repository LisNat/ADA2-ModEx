from entrada_salida import DECIMALES


# Recalcula el esfuerzo, la aplicabilidad y el extremismo de una salida dada.
# Devuelve una lista de errores. Si la lista esta vacia, la salida es correcta.
def verificar_salida(red, estrategia, esfuerzo_informado, extremismo_informado):
    errores = []

    try:
        esfuerzo_real = red.calcular_esfuerzo(estrategia)
    except ValueError as error:
        return [f"Estrategia invalida: {error}"]

    if esfuerzo_real != esfuerzo_informado:
        errores.append(
            f"Esfuerzo informado {esfuerzo_informado}, "
            f"recalculado {esfuerzo_real}."
        )

    if esfuerzo_real > red.presupuesto_maximo:
        errores.append(
            f"No es aplicable: esfuerzo {esfuerzo_real} "
            f"supera Rmax {red.presupuesto_maximo}."
        )

    extremismo_real = round(red.calcular_extremismo(estrategia), DECIMALES)
    tolerancia = 0.5 * 10 ** (-DECIMALES) + 1e-9

    if abs(extremismo_real - extremismo_informado) > tolerancia:
        errores.append(
            f"Extremismo informado {extremismo_informado}, "
            f"recalculado {extremismo_real}."
        )

    return errores
