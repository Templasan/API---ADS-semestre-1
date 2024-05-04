from flask import Flask, render_template

app = Flask(__name__)

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
