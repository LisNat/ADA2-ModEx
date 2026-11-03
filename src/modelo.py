from dataclasses import dataclass
from fractions import Fraction
from math import ceil, sqrt

# Representa un agente de la red social
# Se usa Fraction para evitar errores de precision en los calculos
@dataclass
class Agente:
    opinion: int
    receptividad: Fraction
    influencia: Fraction

    # Validaciones de los datos del agente 
    def __post_init__(self):
        if not -100 <= self.opinion <= 100:
            raise ValueError("La opinion debe estar entre -100 y 100.")

        if not 0 <= self.receptividad <= 1:
            raise ValueError("La receptividad debe estar entre 0 y 1.")

        if not 1 <= self.influencia <= 3:
            raise ValueError("La influencia debe estar entre 1 y 3.")

    # El esfuerzo de moderar al agente: ceil(|o| * (1 - r) * inf)
    def costo_moderacion(self):
        return ceil(
            abs(self.opinion)
            * (1 - self.receptividad)
            * self.influencia
        )


# Representa la red social y el presupuesto disponible para moderar
@dataclass
class RedSocial:
    agentes: list[Agente]
    presupuesto_maximo: int

    def __post_init__(self):
        if not self.agentes:
            raise ValueError("La red debe tener al menos un agente.")

        if self.presupuesto_maximo < 0:
            raise ValueError("El presupuesto no puede ser negativo.")

    # Esfuerzo(RS, E): suma del costo de moderar a los agentes con e_i = 1
    # Un agente con e_i = 0 no aporta al esfuerzo
    def calcular_esfuerzo(self, estrategia):
        self._validar_estrategia(estrategia)

        return sum(
            agente.costo_moderacion()
            for agente, decision in zip(self.agentes, estrategia)
            if decision == 1
        )

    # Calcula la suma del extremismo de los agentes no moderados
    def suma_extremismo(self, estrategia):
        self._validar_estrategia(estrategia)

        return sum(
            (0 if decision == 1 else agente.opinion) ** 2
            * agente.influencia
            for agente, decision in zip(self.agentes, estrategia)
        )

    # Calcula el extremismo de la red despues de aplicar la estrategia
    def calcular_extremismo(self, estrategia):
        suma = self.suma_extremismo(estrategia)

        return sqrt(float(suma)) / len(self.agentes)

    # Mod(RS, E): lista de opiniones despues de moderar. Los moderados quedan en 0
    def moderar(self, estrategia):
        self._validar_estrategia(estrategia)

        return [
            0 if decision == 1 else agente.opinion
            for agente, decision in zip(self.agentes, estrategia)
        ]

    # Una estrategia solo es aplicable si su esfuerzo no supera Rmax
    def es_aplicable(self, estrategia):
        return (
            self.calcular_esfuerzo(estrategia)
            <= self.presupuesto_maximo
        )

    # Verifica que la estrategia tenga un valor valido por cada agente (0 o 1)
    def _validar_estrategia(self, estrategia):
        if len(estrategia) != len(self.agentes):
            raise ValueError(
                "La estrategia debe tener un valor por agente."
            )

        if any(valor not in (0, 1) for valor in estrategia):
            raise ValueError(
                "Cada elemento de la estrategia debe ser 0 o 1."
            )
