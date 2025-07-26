import tkinter as tk
import random
import time
import threading
from PIL import Image, ImageTk
import pygame

# Inicializa o mixer de som
pygame.mixer.init()

# Lista de símbolos do "tigrinho"
SYMBOLS = ['🐯', '🍒', '💰', '⭐', '', '🍀']
user_balance = 300
house_profit = 300000

# JACKPOT: 5% de chance de ativar a qualquer rodada
JACKPOT_CHANCE = 0.05

def tocar_audio_derrota():
    pygame.mixer.music.load("faz_o_L.mp3")
    pygame.mixer.music.play()

def mostrar_derrota():
    derrota_janela = tk.Toplevel()
    derrota_janela.title("Você perdeu tudo!")
    derrota_janela.geometry("300x350")
    
    img = Image.open("tigrinho_L.jpeg")
    img = img.resize((200, 200))
    photo = ImageTk.PhotoImage(img)
    
    label_img = tk.Label(derrota_janela, image=photo)
    label_img.image = photo
    label_img.pack(pady=10)
    
    label_msg = tk.Label(derrota_janela, text="Você zerou a banca!\nFaz o L! 💀", font=("Arial", 14), fg="red")
    label_msg.pack(pady=10)
    
    tocar_audio_derrota()

def animar_slots(slots_labels, resultado_final, callback):
    def animar():
        for _ in range(10):
            for label in slots_labels:
                label.config(text=random.choice(SYMBOLS))
            time.sleep(0.1)
        for i in range(3):
            slots_labels[i].config(text=resultado_final[i])
        callback()
    threading.Thread(target=animar).start()

def piscar_vitoria():
    def piscar():
        for _ in range(6):
            root.configure(bg="yellow")
            time.sleep(0.1)
            root.configure(bg="white")
            time.sleep(0.1)
    threading.Thread(target=piscar).start()

def girar():
    global user_balance, house_profit

    try:
        aposta = float(entry_aposta.get())
    except ValueError:
        resultado_label.config(text="Aposta inválida!")
        return

    if aposta > user_balance:
        resultado_label.config(text="Saldo insuficiente!")
        return
    elif aposta <= 0:
        resultado_label.config(text="Aposta precisa ser maior que zero.")
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
    resultado_final = [random.choice(SYMBOLS) for _ in range(3)]

    def processar_resultado():
        global house_profit
        nonlocal resultado_final
        resultado = random.random()
        jackpot = random.random() < JACKPOT_CHANCE
        ganho = 0

        if jackpot:
            ganho = random.randint(50, 500)
            resultado_label.config(text=f"💰 JACKPOT!!! Você ganhou R${ganho:.2f}!")
            piscar_vitoria()
        elif resultado < chance:
            ganho = aposta * multiplicador
            resultado_label.config(text=f"🎉 Você GANHOU R${ganho:.2f}!")
            piscar_vitoria()
        else:
            resultado_label.config(text=f"💸 Você PERDEU R${aposta:.2f}.")
            house_profit += aposta
            user_balance_update(-aposta)
            if user_balance <= 0:
                user_balance_label.config(text="Saldo: R$0.00")
            return

        lucro = ganho - aposta
        user_balance_update(lucro)
        house_profit -= lucro

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

# Interface Gráfica
root = tk.Tk()
root.title("🎰 Tigrinho Jackpot")
root.geometry("420x430")
root.resizable(False, False)
root.configure(bg="white")

# Saldo e aposta
user_balance_label = tk.Label(root, text=f"Saldo: R${user_balance:.2f}", font=("Arial", 14), bg="white")
user_balance_label.pack(pady=10)

tk.Label(root, text="Valor da Aposta:", font=("Arial", 12), bg="white").pack()
entry_aposta = tk.Entry(root, font=("Arial", 12), justify="center")
entry_aposta.pack(pady=5)

# Slots
slot_frame = tk.Frame(root, bg="white")
slot_frame.pack(pady=20)

slot1 = tk.Label(slot_frame, text='❓', font=("Arial", 36))
slot1.pack(side='left', padx=10)

slot2 = tk.Label(slot_frame, text='❓', font=("Arial", 36))
slot2.pack(side='left', padx=10)

slot3 = tk.Label(slot_frame, text='❓', font=("Arial", 36))
slot3.pack(side='left', padx=10)

# Botão girar
btn_girar = tk.Button(root, text="🎯 GIRAR", font=("Arial", 16), command=girar, bg="#ffae42")
btn_girar.pack(pady=10)

# Resultado
resultado_label = tk.Label(root, text="", font=("Arial", 12), fg="blue", bg="white")
resultado_label.pack(pady=10)

root.mainloop()
