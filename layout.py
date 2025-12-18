# O que é um fork?
#Um fork é uma cópia de um projeto de software que permite modificá-lo independentemente do projeto original. Forks geralmente acontecem quando:
#A comunidade deseja implementar mudanças que o autor original não aceita ou não tem tempo para adicionar.
#O projeto original fica inativo, e alguém decide continuar o desenvolvimento.
#Divergências de visão entre os desenvolvedores originais e novos contribuintes.
#No caso de software open-source (código aberto), como o youtube-dl, qualquer pessoa pode fazer um fork, modificar o código e compartilhar sua #própria versão.

import yt_dlp
import tkinter as tk
import os
import time
import glob
import validators # verificar se a url é válida
from tkinter import Checkbutton, BooleanVar
from tkinter import ttk
from urllib.parse import urlparse

cor_1 = '#030303'  # Preto
cor_3 = '#ffffff'  # Branco
cor_5 = '#616161'  # Cinza
cor_6 = '#23fa02' # verde
cor_7 = '#02faee' # ciano
cor_8 = '#f7f7e6' # sei não


# Janela principal
janela = tk.Tk()

# Configuração da janela
janela.title("URL Downloader")
janela.geometry("800x600")  # Largura x Altura
janela.configure(bg=cor_3)

# Criando a label principal
label = tk.Label(janela, text="Baixe URLs da mídia de sua escolha", font=("Arial", 16), bg=cor_3, fg=cor_1)
label.pack()

# Criar o frame principal
frame = tk.Frame(janela, width=600, height=150, bg=cor_3)
frame.pack(side="top", padx=10, pady=10)

# Variável global para o estado do Checkbutton
apenas_audio = BooleanVar() # audio apenas
legendas = BooleanVar()





# Função para atualizar a tela
def Atualizar_tela():
    # Limpar o conteúdo do frame atual
    for widget in frame.winfo_children():
        widget.destroy()

def Funcoes_botao(entrada):
   url = entrada.get().strip() 
   if url:
        if not validators.url(url):
         print("URL inválida! Por favor, insira uma URL válida.")
         return
        
       # ListarFormatos(url)
        Update_progress()
        Download(url)

def Tela_inicial():

    # Atualiza a tela e limpa widgets existentes no frame
    Atualizar_tela()

    entrada = tk.Entry(frame, font=("Arial", 14), width=30, bg=cor_8,fg=cor_1)
    entrada.pack(pady=5)

    botao = tk.Button(frame,
        text='Download',
        command=lambda: Funcoes_botao(entrada),
            fg=cor_3,
            bg=cor_6,
            width=15,
            height=2,
            font=("Helvetica", 12, "bold"),
            activebackground=cor_7,
            activeforeground=cor_3,
            relief="flat",
            bd=4
        )
    
    botao.pack(side='top', padx=5)

    check1 = Checkbutton(janela, text="Apenas Áudio (MP3)", variable=apenas_audio,bg=cor_8)
    check1.pack()

    check2 = Checkbutton(janela, text="Legendas (pt-BR)", variable=legendas, bg=cor_8)
    check2.pack()


def Update_progress():

    # Barra de progresso
    progress = ttk.Progressbar(janela, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=20)
    for i in range(101):
        progress['value'] = i  # Atualiza a barra
        janela.update_idletasks()  # Atualiza a interface gráfica
        janela.after(50)  # Aguarda 50 milissegundos para dar a sensação de progresso

    progress.destroy()

