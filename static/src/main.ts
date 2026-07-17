document.addEventListener('DOMContentLoaded', () => {
    // Carrega o Font Awesome para os ícones, como o do WhatsApp
    const fontAwesomeLink = document.createElement('link');
    fontAwesomeLink.rel = 'stylesheet';
    fontAwesomeLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
    document.head.appendChild(fontAwesomeLink);

    const clienteModal = document.getElementById('clienteModal');
    const veiculoModal = document.getElementById('veiculoModal');
    const servicoModal = document.getElementById('servicoModal');
    const confirmDeleteModal = document.getElementById('confirmDeleteModal');

    // Função para limpar os formulários antes de abrir um modal de "novo"
    function clearForm(formId: string) {
        const form = document.getElementById(formId) as HTMLFormElement;
        if (form) {
            form.reset();
            // Limpa campos ocultos de ID
            const idField = form.querySelector('input[name="id"]') as HTMLInputElement;
            if (idField) idField.value = '';
            // Limpa campos ocultos de relacionamento
            const clienteIdField = form.querySelector('input[name="cliente_id"]') as HTMLInputElement;
            if (clienteIdField) clienteIdField.value = '';
            const veiculoIdField = form.querySelector('input[name="veiculo_id"]') as HTMLInputElement;
            if (veiculoIdField) veiculoIdField.value = '';

            // Limpar mensagens de erro
            form.querySelectorAll('.text-danger').forEach(el => el.remove());
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        }
    }

    // Modal Cliente
    if (clienteModal) {
        clienteModal.addEventListener('show.bs.modal', async (event) => {
            const button = (event.relatedTarget as HTMLElement);
            const action = button.getAttribute('data-action');
            const modalTitle = clienteModal.querySelector('.modal-title') as HTMLElement;
            const form = clienteModal.querySelector('#clienteForm') as HTMLFormElement;
            const submitButton = form.querySelector('input[type="submit"]') as HTMLInputElement;
            const clienteIdField = form.querySelector('#cliente_id_field') as HTMLInputElement;

            clearForm('clienteForm');

            if (action === 'new') {
                modalTitle.textContent = 'Novo Cliente';
                form.action = '{{ url_for("novo_cliente") }}';
                submitButton.value = 'Salvar Cliente';
            } else if (action === 'edit') {
                modalTitle.textContent = 'Editar Cliente';
                submitButton.value = 'Atualizar Cliente';
                const clientId = button.getAttribute('data-id');
                form.action = `{{ url_for("editar_cliente", cliente_id=0) }}`.replace('0', clientId || '');
                clienteIdField.value = clientId || '';

                if (clientId) {
                    try {
                        const response = await fetch(`/api/cliente/${clientId}`);
                        const data = await response.json();
                        (form.elements.namedItem('nome') as HTMLInputElement).value = data.nome;
                        (form.elements.namedItem('cpf') as HTMLInputElement).value = data.cpf;
                        (form.elements.namedItem('celular') as HTMLInputElement).value = data.celular;
                        (form.elements.namedItem('email') as HTMLInputElement).value = data.email;
                    } catch (error) {
                        console.error('Erro ao buscar dados do cliente:', error);
                    }
                }
            }
        });
    }

    // Modal Veículo
    if (veiculoModal) {
        veiculoModal.addEventListener('show.bs.modal', async (event) => {
            const button = (event.relatedTarget as HTMLElement);
            const action = button.getAttribute('data-action');
            const modalTitle = veiculoModal.querySelector('.modal-title') as HTMLElement;
            const form = veiculoModal.querySelector('#veiculoForm') as HTMLFormElement;
            const submitButton = form.querySelector('input[type="submit"]') as HTMLInputElement;
            const veiculoIdField = form.querySelector('#veiculo_id_field') as HTMLInputElement;
            const clienteIdField = form.querySelector('#veiculo_cliente_id_field') as HTMLInputElement;

            clearForm('veiculoForm');

            if (action === 'new') {
                modalTitle.textContent = 'Novo Veículo';
                submitButton.value = 'Salvar Veículo';
                const clienteId = button.getAttribute('data-cliente-id');
                form.action = `{{ url_for("novo_veiculo", cliente_id=0) }}`.replace('0', clienteId || '');
                clienteIdField.value = clienteId || '';
            } else if (action === 'edit') {
                modalTitle.textContent = 'Editar Veículo';
                submitButton.value = 'Atualizar Veículo';
                const veiculoId = button.getAttribute('data-id');
                form.action = `{{ url_for("editar_veiculo", veiculo_id=0) }}`.replace('0', veiculoId || '');
                veiculoIdField.value = veiculoId || '';

                if (veiculoId) {
                    try {
                        const response = await fetch(`/api/veiculo/${veiculoId}`);
                        const data = await response.json();
                        (form.elements.namedItem('placa') as HTMLInputElement).value = data.placa;
                        (form.elements.namedItem('marca') as HTMLInputElement).value = data.marca;
                        (form.elements.namedItem('modelo') as HTMLInputElement).value = data.modelo;
                        (form.elements.namedItem('ano') as HTMLInputElement).value = data.ano;
                        clienteIdField.value = data.cliente_id;
                    } catch (error) {
                        console.error('Erro ao buscar dados do veículo:', error);
                    }
                }
            }
        });
    }

    // Modal Serviço
    if (servicoModal) {
        servicoModal.addEventListener('show.bs.modal', async (event) => {
            const button = (event.relatedTarget as HTMLElement);
            const action = button.getAttribute('data-action');
            const modalTitle = servicoModal.querySelector('.modal-title') as HTMLElement;
            const form = servicoModal.querySelector('#servicoForm') as HTMLFormElement;
            const submitButton = form.querySelector('input[type="submit"]') as HTMLInputElement;
            const servicoIdField = form.querySelector('#servico_id_field') as HTMLInputElement;
            const veiculoIdField = form.querySelector('#servico_veiculo_id_field') as HTMLInputElement;

            clearForm('servicoForm');

            if (action === 'new') {
                modalTitle.textContent = 'Novo Serviço';
                submitButton.value = 'Salvar Serviço';
                const veiculoId = button.getAttribute('data-veiculo-id');
                form.action = `{{ url_for("novo_servico", veiculo_id=0) }}`.replace('0', veiculoId || '');
                veiculoIdField.value = veiculoId || '';
            } else if (action === 'edit') {
                modalTitle.textContent = 'Editar Serviço';
                submitButton.value = 'Atualizar Serviço';
                const servicoId = button.getAttribute('data-id');
                form.action = `{{ url_for("editar_servico", servico_id=0) }}`.replace('0', servicoId || '');
                servicoIdField.value = servicoId || '';

                if (servicoId) {
                    try {
                        const response = await fetch(`/api/servico/${servicoId}`);
                        const data = await response.json();
                        (form.elements.namedItem('descricao') as HTMLTextAreaElement).value = data.descricao;
                        (form.elements.namedItem('data') as HTMLInputElement).value = data.data;
                        (form.elements.namedItem('valor') as HTMLInputElement).value = data.valor;
                        veiculoIdField.value = data.veiculo_id;
                    } catch (error) {
                        console.error('Erro ao buscar dados do serviço:', error);
                    }
                }
            }
        });
    }

    // Modal de Confirmação de Exclusão
    if (confirmDeleteModal) {
        confirmDeleteModal.addEventListener('show.bs.modal', (event) => {
            const button = (event.relatedTarget as HTMLElement);
            const itemId = button.getAttribute('data-id');
            const itemType = button.getAttribute('data-type');
            const itemName = button.getAttribute('data-nome');
            const deleteItemNameElement = confirmDeleteModal.querySelector('#deleteItemName') as HTMLElement;
            const deleteForm = confirmDeleteModal.querySelector('#deleteForm') as HTMLFormElement;

            deleteItemNameElement.textContent = itemName;

            if (itemType === 'cliente') {
                deleteForm.action = `{{ url_for("excluir_cliente", cliente_id=0) }}`.replace('0', itemId || '');
            } else if (itemType === 'veiculo') {
                deleteForm.action = `{{ url_for("excluir_veiculo", veiculo_id=0) }}`.replace('0', itemId || '');
            } else if (itemType === 'servico') {
                deleteForm.action = `{{ url_for("excluir_servico", servico_id=0) }}`.replace('0', itemId || '');
            }
        });
    }
});