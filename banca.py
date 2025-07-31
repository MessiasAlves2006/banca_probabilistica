import tkinter as tk
import random
from PIL import Image, ImageTk
import pygame

# --- 1. Inicialização e Variáveis Globais ---
pygame.mixer.init()

SYMBOL_IMAGES_PATHS = [
    "img/tigre.png",    # 0
    "img/cereja.png",   # 1
    "img/dinheiro.png", # 2
    "img/estrela.png",  # 3
    "img/sete.png",     # 4
    "img/trevo.png"     # 5
]

user_balance = 300.0
house_profit = 0.0

giro_em_andamento = False # Flag para evitar múltiplos giros simultâneos

# --- 2. Funções de Atualização de Saldo e Estatísticas ---
def user_balance_update(value):
    """Atualiza o saldo do usuário e o label na interface."""
    global user_balance
    user_balance += value
    user_balance = round(user_balance, 2) # Arredonda para evitar valores residuais

    if user_balance < 0.01: # Se o saldo for praticamente zero
        user_balance = 0.0
        user_balance_label.config(text="Saldo: R$0.00")
        mostrar_derrota()
    else:
        user_balance_label.config(text=f"Saldo: R${user_balance:.2f}")

def house_profit_update(value):
    """Atualiza o lucro da casa (se necessário exibir)."""
    global house_profit
    house_profit += value
    house_profit = round(house_profit, 2)
    # Você pode adicionar um label para house_profit na UI se quiser exibir

# --- 3. Funções de UI (Janelas/Mensagens) e Animação ---

def mostrar_derrota():
    """Exibe a tela de derrota quando o saldo zera."""
    derrota_frame = tk.Frame(root, bg="white")
    derrota_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    img = Image.open("img/tigrinho_L.jpeg")
    img = img.resize((300, 300))
    photo = ImageTk.PhotoImage(img)
    label_img = tk.Label(derrota_frame, image=photo, bg="white")
    label_img.image = photo
    label_img.pack(pady=10)

    label_msg = tk.Label(
        derrota_frame,
        text="Você zerou a banca!\nFaz o L!",
        font=("Arial", 18, "bold"),
        fg="red",
        bg="white"
    )
    label_msg.pack(pady=10)

    def depositar():
        derrota_frame.destroy()
        global user_balance
        user_balance = 300.0 # Reseta o saldo
        user_balance_update(0) # Atualiza o label do saldo

    def sair():
        root.destroy()

    btn_depositar = tk.Button(derrota_frame, text="Depositar", font=("Arial", 12), command=depositar, bg="#4caf50", fg="white", width=12)
    btn_depositar.pack(pady=5)

    btn_sair = tk.Button(derrota_frame, text="Sair", font=("Arial", 12), command=sair, bg="#f44336", fg="white", width=12)
    btn_sair.pack(pady=5)

    tocar_audio_derrota()

# --- 4. Funções de Áudio ---
bgMusic = pygame.mixer.Sound("musica.mp3")

def play_background_music():
    bgMusic.play(loops=-1)

def tocar_audio_derrota():
    pygame.mixer.music.load("faz_o_L.mp3")
    pygame.mixer.music.play()

def tocar_audio_perdeu_aposta():
    pygame.mixer.music.load("perdeu.mp3")
    pygame.mixer.music.play()

def tocar_audio_jackpot():
    pygame.mixer.music.load("jackpot.mp3")
    pygame.mixer.music.play()

