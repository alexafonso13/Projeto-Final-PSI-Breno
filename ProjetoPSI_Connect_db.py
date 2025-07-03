import mysql.connector

def iniciar_conexao():
    """
    Inicia a ligação à base de dados MySQL local (XAMPP).
    """
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="projetopsibreno_db",
            port=3306
        )
        return conexao
    except mysql.connector.Error as erro:
        print(f"Erro ao ligar à base de dados: {erro}")
        return None
    