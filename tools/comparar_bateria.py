"""Comparador de la bateria de pruebas del profesor.

Corre los algoritmos (modexFB, modexV, modexPD) sobre cada Prueba*.txt de la bateria
y compara el extremismo obtenido con el valor de tabla_resultados.xlsx.

Uso (desde la carpeta Proyecto1):
    python tools\\comparar_bateria.py
    python tools\\comparar_bateria.py --algoritmos FB PD --max-n-fb 20 --timeout 120
    python tools\\comparar_bateria.py --bateria "C:\\ruta\\Bateria de pruebas" --csv resultados.csv

Por defecto busca la bateria en ..\\..\\Bateria de pruebas (carpeta ADA2).
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(RAIZ, "..", "src")
BATERIA_POR_DEFECTO = os.path.join(RAIZ, "..", "..", "Bateria de pruebas")
NOMBRES_FUNCIONES = {"FB": "modexFB", "V": "modexV", "PD": "modexPD"}
TOLERANCIA = 0.0011  # los valores del profesor vienen con 3 decimales


# Lee tabla_resultados.xlsx sin depender de openpyxl (solo biblioteca estandar).
# Devuelve {numero_prueba: {"raw": texto, "n": int, "tipo": "Óptimo" o "Solución"}}.
def leer_esperados(ruta_xlsx):
    z = zipfile.ZipFile(ruta_xlsx)
    textos = z.read("xl/sharedStrings.xml").decode("utf-8")
    cadenas = [
        "".join(re.findall(r"<t[^>]*>(.*?)</t>", s, flags=re.S))
        for s in re.findall(r"<si>(.*?)</si>", textos, flags=re.S)
    ]
    hoja = z.read("xl/worksheets/sheet1.xml").decode("utf-8")

    filas = []
    for fila in re.findall(r"<row[^>]*>(.*?)</row>", hoja, flags=re.S):
        valores = []
        for atributos, cuerpo in re.findall(r"<c ([^>]*?)(?:/>|>(.*?)</c>)", fila, flags=re.S):
            tipo = re.search(r't="(\w+)"', atributos)
            v = re.search(r"<v>(.*?)</v>", cuerpo or "")
            valor = v.group(1) if v else ""
            if tipo and tipo.group(1) == "s" and valor:
                valor = cadenas[int(valor)]
            valores.append(valor)
        filas.append(valores)

    esperados = {}
    for fila in filas[1:]:  # la primera fila es el encabezado
        numero = int(re.search(r"(\d+)", fila[0]).group(1))
        esperados[numero] = {"raw": fila[2], "n": int(fila[1]), "tipo": fila[3]}
    return esperados


# Convierte el texto del xlsx a numero. Hay dos problemas en la tabla:
# - algunas celdas usan coma decimal ("13,48" = 13.48);
# - algunas perdieron el punto decimal ("14069" = 14.069). Como el extremismo
#   nunca pasa de 100 en estas pruebas, un valor mayor que 100 se divide entre 1000.
def interpretar_valor(raw):
    raw = raw.strip()
    if "," in raw:
        return float(raw.replace(",", "."))
    valor = float(raw)
    return valor / 1000 if valor > 100 else valor


# Modo trabajador: corre UN algoritmo sobre UNA prueba y escribe el resultado en JSON.
# Se usa desde el modo principal con un limite de tiempo (subprocess), para que una
# prueba lenta no detenga toda la comparacion.
def modo_trabajador(algoritmo, ruta_prueba):
    sys.path.insert(0, SRC)
    from entrada_salida import leer_entrada
    import algoritmos

    red = leer_entrada(ruta_prueba)
    funcion = getattr(algoritmos, NOMBRES_FUNCIONES[algoritmo], None)
    if funcion is None:
        print(json.dumps({"error": "no_implementado"}))
        return

    inicio = time.time()
    estrategia, esfuerzo, extremismo = funcion(red)
    duracion = time.time() - inicio
    print(json.dumps({
        "extremismo": extremismo,
        "esfuerzo": esfuerzo,
        "tiempo": round(duracion, 3),
        "aplicable": red.es_aplicable(estrategia),
    }))


# Corre un algoritmo sobre una prueba en otro proceso y devuelve su resultado.
# Si tarda mas que el limite, devuelve {"error": "timeout"}.
def correr_con_limite(algoritmo, ruta_prueba, limite_segundos):
    comando = [sys.executable, os.path.abspath(__file__), "--trabajador", algoritmo, ruta_prueba]
    try:
        salida = subprocess.run(comando, capture_output=True, text=True, timeout=limite_segundos)
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}

    if salida.returncode != 0:
        return {"error": "fallo: " + salida.stderr.strip().splitlines()[-1]}
    return json.loads(salida.stdout)


def formatear(numero):
    return "-" if numero is None else f"{numero:.4f}"


def modo_principal(args):
    ruta_bateria = os.path.abspath(args.bateria)
    esperados = leer_esperados(os.path.join(ruta_bateria, "tabla_resultados.xlsx"))

    filas = []
    for numero in sorted(esperados):
        info = esperados[numero]
        esperado = interpretar_valor(info["raw"])
        ruta = os.path.join(ruta_bateria, f"Prueba{numero}.txt")
        fila = {"prueba": numero, "n": info["n"], "esperado": esperado, "tipo": info["tipo"]}

        for alg in args.algoritmos:
            if alg == "FB" and info["n"] > args.max_n_fb:
                fila[alg] = {"error": f"omitido (n > {args.max_n_fb})"}
                continue
            fila[alg] = correr_con_limite(alg, ruta, args.timeout)
        filas.append(fila)
        print(f"Prueba {numero} (n={info['n']}) lista", flush=True)

    print()
    encabezado = f"{'P':>3} {'n':>5} {'esperado':>9} {'tipo':>8} " + " ".join(
        f"{alg:>22}" for alg in args.algoritmos
    )
    print(encabezado)
    print("-" * len(encabezado))

    aciertos = {alg: [0, 0] for alg in args.algoritmos}
    for fila in filas:
        celdas = []
        for alg in args.algoritmos:
            r = fila[alg]
            if "error" in r:
                celdas.append(f"{r['error'][:22]:>22}")
                continue
            valor = r["extremismo"]
            if fila["tipo"] == "Óptimo":
                ok = abs(round(valor, 3) - round(fila["esperado"], 3)) <= TOLERANCIA
                aciertos[alg][1] += 1
                aciertos[alg][0] += int(ok)
                marca = "ok" if ok else "MAL"
            else:
                marca = "-"
            celdas.append(f"{valor:>14.4f} {marca:>7}")
        print(f"{fila['prueba']:>3} {fila['n']:>5} {fila['esperado']:>9.4f} {fila['tipo']:>8} " + " ".join(celdas))

    print("\nAciertos en pruebas con optimo conocido:")
    for alg in args.algoritmos:
        bien, total = aciertos[alg]
        print(f"  {alg}: {bien}/{total}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["prueba", "n", "esperado", "tipo"] + [f"{a}_extremismo" for a in args.algoritmos] + [f"{a}_tiempo" for a in args.algoritmos] + [f"{a}_nota" for a in args.algoritmos])
            for fila in filas:
                ext = [fila[a].get("extremismo", "") for a in args.algoritmos]
                tiempos = [fila[a].get("tiempo", "") for a in args.algoritmos]
                notas = [fila[a].get("error", "") for a in args.algoritmos]
                escritor.writerow([fila["prueba"], fila["n"], fila["esperado"], fila["tipo"]] + ext + tiempos + notas)
        print(f"\nResultados guardados en {args.csv}")


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--trabajador":
        modo_trabajador(sys.argv[2], sys.argv[3])
        return

    parser = argparse.ArgumentParser(description="Compara los algoritmos con la bateria del profesor.")
    parser.add_argument("--bateria", default=BATERIA_POR_DEFECTO, help="carpeta con Prueba*.txt y tabla_resultados.xlsx")
    parser.add_argument("--algoritmos", nargs="+", default=["FB", "V", "PD"], choices=["FB", "V", "PD"])
    parser.add_argument("--max-n-fb", type=int, default=20, help="no correr fuerza bruta si n es mayor")
    parser.add_argument("--timeout", type=int, default=120, help="segundos maximos por prueba")
    parser.add_argument("--csv", default=None, help="archivo CSV para guardar los resultados")
    modo_principal(parser.parse_args())


if __name__ == "__main__":
    main()
