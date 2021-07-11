
import ledEffects, requests, socket, time
from config import *
from threading import Thread

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
	r = requests.get(f'https://api2.nicehash.com/main/api/v2/mining/external/{ADDR_BTC}/rigs2')
	return 'MINING' in r.json()['minerStatuses'].keys()

def enviarLed(led_array):
	led_envio = str(led_array)
	pc_conexao.sendto(led_envio.encode(), (IP_RPI, 12000))

def ligarLed():
	global ligarOk
	while True:
		if dangerLedLigado:
			ligarOk = True

			for i in range(100):
				led_array = [Color(0,i,0)] * LED_COUNT
				enviarLed(led_array)
				time.sleep(0.005)
				
			for i in reversed(range(100)):
				led_array = [Color(0,i,0)] * LED_COUNT
				enviarLed(led_array)
				time.sleep(0.005)

			time.sleep(1)
		else:
			if ligarOk:
				ligarOk = False
				for i in range(100):
					led_array = [Color(i,0,0)] * LED_COUNT
					enviarLed(led_array)
					time.sleep(0.005)
				for i in reversed(range(100)):
					led_array = [Color(i,0,0)] * LED_COUNT
					enviarLed(led_array)
					time.sleep(0.005)
			# else:
			# 	led_array = [0] * LED_COUNT

			# 	for pos in range(LED_COUNT):
			# 		led_array[pos] = Color(0,0,0)
			# 		led_array[pos-1] = Color(1,3,3)
			# 		led_array[pos-2] = Color(3,3,3)
			# 		led_array[pos-3] = Color(5,3,3)
			# 		led_array[pos-4] = Color(10,3,3)
			# 		led_array[pos-5] = Color(5,3,3)
			# 		led_array[pos-6] = Color(3,3,3)
			# 		led_array[pos-7] = Color(0,0,0)
			# 		enviarLed(led_array)
			# 		time.sleep(0.001)

		if desligarLed:
			return True
	
# Inicia a Thread das cores rodando sempre até o app fechar.
ledThread = Thread(target=ligarLed)
ledThread.start()

while True:
# for i in range(5):
	if mineirando():
		print('mineirando!!!!')
		dangerLedLigado = False
	else:
		print('LIGAAA')
		dangerLedLigado = True

	time.sleep(5)

print('terminei')
desligarLed = True