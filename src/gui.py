import os
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from algoritmos import modexFB, modexV, modexPD
from entrada_salida import DECIMALES, leer_entrada, escribir_salida
from verificador import verificar_salida

class ModExApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ModEx - Moderación de Extremismo en Redes Sociales")
        self.root.geometry("900x730")

        self.red = None
        self.agentes = []
        self.R_max = 0
        self.n = 0
        self.estrategia_resultado = []
        self.esfuerzo_resultado = 0
        self.extremismo_resultado = 0.0

        self._crear_componentes()

    def _crear_componentes(self):
        # Frame Archivo
        frame_archivo = ttk.LabelFrame(self.root, text=" 1. Cargar Archivo de Entrada ", padding=10)
        frame_archivo.pack(fill="x", padx=15, pady=5)

        ttk.Button(frame_archivo, text="Seleccionar Archivo (.txt)", command=self.cargar_archivo).pack(side="left", padx=5)
        self.lbl_archivo = ttk.Label(frame_archivo, text="No se ha seleccionado archivo", font=("Arial", 9, "italic"))
        self.lbl_archivo.pack(side="left", padx=10)

        # Frame Datos Red
        frame_red = ttk.LabelFrame(self.root, text=" 2. Datos de la Red Social ", padding=10)
        frame_red.pack(fill="both", expand=True, padx=15, pady=5)

        self.lbl_info = ttk.Label(frame_red, text="Agentes: 0 | Presupuesto Máximo (R_max): 0", font=("Arial", 10, "bold"))
        self.lbl_info.pack(anchor="w", pady=5)

        # Columnas incluyendo la Estrategia (Moderado)
        columnas = ("id", "op", "recep", "inf", "costo", "beneficio", "moderado")
        self.tabla_agentes = ttk.Treeview(frame_red, columns=columnas, show="headings", height=8)

        self.tabla_agentes.heading("id", text="Agente ID")
        self.tabla_agentes.heading("op", text="Opinión (o_i)")
        self.tabla_agentes.heading("recep", text="Receptividad (r_i)")
        self.tabla_agentes.heading("inf", text="Influencia (inf_i)")
        self.tabla_agentes.heading("costo", text="Esfuerzo (Costo)")
        self.tabla_agentes.heading("beneficio", text="Red. Extremismo")
        self.tabla_agentes.heading("moderado", text="Estrategia (Moderado)")

        self.tabla_agentes.column("id", anchor="center", width=80)
        self.tabla_agentes.column("op", anchor="center", width=100)
        self.tabla_agentes.column("recep", anchor="center", width=110)
        self.tabla_agentes.column("inf", anchor="center", width=110)
        self.tabla_agentes.column("costo", anchor="center", width=110)
        self.tabla_agentes.column("beneficio", anchor="center", width=120)
        self.tabla_agentes.column("moderado", anchor="center", width=130)

        scrollbar = ttk.Scrollbar(frame_red, orient="vertical", command=self.tabla_agentes.yview)
        self.tabla_agentes.configure(yscroll=scrollbar.set)

        self.tabla_agentes.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configurar estilos/tags para filas seleccionadas por la estrategia
        self.tabla_agentes.tag_configure("moderado_si", background="#e6ffe6")

        # Frame Algoritmos
        frame_algoritmos = ttk.LabelFrame(self.root, text=" 3. Ejecución de Algoritmos ", padding=10)
        frame_algoritmos.pack(fill="x", padx=15, pady=5)

        ttk.Button(frame_algoritmos, text="Ejecutar Fuerza Bruta (modexFB)", command=lambda: self.ejecutar_algoritmo("FB")).pack(side="left", padx=10)
        ttk.Button(frame_algoritmos, text="Ejecutar Voraz (modexV)", command=lambda: self.ejecutar_algoritmo("V")).pack(side="left", padx=10)
        ttk.Button(frame_algoritmos, text="Ejecutar Prog. Dinámica (modexPD)", command=lambda: self.ejecutar_algoritmo("PD")).pack(side="left", padx=10)

        # Frame Resultados y Verificación
        frame_res = ttk.LabelFrame(self.root, text=" 4. Resultados de la Solución y Verificación ", padding=10)
        frame_res.pack(fill="x", padx=15, pady=5)

        self.lbl_resultados = ttk.Label(frame_res, text="Selecciona y ejecuta un algoritmo para ver los resultados.", font=("Arial", 10, "bold"), foreground="navy")
        self.lbl_resultados.pack(anchor="w", pady=2)

        self.lbl_verificador = ttk.Label(frame_res, text="Estado Verificador: Pendiente", font=("Arial", 9, "italic"), foreground="gray")
        self.lbl_verificador.pack(anchor="w", pady=2)

        # Barra de progreso visual
        self.progress_bar = ttk.Progressbar(frame_res, orient="horizontal", mode="determinate", length=780)
        self.progress_bar.pack(fill="x", pady=5)

        btn_guardar = ttk.Button(frame_res, text="Guardar Salida en Archivo (.txt)", command=self.guardar_archivo)
        btn_guardar.pack(anchor="e", pady=2)

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos de Texto", "*.txt")])
        if not ruta:
            return

        try:
            self.red = leer_entrada(ruta)
            self.agentes = self.red.agentes
            self.R_max = self.red.presupuesto_maximo
            self.n = len(self.agentes)
            self.lbl_archivo.config(text=os.path.basename(ruta))
            self.lbl_info.config(text=f"Agentes: {self.n} | Presupuesto Máximo (R_max): {self.R_max}")
            self.lbl_verificador.config(text="Estado Verificador: Pendiente", foreground="gray")

            for item in self.tabla_agentes.get_children():
                self.tabla_agentes.delete(item)

            for idx, ag in enumerate(self.agentes):
                beneficio = float(ag.opinion ** 2 * ag.influencia)
                self.tabla_agentes.insert("", "end", values=(f"a_{idx}", ag.opinion, float(ag.receptividad), float(ag.influencia), ag.costo_moderacion(), f"{beneficio:.1f}", "-"))

            self.progress_bar["value"] = 0
            messagebox.showinfo("Éxito", f"Se cargaron {self.n} agentes correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo:\n{str(e)}")

    def ejecutar_algoritmo(self, tipo):
        if not self.agentes:
            messagebox.showwarning("Advertencia", "Por favor carga un archivo de entrada primero.")
            return

        if tipo == "FB" and self.n > 22:
            if not messagebox.askyesno("Confirmación", f"Fuerza Bruta con {self.n} agentes evaluará {2**self.n:,} combinaciones. ¿Deseas continuar?"):
                return

        self.root.config(cursor="watch")
        self.progress_bar["value"] = 0

        nombres_alg = {"FB": "Fuerza Bruta (modexFB)", "V": "Voraz (modexV)", "PD": "Programación Dinámica (modexPD)"}
        nombre_alg = nombres_alg[tipo]

        self.lbl_resultados.config(text=f" ⏳ Procesando con [{nombre_alg}]... Por favor espera.", foreground="darkorange")
        self.lbl_verificador.config(text="Verificando la solución resultante...", foreground="darkorange")

        def actualizar_progreso(val):
            self.root.after(0, lambda: self.progress_bar.config(value=val))

        def tarea_calculo():
            inicio = time.time()

            red = self.red
            if tipo == "FB":
                est, esf, ext = modexFB(red, callback_progreso=actualizar_progreso)
            elif tipo == "V":
                actualizar_progreso(50)
                est, esf, ext = modexV(red)
                actualizar_progreso(100)
            elif tipo == "PD":
                actualizar_progreso(50)
                est, esf, ext = modexPD(red)
                actualizar_progreso(100)

            fin = time.time()
            tiempo_ejecucion = fin - inicio

            # Conexión al verificador.py
            errores = verificar_salida(red, est, esf, ext)

            self.root.after(0, lambda: self._finalizar_calculo(nombre_alg, est, esf, ext, tiempo_ejecucion, errores))

        threading.Thread(target=tarea_calculo, daemon=True).start()

    def _finalizar_calculo(self, nombre_alg, est, esf, ext, tiempo_ejecucion, errores):
        self.root.config(cursor="")
        self.progress_bar["value"] = 100

        self.estrategia_resultado = est
        self.esfuerzo_resultado = esf
        self.extremismo_resultado = ext

        texto_tiempo = "< 0.001 s" if tiempo_ejecucion < 0.001 else f"{tiempo_ejecucion:.4f} s"
        agentes_moderados = sum(est)

        self.lbl_resultados.config(
            text=f"[{nombre_alg}] -> Extremismo: {ext:.{DECIMALES}f} | Esfuerzo: {esf}/{self.R_max} | Tiempo: {texto_tiempo} | Agentes Moderados: {agentes_moderados}/{self.n}",
            foreground="navy"
        )

        # Actualizar visualización de estado en la interfaz
        if not errores:
            self.lbl_verificador.config(text="✔ Verificación exitosa: La solución es válida y cumple todas las restricciones.", foreground="green")
        else:
            self.lbl_verificador.config(text=f"✖ Error de Verificación: {', '.join(errores)}", foreground="red")

        # Actualizar la tabla mostrando qué agente fue moderado en la estrategia
        for i, item_id in enumerate(self.tabla_agentes.get_children()):
            val = list(self.tabla_agentes.item(item_id, "values"))
            es_moderado = (est[i] == 1)
            moderado_txt = "SÍ (1)" if es_moderado else "NO (0)"

            if len(val) >= 7:
                val[6] = moderado_txt
            else:
                val.append(moderado_txt)

            tags = ("moderado_si",) if es_moderado else ()
            self.tabla_agentes.item(item_id, values=val, tags=tags)

        # Mostrar mensaje modal con el veredicto del verificador
        if errores:
            detalles_error = "\n- ".join(errores)
            messagebox.showwarning("Advertencia del Verificador", f"{nombre_alg} finalizó en {texto_tiempo}, pero se detectaron errores de verificación:\n\n- {detalles_error}")
        else:
            messagebox.showinfo("Proceso Completado", f"{nombre_alg} finalizó exitosamente en {texto_tiempo}.\nSolución verificada correctamente.")

    def guardar_archivo(self):
        if not self.estrategia_resultado:
            messagebox.showwarning("Advertencia", "No hay resultados para guardar.")
            return

        ruta = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de Texto", "*.txt")])
        if not ruta:
            return

        try:
            escribir_salida(ruta, (self.estrategia_resultado, self.esfuerzo_resultado, self.extremismo_resultado))
            messagebox.showinfo("Éxito", f"Archivo guardado exitosamente en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el archivo:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModExApp(root)
    root.mainloop()