from collections import defaultdict
import functools
import random
import time


pesos = {}
total_peso = 0

@functools.lru_cache(maxsize=None)
def hallar_min_costo_atm_libres(atm1, atm2, w1, w2):
    """
    Calcula el minimo costo entre 2 atomos. Primero lo busca en el diccionario de pesos, y si está lo retorna directamente.
    Si no está, calcula el peso teniendo en cuenta si tienen el mismo signo, lo guarda en el diccionario y lo retorna.
    """
    # print("Entrando a hallar min costo atm libres")
    if tuple([atm1, atm2, "atmLibres"]) in pesos:
        return pesos[(atm1, atm2, "atmLibres")]

    if (atm1 > 0 and atm2 > 0) or (atm1 < 0 and atm2 < 0):
        peso = 1 + ( abs( abs(atm1) - abs(atm2) ) % w1 )
    else:
        peso = w2 - ( abs( abs(atm1) - abs(atm2) ) % w2 )

    pesos[tuple([atm1, atm2, "atmLibres"])] = peso

    return peso



@functools.lru_cache(maxsize=None)
def hallar_min_costo_atm_enlaces(atm, w1, w2):
    # print("Entrando a hallar min costo atm enlaces")

    if atm in pesos: # Si ya se calculó el peso de este atomo, se retorna directamente
        return pesos[atm]

    min_peso = float('inf')
    atm_min = float('inf')
    atm_min2 = float('inf')


    for atm_libre in atm_libres:

        if abs(atm_libre) == abs(atm) or abs(atm_libre) == abs(atm_min2): # No se puede hacer un enlace con el mismo atomo
            continue
        else:

            if (atm > 0 and atm_libre > 0) or (atm < 0 and atm_libre < 0):
                # Si los pesos son iguales, se puede hacer un enlace boltz directamente calculando el peso izquierdo y derecho del atomo libre
                pesoL1 = hallar_min_costo_atm_libres(atm, atm_libre, w1, w2)
                pesoL2 = hallar_min_costo_atm_libres(atm_libre, -1*atm, w1, w2)
                pesoTotal = pesoL1 + pesoL2

                if pesoTotal < min_peso:
                    min_peso = pesoTotal
                    atm_min = atm_libre

                pesos[tuple([atm, atm_libre])] = pesoTotal, atm_min, None

            else:
                # Si los pesos son diferentes, se debe buscar un atomo adicional para no hacer un enlace toll. Se suma el de toda la subcadena
                for atm_libre2 in atm_libres:
                    if abs(atm_libre2) == abs(atm) or abs(atm_libre2) == abs(atm_libre) or abs(atm_libre2)==abs(atm_min):
                        continue
                    else:

                        pesoL1 = hallar_min_costo_atm_libres(-1*atm, atm_libre, w1, w2)
                        pesoL2 = hallar_min_costo_atm_libres(atm_libre, atm_libre2, w1, w2)
                        pesoL3 = hallar_min_costo_atm_libres(atm_libre2, atm, w1, w2)
                        pesoTotal = pesoL1 + pesoL2 + pesoL3

                        if pesoTotal < min_peso:
                            min_peso = pesoTotal
                            atm_min = atm_libre
                            atm_min2 = atm_libre2

                        pesos[tuple([atm, atm_libre, atm_libre2])] = pesoTotal, atm_min, atm_min2

    # pesos[atm] = min_peso

    if atm_min2:
        pesos[atm] = min_peso, atm_min, atm_min2
        return min_peso, atm_min, atm_min2
    else:
        pesos[atm] = min_peso, atm_min, None
        return min_peso, atm_min, None



