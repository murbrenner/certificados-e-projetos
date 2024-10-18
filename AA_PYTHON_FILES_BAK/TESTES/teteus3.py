import heapq
from time import sleep

class FilaDeAtendimentoPrioritario:
    def __init__(self):
        self.fila = []

    def adicionar_cliente(self):
        numero_de_clientes = int(input("Deseja adicionar quantos clientes?: "))
        for i in range(1, numero_de_clientes + 1):
            cliente = input(f"Adicione o nome do cliente ({i}): ")
            prioridade = int(input(f"Adicione a prioridade do cliente ({i}) (quanto menor o número, maior a prioridade): "))
            heapq.heappush(self.fila, (prioridade, cliente))
            print(f"\033[92mCliente '{cliente}' com prioridade {prioridade} adicionado à fila de atendimento.\033[0m")
        print(f"\033[92m{numero_de_clientes} clientes foram adicionados à fila.\033[0m")

    def atender_cliente(self):
        if self.fila:
            prioridade, cliente_atendido = heapq.heappop(self.fila)
            print(f"\033[91mCliente '{cliente_atendido}' com prioridade {prioridade} foi atendido e removido da fila.\033[0m")
        else:
            print("\033[91mA fila está vazia. Nenhum cliente para atender.\033[0m")

    def visualizar_fila(self):
        fila_ordenada = sorted(self.fila)
        print("\033[93mFila atual de atendimento:\033[0m", fila_ordenada)

    def finalizar(self):
        print("Finalizando o sistema de atendimento.")
        print(".")
        sleep(1)
        print(".")
        sleep(1)
        print(".")
        sleep(1)
        return False

def main():
    sistema = FilaDeAtendimentoPrioritario()
    
    while True:
        print("="*29)
        print("Sistema de Atendimento Prioritário")
        print("="*29)
        print("O que você deseja fazer?")
        print("1. Adicionar cliente à fila")
        print("2. Atender cliente da fila")
        print("3. Visualizar fila de atendimento")
        print("4. Sair")
        opcao = int(input("Escolha uma opção: "))
        
        if opcao == 1:
            sistema.adicionar_cliente()
        elif opcao == 2:
            sistema.atender_cliente()
        elif opcao == 3:
            sistema.visualizar_fila()
        elif opcao == 4:
            if not sistema.finalizar():
                break
        else:
            print("Opção inválida, escolha uma opção válida.")
    
    print("Sistema de atendimento finalizado.\nOs seguintes clientes ainda estão na fila:", sorted(sistema.fila))

if __name__ == "__main__":
    main()
