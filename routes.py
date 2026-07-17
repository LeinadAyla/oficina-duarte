from flask import render_template, request, redirect, url_for, jsonify, flash
from app import app, db
# Importa todos os modelos agora, incluindo Peca e ServicoPeca
from models import Cliente, Veiculo, Servico, Peca, ServicoPeca
# Importa todos os formulários, incluindo os novos
from forms import ClienteForm, VeiculoForm, ServicoForm, PecaForm, AdicionarPecaServicoForm
from datetime import datetime
from sqlalchemy import func # Para funções de agregação no dashboard

# ==========================================
#               ROTAS DO DASHBOARD
# ==========================================

@app.route('/')
def dashboard():
    total_clientes = Cliente.query.count()
    total_veiculos = Veiculo.query.count()
    faturamento_total = db.session.query(func.sum(Servico.valor)).scalar() or 0.00
    alertas_estoque = Peca.query.filter(Peca.quantidade_estoque <= Peca.alerta_estoque_minimo).count()

    return render_template(
        'dashboard.html',
        total_clientes=total_clientes,
        total_veiculos=total_veiculos,
        faturamento_total=faturamento_total,
        alertas_estoque=alertas_estoque
    )

# ==========================================
#               ROTAS DE CLIENTES
# ==========================================

@app.route('/clientes')
def clientes():
    clientes = Cliente.query.all()
    
    cliente_form = ClienteForm()
    veiculo_form = VeiculoForm()
    servico_form = ServicoForm()
    adicionar_peca_servico_form = AdicionarPecaServicoForm() # Instancia o formulário de peças para o serviço
    
    return render_template(
        'clientes.html', # Renomeado de index.html
        clientes=clientes,
        cliente_form=cliente_form,
        veiculo_form=veiculo_form,
        servico_form=servico_form,
        adicionar_peca_servico_form=adicionar_peca_servico_form
    )

# ==========================================
#          ENDPOINTS DA API (JSON)
# ==========================================

@app.route('/api/cliente/<int:cliente_id>', methods=['GET'])
def get_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return jsonify({
        'id': cliente.id,
        'nome': cliente.nome,
        'cpf': cliente.cpf,
        'celular': cliente.celular,
        'email': cliente.email
    })

@app.route('/api/veiculo/<int:veiculo_id>', methods=['GET'])
def get_veiculo(veiculo_id):
    veiculo = Veiculo.query.get_or_404(veiculo_id)
    return jsonify({
        'id': veiculo.id,
        'placa': veiculo.placa,
        'marca': veiculo.marca,
        'modelo': veiculo.modelo,
        'ano': veiculo.ano,
        'cliente_id': veiculo.cliente_id
    })

@app.route('/api/servico/<int:servico_id>', methods=['GET'])
def get_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    pecas_do_servico = []
    for sp in servico.pecas_associadas:
        pecas_do_servico.append({
            'servico_peca_id': f"{sp.servico_id}-{sp.peca_id}", # ID composto para identificação única
            'peca_id': sp.peca.id,
            'nome_peca': sp.peca.nome,
            'quantidade_usada': sp.quantidade_usada,
            'preco_unitario_no_servico': str(sp.preco_unitario_no_servico),
            'preco_venda_atual': str(sp.peca.preco_venda) # Preço atual da peça para referência
        })

    return jsonify({
        'id': servico.id,
        'descricao': servico.descricao,
        'data': servico.data.strftime('%Y-%m-%d') if servico.data else '',
        'valor': str(servico.valor),
        'veiculo_id': servico.veiculo_id,
        'pecas': pecas_do_servico
    })

@app.route('/api/peca/<int:peca_id>', methods=['GET'])
def get_peca(peca_id):
    peca = Peca.query.get_or_404(peca_id)
    return jsonify({
        'id': peca.id,
        'nome': peca.nome,
        'descricao': peca.descricao,
        'preco_custo': str(peca.preco_custo),
        'preco_venda': str(peca.preco_venda),
        'quantidade_estoque': peca.quantidade_estoque,
        'alerta_estoque_minimo': peca.alerta_estoque_minimo
    })

@app.route('/api/servico_peca/<int:servico_id>/<int:peca_id>', methods=['GET'])
def get_servico_peca(servico_id, peca_id):
    servico_peca = ServicoPeca.query.filter_by(servico_id=servico_id, peca_id=peca_id).first_or_404()
    return jsonify({
        'servico_id': servico_peca.servico_id,
        'peca_id': servico_peca.peca_id,
        'nome_peca': servico_peca.peca.nome,
        'quantidade_usada': servico_peca.quantidade_usada,
        'preco_unitario_no_servico': str(servico_peca.preco_unitario_no_servico)
    })

# ==========================================
#        AÇÕES CRUD (CRIAR/EDITAR/DELETAR)
# ==========================================

