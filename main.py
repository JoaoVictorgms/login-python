import os
from flask import Flask, render_template, request, flash, redirect, send_file
from werkzeug.security import  check_password_hash
from werkzeug.utils import secure_filename
import pyexcel as pe
import json
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.security import generate_password_hash

# Resto do seu código...


UPLOAD_FOLDER = 'arquivos'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['SECRET_KEY'] = "joao123"
app.config['UPLOAD_FOLDER'] = 'arquivos'


@app.route("/")
def home():
    return render_template("html/login.html")


@app.route("/login", methods=['POST'])
def login():
    usuario = request.form.get('nome')
    senha = request.form.get('senha')
    with open('usuarios.json') as usuarios:
        lista = json.load(usuarios)
        for c in lista:
            if usuario == c['nome'] and check_password_hash(c['senha'], senha):
                return render_template("html/acesso.html", nomeUsuario=c['nomeCompleto'])
        flash('Acesso Negado')
        return redirect("/")


@app.route("/acesso")
def acesso():
    return render_template("html/acesso.html")


@app.route("/arquivo", methods=['GET', 'POST'])
def arquivo():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado.')
            return redirect("/arquivo")

        arquivo = request.files['file']

        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado.')
            return redirect("/arquivo")

        filename = secure_filename(arquivo.filename)
        arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        pdf_filename = convert_to_pdf(filename)

        if pdf_filename:
            # Retorna o nome do arquivo PDF para a mesma página
            return render_template("html/arquivo.html", pdf_filename=pdf_filename)
        else:
            flash('Erro ao converter arquivo para PDF.')
            return redirect("/arquivo")

    return render_template("html/arquivo.html")


@app.route("/download_pdf", methods=['POST'])
def download_pdf():
    pdf_filename = request.form.get('pdf_filename')
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)

    if os.path.isfile(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    else:
        flash('Erro ao fazer o download do arquivo PDF.')
        return redirect("/arquivo")

def convert_to_pdf(filename):
    extensao = os.path.splitext(filename)[1].lower()
    pdf_filename = filename.replace(extensao, '.pdf')
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)

    if extensao == '.txt':
        txt_to_pdf(os.path.join(app.config['UPLOAD_FOLDER'], filename), pdf_path)
    elif extensao == '.docx':
        if convert_docx_to_pdf(os.path.join(app.config['UPLOAD_FOLDER'], filename), pdf_path):
            return pdf_filename
        else:
            return None
    elif extensao == '.xlsx':
        xlsx_to_pdf(os.path.join(app.config['UPLOAD_FOLDER'], filename), pdf_path)

    if os.path.isfile(pdf_path):
        return pdf_filename
    else:
        return None


@app.route("/audio")
def audio():
    return render_template("html/audio.html")

@app.route("/imagem")
def imagem():
    return render_template("html/imagem.html")

@app.route("/cadastrar", methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        usuario = request.form.get('nome')
        senha = request.form.get('senha')
        nome_completo = request.form.get('nome_completo')

        # Codifica a senha
        senha_codificada = generate_password_hash(senha)

        # Lê o arquivo JSON existente
        with open('usuarios.json') as usuarios_file:
            usuarios = json.load(usuarios_file)

        # Adiciona o novo usuário
        novo_usuario = {
            'nome': usuario,
            'senha': senha_codificada,
            'nomeCompleto': nome_completo
        }
        usuarios.append(novo_usuario)

        # Salva os usuários no arquivo JSON
        with open('usuarios.json', 'w') as usuarios_file:
            json.dump(usuarios, usuarios_file, indent=4)

        flash('Cadastro realizado com sucesso!')
        return redirect("/")
    else:
        return render_template("html/cadastro.html")
def convert_docx_to_pdf(docx_path, pdf_path):
    try:
        subprocess.run(['/usr/bin/libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(pdf_path), docx_path],
         check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def txt_to_pdf(txt_path, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont('Helvetica', 12)

    with open(txt_path, 'r') as txt_file:
        lines = txt_file.readlines()
        for line in lines:
            c.drawString(50, 700, line.strip())
            c.showPage()

    c.save()


def xlsx_to_pdf(xlsx_path, pdf_path):
    sheet = pe.get_sheet(file_name=xlsx_path)
    sheet.save_as(pdf_path)


if __name__ == '__main__':
    app.run()