def find_eulerian_path(graph):
    # Función para encontrar el vértice de inicio
    def find_start_vertex():
        for v in graph:
            if len(graph[v]) % 2 != 0:  # Si el grado del vértice es impar
                return v
        return next(iter(graph))  # Retorna cualquier vértice si todos tienen grado par

    # Función para encontrar el camino euleriano utilizando DFS
    def dfs(v):
        path = []
        stack = [v]

        while stack:
            u = stack[-1]
            if graph[u]:  # Si aún quedan aristas
                w = graph[u].pop()  # Toma y elimina una arista
                graph[w].remove(u)  # Elimina la arista inversa
                stack.append(w)
            else:
                path.append(stack.pop())  # No quedan aristas, agrega al camino
        return path

    # Determinar si el grafo tiene un camino euleriano
    odd_count = sum(len(graph[v]) % 2 != 0 for v in graph)
    if odd_count not in [0, 2]:
        return "NO SE PUEDE"  # No hay camino euleriano

    # Encuentra el vértice de inicio adecuado
    start_vertex = find_start_vertex()
    # Utiliza DFS para encontrar el camino
    return dfs(start_vertex)


def find_weights(path, w1: int, w2: int):
    """
    Esta funcion recibe un camino euleriano y dos pesos w1 y w2, y retorna el camino con los pesos.
    Debe iterar uniendo cada 2 atomos a,b como un enlace (a,b) y uniendolo con el enlace (b,c) calculando y agregando el peso entre a,b y b,c.
    """
    global total_peso

    caminoConPesos = ""

    i, j = 0, 1

    for x in range(len(path) - 1):
        enlace = (path[i], path[j])
        i += 1
        j += 1
        next_enlace = (path[i], path[j]) if i < len(path) - 1 else None
        if next_enlace == None:
            caminoConPesos = caminoConPesos[:-1]
            caminoConPesos += " " + str(total_peso)
        else:
            peso, atm_min1, atm_min2 = hallar_min_costo_atm_enlaces(enlace[1], w1, w2)
            if atm_min2 == float('inf'):
                if x == 0:
                    caminoConPesos += f"{enlace},{atm_min1},{-1*enlace[1]},{next_enlace},"
                else:
                    caminoConPesos += f"{atm_min1},{-1*enlace[1]},{next_enlace},"
            else:
                if x == 0:
                    caminoConPesos += f"{enlace},{atm_min2},{atm_min1},{-1*enlace[1]},{next_enlace},"
                else:
                    caminoConPesos += f"{atm_min2},{atm_min1},{-1*enlace[1]},{next_enlace},"
            total_peso += peso

    return caminoConPesos


# Ejemplo de uso con vértices no secuenciales y un vértice negativo
graph = {
    1: [3, 7],
    3: [1, -6],
    -6: [3],
    7: [1]
}

# atm_libres = [1,-1,3,-3,6,-6,7,-7]
atm_libres = []


graph = defaultdict(list)

# Agregar aristas al grafo
def generarGrafoValido(cantidad:int):
    enlaces = []
    nodos = []
    for i in range(cantidad):
        nodo = random.randint(-1000, 1000)
        while nodo in nodos:
            nodo = random.randint(-2000, 4000)
        nodos.append(nodo)

    for i in range(cantidad):
        # enlace = (nodos[i], nodos[(i+1)%cantidad])
        graph[nodos[i]].append(nodos[(i+1)%cantidad])
        graph[nodos[(i+1)%cantidad]].append(nodos[i])
        atm_libres.append(nodos[i])
        atm_libres.append(nodos[i]*-1)
        # atm_libres.append(nodos[(i+1)%cantidad])
        # atm_libres.append(nodos[(i+1)%cantidad]*-1)


    print("Terminé de generar el grafo")
    # print("Atm libres: ", atm_libres)
    print("Len atm libres: ", len(atm_libres))

    return enlaces

tInicio = time.time()
generarGrafoValido(2000)



# tInicio = time.time()

path = find_eulerian_path(graph)
print("tengo el camino euleriano")
camino_con_pesos = find_weights(path, 3, 5)
print(camino_con_pesos)
tFinal = time.time()
print(tFinal - tInicio)