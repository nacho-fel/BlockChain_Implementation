import BlockChain
from uuid import uuid4
import socket
from flask import Flask, jsonify, request
from argparse import ArgumentParser
import threading
import json
import datetime
import platform
import requests

"""
Integrantes del equipo:
- Ulises Díez Santaolalla
- Ignacio Felices Vera
"""

# Instancia del nodo
app =Flask(__name__)

# Instanciacion de la aplicacion
blockchain =BlockChain.Blockchain()

# Almacenaje de los nodos de la red
nodos_red = set()

# Para saber mi ip
mi_ip ='10.120.151.35'

# Método para recibir transacciones
@app.route('/transacciones/nueva', methods=['POST'])
def nueva_transaccion():
    # Obtengo el json enviado con el POST
    values = request.get_json()

    # Comprobamos que todos los datos de la transaccion estan
    required = ['origen', 'destino', 'cantidad']
    if not all(k in values for k in required):
        return 'Faltan valores', 400
    
    # Creamos una nueva transaccion
    indice = blockchain.nueva_transaccion(values['origen'], values['destino'], values['cantidad'])
    response = {'mensaje': f'La transaccion se incluira en el bloque con indice {indice}'}
    
    return jsonify(response), 201   # función de Flask que convierte objetos de Python en respuestas JSON

# Método para consultar la cadena completa
@app.route('/chain', methods=['GET'])
def blockchain_completa():
    response ={
        # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
        'chain': [b.toDict() for b in blockchain.lista_bloques if b.hash is not None],
        'longitud': len(blockchain.lista_bloques),
    }
    
    return jsonify(response), 200

# Método para minar bloques
@app.route('/minar', methods=['GET'])
def minar():
    if len(blockchain.lista_transacciones) == 0:
        response = {'mensaje': "No es posible crear un nuevo bloque. No hay transacciones"}
        return jsonify(response), 400
    else:
        # Aplico la resolución de confilctos antes de minar el bloque
        hay_conflicto = resuelve_conflictos()

        if hay_conflicto:
            response = {
                'mensaje': "Ha habido un conflicto. Esta cadena se ha actualizado con una versión más larga"
            }
            return jsonify(response), 409  
        
        # Creo una transacción de recompensa para el minero
        recompensa = 1     # La recompensa es 1
        origen = "0"  # Origen de la recompensa
        destino = mi_ip  # Uso la IP
        
        # Creo la transacción de recompensa
        blockchain.nueva_transaccion(origen, destino, recompensa)

        # Mino el bloque
        anterior_bloque = blockchain.lista_bloques[-1]
        nuevo_bloque = blockchain.nuevo_bloque(anterior_bloque.hash)
        blockchain.integra_bloque(nuevo_bloque, nuevo_bloque.hash)
        
        # Mensaje de respuesta
        response = {
            "hash_bloque": nuevo_bloque.hash,
            "hash_previo": nuevo_bloque.hash_previo,
            "indice": nuevo_bloque.indice,
            "mensaje": "Nuevo bloque minado",
            "prueba": nuevo_bloque.prueba,
            "timestamp": nuevo_bloque.timestamp,
            "transacciones": nuevo_bloque.transacciones
        }

    return jsonify(response), 200

# Método para comprobar si hay conflictos entre las blockchain de los nodos
def resuelve_conflictos():
    # Variables Globales
    global blockchain

    # Obtengo los datos del nodo y blockchain actual
    longitud_actual = len(blockchain.lista_bloques)
    cadena_más_larga = None
    nodo_actual = request.url_root.rstrip('/')  
    # Compruebo para cada nodo de la red
    for nodo in nodos_red:  
        # No incluyo al propio nodo
        if nodo != nodo_actual:  
            # Obtengo la cadena de cada nodo
            response = requests.get(f"{nodo}/chain")  
            if response.status_code == 200:
                # Obtengo la longitud de la cadena y la blockchain del nodo
                longitud_nodo = response.json().get('longitud') 
                cadena_nodo = response.json().get('chain')  

                # Si se ha encontrado una cadena más larga
                if longitud_nodo > longitud_actual:
                    longitud_actual = longitud_nodo
                    cadena_más_larga = cadena_nodo

    # Si he encontrado una cadena más larga, la remplazo y devuelvo True
    if cadena_más_larga:
        # Guardo la blockchain actual del nodo, por si el registro sale mal y no se puede sincronizar 
        # con el nodo principal
        lista_actual_blockchain = blockchain.lista_bloques    
        
        # Construyo el blockchain a partir del JSON recibido, ignorando el primer bloque
        blockchain_leida = []
        for bloque_json in cadena_más_larga[1:]:
            nuevo_bloque = BlockChain.Bloque(
                indice=bloque_json['indice'],
                transacciones=bloque_json['transacciones'],
                timestamp=bloque_json['timestamp'],
                hash_previo=bloque_json['hash_previo'],
            )
            nuevo_bloque.prueba=bloque_json['prueba']
            nuevo_bloque.hash=bloque_json['hash']
            blockchain_leida.append(nuevo_bloque)
        
        # Reinicio la BlockChain del nodo
        blockchain.lista_bloques = [blockchain.lista_bloques[0]]
        
        # Verifico que los bloques de la blockchain pasan las pruebas de integra_bloque
        for bloque in blockchain_leida:
            # Si no superan las pruebas de integra bloque, devuelve error, y el nodo vuelve 
            # a tener la blockchain que tenía antes de intentar registrarse
            if not blockchain.integra_bloque(bloque, bloque.hash):
                blockchain.lista_bloques = lista_actual_blockchain
                return "Error al integrar el bloque en el blockchain", 500

        return True  
    
    # Si no ha habido conflicto la comparar las cadenas
    else:
        return False  

