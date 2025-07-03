import sys
sys.path.append('C:/Users/L2453/Desktop/ProjetoPSIFinal')

import time 
import os
import mysql.connector

from ProjetoPSI_Connect_db import iniciar_conexao

idFilme = 0
Nbilhete = 0

class Filme:
    def __init__(self, id_filme, titulo, duracao, classificacao, lugaresdisp=100):
        self.titulo = titulo
        self.duracao = duracao
        self.classificacao = classificacao  # idade mínima
        self.idFilme = id_filme  # Mantemos idFilme para compatibilidade com o resto do código
        self.lugaresdisp = lugaresdisp  # Lugares disponíveis
    def __str__(self):
        return f"{self.idFilme} - {self.titulo} (Duração: {self.duracao} min, Classificação: {self.classificacao}, Lugares disponíveis: {self.lugaresdisp})"

class Cliente:
    def __init__(self, Nbilhete, NIF, nome, filme_id):
        self.nome = nome
        self.NIF = NIF
        self.Nbilhete = Nbilhete
        self.filme_id = filme_id  # Guarda o ID do filme comprado

# Função para inserir um cliente na base de dados
# Esta função é chamada quando um bilhete é comprado
# Recebe o objeto cliente e insere os dados na tabela Cliente
# Utiliza prepared statements para evitar SQL injection

def inserir_cliente_bd(mydb, mycursor, cliente):
    try:
        # Nota: A tabela cliente não tem filme_id, por isso removemos essa coluna
        # sql = "INSERT INTO Cliente (NBilhete, NIF, nome, lugaresdisp) VALUES (%s, %s, %s, %s)"
        # valores = (cliente.Nbilhete, cliente.NIF, cliente.nome, 1)  # lugaresdisp = 1 para indicar que comprou um bilhete
        # mycursor.execute(sql, valores)
        sql = "INSERT INTO Cliente (NBilhete, NIF, nome, lugaresdisp) VALUES (%s, %s, %s, %s)"
        valores = (cliente.Nbilhete, cliente.NIF, cliente.nome, 1)
        mycursor.execute(sql, valores)
        mydb.commit()
        print("Registo inserido com sucesso!")
    except mysql.connector.Error as erro:
        print(f"Erro: {erro}")

# Função para inserir um filme na base de dados
# Recebe o objeto filme e insere os dados na tabela Filme

def inserir_filme_bd(mydb, mycursor, filme):
    try:
        sql = "INSERT INTO Filme (titulo, duracao, classificacao, lugaresdisp) VALUES (%s, %s, %s, %s)"
        valores = (filme.titulo, filme.duracao, filme.classificacao, str(filme.lugaresdisp))  # Converter para string
        mycursor.execute(sql, valores)
        mydb.commit()
        print("Registo inserido com sucesso!")
    except mysql.connector.Error as erro:
        print(f"Erro: {erro}")

# Função para atualizar um filme na base de dados
# Recebe o id do filme e os novos dados

def atualizar_filme_bd(mydb, mycursor, filme_id, titulo, duracao, classificacao, lugaresdisp):
    try:
        sql = "UPDATE Filme SET titulo = %s, duracao = %s, classificacao = %s, lugaresdisp = %s WHERE id_filme = %s"
        valores = (titulo, duracao, classificacao, str(lugaresdisp), filme_id)  # Converter lugaresdisp para string
        mycursor.execute(sql, valores)
        mydb.commit()
        print("Filme atualizado com sucesso!")
    except mysql.connector.Error as erro:
        print(f"Erro: {erro}")

# Função para eliminar um filme da base de dados
# Recebe o id do filme a eliminar

def eliminar_filme_bd(mydb, mycursor, filme_id):
    try:
        sql = "DELETE FROM Filme WHERE id_filme = %s"
        valores = (filme_id,)
        mycursor.execute(sql, valores)
        mydb.commit()
        print("Filme eliminado com sucesso!")
    except mysql.connector.Error as erro:
        print(f"Erro: {erro}")

# Função para carregar todos os filmes da base de dados para memória
# Converte os resultados em objetos Filme
# Corrigida para usar id_filme em vez de idFilme

