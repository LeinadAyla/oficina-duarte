from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, ValidationError
from datetime import datetime # Importar datetime para validação de ano
from models import Peca # Importar Peca para o SelectField de peças

# Validadores personalizados
def validate_cpf(form, field):
    cpf = field.data.replace('.', '').replace('-', '')
    if not cpf.isdigit() or len(cpf) != 11:
        raise ValidationError('CPF deve conter 11 dígitos numéricos.')

def validate_placa(form, field):
    placa = field.data
    # Ex: ABC-1234 (Mercosul antiga) ou ABC1D23 (Mercosul nova)
    if not (len(placa) == 8 and placa[3] == '-' and placa[:3].isalpha() and placa[4:].isdigit()) and \
       not (len(placa) == 7 and placa[:3].isalpha() and placa[3].isdigit() and placa[4].isalpha() and placa[5:].isdigit()):
        raise ValidationError('Formato de placa inválido (ex: AAA-0000 ou AAA0A00).')

class ClienteForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired("O nome é obrigatório."), Length(max=100, message="O nome deve ter no máximo 100 caracteres.")])
    cpf = StringField('CPF', validators=[DataRequired("O CPF é obrigatório."), Length(min=11, max=14, message="O CPF deve ter entre 11 e 14 caracteres."), validate_cpf])
    celular = StringField('Celular', validators=[Optional(), Length(max=15, message="O celular deve ter no máximo 15 caracteres.")])
    email = StringField('E-mail', validators=[Optional(), Email("Formato de e-mail inválido."), Length(max=100, message="O e-mail deve ter no máximo 100 caracteres.")])
    submit = SubmitField('Salvar Cliente')

class VeiculoForm(FlaskForm):
    placa = StringField('Placa', validators=[DataRequired("A placa é obrigatória."), Length(min=7, max=8, message="A placa deve ter entre 7 e 8 caracteres."), validate_placa])
    marca = StringField('Marca', validators=[DataRequired("A marca é obrigatória."), Length(max=50, message="A marca deve ter no máximo 50 caracteres.")])
    modelo = StringField('Modelo', validators=[DataRequired("O modelo é obrigatório."), Length(max=50, message="O modelo deve ter no máximo 50 caracteres.")])
    ano = IntegerField('Ano (opcional)', validators=[Optional(), NumberRange(min=1900, max=datetime.now().year + 1, message="Ano inválido.")])
    submit = SubmitField('Salvar Veículo')

class ServicoForm(FlaskForm):
    descricao = TextAreaField('Descrição do Serviço', validators=[DataRequired("A descrição é obrigatória.")])
    data = DateField('Data', validators=[DataRequired("A data é obrigatória.")], format='%Y-%m-%d')
    valor = DecimalField('Valor (R$)', validators=[DataRequired("O valor é obrigatório."), NumberRange(min=0.01, message="O valor deve ser maior que zero.")])
    submit = SubmitField('Salvar Serviço')

class PecaForm(FlaskForm):
    nome = StringField('Nome da Peça', validators=[DataRequired("O nome da peça é obrigatório."), Length(max=100, message="O nome deve ter no máximo 100 caracteres.")])
    descricao = TextAreaField('Descrição', validators=[Optional(), Length(max=500, message="A descrição deve ter no máximo 500 caracteres.")])
    preco_custo = DecimalField('Preço de Custo (R$)', validators=[DataRequired("O preço de custo é obrigatório."), NumberRange(min=0.00, message="O preço de custo não pode ser negativo.")])
    preco_venda = DecimalField('Preço de Venda (R$)', validators=[DataRequired("O preço de venda é obrigatório."), NumberRange(min=0.01, message="O preço de venda deve ser maior que zero.")])
    quantidade_estoque = IntegerField('Quantidade em Estoque', validators=[DataRequired("A quantidade em estoque é obrigatória."), NumberRange(min=0, message="A quantidade em estoque não pode ser negativa.")])
    alerta_estoque_minimo = IntegerField('Alerta de Estoque Mínimo', validators=[DataRequired("O nível de alerta é obrigatório."), NumberRange(min=0, message="O nível de alerta não pode ser negativo.")])
    submit = SubmitField('Salvar Peça')

class AdicionarPecaServicoForm(FlaskForm):
    peca_id = SelectField('Selecione a Peça', coerce=int, validators=[DataRequired("Selecione uma peça.")])
    quantidade_usada = IntegerField('Quantidade Usada', validators=[DataRequired("A quantidade é obrigatória."), NumberRange(min=1, message="A quantidade deve ser de pelo menos 1.")])
    preco_unitario_no_servico = DecimalField('Preço Unitário (R$)', validators=[DataRequired("O preço unitário é obrigatório."), NumberRange(min=0.01, message="O preço unitário deve ser maior que zero.")])
    submit = SubmitField('Adicionar Peça ao Serviço')

    def __init__(self, *args, **kwargs):
        super(AdicionarPecaServicoForm, self).__init__(*args, **kwargs)
        # Popula as escolhas do SelectField com as peças disponíveis
        self.peca_id.choices = [(p.id, f"{p.nome} (Estoque: {p.quantidade_estoque})") for p in Peca.query.order_by(Peca.nome).all()]
        if not self.peca_id.choices:
            self.peca_id.choices = [(0, 'Nenhuma peça disponível')] # Prevenir erro se não houver peças
            self.peca_id.data = 0 # Define um valor padrão se não houver opções
            self.peca_id.render_kw = {"disabled": "disabled"} # Desabilitar o campo se não houver opções

    def validate_quantidade_usada(self, field):
        peca = Peca.query.get(self.peca_id.data)
        if peca and field.data > peca.quantidade_estoque:
            raise ValidationError(f'Quantidade solicitada ({field.data}) excede o estoque disponível ({peca.quantidade_estoque}).')