# Método para realizar copia de seguridad
mutex = threading.Semaphore(1)      # Semáforo para controlar el acceso único a la blockchain, protegiéndola
@app.route('/respaldo', methods=['GET'])
def realizar_respaldo():
    while True:
        # Bloqueo el acceso a otros hilos
        mutex.acquire()
        try:
            # Obtengo la fecha y hora y la formateo
            fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')

            # Creo el respaldo de los datos
            respaldo_data = {
                "chain": [bloque.toDict() for bloque in blockchain.lista_bloques],
                "longitud": len(blockchain.lista_bloques),
                "date": fecha_actual
            }

            # Escribo el respaldo en un archivo JSON
            nombre_archivo = f"respaldo-nodo{socket.gethostbyname(socket.gethostname())}-{puerto}.json"
            with open(nombre_archivo, 'w') as file:
                json.dump(respaldo_data, file, indent=4)
                
        # Libero el mutex para permitir el acceso a otros hilos
        finally:
            mutex.release()

        # Espero 60 segundos antes de realizar el próximo respaldo
        threading.Event().wait(60)
        
# Creo un hilo para realizar copia de seguridad cada 60 segundos
hilo_respaldo = threading.Thread(target=realizar_respaldo)
hilo_respaldo.start()

# Método para obtener detalles del nodo
@app.route('/system', methods=['GET'])
def obtener_detalles_nodo():
    sistema_operativo = platform.system()  # Nombre del sistema operativo
    version = platform.version()  # Versión del sistema operativo
    tipo_procesador = platform.machine()  # Tipo de procesador
    
    # Formateo la respuesta en formato JSON
    detalles_nodo = {
        "maquina": tipo_procesador,
        "nombre_sistema": sistema_operativo,
        "version": version
    }

    return jsonify(detalles_nodo), 200

# Método para registrar nodos
@app.route('/nodos/registrar', methods=['POST'])
def registrar_nodos_completo():
    # Obtengo el json enviado con el POST
    values = request.get_json()
    
    # Variables Globales
    global blockchain
    global nodos_red
    
    # Obtengo los nodos del json 
    nodos_nuevos = values.get('direccion_nodos')

    # Compruebo si se han registrado nodos o no
    if nodos_nuevos is None:
        return "Error: No se ha proporcionado una lista de nodos", 400

    # Obtengo la dirección desde la que se hace el POST (direccion del nodo actual)
    nodo_actual = request.url_root.rstrip('/')

    # Obtengo todas las direcciones de los nodos en la red (incluyendo el nodo principal y el nodo actual)
    nodos_todos = list(nodos_red.union(set(nodos_nuevos)))
    nodos_todos.append(nodo_actual)  

    # Creo una copia de la blockchain actual en formato JSON
    blockchain_json = [bloque.toDict() for bloque in blockchain.lista_bloques]
    
    # Envío la información de la red y la copia del blockchain a cada nodo de la lista
    for nodo in nodos_nuevos:
        # Excluyo al propio nodo
        nodos_sin_propio = [n for n in nodos_todos if n != nodo]  
        data_to_send = {
            "nodos_direcciones": nodos_sin_propio,
            "blockchain": blockchain_json
        }
        response = requests.post(
            nodo + "/nodos/registro_simple",
            json=data_to_send,
            headers={'Content-Type': "application/json"}
        )
        # Si un nodo no actualiza correctamente la blockchain
        if response.status_code != 200:    
            return f"Error al enviar el blockchain al nodo {nodo}", 500

    # Muestro el registro de los nodos
    response = {
        'mensaje': 'Se han incluido nuevos nodos en la red',
        'nodos_totales': list(nodos_red.union(set(nodos_nuevos)))
    }
    for nodo in nodos_nuevos:
        nodos_red.add(nodo)
    
    return jsonify(response), 201

