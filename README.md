# Raízes do Nordeste API

API REST para a rede de lanchonetes **Raízes do Nordeste**, desenvolvida como projeto multidisciplinar da trilha Back-End (UNINTER 2026).

A solução gerencia múltiplos canais de venda (APP, TOTEM, BALCÃO, PICKUP, WEB), controle de estoque por unidade, programa de fidelidade compatível com LGPD e integração simulada de pagamento.

Link do repositório: <https://github.com/davipferr/raizes-nordeste-api>

---

## Tecnologias

| Camada         | Tecnologia        |
|----------------|-------------------|
| Linguagem      | Python 3.11+      |
| Framework      | FastAPI 0.115     |
| Banco de dados | PostgreSQL 14+    |
| ORM            | SQLAlchemy 2.0    |
| Migrations     | Alembic 1.14      |
| Autenticação   | JWT (python-jose) |
| Hash de senha  | bcrypt (passlib)  |
| Validação      | Pydantic v2       |
| Servidor       | Uvicorn           |
| Testes         | Pytest + httpx    |

---

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.11 ou superior** — verificar com `python --version`
- **PostgreSQL 14 ou superior** — verificar com `psql --version`

Caso não tenha alguma dessas ferramentas instaladas, siga os passos abaixo.

### Instalando o Python 3.11+

**Windows:**

1. Acesse <https://www.python.org/downloads/> e baixe o instalador da versão mais recente do Python 3.11 ou superior, na aba **Downloads** -> **All releases**.
2. Execute o instalador. **Importante:** marque a opção **"Add Python to PATH"** antes de clicar em *Install Now*.
3. Após a instalação, abra o terminal (PowerShell ou CMD) e verifique:

```bash
python --version
```

> Se o comando não for reconhecido, reinicie o terminal ou o computador e tente novamente.

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y
python3.11 --version
```

**macOS:**

```bash
brew install python@3.11
python3 --version
```

> Se não tiver o Homebrew instalado, acesse <https://brew.sh/> e siga as instruções.

---

### Instalando o PostgreSQL 14+

**Windows:**

1. Acesse <https://www.enterprisedb.com/downloads/postgres-postgresql-downloads/> e baixe o instalador do PostgreSQL 14 ou superior.
2. Execute o instalador e siga as etapas. Anote a **senha do usuário `postgres`** que você definir — ela será usada na configuração do `.env`.
3. Na etapa de componentes, mantenha selecionados pelo menos: *PostgreSQL Server* e *Command Line Tools*.
4. Ao final, o instalador perguntará se deseja executar o *Stack Builder* — pode cancelar.
5. Caso os comandos `psql` e `createdb` não sejam reconhecidos no terminal, adicione o diretório `bin` do PostgreSQL ao PATH do sistema (normalmente `C:\Program Files\PostgreSQL\14\bin`).

   **Como adicionar ao PATH no Windows:**
   1. Pressione `Win + R`, digite `sysdm.cpl` e pressione Enter.
   2. Vá na aba **Avançado** → clique em **Variáveis de Ambiente**.
   3. Na seção **Variáveis do sistema**, selecione a variável **Path** e clique em **Editar**.
   4. Clique em **Novo** e adicione o caminho `C:\Program Files\PostgreSQL\14\bin` (ajuste o número `14` para a versão instalada).
   5. Clique em **OK** em todas as janelas abertas.
   6. Feche e reabra o terminal para as alterações surtirem efeito.

6. Verifique a instalação:

```bash
psql --version
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
psql --version
```

Para acessar o PostgreSQL e definir a senha do usuário `postgres`:

```bash
sudo -u postgres psql
ALTER USER postgres PASSWORD 'sua_senha';
\q
```

**macOS:**

```bash
brew install postgresql@14
brew services start postgresql@14
psql --version
```

---

## Instalação passo a passo

### 1. Clonar o repositório

```bash
git clone https://github.com/davipferr/raizes-nordeste-api
cd raizes-nordeste-api
```

### 2. Criar e ativar o ambiente virtual

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

## Configuração das variáveis de ambiente

### 3.1 Copiar o arquivo de exemplo

```bash
cp .env.example .env
```

### 3.2 Editar o arquivo `.env`

Abra o arquivo `.env` e preencha os valores:

```env
# URL de conexão com o banco de dados principal
DATABASE_URL=postgresql://usuario:senha@localhost:5432/raizes_nordeste

# URL de conexão com o banco de dados de testes (banco separado)
DATABASE_TEST_URL=postgresql://usuario:senha@localhost:5432/raizes_nordeste_teste

# Chave secreta para geração dos tokens JWT
# Use uma string aleatória e longa (mínimo 32 caracteres)
CHAVE_SECRETA_JWT=troque_por_uma_chave_segura_de_32_caracteres_minimo

