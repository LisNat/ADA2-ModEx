import os
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from algoritmos import modexFB, modexV, modexPD
from entrada_salida import leer_entrada, escribir_salida

class ModExApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ModEx - Moderación de Extremismo en Redes Sociales")
        self.root.geometry("850x700")

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

        columnas = ("id", "op", "recep", "inf", "costo", "beneficio")
        self.tabla_agentes = ttk.Treeview(frame_red, columns=columnas, show="headings", height=8)

        self.tabla_agentes.heading("id", text="Agente ID")
        self.tabla_agentes.heading("op", text="Opinión (o_i)")
        self.tabla_agentes.heading("recep", text="Receptividad (r_i)")
        self.tabla_agentes.heading("inf", text="Influencia (inf_i)")
        self.tabla_agentes.heading("costo", text="Esfuerzo (Costo)")
        self.tabla_agentes.heading("beneficio", text="Red. Extremismo")

        for col in columnas:
            self.tabla_agentes.column(col, anchor="center", width=120)

        scrollbar = ttk.Scrollbar(frame_red, orient="vertical", command=self.tabla_agentes.yview)
        self.tabla_agentes.configure(yscroll=scrollbar.set)

        self.tabla_agentes.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame Algoritmos
        frame_algoritmos = ttk.LabelFrame(self.root, text=" 3. Ejecución de Algoritmos ", padding=10)
        frame_algoritmos.pack(fill="x", padx=15, pady=5)

        ttk.Button(frame_algoritmos, text="Ejecutar Fuerza Bruta (modexFB)", command=lambda: self.ejecutar_algoritmo("FB")).pack(side="left", padx=10)
        ttk.Button(frame_algoritmos, text="Ejecutar Voraz (modexV)", command=lambda: self.ejecutar_algoritmo("V")).pack(side="left", padx=10)
        ttk.Button(frame_algoritmos, text="Ejecutar Prog. Dinámica (modexPD)", command=lambda: self.ejecutar_algoritmo("PD")).pack(side="left", padx=10)

        # Frame Resultados y Barra de Progreso
        frame_res = ttk.LabelFrame(self.root, text=" 4. Resultados de la Solución ", padding=10)
        frame_res.pack(fill="x", padx=15, pady=5)

        self.lbl_resultados = ttk.Label(frame_res, text="Selecciona y ejecuta un algoritmo para ver los resultados.", font=("Arial", 10, "bold"), foreground="navy")
        self.lbl_resultados.pack(anchor="w", pady=2)

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

            for item in self.tabla_agentes.get_children():
                self.tabla_agentes.delete(item)

            for idx, ag in enumerate(self.agentes):
                beneficio = float(ag.opinion ** 2 * ag.influencia)
                self.tabla_agentes.insert("", "end", values=(f"a_{idx}", ag.opinion, float(ag.receptividad), float(ag.influencia), ag.costo_moderacion(), f"{beneficio:.1f}"))

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

            self.root.after(0, lambda: self._finalizar_calculo(nombre_alg, est, esf, ext, tiempo_ejecucion))

        threading.Thread(target=tarea_calculo, daemon=True).start()

    def _finalizar_calculo(self, nombre_alg, est, esf, ext, tiempo_ejecucion):
        self.root.config(cursor="")
        self.progress_bar["value"] = 100

        self.estrategia_resultado = est
        self.esfuerzo_resultado = esf
        self.extremismo_resultado = ext

        texto_tiempo = "< 0.001 s" if tiempo_ejecucion < 0.001 else f"{tiempo_ejecucion:.4f} s"

        self.lbl_resultados.config(
            text=f"[{nombre_alg}] -> Extremismo: {ext:.2f} | Esfuerzo: {esf}/{self.R_max} | Tiempo: {texto_tiempo}",
            foreground="navy"
        )

        for i, item_id in enumerate(self.tabla_agentes.get_children()):
            val = list(self.tabla_agentes.item(item_id, "values"))
            moderado = "SÍ (1)" if est[i] == 1 else "NO (0)"
            if len(val) == 6:
                val.append(moderado)
            else:
                val[6] = moderado
            self.tabla_agentes.item(item_id, values=val)

        messagebox.showinfo("Proceso Completado", f"{nombre_alg} finalizado en {texto_tiempo}.")

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
