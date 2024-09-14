import textwrap
import abc
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizarTransacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionarConta(self,conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, dataNascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.dataNascimento = dataNascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._numero = numero
        self._cliente = cliente
        self._saldo = 0
        self._agencia = "0001"
        self._historico = Historico()
        
    @classmethod
    def novaConta(cls, cliente, numero):
        return cls(cliente, numero)
    
    @property
    def saldo(self):
        return self._saldo
    @property
    def numero(self):
        return self._numero
    @property
    def agencia(self):
        return self._agencia
    @property
    def cliente(self):
        return self._cliente
    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        saldo = self.saldo
        excedeuSaldo = valor > saldo
        
        if excedeuSaldo:
            print("\n@@@ Operação Falhou!! Você não tem saldo suficiente! @@@")
        elif valor > 0:
            self._saldo -= valor
            print("\n### Saque realizado com sucesso!! ###")
            return True
        else:
            print("\n@@@ Operação Falhou!! O valor informado é inválido@@@")
            return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo +=valor
        else:
            print("\n@@@ Operação Falhou!! O valor informado é inválido@@@")
            return False
        return True
    
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 500, limiteSaques = 3):
        super().__init__(cliente, numero)
        self.limite = limite
        self.limiteSaques = limiteSaques
    
    def sacar(self, valor):
        numeroSaques = len(
            [ transacao for transacao in self.historico.
                transacoes if transacao["tipo"] == Saque.__name__]
        )
        
        excedeuLimite = valor > self.limite
        excedeuSaques = numeroSaques > self.limiteSaques
        if excedeuLimite:
            print("\n@@@ Operação Falhou!! O valor do saque excedeu o limite! @@@")
        elif excedeuSaques:
            print("\n@@@ Operação Falhou!! Número máximo de saques excedido! @@@")
        else:
            return super().sacar(valor)
        return False
    
    def __str__(self):
        return f"""\
                Agência:\t{self.agencia}
                C/C:\t\t{self.numero}
                Titular:\t{self.cliente.nome}
                """

class Historico:
    def __init__(self):
        self._transacoes = []
        
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionarTransacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
        )

class Transacao(abc.ABC):
    @property
    def valor(self):
        pass
    
    @property
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucessoTransacao = conta.sacar(self.valor)
        
        if sucessoTransacao:
            conta.historico.adicionarTransacao(self)

class Deposito(Transacao):
    def __init__(self,valor):
        self._valor = valor  
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucessoTransacao = conta.depositar(self.valor)
        
        if sucessoTransacao:
            conta.historico.adicionarTransacao(self)

def menu():
    menu = """"\n
    ===========MENU==========
    [d].\tDepositar
    [s].\tSacar
    [e].\tExtrato
    [nc].\tNova Conta
    [lc].\tListar Contas
    [nu].\tNovo Usuário
    [q].\tSair
    
    
    ===>"""
    return input(textwrap.dedent(menu))

def filtrarCliente(cpf, clientes):
    clientesFiltrados = [cliente for cliente in clientes if cliente.cpf==cpf]
    return clientesFiltrados[0] if clientesFiltrados else None

def recuperarContaCliente(cliente):
    if not cliente.contas:
        print("\n@@@ O Cliente não possui conta! @@@")
        return
    # FIXME: Não permite cliente escolher a conta
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrarCliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    valor = float(input("Informe o valor do Depósito: "))
    transacao = Deposito(valor)
    conta = recuperarContaCliente(cliente)
    if not conta:
        return
    cliente.realizarTransacao(conta, transacao)
    
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrarCliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    valor = float(input("Informe o valor do Saque: "))
    transacao = Saque(valor)
    conta = recuperarContaCliente(cliente)
    if not conta:
        return
    cliente.realizarTransacao(conta, transacao)
#pode melhorar sacar() e depositar() tem o mesmo código, só muda uma linha

def exibirExtrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrarCliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    conta = recuperarContaCliente(cliente)
    if not conta:
        return
    
    print("\n========== E X T R A T O ==========")
    transacoes = conta.historico.transacoes
    
    extrato = ""
    if not transacoes:
        extrato = "\n@@@ Não foram realizadas movimentações! @@@"
    else:
        for transacao in transacoes:
            extrato == f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"
    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("===================================")

def criarCliente(clientes):
    cpf = input("informe o CPF (apenas números): ")
    cliente = filtrarCliente(cpf, clientes)
    if cliente:
        print("\n@@@ Já existe um cliente cadastrado com esse CPF! @@@")
        return
    nome = input("Informe o nome completo: ")
    dataNascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (Logradouro, nro - bairro - cidade/sigla estado: )")
    
    cliente = PessoaFisica(nome=nome, dataNascimento=dataNascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)

    print("\n===== Cliente cadastrado com sucesso! =====")
    
def criarConta(numeroConta, clientes, contas):
    
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrarCliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return
    conta = ContaCorrente.novaConta(cliente=cliente,numero=numeroConta)
    contas.append(conta)
    cliente.contas.append(conta)
    print("===== Conta criada com sucesso!! =====")

def listarContas(contas):
    for conta in contas:
        print("="* 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas =[]
    
    while True:
        opcao = menu()
        
        if opcao == "d":
            depositar(clientes)
            
        elif opcao == "s":
            sacar(clientes)
            
        elif opcao == "e":
            exibirExtrato(clientes)
            
        elif opcao == "nu":
            criarCliente(clientes)
            
        elif opcao == "nc":
            numeroConta = len(contas) + 1
            criarConta(numeroConta, clientes, contas)
            
        elif opcao == "lc":
            listarContas(contas)
            
        elif opcao == "q":
            break

main()