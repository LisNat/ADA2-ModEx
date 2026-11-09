MODERANDO EL EXTREMISMO DE OPINIONES EN UNA RED SOCIAL (ModEx)
Proyecto de curso - Análisis y Diseño de Algoritmos II
Integrantes: Liseth Natalia Rivera, Juan Diego Cárdenas Mejía,
             Juan David López Vanegas, Luis Carlos Lucero Anaguano

1. REQUISITOS
   - Python 3.12 para Windows (python.org). Durante la instalación marcar "tcl/tk and IDLE"
     (tkinter), que es necesario para la interfaz gráfica.
   - No se necesitan bibliotecas externas: todo el código usa la biblioteca estándar.

2. ARCHIVOS
   src\modelo.py          Clases Agente y RedSocial; cálculo de costo, esfuerzo y extremismo.
   src\entrada_salida.py  Lectura del formato de entrada y escritura del formato de salida.
   src\algoritmos.py      modexFB (fuerza bruta), modexV (voraz) y modexPD (programación dinámica).
   src\verificador.py     Recalcula esfuerzo, aplicabilidad y extremismo de una salida dada.
   src\gui.py             Interfaz gráfica (Tkinter).
   src\test_base.py       Pruebas unitarias de modelo, entrada/salida y verificador.
   src\test_algoritmos.py Pruebas unitarias de los tres algoritmos.
   tools\generar_casos.py Genera casos de prueba (RS3 a RS8 y redes aleatorias) en el formato de entrada.
   tools\benchmark.py     Reproduce las tablas del informe (casos, tiempos y calidad de la voraz).
   tools\comparar_bateria.py  Corre los algoritmos sobre la batería de pruebas.
   tools\construir_exe.bat    Genera el ejecutable ModEx.exe de la interfaz.
   data\ejemplo1.txt, data\ejemplo2.txt  Ejemplos 1 y 2 del enunciado.

3. EJECUTAR LA INTERFAZ
   Opción A (ejecutable): abrir dist\ModEx.exe (ver sección 6 para generarlo).
   Opción B (desde el código):
       cd src
       python gui.py

   Uso:
   a) "Seleccionar Archivo (.txt)": escoger un archivo de entrada.
   b) Se muestran los agentes (opinión, receptividad, influencia, costo y beneficio) y R_max.
   c) Escoger el algoritmo: Fuerza Bruta, Voraz o Programación Dinámica.
   d) Se muestran el extremismo (3 decimales), el esfuerzo frente a R_max y el tiempo.
   e) "Guardar" escribe el archivo de salida.

4. FORMATO DE ENTRADA
   Una línea con n, luego n líneas "opinion, receptividad, influencia" y al final R_max.
   Ejemplo (ejemplo1.txt):
       3
       100, 0.5, 1
       100, 0.1, 1
       -10, 0.1, 1
       55

5. FORMATO DE SALIDA
   Línea 1: extremismo de la red moderada (3 decimales).
   Línea 2: esfuerzo de la estrategia.
   Siguientes n líneas: 1 si el agente se modera, 0 si no.

6. CONSTRUIR EL EJECUTABLE (Windows)
   Desde la carpeta Proyecto1:
       tools\construir_exe.bat
   El resultado queda en dist\ModEx.exe. El script instala PyInstaller la primera vez.

7. PRUEBAS Y HERRAMIENTAS (desde la carpeta indicada)
   Pruebas unitarias (carpeta src):
       cd src
       python -m unittest test_base test_algoritmos -v

   Generar casos de prueba (carpeta Proyecto1):
       python tools\generar_casos.py
       python tools\generar_casos.py --salida data\casos --tamanos 10 20 50 --cantidad 3

   Tablas del informe (carpeta Proyecto1):
       python tools\benchmark.py casos
       python tools\benchmark.py tiempos --latex
       python tools\benchmark.py acierto --redes 500

   Batería del profesor (carpeta Proyecto1). Indicar la carpeta donde están
   Prueba1.txt ... Prueba35.txt y tabla_resultados.xlsx:
       python tools\comparar_bateria.py --bateria "RUTA_A_LA_BATERIA"
       python tools\comparar_bateria.py --algoritmos FB V PD --max-n-fb 20 --timeout 60

8. NOTAS
   - La fuerza bruta tarda 2^n iteraciones: úsela solo con n <= 20.
   - La programación dinámica depende de R_max y de n; con redes muy grandes puede tardar varios
     minutos.
   - Los extremismos se escriben con 3 decimales.
