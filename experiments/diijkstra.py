class Grafo:
    def __init__(self):
        self.adjacencias = {}
    
    def adiciona_vertice(self, vertice):
        if vertice not in self.adjacencias:
            self.adjacencias[vertice] = []
    
    def adiciona_aresta(self, vertice1, vertice2):
        self.adiciona_vertice(vertice1)
        self.adiciona_vertice(vertice2)
        self.adjacencias[vertice1].append(vertice2)
        self.adjacencias[vertice2].append(vertice1)

    def vizinhos(self, vertice):
        return self.adjacencias.get(vertice, [])

def processa_vertice(vertice):
    print(f"Processando vértice: {vertice}")

def processa_aresta(vertice1, vertice2):
    print(f"Processando aresta: ({vertice1}, {vertice2})")


def busca(G, r):
    T = {}  # grafo vazio
    V1 = {}
    processa_vertice(r)
    [r]  # lista inicial com o vértice r
    V2 = set()  # conjunto para os vértices processados
    T = set()  # conjunto das arestas processadas
    
    processa_vertice(r)
    T.add(r)

    while V1:
        v = V1.pop(0)
        if v in V2:
            continue

        vizinhos = grafo.vizinhos(v)
        if not vizinhos:
            V2.add(v)
        else:
            for w in vizinhos:
                if w not in V1 and w not in V2:
                    if (v, w) not in T and (w, v) not in T:
                        processa_aresta(v, w)
                    V1.append(w)
                    T.add((v, w))
                elif (v, w) not in T and (w, v) not in T:
                    processa_aresta(v, w)
                    processa_vertice(w)
                    V1.append(w)
                    T.add((v, w))
                    T.add(w)
                    
    return T, r

# Exemplo de uso:
grafo = Grafo()
grafo.adiciona_aresta(1, 2)
grafo.adiciona_aresta(1, 3)
grafo.adiciona_aresta(2, 4)
grafo.adiciona_aresta(3, 5)
grafo.adiciona_aresta(4, 5)

T, r = busca(grafo, 1)
print("Arestas processadas:", T)
