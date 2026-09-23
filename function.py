import sqlite3
import os
import sys
from datetime import datetime, timedelta
from tkinter import messagebox, Toplevel, scrolledtext, Label
import tkinter as tk


def base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = base_path()
DB_FILE = os.path.join(BASE_DIR, "escala.db")
LOG_FILE = os.path.join(BASE_DIR, "logs.txt")

DATA_BASE = datetime(2026, 7, 11)

# Ciclo correto:
# Sábado 1 -> Sábado 2 -> Domingo -> Folga -> repete
CICLO = ["Sábado 1", "Sábado 2", "Domingo", "Folga"]

# Escala inicial:
# Sábado: Thiago, Riquelme e Isabelle
# Domingo: Michael
# Folga: Guilherme
COLABORADORES_INICIAIS = {
    "Thiago": 1,      # Segundo sábado
    "Isabelle": 0,    # Primeiro sábado
    "Guilherme": 0,   # Primeiro sábado
    "Michael": 2,     # Domingo
    "Riquelme": 3     # Folga
}

proximo_fim_semana = None


def inicializar_banco():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS escalas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_sabado TEXT,
            data_domingo TEXT,
            sabado TEXT,
            domingo TEXT,
            folga TEXT
        )
    """)
    conn.commit()
    conn.close()


def salvar_escala(ds, dd, sabados, domingos, folgas):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO escalas (data_sabado, data_domingo, sabado, domingo, folga) VALUES (?, ?, ?, ?, ?)",
        (ds, dd, ", ".join(sabados), ", ".join(domingos), ", ".join(folgas))
    )
    conn.commit()
    conn.close()

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]\n")
        f.write(f"Sábado ({ds}): {', '.join(sabados)}\n")
        f.write(f"Domingo ({dd}): {', '.join(domingos)}\n")
        f.write(f"Folga: {', '.join(folgas)}\n")
        f.write("-" * 40 + "\n")


def carregar_ultima_escala_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM escalas ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row


def calcular_fds_atual():
    hoje = datetime.now()

    # Próximo sábado
    dias_ate_sabado = (5 - hoje.weekday()) % 7

    sabado = hoje + timedelta(days=dias_ate_sabado)

    sabado = sabado.replace( 
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    domingo = sabado + timedelta(days=1)

    return sabado, domingo


def avancar_semana(fds):
    sabado, domingo = fds
    return sabado + timedelta(days=7), domingo + timedelta(days=7)

def calcular_escala(sabado_dt):
    # Quando não existir nenhuma escala salva, iniciar a rotação do zero.
    if not os.path.exists(DB_FILE):
        semanas = 0
    else:
        semanas = (sabado_dt - DATA_BASE).days // 7

    sabados = []
    domingos = []
    folgas = []

    for colaborador, indice_inicial in COLABORADORES_INICIAIS.items():
        indice_atual = (indice_inicial + semanas) % len(CICLO)
        status = CICLO[indice_atual]

        if status in ("Sábado 1", "Sábado 2"):
            sabados.append(colaborador)
        elif status == "Domingo":
            domingos.append(colaborador)
        else:
            folgas.append(colaborador)

    return sabados, domingos, folgas     


def gerar_escala(texto_sabado, texto_domingo, texto_folga):
    global proximo_fim_semana

    if proximo_fim_semana is None:
        proximo_fim_semana = calcular_fds_atual()

    sabado_dt, domingo_dt = proximo_fim_semana

    sabados, domingos, folgas = calcular_escala(sabado_dt)

    texto_sabado.config(
        text=f"{sabado_dt.strftime('%d/%m/%Y')} - {', '.join(sabados)}"
    )
    texto_domingo.config(
        text=f"{domingo_dt.strftime('%d/%m/%Y')} - {', '.join(domingos)}"
    )
    texto_folga.config(
        text=", ".join(folgas)
    )

    salvar_escala(
        sabado_dt.strftime("%d/%m/%Y"),
        domingo_dt.strftime("%d/%m/%Y"),
        sabados,
        domingos,
        folgas
    )

    proximo_fim_semana = avancar_semana(proximo_fim_semana)


def iniciar_estado_a_partir_do_db(texto_sabado, texto_domingo, texto_folga):
    global proximo_fim_semana

    row = carregar_ultima_escala_db()

    if not row:
        resetar_escala(texto_sabado, texto_domingo, texto_folga, confirm=False)
        return

    ds = row[1]
    dd = row[2]
    sabado = row[3]
    domingo = row[4]
    folga = row[5]

    texto_sabado.config(text=f"{ds} - {sabado}")
    texto_domingo.config(text=f"{dd} - {domingo}")
    texto_folga.config(text=folga)

    sabado_dt = datetime.strptime(ds, "%d/%m/%Y")
    domingo_dt = datetime.strptime(dd, "%d/%m/%Y")

    proximo_fim_semana = (
        sabado_dt + timedelta(days=7),
        domingo_dt + timedelta(days=7)
    )


def exibir_logs(janela):
    if not os.path.exists(LOG_FILE):
        messagebox.showinfo("Logs", "Nenhum log encontrado.")
        return

    win = Toplevel(janela)
    win.title("Histórico de Escalas")
    win.geometry("520x420")
    win.configure(bg="#1e1e1e")

    Label(
        win,
        text="Histórico de Escalas",
        bg="#1e1e1e",
        fg="#00ffff",
        font=("Arial", 13, "bold")
    ).pack(pady=10)

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        conteudo = f.read()

    box = scrolledtext.ScrolledText(
        win,
        wrap=tk.WORD,
        font=("Consolas", 10),
        bg="#111",
        fg="#00ffff"
    )
    box.insert(tk.END, conteudo)
    box.config(state="disabled")
    box.pack(expand=True, fill="both", padx=10, pady=10)

def resetar_escala(texto_sabado, texto_domingo, texto_folga, confirm=True):
    global proximo_fim_semana

    if confirm and not messagebox.askyesno(
        "Resetar Escala",
        "Deseja resetar a escala?"
    ):
        return

    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    inicializar_banco()

    # Sempre começa no próximo fim de semana
    proximo_fim_semana = calcular_fds_atual()

    gerar_escala(texto_sabado, texto_domingo, texto_folga)