# --- 5. Lógica Principal do Jogo (Probabilidade e Resultados Baseados em Símbolos) ---
def girar():
    """Função principal que inicia um giro nos slots."""
    global user_balance, house_profit, giro_em_andamento

    if giro_em_andamento:
        return # Impede múltiplos giros simultâneos

    giro_em_andamento = True
    entry_aposta.config(state="disabled") # Desabilita entrada de aposta
    btn_girar.config(state="disabled") # Desabilita botão de giro

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

    slots_labels = [slot1, slot2, slot3]

    # Dicionário de probabilidades base por tipo de combinação
    probabilidades_base = {
        "JACKPOT": 0.005,  # Chance base de 3 tigres (muito raro)
        "3_SETE": 0.01,    # Chance base de 3 setes
        "3_DINHEIRO": 0.02,
        "3_TREVO": 0.03,
        "3_ESTRELA": 0.04,
        "3_CEREJA": 0.05,
        "2_IGUAIS": 0.20,  # Chance base de 2 símbolos iguais
        "PERDA": 0.645     # O restante é a chance de perda total (1 - soma das outras)
    }

    resultado_final_animacao = [random.randint(0, len(SYMBOL_IMAGES) - 1) for _ in range(3)] # Padrão: aleatório

    
    chance_jackpot_ajustada = probabilidades_base["JACKPOT"]
    chance_3_iguais_ajustada = {}
    chance_2_iguais_ajustada = probabilidades_base["2_IGUAIS"]
    
    # Fatores de ajuste: menores que 1 para reduzir chance, maiores que 1 para aumentar
    fator_aposta_baixa_ganho = 1.8 # Aumenta a chance de vitórias para apostas baixas
    fator_aposta_alta_ganho = 0.6  # Reduz a chance de vitórias para apostas altas

    if aposta <= 5.0: # Aposta baixa
        # Aumenta as chances de todas as vitórias
        chance_jackpot_ajustada *= 1.5 # Jackpot um pouco mais provável
        chance_3_iguais_ajustada = {k: v * fator_aposta_baixa_ganho for k, v in {
            "3_SETE": 0.01, "3_DINHEIRO": 0.02, "3_TREVO": 0.03,
            "3_ESTRELA": 0.04, "3_CEREJA": 0.05
        }.items()}
        chance_2_iguais_ajustada *= fator_aposta_baixa_ganho
    elif aposta > 5.0 and aposta <= 20.0: # Aposta média
        # Chances mais próximas do base, ligeiramente a favor da casa
        chance_3_iguais_ajustada = {k: v for k, v in {
            "3_SETE": 0.01, "3_DINHEIRO": 0.02, "3_TREVO": 0.03,
            "3_ESTRELA": 0.04, "3_CEREJA": 0.05
        }.items()}
    else: # Aposta alta
        # Reduz significativamente as chances de vitória
        chance_jackpot_ajustada *= 0.5 # Jackpot muito mais raro
        chance_3_iguais_ajustada = {k: v * fator_aposta_alta_ganho for k, v in {
            "3_SETE": 0.01, "3_DINHEIRO": 0.02, "3_TREVO": 0.03,
            "3_ESTRELA": 0.04, "3_CEREJA": 0.05
        }.items()}
        chance_2_iguais_ajustada *= fator_aposta_alta_ganho
    
    # Garantir que a soma das chances não ultrapasse 1 e que PERDA seja o complemento
    
    roll = random.random() # Um único roll para decidir o tipo de resultado

    if roll < chance_jackpot_ajustada:
        resultado_final_animacao = [0, 0, 0] # Força 3 tigres (JACKPOT)
    elif roll < chance_jackpot_ajustada + chance_3_iguais_ajustada.get("3_SETE", 0):
        resultado_final_animacao = [4, 4, 4] # 3x Sete
    elif roll < chance_jackpot_ajustada + chance_3_iguais_ajustada.get("3_SETE", 0) + chance_3_iguais_ajustada.get("3_DINHEIRO", 0):
        resultado_final_animacao = [2, 2, 2] # 3x Dinheiro
    elif roll < chance_jackpot_ajustada + sum(chance_3_iguais_ajustada[k] for k in ["3_SETE", "3_DINHEIRO", "3_TREVO"]):
        resultado_final_animacao = [5, 5, 5] # 3x Trevo
    elif roll < chance_jackpot_ajustada + sum(chance_3_iguais_ajustada[k] for k in ["3_SETE", "3_DINHEIRO", "3_TREVO", "3_ESTRELA"]):
        resultado_final_animacao = [3, 3, 3] # 3x Estrela
    elif roll < chance_jackpot_ajustada + sum(chance_3_iguais_ajustada[k] for k in ["3_SETE", "3_DINHEIRO", "3_TREVO", "3_ESTRELA", "3_CEREJA"]):
        resultado_final_animacao = [1, 1, 1] # 3x Cereja
    elif roll < (chance_jackpot_ajustada + sum(chance_3_iguais_ajustada.values()) + chance_2_iguais_ajustada):
        # Para 2 iguais, sorteamos dois símbolos iguais e um diferente
        idx1 = random.randint(0, len(SYMBOL_IMAGES) - 1)
        idx2 = random.randint(0, len(SYMBOL_IMAGES) - 1)
        while idx2 == idx1: # Garante que o terceiro símbolo é diferente
            idx2 = random.randint(0, len(SYMBOL_IMAGES) - 1)
        
        # Sorteia a posição dos dois iguais
        pos1, pos2, pos3 = random.sample(range(3), 3)
        temp_result = [0, 0, 0]
        temp_result[pos1] = idx1
        temp_result[pos2] = idx1
        temp_result[pos3] = idx2
        resultado_final_animacao = temp_result
    else:
        # Padrão: Perda (qualquer combinação não vencedora)
        # Sorteia 3 símbolos diferentes para garantir a perda mais comum
        unique_symbols = random.sample(range(len(SYMBOL_IMAGES)), 3)
        resultado_final_animacao = unique_symbols
        # Ou simplesmente aleatório se não precisar ser 3 diferentes
        # resultado_final_animacao = [random.randint(0, len(SYMBOL_IMAGES) - 1) for _ in range(3)]


    def processar_resultado(simbolos_finais_exibidos):
        """Função chamada após a animação dos slots para determinar o resultado com base nos símbolos."""
        global house_profit, giro_em_andamento
        ganho = 0.0
        premio_encontrado = False

        # Verifica JACKPOT (3 Tigres)
        if simbolos_finais_exibidos == [0, 0, 0]: # Símbolo do Tigre
            ganho = aposta * random.uniform(50, 100) # Valor do Jackpot escala com a aposta agora
            resultado_label.config(text=f"JACKPOT!!! Você ganhou R${ganho:.2f}!")
            tocar_audio_jackpot()
            premio_encontrado = True
        else:
            # Verifica outras combinações de 3 símbolos iguais
            if simbolos_finais_exibidos[0] == simbolos_finais_exibidos[1] == simbolos_finais_exibidos[2]:
                simbolo_ganhador_idx = simbolos_finais_exibidos[0]
                if simbolo_ganhador_idx == 4: # 3x Sete
                    ganho = aposta * 10.0
                elif simbolo_ganhador_idx == 2: # 3x Dinheiro
                    ganho = aposta * 5.0
                elif simbolo_ganhador_idx == 5: # 3x Trevo
                    ganho = aposta * 3.0
                elif simbolo_ganhador_idx == 3: # 3x Estrela
                    ganho = aposta * 2.0
                elif simbolo_ganhador_idx == 1: # 3x Cereja
                    ganho = aposta * 1.5
                
                if ganho > 0: # Se alguma combinação de 3 iguais foi encontrada (e não foi tigre)
                    resultado_label.config(text=f"TRÊS IGUAIS! Você ganhou R${ganho:.2f}!")
                    tocar_audio_jackpot()
                    premio_encontrado = True
            
            # Se não houve 3 iguais, verifica 2 símbolos iguais
            if not premio_encontrado:
                # Conta a frequência de cada símbolo para verificar se há 2 iguais
                from collections import Counter
                contagem_simbolos = Counter(simbolos_finais_exibidos)
                
                # Se algum símbolo aparece 2 vezes (e não 3, pois já foi tratado)
                if any(count == 2 for count in contagem_simbolos.values()):
                    ganho = aposta * 0.5 # Exemplo de prêmio para 2 iguais
                    resultado_label.config(text=f"DOIS IGUAIS! Você ganhou R${ganho:.2f}!")
                    premio_encontrado = True

        # --- Lógica Final de Ajuste de Saldo e Controles ---
        if not premio_encontrado: # Se não houve nenhum tipo de vitória
            resultado_label.config(text=f"Você PERDEU R${aposta:.2f}.")
            house_profit_update(aposta)
            user_balance_update(-aposta)
            if user_balance > 0:
                tocar_audio_perdeu_aposta()
            # Se o saldo zerou, user_balance_update já chama mostrar_derrota()
        else: # Se houve algum ganho (jackpot ou vitória por combinação)
            lucro_liquido = ganho - aposta
            user_balance_update(lucro_liquido)
            house_profit_update(-lucro_liquido) # Lucro da casa diminui com a vitória do jogador

        # Reabilita os controles no final, independentemente do resultado
        entry_aposta.config(state="normal")
        btn_girar.config(state="normal")
        giro_em_andamento = False # Libera para um novo giro

    # Inicia a animação dos slots, passando o resultado_final_animacao para a função de callback
    animar_slots(slots_labels, resultado_final_animacao, lambda: processar_resultado(resultado_final_animacao))

