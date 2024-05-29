from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
from datetime import datetime

app = Flask(__name__)

# Chave que vai cryptografar a senha no DB
app.secret_key = 'your secret key'

# Configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'fatec'
app.config['MYSQL_DB'] = 'scrumteach'

# Inicialização do MySQL
mysql = MySQL(app)

# ------------------------------------------------------- Sistema Login -------------------------------------------------------
# Página Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Mensagem de erro
    msg = ''
    if request.method == 'POST' and 'regfun' in request.form and 'password' in request.form:
        regfun = request.form['regfun']
        password = request.form['password']
        # Cryptografa senha
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        # Checa se a conta ja existe
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE regfun = %s AND password = %s', (regfun, password,))
        account = cursor.fetchone()
        if account:
            # Cria session
            session['loggedin'] = True
            session['idAc'] = account['idAc']
            session['nome'] = account['nome']
            return redirect(url_for('index'))
        else:
            msg = 'Usuário ou senha incorretos!'
    return render_template('login.html', msg=msg)

# Função para logout
@app.route('/logout')
def logout():
    # Remove session data
   session.pop('loggedin', None)
   session.pop('idAc', None)
   session.pop('username', None)
   return redirect(url_for('login'))

#Página Criar Conta
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Mensagem de erro
    msg = ''
    if request.method == 'POST' and 'regfun' in request.form and 'password' in request.form and 'nome' in request.form:
        # Create variables for easy access
        nome = request.form['nome']
        password = request.form['password']
        regfun = request.form['regfun']
                # Checa se conta ja existe usando MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE regfun = %s', (regfun,))
        account = cursor.fetchone()
        # Erros caso conta ja exista oucampo preenchido errado
        if account:
            msg = 'Essa conta já existe!'
        elif not re.match(r'[0-9]+', regfun):
            msg = 'Seu registro de funcionario só pode conter números!'
        elif not re.match(r'[A-Za-z]+', nome):
            msg = 'Nome só pode conter letras!'
        elif not nome or not password or not regfun:
            msg = 'Preencha o formulário!'
        else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (nome, password, regfun,))
            mysql.connection.commit()
            msg = 'Registrado com sucesso!'
    elif request.method == 'POST':
        msg = 'Preencha o formulário!'
    return render_template('register.html', msg=msg)

# Página Perfil
@app.route('/profile')
def profile():
    # Checa se o usuario esta logado
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE idAc = %s', (session['idAc'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))


# ------------------------------------------------------- Comentarios -------------------------------------------------------

# Rota para exibir a lista de tarefas
@app.route('/comentarios')
def comentarios():
    cur = mysql.connection.cursor()

    sql = "SELECT \
          accounts.nome, \
          cmtDB.conteudo, \
          cmtDB.now_date \
          FROM cmtDB \
          INNER JOIN accounts ON cmtDB.idAC = accounts.idAc \
          ORDER BY id DESC"
    
    cur.execute(sql)
    comment = cur.fetchall()
    cur.close()
    return render_template('comentarios.html', comment=comment)

# Rota para adicionar uma nova tarefa
@app.route('/add', methods=['POST'])
def add_comment():
    if request.method == 'POST':
        idAc=session['idAc']
        conteudo = request.form['conteudo']

        now = datetime.now()
        now_date = now.strftime("%d/%m/%Y, %H:%M")

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO cmtDB (idAc, conteudo, now_date) VALUES (%s, %s, %s)", (idAc, conteudo, now_date))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('comentarios'))
    
# Rota para atualizar uma tarefa
@app.route('/update/<int:comment_id>', methods=['POST'])
def update_comment(comment_id):
    if request.method == 'POST':
        idAc=session['idAc']
        conteudo = request.form['conteudo']

        now = datetime.now() # current date and time
        now_date = now.strftime("%d/%m/%Y, %H:%M")

        cur = mysql.connection.cursor()
        cur.execute("UPDATE cmtDB SET idAc=%s, conteudo=%s, now_date=%s WHERE id=%s", (idAc, now_date, comment_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('comentarios'))

# ------------------------------------------------------- Outras Páginas -------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/introducao')
def introducao():
    return render_template('introducao.html')

@app.route('/papeis')
def papeis():
    return render_template('papeis.html')

@app.route('/ferramentas')
def ferramentas():
    return render_template('ferramentas.html')

@app.route('/avaliacao')
def avaliacao():
    return render_template('avaliacao.html')

# ------------------------------------------------------- Avaliação -------------------------------------------------------
answers = {
    "q1": "r4",
    "q2": "r2",
    "q3": "r2",
    "q4": "r3",
    "q5": "r2",
    "q6": "r4",
    "q7": "r3",
    "q8": "r3",
    "q9": "r2",
    "q10": "r2",
    "q11": "r1",
    "q12": "r3",
    "q13": "r3",
    "q14": "r2",
    "q15": "r1",
    "q16": "r4",
    "q17": "r3",
    "q18": "r1",
    "q19": "r3",
    "q20": "r1",
}

@app.route('/submit', methods=['POST'])
def submit():
    score = 0
    total_questions = len(answers)
    results = {}

    for question, correct_answer in answers.items():
        user_answer = request.form.get(question)
        if user_answer == correct_answer:
            score += 1
            results[question] = True
        else:
            results[question] = False

    return render_template('resultado.html', score=score, total=total_questions, results=results)

    # ------------------------------------------------------- Quiz -------------------------------------------------------

questionsE = [
    {
        'question': 'Qual é a definição de uma Sprint na metodologia Scrum?',
        'options': ['Uma Sprint é uma reunião diária para discutir o progresso do projeto.',
                    'Uma Sprint é uma reunião para revisar e ajustar o backlog do produto.',
                    'Uma Sprint é um período de tempo fixo durante o qual um conjunto de atividades específicas deve ser concluído.',
                    'Uma Sprint é uma sessão de treinamento intensivo para os membros da equipe Scrum.'
                    ],
        'answer': 'Uma Sprint é um período de tempo fixo durante o qual um conjunto de atividades específicas deve ser concluído.'
    },
    {
        'question': 'Qual é o objetivo do Sprint Planning na metodologia Scrum?',
        'options': ['Rever o progresso do Sprint anterior.',
                    'Priorizar as tarefas do backlog do produto.',
                    'Determinar o que pode ser entregue no próximo Sprint e como será alcançado.',
                    'Realizar uma revisão detalhada do produto já entregue aos clientes.'],
        'answer': 'Determinar o que pode ser entregue no próximo Sprint e como será alcançado.'
    }
]

@app.route('/eventos')
def eventos():
    score = 0
    total=len(questionsE)
    return render_template('eventos.html', questionsE=questionsE, score=score, total=total)

@app.route('/submitEventos', methods=['POST'])
def submitEventos():
    score = 0
    total=len(questionsE)
    for question in questionsE:
        user_answer = request.form.get(question['question'])
        if user_answer == question['answer']:
            score += 1
    return render_template('eventos.html', questionsE=questionsE, score=score, total=total, scroll='exercicios')

if __name__ == '__main__':
    app.run(debug=True)
