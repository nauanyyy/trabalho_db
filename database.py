import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import mysql, app

def criar_tabelas():
    with app.app_context():
        cursor = mysql.connection.cursor()
        
        # Criar tabela de usuários se não existir
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            senha VARCHAR(255),
            cpf VARCHAR(14),
            telefone VARCHAR(15)
        );
        """)

        # Criar tabela de quartos se não existir
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quartos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            numero VARCHAR(10),
            tipo VARCHAR(50),
            capacidade INT,
            preco DECIMAL(10, 2)
        );
        """)

        # Criar tabela de reservas se não existir
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            quarto_id INT,
            data_checkin DATE,
            data_checkout DATE,
            FOREIGN KEY (usuario_id) REFERENCES users(id),
            FOREIGN KEY (quarto_id) REFERENCES quartos(id)
        );
        """)

        mysql.connection.commit()
        cursor.close()
        print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    criar_tabelas()