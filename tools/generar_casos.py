"""Generador de casos de prueba de ModEx.

Escribe redes sociales en el formato de entrada del enunciado (n + 2 lineas), para
cargarlas desde la interfaz o pasarlas a modexFB, modexV y modexPD.

Genera dos tipos de casos:
- RS3 a RS8: los casos disenados a mano para el informe. RS1 y RS2 son los ejemplos
  del enunciado y ya estan en data\\ejemplo1.txt y data\\ejemplo2.txt.
- Redes aleatorias con semilla fija, para poder repetirlas: la opinion es un entero
  en [-100, 100], la receptividad y la influencia son multiplos de 0.1, y Rmax es un
  entero entre 0 y la suma de los costos de todos los agentes.

Uso (desde la carpeta Proyecto1):
    python tools\\generar_casos.py
    python tools\\generar_casos.py --salida data\\casos --tamanos 10 20 50 --cantidad 3 --semilla 2026

Por defecto escribe en data\\casos.
"""

import argparse
import os
import random
import sys
from fractions import Fraction

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "..", "src"))

from entrada_salida import leer_entrada # type: ignore 
from modelo import Agente, RedSocial # type: ignore

SALIDA_POR_DEFECTO = os.path.join(RAIZ, "..", "data", "casos")


# Construye un agente a partir de textos, por ejemplo ("51", "0.1", "2").
def agente(opinion, receptividad, influencia):
    return Agente(int(opinion), Fraction(receptividad), Fraction(influencia))


# Casos disenados a mano. Cada uno busca algo distinto:
# RS3: el agente mas eficiente deja un hueco en el presupuesto (contraejemplo de la voraz).
# RS4: el presupuesto alcanza para moderar a todos.
# RS5: un agente de costo 0 con presupuesto 0 (debe moderarse igual).
# RS6: un agente pequeno y eficiente bloquea a uno grande.
# RS7 y RS8: redes de cinco agentes con costos mezclados.
def casos_disenados():
    return {
        "RS3": RedSocial(
            [agente(51, "0.1", 2), agente(-93, 0, 1), agente(66, "0.8", 1)], 97
        ),
        "RS4": RedSocial(
            [agente(100, "0.5", 1), agente(100, "0.1", 1), agente(-10, "0.1", 1)], 1000
        ),
        "RS5": RedSocial([agente(50, 1, 1), agente(-100, 0, 1)], 0),
        "RS6": RedSocial([agente(10, "0.95", 3), agente(100, 0, 1)], 100),
        "RS7": RedSocial(
            [
                agente(80, "0.2", "1.5"),
                agente(-60, "0.5", 2),
                agente(40, "0.1", 1),
                agente(-90, "0.3", "2.5"),
                agente(30, "0.7", "1.2"),
            ],
            120,
        ),
        "RS8": RedSocial(
            [
                agente(70, "0.4", 2),
                agente(-95, "0.1", "1.5"),
                agente(55, "0.6", 3),
                agente(-20, 0, 1),
                agente(85, "0.25", "2.2"),
            ],
            110,
        ),
    }


# n agentes aleatorios: opinion entera en [-100, 100], receptividad en {0, 0.1, ..., 1}
# e influencia en {1, 1.1, ..., 3}.
def agentes_aleatorios(n, rng):
    return [
        Agente(
            rng.randint(-100, 100),
            Fraction(rng.randint(0, 10), 10),
            Fraction(rng.randint(10, 30), 10),
        )
        for _ in range(n)
    ]


# Red aleatoria de n agentes. Si se da una fraccion, Rmax es esa fraccion de la suma de
# los costos; si no, es un entero uniforme entre 0 y la suma de los costos.
def red_aleatoria(n, rng, fraccion=None):
    agentes = agentes_aleatorios(n, rng)
    total = sum(a.costo_moderacion() for a in agentes)

    if fraccion is None:
        presupuesto = rng.randint(0, max(total, 1))
    else:
        presupuesto = int(total * fraccion)

    return RedSocial(agentes, presupuesto)


# Escribe un numero sin ceros sobrantes: 1/10 -> "0.1", 2 -> "2".
def texto(valor):
    return f"{float(valor):g}"


# Escribe una red en el formato de entrada del enunciado.
def escribir_entrada(ruta, red):
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(f"{len(red.agentes)}\n")

        for a in red.agentes:
            archivo.write(
                f"{a.opinion}, {texto(a.receptividad)}, {texto(a.influencia)}\n"
            )

        archivo.write(f"{red.presupuesto_maximo}\n")


def main():
    parser = argparse.ArgumentParser(description="Genera casos de prueba en el formato de entrada.")
    parser.add_argument("--salida", default=SALIDA_POR_DEFECTO, help="carpeta donde se escriben los .txt")
    parser.add_argument("--tamanos", nargs="+", type=int, default=[10, 20, 50], help="tamanos de las redes aleatorias")
    parser.add_argument("--cantidad", type=int, default=3, help="redes aleatorias por tamano")
    parser.add_argument("--semilla", type=int, default=2026, help="semilla del generador aleatorio")
    args = parser.parse_args()

    carpeta = os.path.abspath(args.salida)
    os.makedirs(carpeta, exist_ok=True)

    redes = dict(casos_disenados())
    rng = random.Random(args.semilla)
    for n in args.tamanos:
        for k in range(1, args.cantidad + 1):
            redes[f"aleatoria_n{n}_{k}"] = red_aleatoria(n, rng)

    for nombre, red in redes.items():
        ruta = os.path.join(carpeta, nombre + ".txt")
        escribir_entrada(ruta, red)

        # Se lee de nuevo para comprobar que el archivo queda en el formato correcto.
        if leer_entrada(ruta) != red:
            raise ValueError(f"El archivo {ruta} no coincide con la red generada.")

        print(f"{nombre}: n = {len(red.agentes)}, Rmax = {red.presupuesto_maximo} -> {ruta}")


if __name__ == "__main__":
    main()