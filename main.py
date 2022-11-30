from flask import Flask, render_template, request, flash, redirect
import json
import os


app = Flask(__name__)
app.config['SECRET_KEY']= "joao123"
@app.route("/")
def home():
    return render_template("html/login.html")

@app.route("/login", methods=['POST'])
def login():
    usuario = request.form.get('nome')
    senha = request.form.get('senha')
    with open('usuarios.json') as usuarios:
        lista = json.load(usuarios)
        cont = 0
        for c in lista:
            cont+=1
            if usuario == c['nome'] and senha == c['senha']:
                return render_template("html/acesso.html", nomeUsuario=c['nomeCompleto'])
            if cont >= len(lista):
                flash('Acesso Negado')
                return redirect("/")



if __name__ in '__main__':
    app.run(debug=True)