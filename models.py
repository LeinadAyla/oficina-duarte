from app import db
from datetime import datetime
from sqlalchemy.orm import relationship, backref # Importar relationship e backref
from sqlalchemy import event # Para listeners de eventos


class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    celular = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    
    # Relacionamento: Um cliente pode ter vários veículos
    veiculos = db.relationship('Veiculo', backref='dono', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Cliente {self.nome}>'


class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=True)
    
    # Chave Estrangeira ligando ao Cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    # Relacionamento: Um veículo pode ter vários serviços/ordens de serviço
    servicos = db.relationship('Servico', backref='veiculo', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Veiculo {self.placa} - {self.modelo}>'

# Modelo de Associação para a relação muitos-para-muitos entre Servico e Peca
class ServicoPeca(db.Model):
    __tablename__ = 'servicos_pecas'
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), primary_key=True)
    peca_id = db.Column(db.Integer, db.ForeignKey('pecas.id'), primary_key=True)
    quantidade_usada = db.Column(db.Integer, nullable=False, default=1)
    preco_unitario_no_servico = db.Column(db.Numeric(10, 2), nullable=False) # Preço da peça no momento do serviço

    servico = db.relationship('Servico', backref=backref('pecas_associadas', cascade="all, delete-orphan"))
    peca = db.relationship('Peca', backref=backref('servicos_associados', cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<ServicoPeca Servico:{self.servico_id} Peca:{self.peca_id} Qtd:{self.quantidade_usada}>'

# Listener para quando uma ServicoPeca é adicionada, decrementa o estoque
@event.listens_for(ServicoPeca, 'after_insert')
def decrement_peca_estoque(mapper, connection, target):
    peca = Peca.query.get(target.peca_id)
    if peca:
        peca.quantidade_estoque -= target.quantidade_usada
        db.session.add(peca) # Adiciona a peça atualizada à sessão para commit

# Listener para quando uma ServicoPeca é excluída, incrementa o estoque
@event.listens_for(ServicoPeca, 'after_delete')
def increment_peca_estoque(mapper, connection, target):
    peca = Peca.query.get(target.peca_id)
    if peca:
        peca.quantidade_estoque += target.quantidade_usada
        db.session.add(peca) # Adiciona a peça atualizada à sessão para commit

class Servico(db.Model):
    __tablename__ = 'servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Chave Estrangeira ligando ao Veículo
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)

    # Relacionamento muitos-para-muitos com Peca através da tabela de associação ServicoPeca
    pecas = db.relationship('Peca', secondary='servicos_pecas', viewonly=True)

    def __repr__(self):
        return f'<Servico ID {self.id} - Valor {self.valor}>'

class Peca(db.Model):
    __tablename__ = 'pecas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco_custo = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    quantidade_estoque = db.Column(db.Integer, nullable=False, default=0)
    alerta_estoque_minimo = db.Column(db.Integer, nullable=False, default=5) # Nível para alertar estoque baixo

    def __repr__(self):
        return f'<Peca {self.nome} - Estoque: {self.quantidade_estoque}>'
