import os
import unittest
from itertools import product

from entrada_salida import leer_entrada
from fuerza_bruta import modexFB

DATOS = os.path.join(os.path.dirname(__file__), "..", "data")


# Red del ejemplo 1 del enunciado (Rmax = 55).
def red_ejemplo1():
    return leer_entrada(os.path.join(DATOS, "ejemplo1.txt"))


# Red del ejemplo 2 del enunciado (Rmax = 35).
def red_ejemplo2():
    return leer_entrada(os.path.join(DATOS, "ejemplo2.txt"))


# Pruebas de modexFB con los dos ejemplos del enunciado.
class TestModexFBEjemplos(unittest.TestCase):

    # En el ejemplo 1 la optima es <1,0,0>: esfuerzo 50, Ext 33.50.
    def test_ejemplo1(self):
        estrategia, esfuerzo, extremismo = modexFB(red_ejemplo1())
        self.assertEqual(estrategia, [1, 0, 0])
        self.assertEqual(esfuerzo, 50)
        self.assertAlmostEqual(extremismo, 33.50, places=2)

    # En el ejemplo 2 la optima es <1,0,1>: esfuerzo 28, Ext 9.43.
    def test_ejemplo2(self):
        estrategia, esfuerzo, extremismo = modexFB(red_ejemplo2())
        self.assertEqual(estrategia, [1, 0, 1])
        self.assertEqual(esfuerzo, 28)
        self.assertAlmostEqual(extremismo, 9.43, places=2)


# Casos de borde: presupuesto cero y presupuesto suficiente para moderar a todos.
class TestModexFBBordes(unittest.TestCase):

    # Con Rmax = 0 solo es aplicable no moderar a nadie.
    def test_presupuesto_cero_no_modera_a_nadie(self):
        red = red_ejemplo1()
        red.presupuesto_maximo = 0
        estrategia, esfuerzo, _ = modexFB(red)
        self.assertEqual(estrategia, [0, 0, 0])
        self.assertEqual(esfuerzo, 0)

    # Con presupuesto de sobra, la mejor es moderar a todos: Ext = 0.
    def test_presupuesto_suficiente_modera_a_todos(self):
        red = red_ejemplo1()
        red.presupuesto_maximo = 1000
        estrategia, esfuerzo, extremismo = modexFB(red)
        self.assertEqual(estrategia, [1, 1, 1])
        self.assertEqual(esfuerzo, 149)
        self.assertEqual(extremismo, 0)


# Comprueba que modexFB no devuelve una estrategia peor que las demas aplicables.
# Se revisan las 2^n estrategias a mano, sin usar modexFB.
class TestModexFBEsOptima(unittest.TestCase):

    def _mejor_suma_a_mano(self, red):
        aplicables = []
        for E in product([0, 1], repeat=len(red.agentes)):
            E = list(E)
            if red.es_aplicable(E):
                aplicables.append(red.suma_extremismo(E))
        return min(aplicables)

    def test_ejemplo1_es_optima(self):
        red = red_ejemplo1()
        estrategia, _, _ = modexFB(red)
        self.assertEqual(red.suma_extremismo(estrategia), self._mejor_suma_a_mano(red))

    def test_ejemplo2_es_optima(self):
        red = red_ejemplo2()
        estrategia, _, _ = modexFB(red)
        self.assertEqual(red.suma_extremismo(estrategia), self._mejor_suma_a_mano(red))


if __name__ == "__main__":
    unittest.main()