# Método para actualizar la blockchain al registrar un nodo
@app.route('/nodos/registro_simple', methods=['POST'])
def registrar_nodo_actualiza_blockchain():
    # Variables Globales
    global blockchain
    
    # Obtengo el json enviado con el POST
    read_json = request.get_json()
    
    # Obtengo el las direciones de los nodos y la blockchain del json
    direcion_nodos = read_json.get("nodos_direcciones")
    blockchain_json = read_json.get("blockchain")

    # Compruebo si se ha recibido bien la información de los nodos y la blockchain
    if direcion_nodos is None or blockchain_json is None:
        return "Datos insuficientes para actualizar el blockchain", 400

    # Actualizo la lista de nodos con la recibida
    nodos_red.update(direcion_nodos)

    # Guardo la blockchain actual del nodo, por si el registro sale mal y no se puede sincronizar 
    # con el nodo principal
    lista_actual_blockchain = blockchain.lista_bloques    
    
    # Construyo el blockchain a partir del JSON recibido, ignorando el primer bloque
    blockchain_leida = []
    for bloque_json in blockchain_json[1:]:
        nuevo_bloque = BlockChain.Bloque(
            indice=bloque_json['indice'],
            transacciones=bloque_json['transacciones'],
            timestamp=bloque_json['timestamp'],
            hash_previo=bloque_json['hash_previo'],
        )
        nuevo_bloque.prueba=bloque_json['prueba']
        nuevo_bloque.hash=bloque_json['hash']
        blockchain_leida.append(nuevo_bloque)
    
    # Reinicio la BlockChain del nodo
    blockchain.lista_bloques = [blockchain.lista_bloques[0]]
    
    # Verifico que los bloques de la blockchain pasan las pruebas de integra_bloque
    for bloque in blockchain_leida:
        # Si no superan las pruebas de integra bloque, devuelve error, y el nodo vuelve 
        # a tener la blockchain que tenía antes de intentar registrarse
        if not blockchain.integra_bloque(bloque, bloque.hash):
            blockchain.lista_bloques = lista_actual_blockchain
            return "Error al integrar el bloque en el blockchain", 500

    # Devuelvo la blockchain actualizada
    response = {
        'chain': [bloque.toDict() for bloque in blockchain.lista_bloques if bloque.hash is not None],
        'longitud': len(blockchain.lista_bloques)
    }
    
    return jsonify(response), 200

# Método para hacer una llamada PING a los nodos y comprobar que recibe las respuestas PONG
@app.route('/ping', methods=['GET'])
def ping():
    # Obtengo la dirección del nodo actual
    nodo_actual = request.url_root.rstrip('/')

    # Creo el mensaje que voy a enviar a los nodos de la red
    mensaje_ping = {
        "host_origen": nodo_actual,
        "mensaje": "PING",
        "timestamp": datetime.datetime.now().isoformat()
    }

    # Lista para almacenar las respuestas de los nodos
    respuestas = []

    # Envío el mensaje de PING a cada nodo en la red
    for nodo in nodos_red:
        # No incluyo al propio nodo
        if nodo != nodo_actual:  
            # Obtengo la respuesta PONG de los nodos a los que envío el PING
            response = requests.post(f"{nodo}/pong", json=mensaje_ping)
            #Si me han enviado bien la respuesta, la añado a la lista de respuestas
            if response.status_code == 200:
                respuesta_nodo = response.json()
                respuestas.append(respuesta_nodo)

    # Mensaje final una vez he recibido las respuestas PONG  de los nodos
    respuesta_final = f"#PING de {nodo_actual}. Respuestas: "
    if respuestas:
        # Por cada respuesta, muestro el mensaje PONG uq em ha enviado
        for respuesta in respuestas:
            respuesta_final += f"PONG {respuesta['host']} Retardo: {respuesta['delay']}"
        respuesta_final += "#Todos los nodos responden"
    
    # Si no se he recibido respuestas de los nodos
    else:
        respuesta_final += f"No hay respuestas de los nodos {nodos_red}"

    return jsonify({"respuesta_final": respuesta_final}), 200

# Método que devuelve el mensaje PONG cuando recibe una llamada PING de un nodo
@app.route('/pong', methods=['POST'])
def pong():
    # Recibo el mensaje PING del nodo que ha hecho la llamada 
    mensaje_ping = request.get_json()

    # Obtengo los datos del json del mensaje PING
    host_origen = mensaje_ping.get("host_origen")
    mensaje = mensaje_ping.get("mensaje")
    timestamp = mensaje_ping.get("timestamp")

    # Obtengo la dirección del nodo actual
    nodo_actual = request.url_root.rstrip('/')

    # Resto los timestamps para ver el retardo
    retardo = datetime.datetime.now() - datetime.datetime.fromisoformat(timestamp)

    # Creo el mensaje PONG que voy a enviar al que hizo la llamada PING
    respuesta_pong = {
        "host_origen": host_origen,
        "host": nodo_actual,
        "mensaje": mensaje,
        "delay": retardo.total_seconds()
    }

    return jsonify(respuesta_pong), 200

# Main
if __name__ =='__main__':
    parser =ArgumentParser()
    parser.add_argument('-p', '--puerto', default=5000, type=int, help='puerto para escuchar')
    args =parser.parse_args()
    puerto =args.puerto
    app.run(host='0.0.0.0', port=puerto)