# --- 6. Funções de Manipulação Visual dos Slots ---
def animar_slots(slots_labels, resultado_final, callback):
    """Controla a animação de giro dos slots."""
    def animar_passos(passos):
        if passos > 0:
            for i, label in enumerate(slots_labels):
                idx = random.randint(0, len(SYMBOL_IMAGES) - 1)
                label.config(image=SYMBOL_IMAGES[idx])
                label.image = SYMBOL_IMAGES[idx] # Manter referência
            root.after(100, animar_passos, passos - 1)
        else:
            # Exibe o resultado final após a animação
            for i in range(3):
                idx = resultado_final[i]
                slots_labels[i].config(image=SYMBOL_IMAGES[idx])
                slots_labels[i].image = SYMBOL_IMAGES[idx] # Manter referência
            callback() # Chama a função de processamento de resultado com os símbolos finais

    animar_passos(15) # Número de passos da animação

# --- 7. Configuração da Interface Gráfica (Tkinter) ---
root = tk.Tk()
root.title("Tigrinho Jackpot")
root.geometry("1000x700")
root.resizable(False, False)

# Carrega e define o background
bg_img = Image.open("img/bg.jpg").resize((1000, 700))
bg_photo = ImageTk.PhotoImage(bg_img)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Carrega as imagens principais dos símbolos e as miniaturas
SYMBOL_IMAGES = [ImageTk.PhotoImage(Image.open(path).resize((64, 64))) for path in SYMBOL_IMAGES_PATHS]
SYMBOL_THUMBS = [ImageTk.PhotoImage(Image.open(path).resize((24, 24))) for path in SYMBOL_IMAGES_PATHS]

