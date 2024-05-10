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
    return redirect(url_for('index'))

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

@app.route('/avaliacao')
def avaliacao():
    return render_template('avaliacao.html')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/')
def base():
    comentarios = Comentario.query.all()
    return render_template('index.html', comentarios=comentarios)
