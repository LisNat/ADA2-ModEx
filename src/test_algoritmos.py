import os
import random
import unittest
from fractions import Fraction
from itertools import product

from algoritmos import modexFB, modexPD, modexV
from entrada_salida import leer_entrada
from modelo import Agente, RedSocial

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


# Casos de borde: presupuesto cero, presupuesto suficiente y agentes de costo 0.
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

    # Un agente con receptividad 1 cuesta 0: moderarlo es gratis, asi que siempre
    # debe moderarse aunque el presupuesto sea 0. (Este caso fallaba en el codigo de Luis.)
    def test_agente_de_costo_cero_siempre_se_modera(self):
        agentes = [
            Agente(50, Fraction(1), Fraction(1)),   # costo 0
            Agente(-100, Fraction(0), Fraction(1)),  # costo 100
        ]
        red = RedSocial(agentes, presupuesto_maximo=0)
        estrategia, esfuerzo, _ = modexFB(red)
        self.assertEqual(estrategia, [1, 0])
        self.assertEqual(esfuerzo, 0)


# Comprueba que modexFB no devuelve una estrategia peor que las demas aplicables.
# Se revisan las 2^n estrategias con los metodos de RedSocial, sin usar modexFB.
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


# El callback de progreso se llama y termina en 100 %.
class TestModexFBProgreso(unittest.TestCase):

    def test_callback_llega_a_100(self):
        porcentajes = []
        modexFB(red_ejemplo1(), callback_progreso=porcentajes.append)
        self.assertTrue(porcentajes)
        self.assertAlmostEqual(porcentajes[-1], 100.0)


# Red donde la voraz NO da el optimo: toma al agente 2 (muy eficiente, costo 14) y
# luego ya no le cabe el agente 1 (costo 93). La optima es moderar solo al agente 1.
def red_contraejemplo_voraz():
    agentes = [
        Agente(51, Fraction(1, 10), Fraction(2)),   # costo 92, beneficio 5202
        Agente(-93, Fraction(0), Fraction(1)),       # costo 93, beneficio 8649
        Agente(66, Fraction(4, 5), Fraction(1)),     # costo 14, beneficio 4356
    ]
    return RedSocial(agentes, presupuesto_maximo=97)


# Voraz: debe ser aplicable y dar el optimo en los ejemplos, pero no siempre.
class TestModexV(unittest.TestCase):

    def test_ejemplos_dan_el_optimo(self):
        estrategia, _, extremismo = modexV(red_ejemplo1())
        self.assertEqual(estrategia, [1, 0, 0])
        self.assertAlmostEqual(extremismo, 33.50, places=2)

        estrategia, _, extremismo = modexV(red_ejemplo2())
        self.assertEqual(estrategia, [1, 0, 1])
        self.assertAlmostEqual(extremismo, 9.43, places=2)

    # Contraejemplo: la voraz se queda en 39.23 y el optimo es 32.59.
    def test_contraejemplo_voraz_no_es_optimo(self):
        red = red_contraejemplo_voraz()
        estrategia_v, _, extremismo_v = modexV(red)
        estrategia_fb, _, extremismo_fb = modexFB(red)
        self.assertEqual(estrategia_v, [0, 0, 1])
        self.assertEqual(estrategia_fb, [0, 1, 0])
        self.assertGreater(extremismo_v, extremismo_fb)

    def test_resultado_es_aplicable(self):
        red = red_contraejemplo_voraz()
        estrategia, _, _ = modexV(red)
        self.assertTrue(red.es_aplicable(estrategia))

    def test_agente_de_costo_cero_siempre_se_modera(self):
        agentes = [
            Agente(50, Fraction(1), Fraction(1)),
            Agente(-100, Fraction(0), Fraction(1)),
        ]
        red = RedSocial(agentes, presupuesto_maximo=0)
        estrategia, esfuerzo, _ = modexV(red)
        self.assertEqual(estrategia, [1, 0])
        self.assertEqual(esfuerzo, 0)


# PD: debe dar siempre el mismo beneficio que la fuerza bruta (es exacta).
class TestModexPD(unittest.TestCase):

    def test_ejemplos_dan_el_optimo(self):
        estrategia, _, extremismo = modexPD(red_ejemplo1())
        self.assertEqual(estrategia, [1, 0, 0])
        self.assertAlmostEqual(extremismo, 33.50, places=2)

        estrategia, _, extremismo = modexPD(red_ejemplo2())
        self.assertEqual(estrategia, [1, 0, 1])
        self.assertAlmostEqual(extremismo, 9.43, places=2)

    def test_contraejemplo_voraz_pd_si_es_optimo(self):
        red = red_contraejemplo_voraz()
        estrategia, _, _ = modexPD(red)
        self.assertEqual(estrategia, [0, 1, 0])

    # Con redes aleatorias pequenas, la PD debe igualar a la fuerza bruta en beneficio.
    def test_igual_a_fuerza_bruta_en_redes_aleatorias(self):
        rng = random.Random(7)
        for _ in range(150):
            n = rng.randint(1, 7)
            agentes = [
                Agente(
                    rng.randint(-100, 100),
                    Fraction(rng.randint(0, 10), 10),
                    Fraction(rng.randint(10, 30), 10),
                )
                for _ in range(n)
            ]
            red = RedSocial(agentes, presupuesto_maximo=rng.randint(0, 300))

            estrategia_pd, _, _ = modexPD(red)
            estrategia_fb, _, _ = modexFB(red)

            self.assertTrue(red.es_aplicable(estrategia_pd))
            self.assertEqual(
                red.suma_extremismo(estrategia_pd),
                red.suma_extremismo(estrategia_fb),
            )


if __name__ == "__main__":
    unittest.main()