# Saldo do Usuário
user_balance_label = tk.Label(root, text=f"Saldo: R${user_balance:.2f}", font=("Arial", 14), bg="white")
user_balance_label.pack(pady=10)

# Frame dos Slots
slot_frame = tk.Frame(root, bg="white")
slot_frame.pack(pady=20)

slot1 = tk.Label(slot_frame, image=SYMBOL_IMAGES[0], bg="white")
slot1.pack(side='left', padx=10)

slot2 = tk.Label(slot_frame, image=SYMBOL_IMAGES[1], bg="white")
slot2.pack(side='left', padx=10)

slot3 = tk.Label(slot_frame, image=SYMBOL_IMAGES[2], bg="white")
slot3.pack(side='left', padx=10)
    
# Label de Resultado
resultado_label = tk.Label(root, text="", font=("Arial", 12), fg="blue", bg="white")
resultado_label.pack(pady=10)

# Entrada de Aposta
tk.Label(root, text="Valor da Aposta:", font=("Arial", 12), bg="white").pack()
entry_aposta = tk.Entry(root, font=("Arial", 12), justify="center")
entry_aposta.pack(pady=2)
entry_aposta.bind("<Return>", lambda event: girar()) # Permite girar com Enter

# Botão Girar
btn_girar = tk.Button(root, text="GIRAR", font=("Arial", 16), command=girar, bg="#ffae42")
btn_girar.pack(pady=10)

# Rodapé com Combinações e Prêmios
rodape_frame = tk.Frame(root, bg="white")
rodape_frame.pack(side="bottom", pady=1)

combinacoes = [
    ([0, 0, 0], "JACKPOT"),      # 3x Tigre
    ([4, 4, 4], "10x aposta"),   # 3x Sete
    ([2, 2, 2], "5x aposta"),    # 3x Dinheiro
    ([5, 5, 5], "3x aposta"),    # 3x Trevo
    ([3, 3, 3], "2x aposta"),    # 3x Estrela
    ([1, 1, 1], "1.5x aposta"),  # 3x Cereja
    ("2x iguais", "0.5x aposta"),
    ("Outros", "perde"),
]

for comb, premio in combinacoes:
    linha = tk.Frame(rodape_frame, bg="white")
    linha.pack(anchor="w")
    if isinstance(comb, list):
        for idx in comb:
            tk.Label(linha, image=SYMBOL_THUMBS[idx], bg="white").pack(side="left")
        tk.Label(linha, text=f" = {premio}", font=("Arial", 9), fg="gray", bg="white").pack(side="left")
    else:
        tk.Label(linha, text=f"{comb} = {premio}", font=("Arial", 9), fg="gray", bg="white").pack(side="left")

# --- 8. Início do Jogo ---
play_background_music() # Começa a tocar a música de fundo
root.mainloop()