def carregar_filmes_bd(mydb, mycursor):
    try:
        sql = "SELECT * FROM Filme"
        mycursor.execute(sql)
        resultado = mycursor.fetchall()
        filmes = []
        for row in resultado:
            
            # Conversão robusta: garante que lugaresdisp seja inteiro válido, mesmo se o valor vier como None ou não numérico
            try:
                lugaresdisp = int(row[4]) if row[4] is not None and str(row[4]).isdigit() else 100
            except Exception:
                lugaresdisp = 100
            filme = Filme(row[0], row[1], row[2], row[3], lugaresdisp)
            filmes.append(filme)
        return filmes
    except mysql.connector.Error as erro:
        print(f"Erro ao carregar filmes: {erro}")
        return []

# Função para carregar todos os clientes da base de dados
# Retorna uma lista de tuplos com os dados dos clientes

def carregar_clientes_bd(mydb, mycursor):
    try:
        sql = "SELECT * FROM Cliente"
        mycursor.execute(sql)
        resultado = mycursor.fetchall()
        return resultado
    except mysql.connector.Error as erro:
        print(f"Erro ao carregar clientes: {erro}")
        return []

# Função para listar todos os clientes
# Mostra os dados dos clientes de forma organizada

def listar_clientes(mydb, mycursor):
    clientes = carregar_clientes_bd(mydb, mycursor)
    if not clientes:
        print("Não há clientes registados.")
        return
    
    print("\n=== LISTA DE CLIENTES ===")
    print("ID | Nº Bilhete | NIF        | Nome")
    print("-" * 50)
    
    for cliente in clientes:
        
        print(f"{cliente[0]:2} | {cliente[1]:10} | {cliente[2]:10} | {cliente[3]}")
    
    print(f"\nTotal de clientes: {len(clientes)}")

# Função utilitária para limpar o ecrã e mostrar mensagem de loading

def wait_n_clear():
    os.system('cls')  
    print("\nA Loading....")
    time.sleep(2)
    os.system('cls')

# Função principal do programa
# Contém o ciclo principal do menu e gere todas as operações
# As secções mais complexas estão comentadas para facilitar a compreensão

