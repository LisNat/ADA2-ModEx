from fractions import Fraction

from modelo import Agente, RedSocial

# Cantidad de decimales con que se escribe Ext en el archivo de salida.
# 3 decimales, igual que la tabla de resultados del profesor (confirmar con el monitor).
DECIMALES = 3


# Lee un archivo de entrada y construye la red social.
# Formato: n, luego n lineas "opinion, receptividad, influencia", luego Rmax.
def leer_entrada(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        lineas = [
            linea.strip()
            for linea in archivo
            if linea.strip()
        ]

    if len(lineas) < 2:
        raise ValueError("El archivo de entrada esta incompleto.")

    n = int(lineas[0])

    if n <= 0:
        raise ValueError("El numero de agentes debe ser positivo.")

    if len(lineas) != n + 2:
        raise ValueError(
            f"Se esperaban {n + 2} lineas, "
            f"pero se encontraron {len(lineas)}."
        )

    agentes = []

    for i in range(1, n + 1):
        partes = lineas[i].split(",")

        if len(partes) != 3:
            raise ValueError(
                f"Formato incorrecto en el agente {i - 1}."
            )

        # Fraction("0.9") es exacto; float("0.9") no lo es.
        opinion = int(partes[0].strip())
        receptividad = Fraction(partes[1].strip())
        influencia = Fraction(partes[2].strip())

        agentes.append(
            Agente(opinion, receptividad, influencia)
        )

    presupuesto = int(lineas[-1])

    return RedSocial(agentes, presupuesto)


# Escribe la salida en el formato del enunciado: Ext, Esfuerzo y luego un 0/1 por agente.
# resultado es una tupla (estrategia, esfuerzo, extremismo).
def escribir_salida(ruta, resultado):
    estrategia, esfuerzo, extremismo = resultado

    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(f"{extremismo:.{DECIMALES}f}\n")
        archivo.write(f"{esfuerzo}\n")

        for valor in estrategia:
            archivo.write(f"{valor}\n")


# Lee un archivo de salida y devuelve (estrategia, esfuerzo, extremismo).
# Si se pasa n, verifica que la estrategia tenga un valor por agente.
def leer_salida(ruta, n=None):
    with open(ruta, "r", encoding="utf-8") as archivo:
        lineas = [
            linea.strip()
            for linea in archivo
            if linea.strip()
        ]

    if len(lineas) < 2:
        raise ValueError("El archivo de salida esta incompleto.")

    extremismo = float(lineas[0])
    esfuerzo = int(lineas[1])
    estrategia = [int(valor) for valor in lineas[2:]]

    if n is not None and len(lineas) != n + 2:
        raise ValueError(
            f"Se esperaban {n + 2} lineas, "
            f"pero se encontraron {len(lineas)}."
    )

    if any(valor not in (0, 1) for valor in estrategia):
        raise ValueError("La estrategia solo puede contener 0 y 1.")

    if esfuerzo < 0 or extremismo < 0:
        raise ValueError("El esfuerzo y el extremismo no pueden ser negativos.")

    return estrategia, esfuerzo, extremismo
