import speech_recognition as sr
import pyttsx3
import spotipy
import os
import subprocess
import requests
import random
from spotipy import SpotifyOAuth
from datetime import datetime as dt
from num2words import num2words
from deep_translator import GoogleTranslator

reconhecedor = sr.Recognizer()
microfone = sr.Microphone()

escuta = pyttsx3.init()
resposta = ""

agora = dt.now()
hora = agora.hour
minuto = agora.minute

meses = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}

respostas = ["O que deseja?", "Pode falar", "Ao seu dispor", "Estou te ouvindo"]

dia = dt.today().day
mes = dt.today().month
ano = dt.today().year


def ouvir():
    try:
        with sr.Microphone(device_index=1) as source:
            print('Ouvindo...')
            voice = reconhecedor.listen(source)
            command = reconhecedor.recognize_google(voice, language='pt-br')
            print(command)
            return command

    except:
        return 'Não escutei nada :/'


def obter_pokemon():
    id_pokemon = str(random.randint(1, 1010))
    url_pokemon = f"https://pokeapi.co/api/v2/pokemon/{id_pokemon}"
    resposta_pokemon = requests.get(url_pokemon)
    dados_pokemon = resposta_pokemon.json()
    tipos = [tipo['type']['name'] for tipo in dados_pokemon['types']]
    pokemon = dados_pokemon['name']
    return tipos, pokemon


def obter_bored():
    url_bored = "http://www.boredapi.com/api/activity/"
    resposta_bored = requests.get(url_bored)
    dados_bored = resposta_bored.json()
    atividade = dados_bored['activity']
    return atividade


def obter_clima(cidade, chave_api):
    url_localizacao = f"http://dataservice.accuweather.com/locations/v1/cities/search"
    params_localizacao = {
        "apikey": chave_api,
        "q": cidade,
        "language": "pt"
    }

    # Obtendo a localização
    resposta_localizacao = requests.get(url_localizacao, params=params_localizacao)
    dados_localizacao = resposta_localizacao.json()
    localizacao_key = dados_localizacao[0]['Key']

    # Obtendo o clima atual
    url_clima = f"http://dataservice.accuweather.com/currentconditions/v1/{localizacao_key}"
    params_clima = {
        "apikey": chave_api,
        "details": True,
        "language": "pt"
    }

    resposta_clima = requests.get(url_clima, params=params_clima)
    dados_clima = resposta_clima.json()

    temperatura = dados_clima[0]['Temperature']['Metric']['Value']
    weathertext = dados_clima[0]['WeatherText']

    return temperatura, weathertext


cidade = "Osasco"
chave_api = "4UzZJLjlG6jvG9z7ki2AVvjFl60IwAje"


