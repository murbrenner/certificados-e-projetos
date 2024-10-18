class Fila:
    def __init__(self):
        self.fila = []

    def enfileirar(self, item):
        self.fila.append(item)

    def desenfileirar(self):
        if not self.esta_vazia():
            return self.fila.pop(0)
        return None

    def esta_vazia(self):
        return len(self.fila) == 0

    def tamanho(self):
        return len(self.fila)

fila = Fila()
fila.enfileirar(1)
fila.enfileirar(2)
print(fila.desenfileirar())
print(fila.desenfileirar())

