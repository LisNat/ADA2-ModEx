"""Reproduce las tablas del informe: casos disenados, tiempos y calidad de la voraz.

Corre modexFB, modexV y modexPD y muestra los resultados. Con --latex imprime las filas
listas para pegar en las tablas del informe.

Modos:
    casos     RS1 a RS8: solucion de la voraz frente al optimo (fuerza bruta).
    tiempos   Tiempo de cada algoritmo y Ext en redes aleatorias (Rmax = 40 % de la
              suma de los costos). La fuerza bruta solo se corre con n <= 20.
    acierto   En cuantas redes aleatorias la voraz da el optimo (referencia: PD, que se
              comprueba contra la fuerza bruta cuando n <= 10).
    todo      Los tres anteriores.

Uso (desde la carpeta Proyecto1):
    python tools\\benchmark.py casos
    python tools\\benchmark.py tiempos --latex
    python tools\\benchmark.py acierto --redes 500
    python tools\\benchmark.py todo

Las redes aleatorias usan semilla fija, asi que Ext y los porcentajes salen iguales en
cualquier equipo. Los tiempos dependen de la maquina.
"""

import argparse
import os
import random
import sys
import time

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "..", "src"))

from algoritmos import modexFB, modexV, modexPD # type: ignore
from entrada_salida import leer_entrada # type: ignore
from generar_casos import casos_disenados, red_aleatoria

DATOS = os.path.join(RAIZ, "..", "data")
TOLERANCIA = 1e-9


# Ejecuta f sobre la red y devuelve (resultado, segundos).
def medir(f, red):
    inicio = time.perf_counter()
    resultado = f(red)
    return resultado, time.perf_counter() - inicio


# Fila de tabla de LaTeX con su linea horizontal.
def fila_latex(celdas):
    return " & ".join(celdas) + r" \\" + "\n" + r"\hline"


def mat(valor):
    return "$" + valor + "$"


def texto_estrategia(estrategia):
    return "<" + ",".join(str(e) for e in estrategia) + ">"


def latex_estrategia(estrategia):
    return r"$\langle " + ",".join(str(e) for e in estrategia) + r" \rangle$"


# RS1 a RS8: voraz frente al optimo de la fuerza bruta.
def tabla_casos(latex):
    redes = {
        "RS1": leer_entrada(os.path.join(DATOS, "ejemplo1.txt")),
        "RS2": leer_entrada(os.path.join(DATOS, "ejemplo2.txt")),
    }
    redes.update(casos_disenados())

    print("== Casos disenados: voraz frente al optimo")
    if not latex:
        print(f"{'caso':>4} {'E voraz':>12} {'Esf':>5} {'Ext voraz':>10} {'E optima':>12} {'Ext optimo':>11}  optima?")

    for nombre, red in redes.items():
        est_v, esf_v, ext_v = modexV(red)
        est_o, _, ext_o = modexFB(red)
        optima = abs(ext_v - ext_o) < TOLERANCIA

        if latex:
            print(fila_latex([
                mat(f"RS_{nombre[2:]}"), latex_estrategia(est_v), mat(str(esf_v)),
                mat(f"{ext_v:.3f}"), latex_estrategia(est_o), mat(f"{ext_o:.3f}"),
                "Sí" if optima else "No",
            ]))
        else:
            print(f"{nombre:>4} {texto_estrategia(est_v):>12} {esf_v:>5} {ext_v:>10.3f} "
                  f"{texto_estrategia(est_o):>12} {ext_o:>11.3f}  {'Si' if optima else 'No'}")


