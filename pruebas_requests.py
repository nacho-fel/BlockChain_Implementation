import requests
import json
import time

"""
Integrantes del equipo:
- Ulises Díez Santaolalla
- Ignacio Felices Vera
"""

# Cabecera JSON común a todas las solicitudes
cabecera = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# Datos de transacción para prueba
transaccion_nueva = {'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
# Datos para realizar varias transacciones, con diferentes cantidades
transaccion_nueva_1 = {'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 20}
transaccion_nueva_2 = {'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 15}
transaccion_nueva_3 = {'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 35}
# Datos de una nueva transacción, utilizada para probar los conflictos de la blockcahin
# una vez se han registrado los nodos
transaccion_nueva_4 = {'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 54}
transaccion_nueva_5 = {'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 46}

# URL de los nodos en la red 
urls = [
    'http://localhost:5000',
    'http://localhost:5001',
    'http://localhost:5002'
]

# Realizo la prueba con cada uno de los nodos
for url in urls:
    print(f"\nNodo: {url}")

    # Envío una nueva transacción al nodo
    r = requests.post(f'{url}/transacciones/nueva', data=json.dumps(transaccion_nueva), headers=cabecera)
    print("Respuesta de nueva transacción:", r.text)

    # Mino un bloque en el nodo
    r = requests.get(f'{url}/minar')
    print("Respuesta de minar bloque:", r.text)
    
    # Obtengo la cadena completa del nodo
    r = requests.get(f'{url}/chain')
    print("Respuesta de obtener cadena completa:", r.text)
    
    # Envío varias transacciones al nodo
    r = requests.post(f'{url}/transacciones/nueva', data=json.dumps(transaccion_nueva_1), headers=cabecera)
    print("Respuesta de nueva transacción:", r.text)
    r = requests.post(f'{url}/transacciones/nueva', data=json.dumps(transaccion_nueva_2), headers=cabecera)
    print("Respuesta de nueva transacción:", r.text)
    r = requests.post(f'{url}/transacciones/nueva', data=json.dumps(transaccion_nueva_3), headers=cabecera)
    print("Respuesta de nueva transacción:", r.text)
    
    # Mino un bloque en el nodo
    r = requests.get(f'{url}/minar')
    print("Respuesta de minar bloque:", r.text)

    # Obtengo la cadena completa del nodo
    r = requests.get(f'{url}/chain')
    print("Respuesta de obtener cadena completa:", r.text)

    # Obtengo los detalles del nodo
    response = requests.get(f'{url}/system')
    print("Respuesta de obtener detalles del nodo:", response.text)

    # Registro nuevos nodos en la red
    nodos = []
    nuevos_nodos = False
    for otras_url in urls:
        if otras_url != url:
            nodos.append(otras_url)
            nuevos_nodos = True
    if nuevos_nodos:
        data = {'direccion_nodos': nodos}
        response = requests.post(f'{url}/nodos/registrar', json=data)
        print("Respuesta de registrar nodos:", response.text)

    # Hago una llamada PING y obtengo las respuestas PONG
    response = requests.get(f'{url}/ping')
    print("Respuesta de ping a nodos:", response.text)
    
    # Se comprueba que haya conflictos cuando se añade nueva transacción y se mina un bloque, ya que al comparar 
    # las blockchains de los nodos de la red, tendrían distinta longitud
    # Envío una nueva transacción al nodo
    r = requests.post(f'{url}/transacciones/nueva', data=json.dumps(transaccion_nueva_4), headers=cabecera)
    print("Respuesta de nueva transacción:", r.text)
    # Mino un bloque en el nodo
    r = requests.get(f'{url}/minar')
    print("Respuesta de minar bloque:", r.text)
    # Añado una transacción y mino un bloque en otro nodo para ver que salta conflicto
    r = requests.post(f'{nodos[0]}/transacciones/nueva', data=json.dumps(transaccion_nueva_5), headers=cabecera)
    print("Respuesta de nueva transacción:", r.text)
    # Mino un bloque en el nodo
    r = requests.get(f'{nodos[0]}/minar')
    print("Respuesta de minar bloque:", r.text)
    
    # Espero un tiempo antes de hacer la siguiente prueba
    print(f"----------------- Pruebas en el nodo {url} terminadas -----------------")
    time.sleep(1)  