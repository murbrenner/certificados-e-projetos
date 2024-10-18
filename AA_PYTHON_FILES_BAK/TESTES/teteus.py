import heapq

class FilaPrioritaria:
    def __init__(self):
        self.fila = []

    def enfileirar(self, item, prioridade):
        heapq.heappush(self.fila, (prioridade, item))

    def desenfileirar(self):
        if not self.esta_vazia():
            return heapq.heappop(self.fila)[1]
        return None

    def esta_vazia(self):
        return len(self.fila) == 0

    def tamanho(self):
        return len(self.fila)

fila = FilaPrioritaria()
fila.enfileirar('tarefa1', 2)
fila.enfileirar('tarefa2', 1)
print(fila.desenfileirar())
print(fila.desenfileirar())