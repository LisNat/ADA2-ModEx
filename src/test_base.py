import os
import unittest
from fractions import Fraction

from entrada_salida import escribir_salida, leer_entrada, leer_salida
from modelo import Agente
from verificador import verificar_salida

DATOS = os.path.join(os.path.dirname(__file__), "..", "data")


# Red del ejemplo 1 del enunciado.
def red_ejemplo1():
    return leer_entrada(os.path.join(DATOS, "ejemplo1.txt"))


# Red del ejemplo 2 del enunciado.
def red_ejemplo2():
    return leer_entrada(os.path.join(DATOS, "ejemplo2.txt"))


# Valores del ejemplo 1 que aparecen en el enunciado (seccion 2.3.1).
class TestEjemplo1(unittest.TestCase):
    def test_lectura(self):
        red = red_ejemplo1()
        self.assertEqual(len(red.agentes), 3)
        self.assertEqual(red.presupuesto_maximo, 55)
        self.assertEqual(red.agentes[2].opinion, -10)

    def test_E1_aplicable_y_extremismo(self):
        red = red_ejemplo1()
        E1 = [0, 0, 1]
        self.assertEqual(red.calcular_esfuerzo(E1), 9)
        self.assertTrue(red.es_aplicable(E1))
        self.assertAlmostEqual(red.calcular_extremismo(E1), 47.14, places=2)

    def test_E2_aplicable_y_extremismo(self):
        red = red_ejemplo1()
        E2 = [1, 0, 0]
        self.assertEqual(red.calcular_esfuerzo(E2), 50)
        self.assertTrue(red.es_aplicable(E2))
        self.assertAlmostEqual(red.calcular_extremismo(E2), 33.50, places=2)

    # <1,0,1> cuesta 59 > 55: no es aplicable aunque su extremismo sea menor.
    def test_E_no_aplicable(self):
        red = red_ejemplo1()
        self.assertFalse(red.es_aplicable([1, 0, 1]))


# Valores del ejemplo 2 del enunciado (seccion 2.3.2).
class TestEjemplo2(unittest.TestCase):
    def test_E1_no_aplicable(self):
        red = red_ejemplo2()
        self.assertEqual(red.calcular_esfuerzo([0, 1, 0]), 36)
        self.assertFalse(red.es_aplicable([0, 1, 0]))

    def test_E2_aplicable_y_extremismo(self):
        red = red_ejemplo2()
        E2 = [1, 0, 1]
        self.assertEqual(red.calcular_esfuerzo(E2), 28)
        self.assertTrue(red.es_aplicable(E2))
        self.assertAlmostEqual(red.calcular_extremismo(E2), 9.43, places=2)


# Moderacion, suma exacta, costos exactos y validacion de estrategias.
class TestModYExactitud(unittest.TestCase):
    def test_moderar_pone_cero_solo_a_los_moderados(self):
        red = red_ejemplo1()
        self.assertEqual(red.moderar([1, 0, 0]), [0, 100, -10])

    def test_suma_extremismo_exacta(self):
        red = red_ejemplo1()
        self.assertEqual(red.suma_extremismo([1, 0, 0]), 10100)

    # 10 * (1 - 0.7) * 1 = 3 exacto. Con floats daria 4 por error de redondeo.
    def test_costo_exacto_con_fracciones(self):
        agente = Agente(10, Fraction("0.7"), Fraction(1))
        self.assertEqual(agente.costo_moderacion(), 3)

    def test_estrategia_vacia_siempre_aplicable(self):
        red = red_ejemplo2()
        self.assertEqual(red.calcular_esfuerzo([0, 0, 0]), 0)
        self.assertTrue(red.es_aplicable([0, 0, 0]))

    def test_estrategia_con_longitud_incorrecta(self):
        red = red_ejemplo1()
        with self.assertRaises(ValueError):
            red.calcular_esfuerzo([1, 0])

    def test_estrategia_con_valor_invalido(self):
        red = red_ejemplo1()
        with self.assertRaises(ValueError):
            red.calcular_esfuerzo([1, 2, 0])


# Escritura y lectura de salidas, y el verificador independiente.
class TestSalidaYVerificador(unittest.TestCase):
    def test_escritura_y_lectura_roundtrip(self):
        red = red_ejemplo1()
        estrategia = [1, 0, 0]
        ruta = os.path.join(DATOS, "_tmp_salida_test.txt")
        try:
            resultado = (
                estrategia,
                red.calcular_esfuerzo(estrategia),
                red.calcular_extremismo(estrategia),
            )
            escribir_salida(ruta, resultado)
            estrategia_leida, esfuerzo, extremismo = leer_salida(ruta, len(red.agentes))
            self.assertEqual(estrategia_leida, estrategia)
            self.assertEqual(esfuerzo, 50)
            self.assertAlmostEqual(extremismo, 33.50, places=2)
        finally:
            if os.path.exists(ruta):
                os.remove(ruta)

    def test_verificador_acepta_salida_correcta(self):
        red = red_ejemplo1()
        self.assertEqual(verificar_salida(red, [1, 0, 0], 50, 33.50), [])

    def test_verificador_detecta_no_aplicable(self):
        red = red_ejemplo1()
        errores = verificar_salida(red, [1, 1, 0], 140, 3.33)
        self.assertTrue(any("No es aplicable" in e for e in errores))


if __name__ == "__main__":
    unittest.main()
