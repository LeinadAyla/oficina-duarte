from flask import render_template, request, redirect, url_for, jsonify, flash
from app import app, db
# Importa todos os modelos agora, incluindo Peca e ServicoPeca
from models import Cliente, Veiculo, Servico, Peca, ServicoPeca, Mecanico

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
    # Alertas de estoque (estoque atual <= mínimo configurado)
    alertas_estoque = db.session.query(Peca).filter(
        Peca.quantidade_estoque <= Peca.alerta_estoque_minimo
    ).count()

    # Faturamento bruto: apenas serviços concluídos/pagos
    faturamento_bruto = db.session.query(func.sum(Servico.valor)).filter(
        (Servico.pago.is_(True)) | (Servico.status == 'Concluído')
    ).scalar() or 0.00

    # Comissão: desconta com base na comissão percentual do mecânico
    mecanico_id = Servico.mecanico_id
    faturamento_comissoes = db.session.query(
        func.sum(Servico.valor * (Mecanico.comissao_percentual / 100.0))
    ).join(Mecanico, Mecanico.id == mecanico_id, isouter=True).filter(
        (Servico.pago.is_(True)) | (Servico.status == 'Concluído')
    ).scalar() or 0.00

    faturamento_liquido = faturamento_bruto - faturamento_comissoes

    return render_template(
        'dashboard.html',
        total_clientes=total_clientes,
        total_veiculos=total_veiculos,
        faturamento_bruto=faturamento_bruto,
        faturamento_comissoes=faturamento_comissoes,
        faturamento_liquido=faturamento_liquido,
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
        # Campos necessários para o modal de edição
        'status': servico.status,
        'pago': bool(servico.pago),
        'mecanico_id': servico.mecanico_id,
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
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
        return redirect(url_for('clientes'))

@app.route('/cliente/editar/<int:cliente_id>', methods=['POST'])
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    form = ClienteForm(obj=cliente)
    if form.validate_on_submit():
        form.populate_obj(cliente)
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
        return redirect(url_for('clientes'))

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
    if not form.tipo_propagacao.choices:
        form.tipo_propagacao.choices = [
            ('', 'Selecione...'),
            ('Híbrido', 'Híbrido'),
            ('100% Elétrico', '100% Elétrico'),
        ]

    if form.validate_on_submit():
        novo = Veiculo(
            placa=form.placa.data,
            marca=form.marca.data,
            modelo=form.modelo.data,
            ano=form.ano.data,
            quilometragem=form.quilometragem.data,
            tipo_propulsao=form.tipo_propagacao.data,
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
        return redirect(url_for('clientes'))

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
        return redirect(url_for('clientes'))

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
@app.route('/servico/novo/<int:veiculo_id>', methods=['GET', 'POST'])
def novo_servico(veiculo_id):
    form = ServicoForm()
    form.mecanico_id.choices = [(-1, 'Nenhum mecânico')] + [
        (m.id, f"{m.nome} ({m.especialidade}) - {m.comissao_percentual}%") for m in Mecanico.query.order_by(Mecanico.nome).all()
    ]
    if request.method == 'GET':
        return render_template('novo_servico.html', form=form, veiculo_id=veiculo_id)

    if form.validate_on_submit():
        pago_bool = True if form.pago.data == 'true' else False
        mecanico_id = None if form.mecanico_id.data in (None, -1) else form.mecanico_id.data
        novo = Servico(
            descricao=form.descricao.data,
            data=form.data.data,
            valor=form.valor.data,
            status=form.status.data,
            pago=pago_bool,
            mecanico_id=mecanico_id,
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

@app.route('/servicos')
def listar_servicos():
    servicos = Servico.query.order_by(Servico.data.desc()).all()
    return render_template('servicos.html', servicos=servicos)

@app.route('/servico/editar/<int:servico_id>', methods=['GET', 'POST'])
def editar_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    if request.method == 'GET':
        form = ServicoForm(obj=servico)
        form.mecanico_id.choices = [(-1, 'Nenhum mecânico')] + [
            (m.id, f"{m.nome} ({m.especialidade}) - {m.comissao_percentual}%") for m in Mecanico.query.order_by(Mecanico.nome).all()
        ]
        form.status.data = servico.status
        form.pago.data = 'true' if servico.pago else 'false'
        if servico.mecanico_id is None:
            form.mecanico_id.data = -1
        return render_template('editar_servico.html', form=form, servico_id=servico_id)

    form = ServicoForm(obj=servico)
    form.mecanico_id.choices = [(-1, 'Nenhum mecânico')] + [
        (m.id, f"{m.nome} ({m.especialidade}) - {m.comissao_percentual}%") for m in Mecanico.query.order_by(Mecanico.nome).all()
    ]
    form.status.data = servico.status
    form.pago.data = 'true' if servico.pago else 'false'
    if servico.mecanico_id is None:
        form.mecanico_id.data = -1
        
    if form.validate_on_submit():
        pago_bool = True if form.pago.data == 'true' else False
        mecanico_id = None if form.mecanico_id.data in (None, -1) else form.mecanico_id.data
        
        antes_concluido_ou_pago = (servico.status == 'Concluído') or (servico.pago is True)
        
        servico.descricao = form.descricao.data
        servico.data = form.data.data
        servico.valor = form.valor.data
        servico.status = form.status.data
        servico.pago = pago_bool
        servico.mecanico_id = mecanico_id
        
        depois_concluido_ou_pago = (servico.status == 'Concluído') or (servico.pago is True)
        try:
            if (not antes_concluido_ou_pago) and depois_concluido_ou_pago and not servico.bonus_aplicado:
                cliente = servico.veiculo.dono
                if cliente and cliente.elegivel_para_bonus():
                    servicos_disponiveis_bonuses = ['Troca de Óleo', 'Alinhamento', 'Lavagem a Seco']
                    indice = (cliente.id + servico.id) % len(servicos_disponiveis_bonuses)
                    servico.bonus_aplicado = servicos_disponiveis_bonuses[indice]
                    flash(f"Parabéns! Cliente elegível para bônus: {servico.bonus_aplicado}!", 'success')
            db.session.add(servico)
            db.session.commit()
            flash('Serviço updated com sucesso!', 'success')
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
#           ROTAS DE PEÇAS (ESTOQUE)
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
#             ROTAS DE MECÂNICOS
# ==========================================

@app.route('/mecanicos')
def mecanicos():
    mecanicos_list = Mecanico.query.order_by(Mecanico.nome).all()
    return render_template('mecanicos.html', mecanicos=mecanicos_list)

@app.route('/mecanicos/novo', methods=['POST'])
def novo_mecanico():
    nome = request.form.get('nome', '').strip()
    telefone = request.form.get('telefone', '').strip() or None
    especialidade = request.form.get('especialidade', '').strip() or None
    comissao_percentual_raw = request.form.get('comissao_percentual', '0').strip()

    try:
        comissao_percentual = float(comissao_percentual_raw)
    except ValueError:
        flash('Percentual de comissão inválido.', 'danger')
        return redirect(url_for('mecanicos'))

    novo = Mecanico(
        nome=nome,
        telefone=telefone,
        especialidade=especialidade,
        comissao_percentual=comissao_percentual,
    )
    try:
        db.session.add(novo)
        db.session.commit()
        flash('Mecânico cadastrado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar mecânico: {str(e)}', 'danger')
    return redirect(url_for('mecanicos'))

@app.route('/mecanicos/editar/<int:mecanico_id>', methods=['POST'])
def editar_mecanico(mecanico_id):
    mecanico = Mecanico.query.get_or_404(mecanico_id)
    mecanico.nome = request.form.get('nome', '').strip()
    mecanico.telefone = request.form.get('telefone', '').strip() or None
    mecanico.especialidade = request.form.get('especialidade', '').strip() or None
    comissao_percentual_raw = request.form.get('comissao_percentual', '0').strip()
    try:
        mecanico.comissao_percentual = float(comissao_percentual_raw)
    except ValueError:
        flash('Percentual de comissão inválido.', 'danger')
        return redirect(url_for('mecanicos'))

    try:
        db.session.add(mecanico)
        db.session.commit()
        flash('Mecânico atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar mecânico: {str(e)}', 'danger')
    return redirect(url_for('mecanicos'))

@app.route('/mecanicos/excluir/<int:mecanico_id>', methods=['POST'])
def excluir_mecanico(mecanico_id):
    mecanico = Mecanico.query.get_or_404(mecanico_id)
    try:
        db.session.delete(mecanico)
        db.session.commit()
        flash('Mecânico excluído com sucesso!', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir mecânico: {str(e)}', 'danger')
    return redirect(url_for('mecanicos'))

# ==========================================
#        AÇÕES DE PEÇAS EM SERVIÇOS
# ==========================================

@app.route('/veiculo/<int:veiculo_id>/servicos')
def ver_servicos_do_veiculo(veiculo_id):
    veiculo = Veiculo.query.get_or_404(veiculo_id)
    return render_template('servicos.html', veiculo=veiculo, servicos=veiculo.servicos)

@app.route('/servico/<int:servico_id>/peca/adicionar', methods=['POST'])
def adicionar_peca_ao_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    form = AdicionarPecaServicoForm()
    form.peca_id.choices = [(p.id, f"{p.nome} (Estoque: {p.quantidade_estoque})") for p in Peca.query.order_by(Peca.nome).all()]

    if form.validate_on_submit():
        peca_selecionada = Peca.query.get(form.peca_id.data)
        if not peca_selecionada:
            flash('Peça não encontrada.', 'danger')
            return redirect(url_for('clientes'))

        servico_peca_existente = ServicoPeca.query.filter_by(
            servico_id=servico_id,
            peca_id=form.peca_id.data
        ).first()

        if servico_peca_existente:
            flash('Esta peça já foi adicionada a este serviço. Edite-a se precisar alterar a quantidade.', 'warning')
        else:
            try:
                if peca_selecionada.quantidade_estoque < form.quantidade_usada.data:
                    raise ValueError(
                        f'Quantidade solicitada ({form.quantidade_usada.data}) excede o estoque disponível ({peca_selecionada.quantidade_estoque}).'
                    )
                nova_associacao = ServicoPeca(
                    servico_id=servico_id,
                    peca_id=form.peca_id.data,
                    quantidade_usada=form.quantidade_usada.data,
                    preco_unitario_no_servico=form.preco_unitario_no_servico.data
                )
                db.session.add(nova_associacao)
                peca_selecionada.quantidade_estoque -= form.quantidade_usada.data
                db.session.add(peca_selecionada)
                db.session.commit()
                flash('Peça adicionada ao serviço com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao adicionar peça ao serviço: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
    return redirect(url_for('clientes'))

@app.route('/servico/<int:servico_id>/peca/editar/<int:peca_id>', methods=['POST'])
def editar_peca_do_servico(servico_id, peca_id):
    servico_peca = ServicoPeca.query.filter_by(servico_id=servico_id, peca_id=peca_id).first_or_404()
    form = AdicionarPecaServicoForm()
    form.peca_id.choices = [(p.id, f"{p.nome} (Estoque: {p.quantidade_estoque})") for p in Peca.query.order_by(Peca.nome).all()]

    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
        return redirect(url_for('clientes'))

    quantidade_antiga = servico_peca.quantidade_usada
    quantidade_nova = form.quantidade_usada.data

    try:
        peca = Peca.query.get(peca_id)
        if not peca:
            raise ValueError('Peça não encontrada para atualização de estoque.')

        servico_peca.quantidade_usada = quantidade_nova
        servico_peca.preco_unitario_no_servico = form.preco_unitario_no_servico.data

        delta = quantidade_antiga - quantidade_nova
        peca.quantidade_estoque += delta

        if peca.quantidade_estoque < 0:
            raise ValueError('Estoque não pode ficar negativo.')

        db.session.add(peca)
        db.session.add(servico_peca)
        db.session.commit()
        flash('Peça no serviço atualizada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar peça no serviço: {str(e)}', 'danger')
    return redirect(url_for('clientes'))

@app.route('/servico/<int:servico_id>/peca/excluir/<int:peca_id>', methods=['POST'])
def excluir_peca_do_servico(servico_id, peca_id):
    servico_peca = ServicoPeca.query.filter_by(servico_id=servico_id, peca_id=peca_id).first_or_404()
    try:
        peca = Peca.query.get_or_404(peca_id)
        peca.quantidade_estoque += servico_peca.quantidade_usada
        if peca.quantidade_estoque < 0:
            raise ValueError('Estoque não pode ficar negativo.')

        db.session.add(peca)
        db.session.delete(servico_peca)
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