def Download(url):

    dominio = urlparse(url).netloc

    # ===============================
    # BASE LOCAL (SEM GLOBAL)
    # ===============================
    base_opts = {
        # JS necessário para player moderno
        'js_runtimes': {'node': {}},
        'remote_components': ['ejs:github'],

        # FFmpeg
        'ffmpeg_location': r'C:\ProgramData\chocolatey\bin\ffmpeg.exe',

        # Estabilidade
        'sleep_interval': 4,
        'max_sleep_interval': 6,
        'retries': 5,
        'fragment_retries': 5,
    }

    # ===============================
    # 1) DOWNLOAD VÍDEO / ÁUDIO
    # ===============================
    ydl_video_opts = dict(base_opts)
    ydl_video_opts['outtmpl'] = 'downloads/%(title)s.%(ext)s'

    if "youtube.com" in dominio or "youtu.be" in dominio:
        if apenas_audio.get():
            ydl_video_opts.update({
                'format': 'bestaudio[ext=m4a]/bestaudio',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'downloads/youtube/%(title)s.%(ext)s',
            })
        else:
            ydl_video_opts.update({
                'format': '(bestvideo[ext=mp4]/best[ext=mp4])+(bestaudio[ext=m4a]/bestaudio)',
                'merge_output_format': 'mp4',
                'outtmpl': 'downloads/youtube/%(title)s.%(ext)s',
            })
    else:
        ydl_video_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_video_opts) as ydl:
            ydl.download([url])
            print("Vídeo/áudio baixado com sucesso")
    except yt_dlp.utils.DownloadError as e:
        print(f"Erro no download do vídeo: {e}")
        return
    
    time.sleep(35)
    # ===============================
    # FUNÇÃO AUXILIAR: VERIFICA SRT
    # ===============================
    def legenda_existe():
        return bool(glob.glob('downloads/youtube/*.srt'))

    # ===============================
    # 2) LEGENDAS — TENTATIVA SEM JS
    # ===============================
    if legendas.get():

        ydl_sub_opts = dict(base_opts)
        ydl_sub_opts.update({
            # DESATIVA JS
            'js_runtimes': {},
            'remote_components': [],

            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['pt-BR'],
            'subtitlesformat': 'srt',
            'outtmpl': 'downloads/youtube/%(title)s.%(ext)s',

            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,

            'sleep_interval': 6,
            'max_sleep_interval': 10,
            'retries': 3,
            'fragment_retries': 3,
        })

        with yt_dlp.YoutubeDL(ydl_sub_opts) as ydl:
            ydl.download([url])

        # ===============================
        # 3) FALLBACK COM JS (SE NECESSÁRIO)
        # ===============================
        if not legenda_existe():

            ydl_sub_opts_js = dict(base_opts)
            ydl_sub_opts_js.update({
                # JS ATIVO AQUI
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,

                'subtitleslangs': ['pt-BR'],
                'subtitlesformat': 'srt',
                'outtmpl': 'downloads/youtube/%(title)s.%(ext)s',

                'ignoreerrors': True,
                'quiet': True,
            })

            try:
                with yt_dlp.YoutubeDL(ydl_sub_opts_js) as ydl:
                    ydl.download([url])
                    print("Legenda obtida via fallback JS")
            except yt_dlp.utils.DownloadError:
                print("Legenda indisponível para este vídeo")
        else:
            print("Legenda obtida sem JS")

# def ListarFormatos(url):
#    try:
#        with yt_dlp.YoutubeDL({'listformats': None}) as ydl:
#            info = ydl.extract_info(url, download=False)
#            formatos = info.get('formats', [])
#            print("Formatos disponíveis:")
#            for formato in formatos:
#                print(f"ID: {formato['format_id']}, Resolução: {formato.get('resolution', 'N/A')}, Extensão: {formato.get('ext', 'N/A')}")
#    except Exception as e:
#        print(f"Erro ao listar formatos: {e}")
#



Tela_inicial()
# Inicializar o projeto
janela.mainloop()

# bolar maneira de baixar video de outras midias alem do yt (ok)

# testes

# https://youtu.be/C6h0Qt329jI?si=YEP0SrQrm_g6eUuj

# https://www.tiktok.com/@zueirarrando/video/7436160671470914871?is_from_webapp=1&sender_device=pc

# https://www.twitch.tv/alanzoka/clip/BenevolentTawdryNightingaleCmonBruh-IhSaugl3kdXkyhtj

# https://youtu.be/HARmkzmXtfY?si=x02Oa9boc2kYBfif Testar a parte de legenda automatica

#  https://youtu.be/QNJL6nfu__Q?si=Zl621fLLweAq-zQQ  testar apenas audio mp3