def main():
    global idFilme, Nbilhete
    
    # Iniciar ligação à base de dados
    mydb = iniciar_conexao()
    if mydb is None:
        print("Erro de conexão")
        return
    
    mycursor = mydb.cursor()
    
    # Carregar filmes existentes da base de dados
    lista_filmes = carregar_filmes_bd(mydb, mycursor)
    if lista_filmes:
        # Obtém o maior idFilme já existente para garantir que novos filmes tenham um id único e sequencial
        idFilme = max(filme.idFilme for filme in lista_filmes)
    
    Bilhetes = []

    while True:
        wait_n_clear()
        print("\n=== CINEMA ===")
        print("1. Listar sessões disponíveis")
        print("2. Comprar bilhete")
        print("3. Adicionar Filme (Admin)")
        print("4. Atualizar informações do Filme (Admin)")
        print("5. Eliminar Filme (Admin)")
        print("6. Listar Clientes (Admin)")
        print("0. Sair")

        op = input("Escolha uma opção: ")
            
        match op:
            case "1":
                wait_n_clear()
                if not lista_filmes:
                    print("Ainda não há filmes disponíveis.")
                    input("Prima Enter para continuar...")
                    continue
                for filme in lista_filmes:
                    print(filme)
                    print("________________________")
                input("Prima Enter para continuar...")

            case "2":
                # Comprar bilhete
                if not lista_filmes:
                    print("Ainda não há filmes disponíveis.")
                    input("Prima Enter para continuar...")
                    continue

                for filme in lista_filmes:
                    print(filme)
                    print("________________________")

                while True:
                    try:
                        escolha = int(input("Digite o ID do filme que deseja assistir: "))
                    except ValueError:
                        print("Entrada inválida. Digite um número.")
                        input("Prima Enter para continuar...")
                        wait_n_clear()
                        continue
                    # Procura o filme escolhido pelo utilizador
                    filme_escolhido = next((filme for filme in lista_filmes if filme.idFilme == escolha), None)
                    if not filme_escolhido:
                        print("Filme não encontrado.")
                        input("Prima Enter para continuar...")
                        wait_n_clear()
                        continue
                    
                    if filme_escolhido.lugaresdisp <= 0:
                        print("Este filme está esgotado!")
                        input("Prima Enter para continuar...")
                        wait_n_clear()
                        break
                    
                    # Pedir dados do comprador
                    while True:
                        entrada = input("NIF do comprador (9 dígitos): ")
                        try:
                            NIF = int(entrada)
                            # Verificar se o NIF tem exatamente 9 dígitos
                            if len(entrada) != 9:
                                print("Erro: O NIF deve ter exatamente 9 dígitos!")
                                continue
                            break
                        except ValueError:
                            print("Valor inválido! Digite apenas números inteiros.")
                    nome = input("Nome do comprador: ")
                    Nbilhete = len(Bilhetes) + 1
                    # Criar cliente e guardar bilhete
                    cliente = Cliente(Nbilhete, NIF, nome, filme_escolhido.idFilme)
                    Bilhetes.append(cliente)
                    
                    inserir_cliente_bd(mydb, mycursor, cliente)

                    # Reduzir lugares disponíveis no filme
                    filme_escolhido.lugaresdisp -= 1
                    atualizar_filme_bd(mydb, mycursor, filme_escolhido.idFilme, 
                                  filme_escolhido.titulo, filme_escolhido.duracao, 
                                  filme_escolhido.classificacao, filme_escolhido.lugaresdisp)

                    print(f"Bilhete comprado com sucesso! Número do bilhete: {Nbilhete}")
                    print(f"Lugares restantes para o filme '{filme_escolhido.titulo}': {filme_escolhido.lugaresdisp}")

                    # Verificar desconto para estudante
                    while True:
                        estudante = input("É estudante? (s/n): ").lower()
                        if estudante in ["s", "n"]:
                            if estudante == "s":
                                print("Recebeu um desconto de 50%.")
                            break
                        else:
                            print("Por favor, responda com 's' ou 'n'.")

                    continuar = input("Deseja comprar outro bilhete? (s/n): ").lower()
                    while continuar not in ["s", "n"]:
                        continuar = input("Por favor, responda com 's' ou 'n': ").lower()
                    if continuar == "n":
                        break            

            case "3":
                # Adicionar filmes (Admin)
                password = input("Introduza a Palavra-Passe: ")
                while password != "breno123BEST":
                    wait_n_clear()
                    print("Palavra-passe incorreta! Tente novamente...")
                    password = input("Introduza a Palavra-Passe novamente: ")

                wait_n_clear()
                while True:
                    titulo = input("Título do filme: ")

                    while True:
                        entrada = input("Duração (em minutos): ")
                        try:
                            duracao = int(entrada)
                            break
                        except ValueError:
                            print("Número inválido! Digite apenas números inteiros.")

                    while True:
                        entrada = input("Classificação de Idade: ")
                        try:
                            classificacao = int(entrada)
                            break
                        except ValueError:
                            print("Número inválido! Digite apenas números inteiros.")

                    while True:
                        entrada = input("Número de lugares disponíveis: ")
                        try:
                            lugaresdisp = int(entrada)
                            if lugaresdisp < 0:
                                print("Número inválido! Deve ser maior ou igual a zero.")
                                continue
                            break
                        except ValueError:
                            print("Número inválido! Digite apenas números inteiros.")

                    idFilme += 1
                    filme = Filme(idFilme, titulo, duracao, classificacao, lugaresdisp)
                    lista_filmes.append(filme)

                    inserir_filme_bd(mydb, mycursor, filme)

                    continuar = input("Deseja adicionar outro filme? (s/n): ").lower()
                    while continuar not in ["s", "n"]:
                        wait_n_clear()
                        continuar = input("Por favor, responda com 's' ou 'n': ").lower()
                    if continuar == "n":
                        break

            case "4":
                # Atualizar informações do filme (Admin)
                password = input("Introduza a Palavra-Passe: ")
                while password != "breno123BEST":
                    wait_n_clear()
                    print("Palavra-passe incorreta! Tente novamente...")
                    password = input("Introduza a Palavra-Passe novamente: ")

                wait_n_clear()
                if not lista_filmes:
                    print("Não há filmes para atualizar.")
                    input("Prima Enter para continuar...")
                    continue

                for filme in lista_filmes:
                    print(filme)
                    print("________________________")

                try:
                    filme_id = int(input("Digite o ID do filme que deseja atualizar: "))
                    filme_atualizar = next((filme for filme in lista_filmes if filme.idFilme == filme_id), None)
                    
                    if not filme_atualizar:
                        print("Filme não encontrado.")
                        input("Prima Enter para continuar...")
                        continue

                    # Atualiza os dados do filme selecionado em memória com as novas informações fornecidas pelo admin
                    titulo = input(f"Novo título (atual: {filme_atualizar.titulo}): ") or filme_atualizar.titulo
                    duracao = int(input(f"Nova duração (atual: {filme_atualizar.duracao}): ") or filme_atualizar.duracao)
                    classificacao = int(input(f"Nova classificação (atual: {filme_atualizar.classificacao}): ") or filme_atualizar.classificacao)
                    lugaresdisp = int(input(f"Novos lugares disponíveis (atual: {filme_atualizar.lugaresdisp}): ") or filme_atualizar.lugaresdisp)

                    # Atualizar em memória
                    filme_atualizar.titulo = titulo
                    filme_atualizar.duracao = duracao
                    filme_atualizar.classificacao = classificacao
                    filme_atualizar.lugaresdisp = lugaresdisp

                    # Atualizar na base de dados
                    atualizar_filme_bd(mydb, mycursor, filme_id, titulo, duracao, classificacao, lugaresdisp)
                    
                except ValueError:
                    print("Entrada inválida.")
                    input("Prima Enter para continuar...")

            case "5":
                # Eliminar filme (Admin)
                password = input("Introduza a Palavra-Passe: ")
                while password != "breno123BEST":
                    wait_n_clear()
                    print("Palavra-passe incorreta! Tente novamente...")
                    password = input("Introduza a Palavra-Passe novamente: ")

                wait_n_clear()
                if not lista_filmes:
                    print("Não há filmes para eliminar.")
                    input("Prima Enter para continuar...")
                    continue

                for filme in lista_filmes:
                    print(filme)
                    print("________________________")

                try:
                    filme_id = int(input("Digite o ID do filme que deseja eliminar: "))
                    filme_eliminar = next((filme for filme in lista_filmes if filme.idFilme == filme_id), None)
                    
                    if not filme_eliminar:
                        print("Filme não encontrado.")
                        input("Prima Enter para continuar...")
                        continue

                    confirmacao = input(f"Tem a certeza que deseja eliminar '{filme_eliminar.titulo}'? (s/n): ").lower()
                    if confirmacao == "s":
                        # Remover da memória
                        lista_filmes.remove(filme_eliminar)
                        # Remover da base de dados
                        eliminar_filme_bd(mydb, mycursor, filme_id)
                        print("Filme eliminado com sucesso!")
                    else:
                        print("Operação cancelada.")
                    
                except ValueError:
                    print("Entrada inválida.")
                    input("Prima Enter para continuar...")

            case "6":
                # Listar clientes (Admin)
                password = input("Introduza a Palavra-Passe: ")
                while password != "breno123BEST":
                    wait_n_clear()
                    print("Palavra-passe incorreta! Tente novamente...")
                    password = input("Introduza a Palavra-Passe novamente: ")

                wait_n_clear()
                listar_clientes(mydb, mycursor)
                input("Prima Enter para continuar...")

            case "0":
                wait_n_clear()
                print("Obrigado(a)! Volte sempre!!")
                time.sleep(3)
                break

            case _:
                print("Opção inválida!")
                time.sleep(3)
                wait_n_clear()
    
    mycursor.close()
    mydb.close()

if __name__ == "__main__":
    main()1