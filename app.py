from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secreta'

# Configurações do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hotel_reservas'

mysql = MySQL(app)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    
    if user and check_password_hash(user[3], senha):
        session['user_id'] = user[0]
        return redirect(url_for('home_page'))
    flash('Login falhou! E-mail ou senha incorretos.', 'error')
    return redirect(url_for('login_page'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cursor = mysql.connection.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Cadastro falhou! E-mail já cadastrado.', 'error')
            cursor.close()
            return redirect(url_for('cadastro'))

        hashed_senha = generate_password_hash(senha)
        cursor.execute("INSERT INTO users (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, hashed_senha))
        mysql.connection.commit()
        cursor.close()
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login_page'))
    return render_template('cadastro.html')

@app.route('/home')
def home_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('home.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('login_page'))

# Rotas para cadastro de hóspedes, quartos e reservas
@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    nome = request.form['nome']
    cpf = request.form['cpf']
    telefone = request.form['telefone']
    email = request.form['email']
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO users (nome, cpf, telefone, email) VALUES (%s, %s, %s, %s)", (nome, cpf, telefone, email))
        mysql.connection.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@app.route('/cadastrar_quarto', methods=['POST'])
def cadastrar_quarto():
    numero = request.form['numero']
    tipo = request.form['tipo']
    capacidade = request.form['capacidade']
    preco = request.form['preco']
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO quartos (numero, tipo, capacidade, preco) VALUES (%s, %s, %s, %s)", (numero, tipo, capacidade, preco))
        mysql.connection.commit()
        return jsonify({"message": "Quarto cadastrado com sucesso!"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@app.route('/cadastrar_reserva', methods=['POST'])
def cadastrar_reserva():
    usuario_id = request.form['usuario_id']
    quarto_id = request.form['quarto_id']
    data_checkin = request.form['data_checkin']
    data_checkout = request.form['data_checkout']
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO reservas (usuario_id, quarto_id, data_checkin, data_checkout) VALUES (%s, %s, %s, %s)", (usuario_id, quarto_id, data_checkin, data_checkout))
        mysql.connection.commit()
        return jsonify({"message": "Reserva cadastrada com sucesso!"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@app.route('/listar_usuarios', methods=['GET'])
def listar_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users")
    usuarios = cursor.fetchall()
    cursor.close()
    
    usuarios_json = []
    for usuario in usuarios:
        usuarios_json.append({
            'id': usuario[0],
            'nome': usuario[1],
            'cpf': usuario[2],
            'telefone': usuario[3],
            'email': usuario[4]
        })
    
    return jsonify(usuarios_json)

@app.route('/listar_quartos', methods=['GET'])
def listar_quartos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM quartos")
    quartos = cursor.fetchall()
    cursor.close()
    
    quartos_json = []
    for quarto in quartos:
        quartos_json.append({
            'id': quarto[0],
            'numero': quarto[1],
            'tipo': quarto[2],
            'capacidade': quarto[3],
            'preco': quarto[4]
        })
    
    return jsonify(quartos_json)

@app.route('/listar_reservas', methods=['GET'])
def listar_reservas():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT reservas.id, users.nome, quartos.numero, reservas.data_checkin, reservas.data_checkout 
        FROM reservas 
        JOIN users ON reservas.usuario_id = users.id 
        JOIN quartos ON reservas.quarto_id = quartos.id
    """)
    reservas = cursor.fetchall()
    cursor.close()
    
    reservas_json = []
    for reserva in reservas:
        reservas_json.append({
            'id': reserva[0],
            'hospede': reserva[1],
            'quarto': reserva[2],
            'data_checkin': reserva[3],
            'data_checkout': reserva[4]
        })
    
    return jsonify(reservas_json)

# Nova rota para a página de listagens
@app.route('/listagens')
def listagens_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('listagens.html')

if __name__ == '__main__':
    app.run(debug=True)