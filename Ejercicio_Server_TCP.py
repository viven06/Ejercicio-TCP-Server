import socket
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime

host = "10.14.87.156"
port = 5050
logs = "solicitudes.txt"
contador_solicitudes = 0
lock = threading.Lock()

def es_primo(n):
    
    if n <= 1: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def manejar_cliente(conexion,direccion):
    global contador_solicitudes
    try:
        cadena = conexion.recv(1024).decode()

        if cadena:
            ultimo_char = cadena[-1]
            cuenta = cadena.count(ultimo_char)
            primo_msg = "es primo" if es_primo(cuenta) else "no es primo"
            response = f"Caracter {ultimo_char} aparece {cuenta} veces y {primo_msg}."
            conexion.send(response.encode())

            with lock:
                contador_solicitudes += 1
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                registro= f"Solicitud #{contador_solicitudes} - Fecha {ahora}, cadena: '{cadena}', resultado: {response}"
                with open(logs, "a") as f:
                    f.write(registro + "\n")
                print(f"Registrada {registro.strip()}")
    except Exception as e:
        print(f"Error con direccion {direccion}: {e}")
    finally:
        conexion.close()    

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((host, port))

server.listen(5)
print(f'Servidor TCP escuchando en {host}:{port}...')

with ThreadPoolExecutor(max_workers=20) as executor:
    while True:
        conexion, direccion = server.accept()
        executor.submit(manejar_cliente, conexion, direccion)