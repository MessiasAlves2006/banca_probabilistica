import tkinter as tk
import random
import time
import threading
from PIL import Image, ImageTk
import pygame

# Inicializa o mixer de som
pygame.mixer.init()

# Lista de caminhos das imagens dos símbolos
SYMBOL_IMAGES_PATHS = [
    "img/tigre.png",
    "img/cereja.png",
    "img/dinheiro.png",
    "img/estrela.png",
    "img/sete.png",
    "img/trevo.png"
]

user_balance = 300
house_profit = 0

# JACKPOT: 5% de chance de ativar a qualquer rodada
JACKPOT_CHANCE = 0.05

#tocar musica de fundo
bgMusic = pygame.mixer.Sound("musica.mp3")
bgMusic.play(loops=-1)

def tocar_audio_derrota():
    pygame.mixer.music.load("faz_o_L.mp3")
    pygame.mixer.music.play()  # Remove loops=-1 para tocar só uma vez

def tocar_audio_perdeu_aposta():
    pygame.mixer.music.load("perdeu.mp3")
    pygame.mixer.music.play()

def tocar_audio_jackpot():
    pygame.mixer.music.load("jackpot.mp3")
    pygame.mixer.music.play()

def mostrar_derrota():
    # Cria um frame sobreposto cobrindo toda a janela
    derrota_frame = tk.Frame(root, bg="white")
    derrota_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Imagem do tigre
    img = Image.open("img/tigrinho_L.jpeg")
    img = img.resize((220, 220))
    photo = ImageTk.PhotoImage(img)
    label_img = tk.Label(derrota_frame, image=photo, bg="white")
    label_img.image = photo
    label_img.pack(pady=10)

    # Mensagem
    label_msg = tk.Label(
        derrota_frame,
        text="Você zerou a banca!\nFaz o L!",
        font=("Arial", 18, "bold"),
        fg="red",
        bg="white"
    )
    label_msg.pack(pady=10)

    # Botões
    def depositar():
        derrota_frame.destroy()
        # Aqui você pode adicionar lógica para depósito, ex: abrir um popup ou resetar saldo
        # Exemplo simples: adicionar saldo
        global user_balance
        user_balance = 300
        user_balance_label.config(text=f"Saldo: R${user_balance:.2f}")

    def sair():
        root.destroy()

    btn_depositar = tk.Button(derrota_frame, text="Depositar", font=("Arial", 12), command=depositar, bg="#4caf50", fg="white", width=12)
    btn_depositar.pack(pady=5)

    btn_sair = tk.Button(derrota_frame, text="Sair", font=("Arial", 12), command=sair, bg="#f44336", fg="white", width=12)
    btn_sair.pack(pady=5)

    # Toca o áudio
    tocar_audio_derrota()

def animar_slots(slots_labels, resultado_final, callback):
    def animar_passos(passos):
        if passos > 0:
            for i, label in enumerate(slots_labels):
                idx = random.randint(0, len(SYMBOL_IMAGES) - 1)
                label.config(image=SYMBOL_IMAGES[idx])
                label.image = SYMBOL_IMAGES[idx]
            root.after(100, animar_passos, passos - 1)
        else:
            for i in range(3):
                idx = resultado_final[i]
                slots_labels[i].config(image=SYMBOL_IMAGES[idx])
                slots_labels[i].image = SYMBOL_IMAGES[idx]
            callback()
    animar_passos(10)

def piscar_vitoria():
    def piscar():
        for _ in range(6):
            root.configure(bg="yellow")
            time.sleep(0.1)
            root.configure(bg="white")
            time.sleep(0.1)
    threading.Thread(target=piscar).start()

giro_em_andamento = False

def girar():
    global user_balance, house_profit, giro_em_andamento

    if giro_em_andamento:
        return  # Impede múltiplos giros simultâneos

    giro_em_andamento = True
    entry_aposta.config(state="disabled")
    btn_girar.config(state="disabled")

    try:
        aposta = float(entry_aposta.get())
    except ValueError:
        resultado_label.config(text="Aposta inválida!")
        entry_aposta.config(state="normal")
        btn_girar.config(state="normal")
        giro_em_andamento = False
        return

    if aposta > user_balance:
        resultado_label.config(text="Saldo insuficiente!")
        entry_aposta.config(state="normal")
        btn_girar.config(state="normal")
        giro_em_andamento = False
        return
    elif aposta <= 0:
        resultado_label.config(text="Aposta precisa ser maior que zero.")
        entry_aposta.config(state="normal")
        btn_girar.config(state="normal")
        giro_em_andamento = False
        return

    # Define chance de vitória
    if aposta <= 5:
        chance = 0.6
        multiplicador = random.uniform(1.5, 3.0)
    elif aposta <= 20:
        chance = 0.4
        multiplicador = random.uniform(1.2, 2.0)
    else:
        chance = 0.15
        multiplicador = random.uniform(1.0, 5.0)

    slots_labels = [slot1, slot2, slot3]
    resultado_final = [random.randint(0, len(SYMBOL_IMAGES) - 1) for _ in range(3)]

    def processar_resultado():
        global house_profit, giro_em_andamento
        nonlocal resultado_final
        resultado = random.random()
        jackpot = random.random() < JACKPOT_CHANCE
        ganho = 0

        if jackpot:
            ganho = random.randint(50, 500)
            resultado_label.config(text=f"JACKPOT!!! Você ganhou R${ganho:.2f}!")
            piscar_vitoria()
            tocar_audio_jackpot()

        elif resultado < chance:
            ganho = aposta * multiplicador
            resultado_label.config(text=f"Você GANHOU R${ganho:.2f}!")
            piscar_vitoria()
            tocar_audio_jackpot()

        else:
            resultado_label.config(text=f"Você PERDEU R${aposta:.2f}.")
            house_profit += aposta
            user_balance_update(-aposta)
            if user_balance > 0:
                tocar_audio_perdeu_aposta()
            if user_balance <= 0:  
                user_balance_label.config(text="Saldo: R$0.00")
            # Reabilita controles ao final
            entry_aposta.config(state="normal")
            btn_girar.config(state="normal")
            giro_em_andamento = False
            return

        lucro = ganho - aposta
        user_balance_update(lucro)
        house_profit -= lucro
        # Reabilita controles ao final
        entry_aposta.config(state="normal")
        btn_girar.config(state="normal")
        giro_em_andamento = False  # Libera para novo giro

    animar_slots(slots_labels, resultado_final, processar_resultado)

