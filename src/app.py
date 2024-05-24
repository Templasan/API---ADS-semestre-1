from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'teste'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comentarios.db'
db = SQLAlchemy(app)

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    comentario = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    usuario = request.form['usuario']
    senha = request.form['senha']
    comentario = request.form['comentario']
    
    novo_comentario = Comentario(usuario=usuario, senha=senha, comentario=comentario)
    db.session.add(novo_comentario)
    db.session.commit()
    
    flash('Seu comentário foi enviado com sucesso!', 'success')
    return redirect(url_for('comment'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/introducao')
def introducao():
    return render_template('introducao.html')

@app.route('/papeis')
def papeis():
    return render_template('papeis.html')

@app.route('/eventos')
def eventos():
    return render_template('eventos.html')

@app.route('/ferramentas')
def ferramentas():
    return render_template('ferramentas.html')

@app.route('/comentarios')
def comment():
    comentarios = Comentario.query.all()
    return render_template('comentarios.html', comentarios=comentarios)

# Gabarito do quiz
answers = {
    "q1": "r3",
    "q2": "r2",
    "q3": "r1",
    "q4": "r4",
    "q5": "r3"
}

@app.route('/avaliacao')
def avaliacao():
    return render_template('avaliacao.html')

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

if __name__ == '__main__':
    app.run(debug=True)
