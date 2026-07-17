# Sistema de Gestão para Oficina de Veículos

Este projeto implementa um sistema web completo para gestão de clientes, veículos e serviços de uma oficina, utilizando Flask, SQLite e TypeScript.

## Funcionalidades

*   **Clientes:** Cadastro, edição e exclusão de clientes, com validação de CPF e email.
*   **Veículos:** Cadastro, edição e exclusão de veículos associados a clientes, com validação de placa.
*   **Serviços:** Cadastro, edição e exclusão de serviços associados a veículos.
*   **Interface:** Layout responsivo com Bootstrap 5 e modais interativos para as operações de CRUD.
*   **Seção Especial:** Destaque para o profissional Duarte, especialista em veículos híbridos e elétricos BYD, com botão de contato via WhatsApp.
*   **Banco de Dados:** SQLite para armazenamento de dados, gerenciado com Flask-SQLAlchemy e Flask-Migrate para migrações.
*   **TypeScript:** Código TypeScript para interações de frontend, compilado para JavaScript.

## Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

*   **Python 3.8+**
*   **pip** (gerenciador de pacotes Python)
*   **Node.js** (LTS recomendado)
*   **npm** (gerenciador de pacotes Node.js, vem com Node.js)
*   **TypeScript** (instalado globalmente)

## Configuração do Ambiente

Siga os passos abaixo para configurar e executar o projeto.

### 1. Clonar o Repositório (se aplicável)

```bash
# Se você tiver um repositório, use:
# git clone <URL_DO_SEU_REPOSITORIO>
# cd <NOME_DO_DIRETORIO>
```
Se você criou os arquivos manualmente seguindo as instruções, você já está no diretório correto.

### 2. Instalar Dependências Python

Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv venv
# No Windows
.\venv\Scripts\activate
# No macOS/Linux
source venv/bin/activate
```

Instale as dependências Python usando o `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Instalar TypeScript Globalmente (se ainda não o fez)

```bash
npm install -g typescript
```

### 4. Instalar Dependências JavaScript/TypeScript

Instale as dependências definidas no `package.json` (apenas `typescript` para `devDependencies` neste caso):

```bash
npm install
```

### 5. Compilar TypeScript

Compile o arquivo TypeScript para JavaScript. Isso criará `main.js` na pasta `static/dist`.

```bash
npm run build
```

### 6. Configurar o Banco de Dados com Flask-Migrate

O Flask-Migrate é usado para gerenciar as migrações do banco de dados.

```bash
# Inicializa o ambiente de migrações (apenas na primeira vez)
flask db init

# Cria uma migração inicial baseada nos modelos (execute após criar/modificar modelos)
flask db migrate -m "Initial migration"

# Aplica as migrações ao banco de dados (cria o arquivo site.db)
flask db upgrade
```
**Nota:** Sempre que você fizer alterações nos modelos (`models.py`), execute `flask db migrate -m "Descrição da sua alteração"` e depois `flask db upgrade`.

### 7. Variável de Ambiente `SECRET_KEY`

O Flask exige uma `SECRET_KEY`. Para desenvolvimento, você pode defini-la temporariamente no ambiente ou usar um arquivo `.env`.

Crie um arquivo `.env` na raiz do projeto:

```
SECRET_KEY='sua_chave_secreta_aqui_para_desenvolvimento'
```
Substitua `'sua_chave_secreta_aqui_para_desenvolvimento'` por uma string longa e aleatória. **Para produção, use uma chave realmente forte e segura.**

### 8. Executar a Aplicação Flask

Execute a aplicação Flask:

```bash
flask run
```

A aplicação estará disponível em `http://127.0.0.1:5000/` (ou outra porta indicada no console).

## Estrutura do Projeto

```
.
├── app.py                  # Inicializa a aplicação Flask, SQLAlchemy e Migrate.
├── models.py               # Define os modelos de banco de dados (Cliente, Veiculo, Servico).
├── forms.py                # Define os formulários Flask-WTF com validações.
├── routes.py               # Contém as rotas da aplicação (CRUD de clientes, veículos, serviços).
├── requirements.txt        # Lista de dependências Python.
├── package.json            # Configuração do projeto Node/npm e script de build TypeScript.
├── README.md               # Este arquivo.
├── venv/                   # Ambiente virtual Python.
├── migrations/             # Gerenciado por Flask-Migrate.
├── site.db                 # Banco de dados SQLite (gerado após db upgrade).
├── templates/
│   ├── base.html           # Layout base com Bootstrap 5 e navbar.
│   └── index.html          # Página principal com listagem, seção Duarte e modais de CRUD.
└── static/
    ├── css/
    │   └── style.css       # Estilos CSS customizados.
    ├── src/
    │   └── main.ts         # Código TypeScript para interações de frontend (modais).
    └── dist/
        └── main.js         # Saída compilada do main.ts.
```

## Como Usar

1.  Acesse a URL `http://127.0.0.1:5000/` no seu navegador.
2.  Use o botão "Novo Cliente" na barra de navegação para adicionar novos clientes.
3.  Na listagem de clientes, você pode "Editar Cliente" ou "Excluir Cliente".
4.  Para cada cliente, é possível adicionar, editar e excluir veículos.
5.  Para cada veículo, é possível adicionar, editar e excluir serviços.
6.  Os formulários de cadastro e edição são exibidos em modais.
7.  A seção especial "Duarte" na página inicial permite um contato direto via WhatsApp.

---
Desenvolvido por [Seu Nome]
Data: 2026-07-16