# Tiempo de cada algoritmo y Ext en redes aleatorias con Rmax = 40 % de la suma de costos.
def tabla_tiempos(latex):
    rng = random.Random(11)

    print("== Tiempos (FB en s, V y PD en ms). Rmax = 40 % de la suma de los costos")
    if not latex:
        print(f"{'n':>5} {'Rmax':>7} {'FB (s)':>9} {'V (ms)':>9} {'PD (ms)':>10} {'Ext optimo':>11} {'Ext voraz':>10}")

    for n in (10, 14, 16, 18, 20, 50, 100, 200, 400, 800):
        red = red_aleatoria(n, rng, 0.4)
        (_, _, ext_v), t_v = medir(modexV, red)
        (_, _, ext_pd), t_pd = medir(modexPD, red)

        t_fb = None
        if n <= 20:
            (_, _, ext_fb), t_fb = medir(modexFB, red)
            if abs(ext_fb - ext_pd) > TOLERANCIA:
                raise ValueError(f"PD no coincide con la fuerza bruta en n = {n}.")

        if latex:
            print(fila_latex([
                mat(str(n)), mat(str(red.presupuesto_maximo)),
                "-" if t_fb is None else mat(f"{t_fb:.3f}"),
                mat(f"{t_v * 1000:.2f}"), mat(f"{t_pd * 1000:.2f}"),
                mat(f"{ext_pd:.3f}"), mat(f"{ext_v:.3f}"),
            ]))
        else:
            fb = "-" if t_fb is None else f"{t_fb:.3f}"
            print(f"{n:>5} {red.presupuesto_maximo:>7} {fb:>9} {t_v * 1000:>9.2f} "
                  f"{t_pd * 1000:>10.2f} {ext_pd:>11.3f} {ext_v:>10.3f}")


# En cuantas redes aleatorias la voraz da el optimo y que tan lejos queda cuando falla.
def tabla_acierto(latex, redes_por_tamano):
    rng = random.Random(2026)

    print(f"== Calidad de la voraz en {redes_por_tamano} redes aleatorias por tamano")
    if not latex:
        print(f"{'n':>4} {'optima':>8} {'brecha media':>13} {'peor brecha':>12}")

    for n in (5, 8, 10, 15, 20, 30):
        aciertos = 0
        peor = 0.0
        suma = 0.0

        for _ in range(redes_por_tamano):
            red = red_aleatoria(n, rng)
            _, _, ext_v = modexV(red)
            _, _, ext_pd = modexPD(red)

            # La PD es la referencia; con n pequeno se comprueba contra la fuerza bruta.
            if n <= 10:
                _, _, ext_fb = modexFB(red)
                if abs(ext_fb - ext_pd) > TOLERANCIA:
                    raise ValueError(f"PD no coincide con la fuerza bruta en n = {n}.")

            brecha = (ext_v - ext_pd) / ext_pd * 100 if ext_pd > 0 else 0.0
            if brecha < TOLERANCIA:
                aciertos += 1
            peor = max(peor, brecha)
            suma += brecha

        porcentaje = 100 * aciertos / redes_por_tamano
        media = suma / redes_por_tamano

        if latex:
            print(fila_latex([
                mat(str(n)), mat(f"{porcentaje:.1f}" + r"\%"),
                mat(f"{media:.2f}" + r"\%"), mat(f"{peor:.2f}" + r"\%"),
            ]))
        else:
            print(f"{n:>4} {porcentaje:>7.1f}% {media:>12.2f}% {peor:>11.2f}%")


def main():
    parser = argparse.ArgumentParser(description="Reproduce las tablas del informe.")
    parser.add_argument("modo", choices=["casos", "tiempos", "acierto", "todo"])
    parser.add_argument("--latex", action="store_true", help="imprime las filas listas para pegar en LaTeX")
    parser.add_argument("--redes", type=int, default=500, help="redes aleatorias por tamano en el modo acierto")
    args = parser.parse_args()

    if args.modo in ("casos", "todo"):
        tabla_casos(args.latex)
        print()
    if args.modo in ("tiempos", "todo"):
        tabla_tiempos(args.latex)
        print()
    if args.modo in ("acierto", "todo"):
        tabla_acierto(args.latex, args.redes)


if __name__ == "__main__":
    main()