def user_balance_update(value):
    global user_balance
    user_balance += value
    # Arredonda para evitar valores residuais
    user_balance = round(user_balance, 2)
    if user_balance < 0.01:
        user_balance = 0.0
        user_balance_label.config(text="Saldo: R$0.00")
        mostrar_derrota()
    else:
        user_balance_label.config(text=f"Saldo: R${user_balance:.2f}")
#def house_profit_update(value):
#    global house_profit
#    house_profit += value
#    # Arredonda para evitar valores residuais
#    user_balance = round(user_balance, 2)

# Interface Gráfica
root = tk.Tk()
root.title("Tigrinho Jackpot")
root.geometry("500x500")
root.resizable(False, False)
root.configure(bg="white")


# Carrega as imagens principais
SYMBOL_IMAGES = [ImageTk.PhotoImage(Image.open(path).resize((64, 64))) for path in SYMBOL_IMAGES_PATHS]
# Carrega miniaturas para o rodapé
SYMBOL_THUMBS = [ImageTk.PhotoImage(Image.open(path).resize((24, 24))) for path in SYMBOL_IMAGES_PATHS]

# Saldo e aposta
user_balance_label = tk.Label(root, text=f"Saldo: R${user_balance:.2f}", font=("Arial", 14), bg="white")
user_balance_label.pack(pady=10)

# Slots
#root.attributes('-transparentcolor', "white")
slot_frame = tk.Frame(root, bg="white")
slot_frame.pack(pady=20)

slot1 = tk.Label(slot_frame, image=SYMBOL_IMAGES[0], bg="white")
slot1.pack(side='left', padx=10)

slot2 = tk.Label(slot_frame, image=SYMBOL_IMAGES[1], bg="white")
slot2.pack(side='left', padx=10)

slot3 = tk.Label(slot_frame, image=SYMBOL_IMAGES[2], bg="white")
slot3.pack(side='left', padx=10)

# Resultado
resultado_label = tk.Label(root, text="", font=("Arial", 12), fg="blue", bg="white")
resultado_label.pack(pady=10)

tk.Label(root, text="Valor da Aposta:", font=("Arial", 12), bg="white").pack()
entry_aposta = tk.Entry(root, font=("Arial", 12), justify="center")
entry_aposta.pack(pady=2)
entry_aposta.bind("<Return>", lambda event: girar())

# Botão girar
btn_girar = tk.Button(root, text="GIRAR", font=("Arial", 16), command=girar, bg="#ffae42")
btn_girar.pack(pady=10)

rodape_frame = tk.Frame(root, bg="white")
rodape_frame.pack(side="bottom", pady=1)

# Defina as combinações e prêmios (usando índices dos símbolos)
combinacoes = [
    ([4, 4, 4], "10x aposta"),      # 3x Sete
    ([0, 0, 0], "JACKPOT"),         # 3x Tigre
    ([2, 2, 2], "5x aposta"),       # 3x Dinheiro
    ([5, 5, 5], "3x aposta"),       # 3x Trevo
    ([3, 3, 3], "2x aposta"),       # 3x Estrela
    ([1, 1, 1], "1.5x aposta"),     # 3x Cereja
    ("2x iguais", "0.5x aposta"),
    ("Outros", "perde"),
]   

# Divide as combinações em duas colunas
col1 = combinacoes[:4]  # Primeira metade
col2 = combinacoes[4:]  # Segunda metade

col_frame1 = tk.Frame(rodape_frame, bg="white")
col_frame1.pack(side="left", padx=10, anchor="n")
col_frame2 = tk.Frame(rodape_frame, bg="white")
col_frame2.pack(side="left", padx=10, anchor="n")

for comb, premio in col1:
    linha = tk.Frame(col_frame1, bg="white")
    linha.pack(anchor="w")
    if isinstance(comb, list):
        for idx in comb:
            tk.Label(linha, image=SYMBOL_THUMBS[idx], bg="white").pack(side="left")
        tk.Label(linha, text=f" = {premio}", font=("Arial", 9), fg="gray", bg="white").pack(side="left")
    else:
        tk.Label(linha, text=f"{comb} = {premio}", font=("Arial", 9), fg="gray", bg="white").pack(side="left")

for comb, premio in col2:
    linha = tk.Frame(col_frame2, bg="white")
    linha.pack(anchor="w")
    if isinstance(comb, list):
        for idx in comb:
            tk.Label(linha, image=SYMBOL_THUMBS[idx], bg="white").pack(side="left")
        tk.Label(linha, text=f" = {premio}", font=("Arial", 9), fg="gray", bg="white").pack(side="left")
    else:
        tk.Label(linha, text=f"{comb} = {premio}", font=("Arial", 9), fg="gray", bg="white").pack(side="left")

root.mainloop()
