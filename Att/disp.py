
import time
import datetime
import requests
import math
import re
import ctypes
import os
import sys
import mysql.connector
import subprocess
import webbrowser
import pytz

ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)

conn = mysql.connector.connect(
    host='login-database.cambz5iefybx.us-east-1.rds.amazonaws.com',
    user='admin',
    password='WFHzZoa#',
    database='logins'
)

configuracoes = {}


def ler_configuracoes_banco():
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM configs_envios LIMIT 1")
        return cursor.fetchone()
    except Exception as e:
        print(f"Erro ao ler configurações do banco de dados: {str(e)}")
        exit(1)


def ler_numeros_envio():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT numeros FROM envios_e_status")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Erro ao ler números de envio do banco de dados: {str(e)}")
        exit(1)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def isNaN(value):
    try:
        return math.isnan(float(value))
    except (ValueError, TypeError):
        return False


# Função para enviar mensagem de texto
def enviar_mensagem(numero, porta, message):
    url = f"http://localhost:{porta}/send-message"
    payload = {
        "number": f"{numero}",
        "message": message,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.status_code == 200


def abrir_qrcode(porta_min, porta_max):
    # Use resource_path para obter o caminho absoluto para os arquivos disparadores
    js_path_8000 = resource_path('disparador8000.js')
    js_path_8001 = resource_path('disparador8001.js')
    js_path_8002 = resource_path('disparador8002.js')
    js_path_8003 = resource_path('disparador8003.js')
    js_path_8004 = resource_path('disparador8004.js')

    # Inicia o Node.js com base nas portas selecionadas
    for porta in range(porta_min, porta_max + 1):
        if porta == 8000:
            js_path = js_path_8000
        elif porta == 8001:
            js_path = js_path_8001
        elif porta == 8002:
            js_path = js_path_8002
        elif porta == 8003:
            js_path = js_path_8003
        elif porta == 8004:
            js_path = js_path_8004
        else:
            # Trate outras portas, se necessário
            js_path = None

        if js_path:
            print(f"Iniciando Node.js com o arquivo {js_path}")
            try:
                subprocess.Popen(["node", js_path])
            except Exception as e:
                print(f"Erro ao iniciar o subprocesso: {e}")

        time.sleep(5)

        # Abre o web browser para cada porta
        for porta in range(porta_min, porta_max + 1):
            webbrowser.open(f"http://localhost:{porta}")

try:
    # Leitura das configurações do banco de dados
    configuracoes = ler_configuracoes_banco()

    # Utilize as informações lidas do banco de dados no seu código
    limiteQuantidade = int(configuracoes.get("limiteQuantidade"))
    saudacaoPersonalizada = configuracoes["saudacaoPersonalizada"]
    porta_min = int(configuracoes.get("porta_min"))
    porta_max = int(configuracoes.get("porta_max"))
    delay_mensagem_min = int(configuracoes.get("delay_min"))
    delay_mensagem_max = int(configuracoes.get("delay_max"))
    
    # Determine a saudação com base na hora atual
    agora = datetime.datetime.now(pytz.timezone("America/Sao_Paulo"))
    if 6 <= agora.hour < 12:
        saudacao = "Bom dia"
    elif 12 <= agora.hour < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    # Verifique se a saudacaoPersonalizada contém a string "{{saudacao}}"
    if "{{saudacao}}" in saudacaoPersonalizada:
        saudacaoPersonalizada = saudacaoPersonalizada.replace(
            '{{saudacao}}', saudacao)

    # Inicializa a contagem de envios
    quantidade = 0

    # Definindo a porta inicial para o envio das mensagens
    porta = porta_min

    # Obtendo os números de envio da tabela envios_e_status
    numeros_envio = ler_numeros_envio()

    # Verifica se os números de envio foram lidos corretamente
    if numeros_envio:
        # Abre os QR codes
        abrir_qrcode(porta_min, porta_max)
        tempo_espera = 50  # Tempo de espera em segundos
        time.sleep(tempo_espera)

        # Loop principal: percorre a lista de números de envio e envia mensagens
        for numero in numeros_envio:
            if porta > porta_max:
                porta = porta_min

            def substituir_opcoes(match):
                opcoes = match.group(1).split('|')
                return random.choice(opcoes)

            # Use uma expressão regular para encontrar as opções dentro das chaves {} e substituí-las aleatoriamente
            saudacaoPersonalizada_randomizada = re.sub(
                r'{([^}]+)}', substituir_opcoes, saudacaoPersonalizada)

            # Verifica se o limite de quantidade não excedeu o limite máximo definido
            if quantidade < limiteQuantidade:
                print(
                    f"Enviando saudação para o número {numero} da porta: {porta}"
                )
                if enviar_mensagem(numero, porta, saudacaoPersonalizada_randomizada):
                    quantidade += 1
                    # Atualiza o status na tabela envios_e_status
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE envios_e_status SET status = 'SUCESSO' WHERE numeros = %s", (numero,))
                    conn.commit()
                    print(f"Saudação enviada com sucesso!\n")
                else:
                    # Atualiza o status na tabela envios_e_status
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE envios_e_status SET status = 'ERRO' WHERE numeros = %s", (numero,))
                    conn.commit()
                    print(
                        f"Erro ao enviar saudação para o número {numero}!\n")
                porta += 1
                print(f"Total de envios: {quantidade}\n")

                delay = random.randint(
                    delay_mensagem_min, delay_mensagem_max)
                print(
                    f"Aguardando {delay} segundos antes de enviar para o próximo número...\n"
                )
                time.sleep(delay)

except Exception as e:
    print(f"Erro: {str(e)}")
finally:
    # Fechando a conexão com o banco de dados
    conn.close()
