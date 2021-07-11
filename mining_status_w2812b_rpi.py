# -*- coding: utf-8 -*-
import ledEffects, requests, locale, socket, time
from decimal import Decimal
from config import *
from threading import Thread
from datetime import datetime
import board, neopixel
locale.setlocale(locale.LC_ALL, '')

# Configuração dos LEDs
LED_COUNT	= 144			# Número de pixels no LED.
LED_PIN		= board.D18		# Pino GPIO do Raspberry. Só funciona no D10, 12, 18 e 21.
LED_ORDER = neopixel.GRB 	# Ordem dos LEDs. RGB, GRB, RGBW e GRBW
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, auto_write=False, pixel_order=LED_ORDER) #Fita LED

# Variáveis parâmetros
dangerLedLigado = False
desligarLed = False
ligarOk = False

# Conexão com o RPi usando IPv4 e UDP
pc_conexao = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Função para transformar a cor em Bytes
def Color(red, green, blue, white = 0): return (white << 24) | (red << 16)| (green << 8) | blue

# Obtém a requisição e retorna se contém MINING na propriedade 'minerStatuses'
def mineirando():
	try:
		r = requests.get("https://api2.nicehash.com/main/api/v2/mining/external/%s/rigs2" % ADDR_BTC).json()
		try: p = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCBRL").json()
		except: p.price = btc_brl

		agora = datetime.now().strftime('%H:%M:%S')
		status_mining = list(r['minerStatuses'].keys())[0]
		proft = float(r['totalProfitability'])
		unpaid = float(r['unpaidAmount'])
		btc_brl = float(p['price'])
		pft_brl = proft * btc_brl
		unp_brl = unpaid * btc_brl

		status = '[{}][R${:n}] {} | '.format(agora, btc_brl, status_mining)

		status += 'Pft: {:.8f} BTC (R${:.2f}) | Unp: {:.8f} BTC (R${:.2f})'.format(proft, pft_brl, unpaid, unp_brl) if 'stMining' in globals() else 'Iniciando verificação...'

		print(status)

		return status_mining
	except Exception as e:
		print('[%s] PYTHON ERROR: %s' % (datetime.now().strftime('%H:%M:%S'), e))
		return 'PYTHON ERROR'

def enviarLed(led_array):
	led_envio = str(led_array)
	pc_conexao.sendto(led_envio.encode(), (IP_RPI, 12000))

def off():
	strip.fill((0,0,0))
	strip.show()

def statusOkLed():
	delaySeg = 0.001
	progressao = 1.3

	for i in range(25):
		delaySeg = delaySeg * progressao
		strip[(i*-1)-1] = Color(0,1,0)
		strip[i] = Color(0,1,0)
		strip.show()
		time.sleep(delaySeg)

	for i in reversed(range(25)):
		delaySeg = delaySeg / (progressao - 0.2)
		strip[(i*-1)-1] = Color(0,0,0)
		strip[i] = Color(0,0,0)
		strip.show()
		time.sleep(delaySeg)

def fadeLed(r,g,b):
	delaySeg = 0.001

	for i in range(100):

		strip.fill((r*i,g*i,b*i))
		strip.show()
		time.sleep(delaySeg)
		
	for i in reversed(range(100)):
		strip.fill((r*i,g*i,b*i))
		strip.show()
		time.sleep(delaySeg)
	

def ligarLed():
	global ligarOk, stMining
	while True:
		if desligarLed: return

		if stMining == 'MINING':
			if ligarOk:
				fadeLed(0,1,0)
				ligarOk = False

		elif stMining == 'PYTHON ERROR': fadeLed(2,0.5,0)

		else:
			fadeLed(1,0,0)
			ligarOk = True


def appSendoExecutadoLed():
	global ligarOk, stMining
	while True:
		for seg in range(30):
			time.sleep(1)
			if desligarLed: return

		if stMining == 'MINING':
			statusOkLed()
			off()

# Obtém o status da mineiração
stMining = mineirando()

# Inicia a Thread das cores rodando sempre até o app fechar.
ledThread = Thread(target=ligarLed)
ledThread.start()

# Thread para imprimir no LED que o app está executando
appSendoExecutado = Thread(target=appSendoExecutadoLed)
appSendoExecutado.start()

try:
	while True:
		stMining = mineirando()
		if stMining == 'MINING': dangerLedLigado = False
		else: dangerLedLigado = True
		time.sleep(15)

except KeyboardInterrupt:
	print('[%s] Fechando' % datetime.now().strftime('%H:%M:%S'))
	desligarLed = True
	ledThread.join()
	appSendoExecutado.join()
	for i in reversed(range(3)):
		print('Fechando em {}...'.format(i+1))
		time.sleep(1)
	quit()