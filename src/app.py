from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
from datetime import datetime
import random

app = Flask(__name__)

# Chave que vai cryptografar a senha no DB
app.secret_key = 'your secret key'

# Configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
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
        cursor.close()
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
        cursor.close()
    elif request.method == 'POST':
        msg = 'Preencha o formulário!'
    return render_template('register.html', msg=msg)

# Página Perfil
@app.route('/profile')
def profile():
    # Checa se o usuario esta logado
    if 'loggedin' in session:
        # Dados da conta
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE idAc = %s', (session['idAc'],))
        account = cursor.fetchone()
        cursor.close()
        # Score Avaliações
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM scoreAv WHERE idAc = %s', (session['idAc'],))
        avScore = cursor.fetchall()
        cursor.close()

        return render_template('profile.html', account=account, avScore=avScore)
    return redirect(url_for('login'))


# ------------------------------------------------------- Comentarios -------------------------------------------------------

# Rota para exibir a lista de tarefas
@app.route('/comentarios')
def comentarios():
    cursor = mysql.connection.cursor()

    sql = "SELECT \
          accounts.nome, \
          cmtDB.conteudo, \
          cmtDB.now_date \
          FROM cmtDB \
          INNER JOIN accounts ON cmtDB.idAC = accounts.idAc \
          ORDER BY id DESC"
    
    cursor.execute(sql)
    comment = cursor.fetchall()
    cursor.close()
    return render_template('comentarios.html', comment=comment)

# Rota para adicionar um novo comentário
@app.route('/add', methods=['POST'])
def add_comment():
    if request.method == 'POST':
        idAc=session['idAc']
        conteudo = request.form['conteudo']

        now = datetime.now()
        now_date = now.strftime("%d/%m/%Y, %H:%M")

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO cmtDB (idAc, conteudo, now_date) VALUES (%s, %s, %s)", (idAc, conteudo, now_date))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('comentarios'))

# ------------------------------------------------------- Outras Páginas -------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

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
    user_answers = {}
    all_answered = True

    for question in answers:
        user_answer = request.form.get(question)
        user_answers[question] = user_answer
        if user_answer is None:
            all_answered = False

    if not all_answered:
        error_message = "Por favor, responda todas as perguntas antes de enviar o formulário."
        return render_template('avaliacao.html', error_message=error_message, user_answers=user_answers)

    score = 0
    results = {}
    for question, correct_answer in answers.items():
        user_answer = user_answers.get(question)
        if user_answer == correct_answer:
            score += 1
            results[question] = True
        else:
            results[question] = False

    total_questions = len(answers)

    # Salva Desempenho no DB se logado
    if 'loggedin' in session:
        idAc=session['idAc']
        scorePorcento = str(int((score / total_questions) * 100)) + '%'
        now = datetime.now()
        now_date = now.strftime("%d/%m/%Y, %H:%M")

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO scoreAv (idAc, scorePorcento, now_date) VALUES (%s, %s, %s)", (idAc, scorePorcento, now_date))
        mysql.connection.commit()
        cursor.close()

    return render_template('resultado.html', score=score, total=total_questions, results=results)

    # ------------------------------------------------------- Quiz -------------------------------------------------------

questionsF = [
    {
        'question': 'Qual é a função do Product Backlog no Scrum?',
        'options': ['Detalhar as tarefas diárias dos membros da equipe.',
                    'Listar todos os produtos concorrentes no mercado.',
                    'Priorizar e listar todas as funcionalidades desejadas do produto.',
                    'Documentar todos os erros encontrados no sistema.'
                    ],
        'answer': 'Priorizar e listar todas as funcionalidades desejadas do produto.'
    },
    {
        'question': 'O que é o Sprint Backlog no Scrum?',
        'options': ['Uma lista de todas as tarefas que precisam ser concluídas durante o projeto.',
                    'Uma lista de itens do Product Backlog selecionados para o Sprint, junto com um plano para entregá-los.',
                    'Uma lista de impedimentos que precisam ser resolvidos pela equipe.',
                    'Um documento detalhando as funcionalidades do produto final.'],
        'answer': 'Uma lista de itens do Product Backlog selecionados para o Sprint, junto com um plano para entregá-los.'
    }
]

