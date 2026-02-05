from typing import Tuple, List, Dict
import json
import hashlib
import time

"""
Integrantes del equipo:
- Ulises Díez Santaolalla
- Ignacio Felices Vera
"""

class Bloque:
    # Las transacciones llegarán de la forma de una lista de diccionarios, que se convertirá al JSON
    def __init__(self, indice: int, transacciones: List[dict], timestamp: int, hash_previo: str, prueba: int =0):
        """
        Constructor de la clase `Bloque`.
        :param indice: ID unico del bloque.
        :param transacciones: Lista de transacciones.
        :param timestamp: Momento en que el bloque fue generado.
        :param hash_previo hash previo
        :param prueba: prueba de trabajo
        """
        # Codigo a completar (inicializacion de los elementos del bloque)
        self.indice = indice
        self.transacciones = transacciones
        self.timestamp = timestamp
        self.hash_previo = hash_previo
        self.prueba = prueba
        self.hash = None  # Inicialmente establecemos el hash como None
    
    def calcular_hash(self):
        """
        Metodo que devuelve el hash de un bloque
        """        
        block_string =json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def toDict(self):
        """
        Método que convierte un objeto Bloque a un diccionario.
        """
        bloque_dicc =  {
            "indice": self.indice,
            "transacciones": self.transacciones,
            "timestamp": self.timestamp,
            "hash_previo": self.hash_previo,
            "prueba": self.prueba,
            "hash": self.hash
        }
        
        return bloque_dicc   
    
class Blockchain(object):
    def __init__(self):
        """
        Inizializo la BlockChain con una lista de bloques vacía, 
        y además debe almacenar en otra lista aquellas transacciones que
        todavía no están confirmadas para ser introducidas en un bloque 
        (el siguiente bloque que sería introducido en la cadena)
        """
        self.dificultad = 4
        self.lista_transacciones = []
        self.lista_bloques = []
        self.primer_bloque()  # Creo el primer bloque
        
    def primer_bloque(self):
        """Función encargada de crear el primer bloque de la cadena
        para que luego puedan añadirse más bloques a dicha cadena.
        Returns:
            object: primer bloque inicializado con índice 1
        """
        # Crear el primer bloque
        bloque_inicio = Bloque(1, [], "0", "1")  # Índice 1, sin transacciones y hash_previo de 1
        bloque_inicio.hash = bloque_inicio.calcular_hash()   # Genero hash
        self.lista_bloques.append(bloque_inicio)    # Añado el bloque a la cadena
    
    def nuevo_bloque(self, hash_previo: str) ->Bloque:
        """
        Crea un nuevo bloque a partir de las transacciones que no estan
        confirmadas
        :param hash_previo: el hash del bloque anterior de la cadena
        :return: el nuevo bloque
        """
        nuevo_indice = len(self.lista_bloques) + 1   # El índice será el uno más del número de bloques ya existentes
        nuevo_bloque = Bloque(nuevo_indice, self.lista_transacciones, time.time(), hash_previo)   # Genero el bloque
        nuevo_bloque.hash = self.prueba_trabajo(nuevo_bloque)    # Genero hashes hasta que empiece por 0000
        return nuevo_bloque
    
    def nueva_transaccion(self, origen: str, destino: str, cantidad: int) ->int:
        """
        Crea una nueva transaccion a partir de un origen, un destino y una
        cantidad y la incluye en las listas de transacciones
        :param origen: <str> el que envia la transaccion
        :param destino: <str> el que recibe la transaccion
        :param cantidad: <int> la candidad
        :return: <int> el indice del bloque que va a almacenar la transaccion
        """
        tiempo_actual = time.time()     # Tomo el tiempo en el momento que se crea la transacción
        # Creo la transacción con sus correspondientes valores
        nueva_transaccion = {
            'origen': origen,
            'destino': destino,
            'cantidad': cantidad,
            'tiempo': tiempo_actual
        }
        self.lista_transacciones.append(nueva_transaccion)      # Añado la transacción a la lista de transacciones
        indice_bloque = len(self.lista_bloques) + 1  # Devuelve el índice del bloque que almacenará la transacción
        return indice_bloque
    
    def prueba_trabajo(self, bloque: Bloque) ->str:
        """
        Algoritmo simple de prueba de trabajo:
        - Calculara el hash del bloque hasta que encuentre un hash que empiece
        por tantos ceros como dificultad
        .
        - Cada vez que el bloque obtenga un hash que no sea adecuado,
        incrementara en uno el campo de
        ``prueba'' del bloque
        :param bloque: objeto de tipo bloque
        :return: el hash del nuevo bloque (dejara el campo de hash del bloque sin
        modificar)
        """
        hash_bloque = bloque.calcular_hash()    # Calculo el hash inicial del bloque
        # Compruebo si tiene tantos 0 como dificultad, de lo contrario aumento el campo prueba
        while not hash_bloque.startswith('0' * self.dificultad):
            bloque.prueba += 1
            hash_bloque = bloque.calcular_hash()
        return hash_bloque

    def prueba_valida(self, bloque: Bloque, hash_bloque: str) ->bool:
        """
        Metodo que comprueba si el hash_bloque comienza con tantos ceros como la
        dificultad estipulada en el
        blockchain
        Ademas comprobara que hash_bloque coincide con el valor devuelvo del
        metodo de calcular hash del
        bloque.
        Si cualquiera de ambas comprobaciones es falsa, devolvera falso y en caso
        contrario, verdarero
        :param bloque:
        :param hash_bloque:
        :return:
        """
        empieza_ceros = hash_bloque.startswith('0' * self.dificultad)
        # Compruebo si empieza por los ceros correspondientes a la dificultad
        if empieza_ceros:
            # Compruebo si los hashes coinciden
            if hash_bloque == bloque.hash:
                return True
            # Si los hashes no coinciden
            else:
                return False
        # Si no comienza por los ceros correspondientes
        else:
            return False
        
    
    def integra_bloque(self, bloque_nuevo: Bloque, hash_prueba: str) ->bool:
        """
        Metodo para integrar correctamente un bloque a la cadena de bloques.
        Debe comprobar que hash_prueba es valida y que el hash del bloque ultimo
        de la cadena
        coincida con el hash_previo del bloque que se va a integrar. Si pasa las
        comprobaciones, actualiza el hash
        7
        del bloque nuevo a integrar con hash_prueba, lo inserta en la cadena y
        hace un reset de las
        transacciones no confirmadas (
        vuelve
        a dejar la lista de transacciones no confirmadas a una lista vacia)
        :param bloque_nuevo: el nuevo bloque que se va a integrar
        :param hash_prueba: la prueba de hash
        :return: True si se ha podido ejecutar bien y False en caso contrario (si
        no ha pasado alguna prueba)
        """
        ultimo_bloque = self.lista_bloques[-1]
        # Compruebo si el bloque coincide con su hash
        if self.prueba_valida(bloque_nuevo, hash_prueba):
            # Compruebo que el hash_previo del bloque corresponda con el hash del último bloque de la lista
            if bloque_nuevo.hash_previo == ultimo_bloque.hash:
                # Actualizo el hash del bloque
                bloque_nuevo.hash = hash_prueba
                # Añado el bloque a la cadena
                self.lista_bloques.append(bloque_nuevo)
                # Reseteo la lista de transacciones
                self.lista_transacciones = []
                # Indico que se ha podido ejecutar correctamente
                return True
            # Si no coincide los hashes del bloque previo
            else:
                return False
        # Si no coincide el hash del bloque
        return False