# --- AÇÕES DO CLIENTE ---
@app.route('/cliente/novo', methods=['POST'])
def novo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        novo = Cliente(
            nome=form.nome.data,
            cpf=form.cpf.data,
            celular=form.celular.data,
            email=form.email.data
        )
        try:
            db.session.add(novo)
            db.session.commit()
            flash('Cliente adicionado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar cliente: {str(e)}', 'danger')
        return redirect(url_for('clientes'))
    else:
        # Se a validação falhar, podemos querer retornar ao modal ou exibir erros.
        # Por simplicidade, vamos redirecionar e flashear os erros.
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
        return redirect(url_for('clientes'))


@app.route('/cliente/editar/<int:cliente_id>', methods=['POST'])
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    form = ClienteForm(obj=cliente) # Popula o formulário com dados do cliente existente
    if form.validate_on_submit():
        form.populate_obj(cliente) # Atualiza o objeto cliente com os dados do formulário
        try:
            db.session.commit()
            flash('Cliente atualizado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar cliente: {str(e)}', 'danger')
        return redirect(url_for('clientes'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
        return redirect(url_for('clientes')) # Redireciona de volta para a lista de clientes


@app.route('/cliente/excluir/<int:cliente_id>', methods=['POST'])
def excluir_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente excluído com sucesso!', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir cliente: {str(e)}', 'danger')
    return redirect(url_for('clientes'))

# --- AÇÕES DO VEÍCULO ---
@app.route('/veiculo/novo/<int:cliente_id>', methods=['POST'])
def novo_veiculo(cliente_id):
    form = VeiculoForm()
    if form.validate_on_submit():
        novo = Veiculo(
            placa=form.placa.data,
            marca=form.marca.data,
            modelo=form.modelo.data,
            ano=form.ano.data,
            cliente_id=cliente_id
        )
        try:
            db.session.add(novo)
            db.session.commit()
            flash('Veículo adicionado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar veículo: {str(e)}', 'danger')
        return redirect(url_for('clientes'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
        return redirect(url_for('clientes')) # Redireciona de volta para a lista de clientes


@app.route('/veiculo/editar/<int:veiculo_id>', methods=['POST'])
def editar_veiculo(veiculo_id):
    veiculo = Veiculo.query.get_or_404(veiculo_id)
    form = VeiculoForm(obj=veiculo)
    if form.validate_on_submit():
        form.populate_obj(veiculo)
        try:
            db.session.commit()
            flash('Veículo atualizado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar veículo: {str(e)}', 'danger')
        return redirect(url_for('clientes'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
        return redirect(url_for('clientes')) # Redireciona de volta para a lista de clientes


@app.route('/veiculo/excluir/<int:veiculo_id>', methods=['POST'])
def excluir_veiculo(veiculo_id):
    veiculo = Veiculo.query.get_or_404(veiculo_id)
    try:
        db.session.delete(veiculo)
        db.session.commit()
        flash('Veículo excluído com sucesso!', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir veículo: {str(e)}', 'danger')
    return redirect(url_for('clientes'))

# --- AÇÕES DO SERVIÇO ---
@app.route('/servico/novo/<int:veiculo_id>', methods=['POST'])
def novo_servico(veiculo_id):
    form = ServicoForm()
    if form.validate_on_submit():
        novo = Servico(
            descricao=form.descricao.data,
            data=form.data.data,
            valor=form.valor.data,
            veiculo_id=veiculo_id
        )
        try:
            db.session.add(novo)
            db.session.commit()
            flash('Serviço adicionado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar serviço: {str(e)}', 'danger')
        return redirect(url_for('clientes'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
        return redirect(url_for('clientes'))


@app.route('/servico/editar/<int:servico_id>', methods=['POST'])
def editar_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    form = ServicoForm(obj=servico)
    if form.validate_on_submit():
        form.populate_obj(servico)
        try:
            db.session.commit()
            flash('Serviço atualizado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar serviço: {str(e)}', 'danger')
        return redirect(url_for('clientes'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
        return redirect(url_for('clientes'))


@app.route('/servico/excluir/<int:servico_id>', methods=['POST'])
def excluir_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    try:
        db.session.delete(servico)
        db.session.commit()
        flash('Serviço excluído com sucesso!', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir serviço: {str(e)}', 'danger')
    return redirect(url_for('clientes'))

# ==========================================
#               ROTAS DE PEÇAS (ESTOQUE)
# ==========================================

@app.route('/pecas')
def pecas():
    pecas = Peca.query.order_by(Peca.nome).all()
    peca_form = PecaForm()
    return render_template('pecas.html', pecas=pecas, peca_form=peca_form)

@app.route('/pecas/novo', methods=['POST'])
def nova_peca():
    form = PecaForm()
    if form.validate_on_submit():
        novo_peca = Peca(
            nome=form.nome.data,
            descricao=form.descricao.data,
            preco_custo=form.preco_custo.data,
            preco_venda=form.preco_venda.data,
            quantidade_estoque=form.quantidade_estoque.data,
            alerta_estoque_minimo=form.alerta_estoque_minimo.data
        )
        try:
            db.session.add(novo_peca)
            db.session.commit()
            flash('Peça adicionada ao estoque com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar peça: {str(e)}', 'danger')
        return redirect(url_for('pecas'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
        return redirect(url_for('pecas'))

@app.route('/pecas/editar/<int:peca_id>', methods=['POST'])
def editar_peca(peca_id):
    peca = Peca.query.get_or_404(peca_id)
    form = PecaForm(obj=peca)
    if form.validate_on_submit():
        form.populate_obj(peca)
        try:
            db.session.commit()
            flash('Peça atualizada com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar peça: {str(e)}', 'danger')
        return redirect(url_for('pecas'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
        return redirect(url_for('pecas'))

@app.route('/pecas/excluir/<int:peca_id>', methods=['POST'])
def excluir_peca(peca_id):
    peca = Peca.query.get_or_404(peca_id)
    try:
        db.session.delete(peca)
        db.session.commit()
        flash('Peça excluída com sucesso!', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir peça: {str(e)}', 'danger')
    return redirect(url_for('pecas'))

# ==========================================
#          AÇÕES DE PEÇAS EM SERVIÇOS
# ==========================================

@app.route('/servico/<int:servico_id>/peca/adicionar', methods=['POST'])
def adicionar_peca_ao_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    form = AdicionarPecaServicoForm()
    # Para o SelectField do formulário, precisamos popular as opções de peças
    form.peca_id.choices = [(p.id, f"{p.nome} (Estoque: {p.quantidade_estoque})") for p in Peca.query.order_by(Peca.nome).all()]

    if form.validate_on_submit():
        peca_selecionada = Peca.query.get(form.peca_id.data)
        if not peca_selecionada:
            flash('Peça não encontrada.', 'danger')
            return redirect(url_for('clientes'))

        # Verifica se a peça já está no serviço
        servico_peca_existente = ServicoPeca.query.filter_by(
            servico_id=servico_id,
            peca_id=form.peca_id.data
        ).first()

        if servico_peca_existente:
            flash('Esta peça já foi adicionada a este serviço. Edite-a se precisar alterar a quantidade.', 'warning')
        else:
            try:
                nova_associacao = ServicoPeca(
                    servico_id=servico_id,
                    peca_id=form.peca_id.data,
                    quantidade_usada=form.quantidade_usada.data,
                    preco_unitario_no_servico=form.preco_unitario_no_servico.data
                )
                db.session.add(nova_associacao)
                # O listener 'after_insert' em models.py cuidará de decrementar o estoque da peça
                db.session.commit()
                flash('Peça adicionada ao serviço com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao adicionar peça ao serviço: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
    
    return redirect(url_for('clientes')) # Sempre redireciona para a página de clientes após a ação


@app.route('/servico/<int:servico_id>/peca/editar/<int:peca_id>', methods=['POST'])
def editar_peca_do_servico(servico_id, peca_id):
    servico_peca = ServicoPeca.query.filter_by(servico_id=servico_id, peca_id=peca_id).first_or_404()
    
    # Criamos o formulário. O WTForms lerá automaticamente o request.form se a requisição for POST.
    form = AdicionarPecaServicoForm()
    
    # Populamos o SelectField dinamicamente antes do validate_on_submit()
    form.peca_id.choices = [(p.id, f"{p.nome} (Estoque: {p.quantidade_estoque})") for p in Peca.query.order_by(Peca.nome).all()]
    
    # Executa a validação se for uma requisição POST
    if form.validate_on_submit():
        quantidade_antiga = servico_peca.quantidade_usada # Guarda a quantidade antiga para ajuste de estoque
        
        # Como é uma edição, o peca_id é parte do ID composto e não é alterado. Atualizamos apenas quantidade e preço.
        servico_peca.quantidade_usada = form.quantidade_usada.data
        servico_peca.preco_unitario_no_servico = form.preco_unitario_no_servico.data

        try:
            # Ajusta o estoque da peça manualmente antes do commit para refletir a mudança
            peca = Peca.query.get(peca_id)
            if peca:
                diferenca = quantidade_antiga - servico_peca.quantidade_usada
                peca.quantidade_estoque += diferenca
                db.session.add(peca) # Adiciona a peça atualizada à sessão

            db.session.commit()
            flash('Peça no serviço atualizada com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar peça no serviço: {str(e)}', 'danger')
    else:
        # Se for um GET ou a validação falhar, podemos exibir os erros do formulário
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
    
    return redirect(url_for('clientes'))


@app.route('/servico/<int:servico_id>/peca/excluir/<int:peca_id>', methods=['POST'])
def excluir_peca_do_servico(servico_id, peca_id):
    servico_peca = ServicoPeca.query.filter_by(servico_id=servico_id, peca_id=peca_id).first_or_404()
    try:
        db.session.delete(servico_peca)
        # O listener 'after_delete' em models.py cuidará de incrementar o estoque da peça
        db.session.commit()
        flash('Peça removida do serviço com sucesso!', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover peça do serviço: {str(e)}', 'danger')
    return redirect(url_for('clientes'))

# Endpoint para fornecer opções de peças para SelectField de forma dinâmica
@app.route('/api/pecas_choices', methods=['GET'])
def get_pecas_choices():
    pecas = Peca.query.order_by(Peca.nome).all()
    choices = [(p.id, f"{p.nome} (Estoque: {p.quantidade_estoque})") for p in pecas]
    return jsonify(choices)