# Algoritmo de assinatura do JWT (não alterar)
ALGORITMO_JWT=HS256

# Tempo de expiração do token em minutos
MINUTOS_EXPIRACAO_TOKEN=60

# Ambiente de execução
AMBIENTE=desenvolvimento
```

**Exemplo com usuário padrão do PostgreSQL:**

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/raizes_nordeste
DATABASE_TEST_URL=postgresql://postgres:postgres@localhost:5432/raizes_nordeste_teste
CHAVE_SECRETA_JWT=minha-chave-super-secreta-para-o-projeto-raizes-nordeste
ALGORITMO_JWT=HS256
MINUTOS_EXPIRACAO_TOKEN=60
AMBIENTE=desenvolvimento
```

---

## Banco de dados

### 4. Criar os bancos no PostgreSQL

Acesse o psql pelo terminal e execute os comandos abaixo:

**Windows:**

```bash
psql -U postgres
# Será solicitada a senha definida durante a instalação do PostgreSQL, aperte enter para confirmar a senha
```

**Linux/macOS:**

```bash
sudo -u postgres psql
# No Linux/macOS a autenticação é feita pelo sistema operacional, sem necessidade de senha
```

Dentro do psql, execute:

```sql
CREATE DATABASE raizes_nordeste;
CREATE DATABASE raizes_nordeste_teste;
\q
```

> `\q` é o comando para sair do psql e voltar ao terminal.

### 5. Executar as migrations

> **Lembrete:** Certifique-se de que o ambiente virtual está ativado antes de continuar (veja o passo 2).

As migrations criam todas as tabelas e tipos ENUM **apenas no banco principal** (`DATABASE_URL`):

```bash
alembic upgrade head
```

> **Windows:** Se o comando acima for bloqueado por política de segurança do sistema, use a alternativa abaixo — ela tem o mesmo efeito:
>
> ```bash
> python -m alembic upgrade head
> ```

Saída esperada:

```bash
INFO  [alembic.runtime.migration] Running upgrade  -> 001, criar tabelas iniciais
```

> **Nota:** O banco de testes (`DATABASE_TEST_URL`) é criado e populado automaticamente pelo pytest — as migrations não precisam ser executadas nele.

### 6. Popular com dados iniciais (seed)

> **Lembrete:** Certifique-se de que o ambiente virtual está ativado antes de continuar (veja o passo 2).

O seed insere dados de demonstração **apenas no banco principal** (`DATABASE_URL`): 2 unidades, 6 produtos nordestinos, 6 usuários com perfis diferentes e estoque configurado.

```bash
python seed.py
```

Saída esperada:

```bash
Banco populado com sucesso!
Usuários: 6
Unidades: 2
Produtos: 6

Credenciais para teste:
admin@raizesnordeste.com.br / Admin@123
gerente@raizesnordeste.com.br / Gerente@123
cozinha@raizesnordeste.com.br / Cozinha@123
atendente@raizesnordeste.com.br / Atendente@123
cliente@raizesnordeste.com.br / Cliente@123  (com consentimento LGPD)
fernanda@email.com / Cliente@123  (sem consentimento LGPD)
```

> **Nota:** O banco de testes (`DATABASE_TEST_URL`) possui seus próprios dados de teste, criados automaticamente pelo pytest — o seed não precisa ser executado nele.

---

## Iniciando a API

```bash
uvicorn main:app --reload
```

A API estará disponível em: `http://localhost:8000`

Para confirmar que está rodando, acesse `http://localhost:8000/` e verifique:

```json
{
  "status": "online",
  "servico": "API Raízes do Nordeste",
  "versao": "1.0.0"
}
```

Para encerrar a API, pressione `Ctrl + C` no terminal onde o uvicorn está rodando.

---

## Documentação da API (Swagger/OpenAPI)

Com a API rodando, acesse:

| Interface                   | URL                                  |
|-----------------------------|--------------------------------------|
| **Swagger UI** (interativo) | <http://localhost:8000/docs>         |
| ReDoc (leitura)             | <http://localhost:8000/redoc>        |
| JSON bruto (OpenAPI)        | <http://localhost:8000/openapi.json> |

### Como autenticar no Swagger

1. Acesse `http://localhost:8000/docs`
2. Clique em **POST /auth/login**
3. Clique em **Try it out**
4. Preencha com as credenciais do seed (ex: `admin@raizesnordeste.com.br` / `Admin@123`)
5. Execute e copie o valor do campo `access_token` da response
6. Clique no botão **Authorize** (cadeado) no topo da página
7. Cole o token no campo **Value** (sem o prefixo "Bearer") e clique em **Authorize**
8. Agora todos os endpoints protegidos funcionarão

