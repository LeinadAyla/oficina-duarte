import os
import datetime  # Importado para injetar nos templates do Jinja2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Importa Flask-Migrate

app = Flask(__name__)

# Configurações básicas
app.config['SECRET_KEY'] = 'uma-chave-secreta-bem-segura'
# Cria o banco de dados sqlite na raiz do projeto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oficina.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Inicializa Flask-Migrate

# Disponibiliza variáveis e funções de tempo para os templates Jinja2 de forma segura
@app.context_processor
def inject_now():
    return {
        'datetime': datetime,                  # Permite usar {{ datetime.now().year }}
        'now': lambda: datetime.now(),          # Permite usar {{ now().year }} (com parênteses no now)
        'year_now': datetime.now().year        # Permite usar o simples {{ year_now }}
    }

# Importa as rotas para o Flask reconhecê-las
from routes import *

if __name__ == '__main__':
    # Garante que os modelos foram registrados e recria o banco corretamente.
    # Mantém tudo dentro do app context para evitar "Working outside of application context".
    with app.app_context():
        # Importa os modelos para que todas as tabelas existam no metadata do SQLAlchemy.
        # (Isso evita erros como "no such table: clientes").
        from models import Cliente, Veiculo, Servico, Peca, ServicoPeca, Mecanico  # noqa: F401

        db.create_all()

    app.run(debug=True)
