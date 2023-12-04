import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import math

# Função que realiza a triangulação com base nos dados de RSSI e localização das redes
def triangulacao(x1, y1, rssi1, x2, y2, rssi2, x3, y3, rssi3):
    raio1 = rssiParaDistancia(rssi1)
    raio2 = rssiParaDistancia(rssi2)
    raio3 = rssiParaDistancia(rssi3)

    # Cálculos para determinar as coordenadas do ponto atual
    a = 2 * (-x1 + x2)
    b = 2 * (-y1 + y2)
    c = (raio1 ** 2) - (raio2 ** 2) - (x1 ** 2) + (x2 ** 2) - (y1 ** 2) + (y2 ** 2)
    d = 2 * (-x2 + x3)
    e = 2 * (-y2 + y3)
    f = (raio2 ** 2) - (raio3 ** 2) - (x2 ** 2) + (x3 ** 2) - (y2 ** 2) + (y3 ** 2)

    x = 10000
    y = 10000

    # Lógica para determinar as coordenadas com base na triangulação
    if ((e * a) - (b * d)) == 0 & ((b * d) - (a * e)) == 0:
        x = 0
        y = 0
    elif ((e * a) - (b * d)) == 0:
        y = ((c * d) - (a * f)) / ((b * d) - (a * e))
        x = 0
    elif ((b * d) - (a * e)) == 0:
        x = ((c * e) - (f * b)) / ((e * a) - (b * d))
        y = 0
    else:
        x = ((c * e) - (f * b)) / ((e * a) - (b * d))
        y = ((c * d) - (a * f)) / ((b * d) - (a * e))

    return x, y

# Converte o RSSI para distância
def rssiParaDistancia(rssi):
    a = -45
    w = (rssi - a) / -40
    distancia = 10 ** w
    return distancia

# Converte distância para RSSI
def distanciaParaRssi(distancia):
    rssi = -50 - 40 * math.log(distancia, 10)
    return rssi

# Compara o MAC fornecido com os MACs na lista de redes
def compararMac(redes, mac):
    for rede in redes:
        if rede["mac"] == mac:
            return rede["x"], rede["y"]
    return None

# Inicialização da conexão com o Firebase
cred = credentials.Certificate("esp8266.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://esp8266-2dca6-default-rtdb.firebaseio.com/'
})

# Lista de redes e referências aos nós correspondentes no Firebase
redes = [
  {"mac": "20:58:69:0E:AA:38", "nome": "WLL-Inatel", "x": "0", "y": "1"},
  {"mac": "30:87:D9:02:FA:C8", "nome": "WLL-Inatel", "x": "0", "y": "1"},
  {"mac": "30:87:D9:02:FE:08", "nome": "WLL-Inatel", "x": "0", "y": "1"},
  {"mac": "B4:79:C8:05:B9:38", "nome": "WLL-Inatel", "x": "0", "y": "1"},
  {"mac": "B4:79:C8:05:B9:A8", "nome": "WLL-Inatel", "x": "0", "y": "1"},
  {"mac": "B4:79:C8:05:C2:38", "nome": "WLL-Inatel", "x": "0", "y": "1"},
  {"mac": "B4:79:C8:05:C2:78", "nome": "WLL-Inatel", "x": "0", "y": "1"},
  {"mac": "B4:79:C8:38:B1:C8", "nome": "WLL-Inatel", "x": "10", "y": "5"},
  {"mac": "B4:79:C8:38:C0:B8", "nome": "WLL-Inatel", "x": "0", "y": "1"},
  {"mac": "B4:79:C8:39:31:28", "nome": "WLL-Inatel", "x": "0", "y": "1"},
  {"mac": "30:87:D9:42:FA:C8", "nome": "WLL-CDGHub", "x": "5", "y": "2"},
  {"mac": "6C:14:6E:3E:DB:50", "nome": "wlanaccessv2.0", "x": "0", "y": "1"},
  {"mac": "6C:14:6E:3E:DF:10", "nome": "wlanaccessv2.0", "x": "0", "y": "1"},
  {"mac": "6C:14:6E:3E:DB:51", "nome": "Huawei-Employee", "x": "0", "y": "1"},
  {"mac": "6C:14:6E:3E:DB:52", "nome": "Huawei-Employee", "x": "0", "y": "1"},
  {"mac": "6C:14:6E:3E:DE:71", "nome": "Huawei-Employee", "x": "0", "y": "1"},
  {"mac": "6C:14:6E:3E:DE:72", "nome": "Huawei-Employee", "x": "0", "y": "1"},
  {"mac": "B4:79:C8:45:C2:38", "nome": "Inatel-BRDC-V", "x": "0", "y": "1"},
  {"mac": "B4:79:C8:45:C2:78", "nome": "Inatel-BRDC-V", "x": "0", "y": "1"},
  {"mac": "B4:79:C8:78:B1:C8", "nome": "Inatel-BRDC-V", "x": "8", "y": "3"},
  {"mac": "E8:1D:A8:30:F1:E8", "nome": "Inatel-BRDC-V", "x": "0", "y": "1"}
]

mac1 = db.reference('/networks/0')
mac2 = db.reference('/networks/1')
mac3 = db.reference('/networks/2')

data1 = mac1.get()
data2 = mac2.get()
data3 = mac3.get()

x1, y1 = compararMac(redes, data1.get("mac"))
x2, y2 = compararMac(redes, data2.get("mac"))
x3, y3 = compararMac(redes, data3.get("mac"))

# Verificação e cálculo da triangulação caso os dados sejam válidos
if data1 is not None or data2 is not None or data3 is not None:
    x, y = triangulacao(int(x1), int(y1), data1["rssi"], int(x2), int(y2), data2["rssi"], int(x3), int(y3), data3["rssi"])
    print(f"X: {round(x,3)} metros")
    print(f"Y: {round(y,3)} metros")