while True:
    with microfone as mic:
        reconhecedor.adjust_for_ambient_noise(mic)
        print("Estou ligada")
        audio = reconhecedor.listen(mic)
        resposta = reconhecedor.recognize_google(audio, language='pt')
        if resposta == "Alexa" or resposta == "sexta-feira":
            resposta = random.choice(respostas)
            escuta.say(resposta)
            escuta.runAndWait()
            # Variaveis do spotify
            os.environ['SPOTIPY_CLIENT_ID'] = '20b9cdbe8d59432dab55d7dba0fb150b'
            os.environ['SPOTIPY_CLIENT_SECRET'] = '19439bb9d4774dfbb29c6b9fea2a5479'
            os.environ['SPOTIPY_REDIRECT_URI'] = 'https://example.com/callback'

            # Termos e condições do spotify
            scope = "user-read-playback-state,user-modify-playback-state"
            sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

            # Teste de query - Sem microfone
            # query = 'hum of the fayth'
            # results = sp.search(query,1,0,"track")
            #
            # track_uri = results['tracks']['items'][0]['uri']
            # sp.start_playback(uris=[track_uri])

            reconhecedor.adjust_for_ambient_noise(mic)
            command = ouvir()

            # Spotify - Comandos "Toca <Nome da Música>" , "Para" ou "Continua"
            if 'toca' in command.lower():
                query = command.lower().replace('toca', '').strip()

                results = sp.search(query, 1, 0, "track")

                nome_artista = results['tracks']['items'][0]['artists'][0]['name']
                nome_musica = results['tracks']['items'][0]['name']
                track_uri = results['tracks']['items'][0]['uri']

                escuta.say(f'Tocando {nome_musica} por {nome_artista}')
                escuta.runAndWait()

                sp.start_playback(uris=[track_uri])

            elif 'para' in command.lower():
                sp.pause_playback()
            elif 'continua' in command.lower():
                sp.start_playback()

            if 'ler agenda' in command.lower():
                with open("agenda.txt", "r", encoding="utf-8") as arquivo:
                    texto = arquivo.read()
                    escuta.say(texto)
                    escuta.runAndWait()

            if 'escrever' in command.lower():
                escuta.say("O que deseja escrever?")
                escuta.runAndWait()
                reconhecedor.adjust_for_ambient_noise(mic)
                command = ouvir()
                with open("agenda.txt", "r+", encoding="utf-8") as arquivo:
                    arquivo.write("\n")
                    arquivo.write(command)
                    linhas = arquivo.readlines()
                    for i, linha in enumerate(linhas):
                        if linha == '\n':  # encontra a linha vazia
                            linhas.pop(i)  # remove a linha
                            break  # interrompe a iteração após encontrar a primeira linha vazia
                escuta.say("Escrito com sucesso")
                escuta.runAndWait()

            if 'deletar' in command.lower():
                with open('agenda.txt', 'r+') as arquivo:
                    linhas = arquivo.readlines()
                    linhas.pop()  # remove a última linha
                    arquivo.seek(0)
                    arquivo.writelines(linhas)
                    arquivo.truncate()  # apaga qualquer conteúdo que sobrou depois da última linha escrita
                    for i, linha in enumerate(linhas):
                        if linha == '\n':  # encontra a linha vazia
                            linhas.pop(i)  # remove a linha
                            break  # interrompe a iteração após encontrar a primeira linha vazia
                    arquivo.seek(0)
                    arquivo.writelines(linhas)
                    arquivo.truncate()  # apaga qualquer conteúdo que sobrou depois da última linha escrita
                escuta.say("Deletado com sucesso")
                escuta.runAndWait()

            if 'contar' in command.lower():
                with open("agenda.txt", "r") as arquivo:
                    contador = 0
                    conteudo = arquivo.read()
                    lista = conteudo.split("\n")

                    for i in lista:
                        if i:
                            contador += 1
                escuta.say("A quantidade de tarefas é: ")
                escuta.say(str(contador))
                escuta.runAndWait()

            if 'navegador' in command.lower():
                escuta.say("Abrindo navegador")
                escuta.runAndWait()
                subprocess.Popen('C:/Users/Erick/AppData/Local/Programs/Opera GX/opera.exe')

            if 'obrigado' in command.lower():
                escuta.say("É um prazer te ajudar mestre.")
                escuta.runAndWait()

            if 'qual o clima' in command.lower():
                temperatura, weathertext = obter_clima(cidade, chave_api)
                msg = "Agora está com" + str(int(temperatura)) + "graus em Osasco, e está" + weathertext
                escuta.say(msg)
                escuta.runAndWait()

            if 'que horas são' in command.lower():
                msg = "Agora são " + str(hora) + "horas e" + str(minuto) + "minutos"
                escuta.say(msg)
                escuta.runAndWait()

            if 'que dia é hoje' in command.lower():
                ano_por_extenso = num2words(ano, lang='pt_BR').replace('-', ' ')
                msg = ("Hoje é dia" + str(dia) + "de" + meses[mes] + "de" + str(ano_por_extenso))
                escuta.say(msg)
                escuta.runAndWait()

            if 'estou com tédio' in command.lower():
                atividade = obter_bored()
                msg = GoogleTranslator(source='auto', target='pt').translate(atividade)
                escuta.say("Aqui está uma coisa que você deveria fazer: ")
                escuta.say(msg)
                escuta.runAndWait()

            if 'desligue meu computador' in command.lower():
                escuta.say("Desligando seu computador em:")
                escuta.say("3")
                escuta.say("2")
                escuta.say("1")
                escuta.runAndWait()
                os.system('shutdown.exe -s -t 1')

            if 'me dê um pokémon aleatório' in command.lower():
                tipos, nome = obter_pokemon()
                qtd_poke = len(tipos)
                if qtd_poke == 1:
                    msg = ("O nome do seu Pokémon é: " + nome + "e o seu tipo é :" +
                           GoogleTranslator(source='auto', target='pt').translate(tipos[0]))
                else:
                    msg = "O nome do seu Pokémon é: " + nome + "e os seus tipos são :" + \
                          GoogleTranslator(source='auto', target='pt').translate(tipos[0]) + "e" + \
                          GoogleTranslator(source='auto', target='pt').translate(tipos[1])
                escuta.say(msg)
                escuta.runAndWait()
