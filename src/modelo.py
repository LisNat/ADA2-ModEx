from dataclasses import dataclass
from fractions import Fraction
from math import ceil, sqrt


# Un agente de la red.
# La receptividad y la influencia se guardan como Fraction (no float) para que
# el calculo del costo con ceil() sea exacto: con float, (1 - 0.7) * 10 da
# 3.0000000000000004 y el ceil daria 4 en lugar de 3.
@dataclass
class Agente:
    opinion: int
    receptividad: Fraction
    influencia: Fraction

    # Valida los rangos que pide el enunciado al crear el agente.
    def __post_init__(self):
        if not -100 <= self.opinion <= 100:
            raise ValueError("La opinion debe estar entre -100 y 100.")

        if not 0 <= self.receptividad <= 1:
            raise ValueError("La receptividad debe estar entre 0 y 1.")

        if not 1 <= self.influencia <= 3:
            raise ValueError("La influencia debe estar entre 1 y 3.")

    # Esfuerzo de moderar a este agente: ceil(|o| * (1 - r) * inf).
    def costo_moderacion(self):
        return ceil(
            abs(self.opinion)
            * (1 - self.receptividad)
            * self.influencia
        )


# Una red social: sus agentes y el presupuesto maximo Rmax.
# Una estrategia es una lista de 0/1 con un valor por agente:
# e_i = 1 significa que la opinion del agente i se modera.
@dataclass
class RedSocial:
    agentes: list[Agente]
    presupuesto_maximo: int

    # Valida que la red tenga agentes y que el presupuesto no sea negativo.
    def __post_init__(self):
        if not self.agentes:
            raise ValueError("La red debe tener al menos un agente.")

        if self.presupuesto_maximo < 0:
            raise ValueError("El presupuesto no puede ser negativo.")

    # Esfuerzo(RS, E): suma del costo de moderar a los agentes con e_i = 1.
    # Un agente con e_i = 0 no aporta al esfuerzo.
    def calcular_esfuerzo(self, estrategia):
        self._validar_estrategia(estrategia)

        return sum(
            agente.costo_moderacion()
            for agente, decision in zip(self.agentes, estrategia)
            if decision == 1
        )

    # Suma de o_i^2 * inf_i sobre la red moderada (los moderados valen 0).
    # Ext es la raiz de esta suma dividida entre n. La raiz y la division no
    # cambian el orden entre estrategias, asi que comparar esta suma da la
    # misma respuesta que comparar Ext, pero sin floats.
    # Los algoritmos de fuerza bruta, voraz y PD deben usar este metodo para comparar.
    def suma_extremismo(self, estrategia):
        self._validar_estrategia(estrategia)

        return sum(
            (0 if decision == 1 else agente.opinion) ** 2
            * agente.influencia
            for agente, decision in zip(self.agentes, estrategia)
        )

    # Ext(Mod(RS, E)) = raiz(suma o_i^2 * inf_i) / n.
    # Se usa solo para reportar el valor; para comparar usar suma_extremismo.
    def calcular_extremismo(self, estrategia):
        suma = self.suma_extremismo(estrategia)

        return sqrt(float(suma)) / len(self.agentes)

    # Mod(RS, E): lista de opiniones despues de moderar. Los moderados quedan en 0.
    def moderar(self, estrategia):
        self._validar_estrategia(estrategia)

        return [
            0 if decision == 1 else agente.opinion
            for agente, decision in zip(self.agentes, estrategia)
        ]

    # Una estrategia es aplicable si su esfuerzo no supera Rmax.
    def es_aplicable(self, estrategia):
        return (
            self.calcular_esfuerzo(estrategia)
            <= self.presupuesto_maximo
        )

    # Revisa que la estrategia tenga exactamente un 0 o 1 por cada agente.
    def _validar_estrategia(self, estrategia):
        if len(estrategia) != len(self.agentes):
            raise ValueError(
                "La estrategia debe tener un valor por agente."
            )

        if any(valor not in (0, 1) for valor in estrategia):
            raise ValueError(
                "Cada elemento de la estrategia debe ser 0 o 1."
            )
