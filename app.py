import os
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate # Importa Flask-Migrate

app = Flask(__name__)

# Configurações básicas
app.config['SECRET_KEY'] = 'uma-chave-secreta-bem-segura'
# Cria o banco de dados sqlite na raiz do projeto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oficina.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db) # Inicializa Flask-Migrate

# Importa as rotas para o Flask reconhecê-las
from routes import *

if __name__ == '__main__':
    # Não precisamos mais de db.create_all() aqui se estivermos usando migrações.
    # As migrações criarão/atualizarão o esquema do banco de dados.
    app.run(debug=True)
