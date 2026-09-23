import tkinter as tk
from function import (
    inicializar_banco,
    iniciar_estado_a_partir_do_db,
    gerar_escala,
    exibir_logs,
    resetar_escala
)

janela = tk.Tk()
janela.title("Gerador de Escala Semanal")
janela.geometry("560x420")
janela.configure(bg="#1e1e1e")

titulo = tk.Label(
    janela,
    text="GERADOR DE ESCALA DO FINAL DE SEMANA",
    bg="#1e1e1e",
    fg="#00ffff",
    font=("Arial", 13, "bold")
)
titulo.pack(pady=15)

frame = tk.Frame(janela, bg="#1e1e1e")
frame.pack(pady=10)

tk.Label(frame, text="Sábado:", bg="#1e1e1e", fg="white",
         font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")

texto_sabado = tk.Label(frame, text="—", bg="#1e1e1e",
                        fg="#00ffff", font=("Arial", 12),
                        wraplength=390, justify="left")
texto_sabado.grid(row=0, column=1, sticky="w")

tk.Label(frame, text="Domingo:", bg="#1e1e1e", fg="white",
         font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")

texto_domingo = tk.Label(frame, text="—", bg="#1e1e1e",
                         fg="#00ffff", font=("Arial", 12))
texto_domingo.grid(row=1, column=1, sticky="w")

tk.Label(frame, text="Folga:", bg="#1e1e1e", fg="white",
         font=("Arial", 12, "bold")).grid(row=2, column=0, padx=10, pady=5, sticky="w")

texto_folga = tk.Label(frame, text="—", bg="#1e1e1e",
                       fg="#00ffff", font=("Arial", 12))
texto_folga.grid(row=2, column=1, sticky="w")

tk.Button(
    janela,
    text="Gerar Nova Escala",
    command=lambda: gerar_escala(texto_sabado, texto_domingo, texto_folga),
    bg="#00ffff",
    fg="#1e1e1e",
    font=("Arial", 12, "bold"),
    width=24
).pack(pady=6)

tk.Button(
    janela,
    text="Ver Histórico de Escalas",
    command=lambda: exibir_logs(janela),
    bg="#00ffff",
    fg="#1e1e1e",
    font=("Arial", 11, "bold"),
    width=24
).pack(pady=6)

tk.Button(
    janela,
    text="Resetar Escala",
    command=lambda: resetar_escala(texto_sabado, texto_domingo, texto_folga, confirm=True),
    bg="#ff1e00",
    fg="#1e1e1e",
    font=("Arial", 11, "bold"),
    width=24
).pack(pady=20)

inicializar_banco()
iniciar_estado_a_partir_do_db(texto_sabado, texto_domingo, texto_folga)

janela.mainloop()