@app.route('/ferramentas')
def ferramentas():
    score = 0
    total=len(questionsI)

    # Randomiza ordem das perguntas
    for question in questionsP:
        randQuestions = question['options']
        random.shuffle(randQuestions)
        question['options'] = randQuestions

    return render_template('ferramentas.html', questionsF=questionsF, score=score, total=total)

@app.route('/submitFerramentas', methods=['POST'])
def submitFerramentas():
    score = 0
    total=len(questionsF)
    for question in questionsF:
        user_answer = request.form.get(question['question'])
        if user_answer == question['answer']:
            score += 1
    return render_template('ferramentas.html', questionsF=questionsF, score=score, total=total, scroll='exercicios')

questionsI = [
    {
        'question': 'Qual a importância do pilar de Transparência no Scrum?',
        'options': ['Adaptar o projeto para resolução de problemas.',
                    'Permitir que somente um membro saiba como estão os processos do projeto.',
                    'Permitir com que todos da equipe estejam em sintonia e com uma visão clara do andamento e processos do projeto.',
                    'Ajudar no desempenho pessoal de cada um dentro da equipe.'
                    ],
        'answer': 'Permitir com que todos da equipe estejam em sintonia e com uma visão clara do andamento e processos do projeto.'
    },
    {
        'question': 'Qual desses não é um motivo para utilizar o Scrum?',
        'options': ['Análise lenta dos processos.',
                    'Simplicidade na resolução de problemas.',
                    'Facilidade no aprendizado da metodologia.',
                    'Melhora na qualidade do produto.'],
        'answer': 'Análise lenta dos processos.'
    }
]

@app.route('/introducao')
def introducao():
    score = 0
    total=len(questionsI)

    # Randomiza ordem das perguntas
    for question in questionsP:
        randQuestions = question['options']
        random.shuffle(randQuestions)
        question['options'] = randQuestions

    return render_template('introducao.html', questionsI=questionsI, score=score, total=total)

@app.route('/submitIntroducao', methods=['POST'])
def submitIntroducao():
    score = 0
    total=len(questionsI)
    for question in questionsI:
        user_answer = request.form.get(question['question'])
        if user_answer == question['answer']:
            score += 1
    return render_template('introducao.html', questionsI=questionsI, score=score, total=total, scroll='exercicios')


questionsP = [
    {
        'question': 'Qual é a função do Product Owner no Scrum?',
        'options': ['Responsável por liderar as reuniões diárias do Scrum.',
                    'Encarregado de definir os critérios de aceitação das histórias de usuário.',
                    'Responsável por garantir que o time Scrum atenda às expectativas dos stakeholders.',
                    'Encarregado de manter a equipe motivada e produtiva durante o sprint.'
                    ],
        'answer': 'Encarregado de definir os critérios de aceitação das histórias de usuário.'
    },
    {
        'question': 'Qual é o papel do Scrum Master no método Scrum?',
        'options': ['O Scrum Master é responsável por definir as metas do projeto.',
                    'O Scrum Master é o líder técnico da equipe de desenvolvimento.',
                    'O Scrum Master protege a equipe de desenvolvimento de interferências externas.',
                    'O Scrum Master é responsável por aprovar todas as mudanças no produto.'],
        'answer': 'O Scrum Master protege a equipe de desenvolvimento de interferências externas.'
    }
]

@app.route('/papeis')
def papeis():
    score = 0
    total=len(questionsP)

    # Randomiza ordem das perguntas
    for question in questionsP:
        randQuestions = question['options']
        random.shuffle(randQuestions)
        question['options'] = randQuestions

    return render_template('papeis.html', questionsP=questionsP, score=score, total=total)

@app.route('/submitPapeis', methods=['POST'])
def submitPapeis():
    score = 0
    total=len(questionsP)
    for question in questionsP:
        user_answer = request.form.get(question['question'])
        if user_answer == question['answer']:
            score += 1
    return render_template('papeis.html', questionsP=questionsP, score=score, total=total, scroll='exercicios')

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

    # Randomiza ordem das perguntas
    for question in questionsE:
        randQuestions = question['options']
        random.shuffle(randQuestions)
        question['options'] = randQuestions

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