---

## Coleção de testes (Postman)

O arquivo `colecao_postman/raizes_nordeste.json` contém os 14 cenários de teste organizados em pastas.

### Como importar e usar

1. Abra o **Postman**.
2. No canto superior esquerdo, clique na seta ao lado do seu nome de usuário → **File** → **Import**.
3. Selecione o arquivo `colecao_postman/raizes_nordeste.json` na pasta do projeto e confirme a importação (faça login se necessário).
4. A coleção **"Raízes do Nordeste API - Plano de Testes"** aparecerá na barra lateral esquerda.
5. Certifique-se de que a API está rodando antes de executar os testes (`uvicorn main:app --reload`).
6. Execute as pastas **na ordem**: Auth → Cardápio e Produtos → Estoque (referência) → Pedidos → Pagamentos → Fidelidade.
   - Para executar uma pasta: clique nos **três pontos (...)** ao lado do nome da pasta → **Run** → **Start run**.

> **Importante:** Execute a pasta **Auth** primeiro (T01 e T01b) — ela preenche automaticamente os tokens de autenticação usados pelas demais requisições.

### Cenários cobertos

| ID  | Cenário                           | Tipo      | Status Esperado    |
|-----|-----------------------------------|-----------|--------------------|
| T01 | Login com credenciais válidas     | Positivo  | 200 + token        |
| T02 | Cadastro de novo usuário          | Positivo  | 201                |
| T03 | Listar cardápio por unidade       | Positivo  | 200                |
| T04 | Criar pedido válido via APP       | Positivo  | 201                |
| T05 | Pagamento mock aprovado           | Positivo  | 200 + APROVADO     |
| T06 | Filtrar pedidos por canal         | Positivo  | 200                |
| T07 | Acesso sem token                  | Negativo  | 401                |
| T08 | Perfil sem permissão              | Negativo  | 403                |
| T09 | Estoque insuficiente              | Negativo  | 409                |
| T10 | Pedido sem canalPedido            | Negativo  | 422                |
| T11 | Login com senha errada            | Negativo  | 401                |
| T12 | Pagamento mock recusado           | Negativo  | 200 + RECUSADO     |
| T13 | Consultar saldo de fidelidade     | Positivo  | 200                |
| T14 | Fidelidade sem consentimento LGPD | Negativo  | 403                |

---

## Testes automatizados (pytest)

Os testes usam um banco PostgreSQL separado (`raizes_nordeste_teste`) e testam o fluxo completo da API.

### Pré-requisito

Certifique-se de que `DATABASE_TEST_URL` está configurado no `.env` e o banco de testes existe:

```bash
createdb raizes_nordeste_teste
```

### Executar todos os testes

```bash
pytest -v
```

### Executar por arquivo

```bash
pytest test_autenticacao.py -v
pytest test_pedidos.py -v
pytest test_pagamento.py -v
pytest test_fidelidade.py -v
```

Saída esperada (todos passando):

```bash
testes/test_autenticacao.py::test_t01_login_valido PASSED
testes/test_autenticacao.py::test_t02_cadastro_novo_usuario PASSED
testes/test_autenticacao.py::test_t07_acesso_sem_token PASSED
testes/test_autenticacao.py::test_t08_acesso_com_perfil_sem_permissao PASSED
testes/test_autenticacao.py::test_t11_login_senha_errada PASSED
testes/test_pedidos.py::test_t03_listar_cardapio PASSED
testes/test_pedidos.py::test_t04_criar_pedido_valido PASSED
...
```

> **Nota:** O banco de dados precisa ser criado manualmente (`createdb raizes_nordeste_teste`), mas as tabelas e dados de teste são criados e destruídos automaticamente pelo pytest — não interfere com o banco principal.

---

## Estrutura do projeto

```bash
raizes-nordeste-api/
├── src/
│   ├── dominio/            # Entidades, enums, exceções e interfaces
│   ├── aplicacao/          # Casos de uso (regras de negócio)
│   ├── infraestrutura/     # ORM, repositórios, JWT, bcrypt, pagamento mock
│   └── api/                # Routers, schemas, dependências, middleware
├── migrations/             # Migrations Alembic
├── testes/                 # Testes automatizados (pytest)
├── colecao_postman/        # Coleção de testes Postman (.json)
├── main.py                 # Entrada da aplicação
├── seed.py                 # Dados iniciais
├── requirements.txt        # Dependências Python
├── alembic.ini             # Configuração do Alembic
├── pytest.ini              # Configuração do pytest
└── .env.example            # Modelo de variáveis de ambiente
```
