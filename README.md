# Data Copilot MVP

O **Data Copilot** é uma ferramenta de inteligência de dados que permite aos usuários carregar arquivos estruturados (CSV/XLSX) e realizar consultas em linguagem natural. A aplicação gera SQL dinâmico e seguro para execução local no DuckDB e retorna respostas detalhadas geradas por IA.

---

## 🛠️ Arquitetura e Fluxo

```
Usuário → React Frontend → FastAPI Backend → Orchestrator → LLM (Gera SQL)
                                                       ↓
                                                    SQL Query
                                                       ↓
                                                  SQL Validator
                                                       ↓
                                                    DuckDB
                                                       ↓
                                                    Resultado Tabular
                                                       ↓
                                                    LLM (Explica Resultado)
                                                       ↓
                                                    Resposta Final
```

1. **Upload**: O arquivo CSV ou XLSX é carregado no DuckDB local.
2. **Schema**: O schema da tabela logicamente nomeada como `data` é inferido.
3. **Pergunta**: O usuário submete uma pergunta em linguagem natural.
4. **SQL**: A pergunta e o schema do banco de dados são enviados ao LLM para geração do código SQL.
5. **Validação**: O SQL gerado passa por um validador estrito (verificação de consultas de leitura, prevenção de SQL injection e comandos destrutivos).
6. **Execução**: O SQL validado roda contra a tabela `data` no DuckDB.
7. **Explicação**: O resultado do DuckDB é enviado de volta ao LLM para explicar a resposta final de forma contextual.

---

## 🗂️ Estrutura do Projeto

```text
data-copilot/
├── backend/
│   ├── app/
│   │   ├── main.py                # Entrada do servidor FastAPI e CORS
│   │   ├── api/                   # Rotas da API (chat, upload, datasets)
│   │   ├── agent/                 # Lógica do agente (orquestrador, prompts, validador)
│   │   ├── data/                  # Conexão DuckDB e carregamento de arquivos
│   │   ├── llm/                   # Abstrações e provedores de LLM
│   │   └── models/                # Esquemas Pydantic / Modelos de dados
│   └── tests/                     # Testes automatizados (pytest)
├── frontend/
│   └── src/
│       ├── components/            # Componentes React
│       ├── pages/                 # Páginas da aplicação
│       ├── services/              # Serviços de Integração API
│       └── types/                 # Definições de tipos TypeScript
├── data/                          # Diretório de dados estáticos/exemplos
├── uploads/                       # Diretório temporário de uploads de arquivos
├── docker-compose.yml             # Orquestração de containers Docker
├── .env.example                   # Exemplo de configuração de variáveis de ambiente
├── README.md                      # Documentação do projeto
└── AGENTS.md                      # Regras e cronograma de implementação do agente
```

---

## 🚀 Como Iniciar

### Pré-requisitos
- Python 3.12+
- Node.js 18+ (para frontend)
- Docker / Docker Compose (opcional)

### Configuração das Variáveis de Ambiente
1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```
2. Adicione sua chave de API do provedor LLM escolhido (ex: Anthropic Claude, OpenAI, etc.) no `.env`.

---

## ⚙️ Execução Local

### Backend (FastAPI)

1. Entre no diretório do backend:
   ```bash
   cd backend
   ```
2. Crie e ative o ambiente virtual:
   - **Windows (PowerShell):**
     > [!IMPORTANT]
     > Se o PowerShell bloquear a execução de scripts (erro de diretiva de execução), execute `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` antes de ativar.
     ```powershell
     python -m venv .venv
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
     .venv\Scripts\Activate.ps1
     ```
   - **Linux/macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute o servidor de desenvolvimento:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
5. Acesse o endpoint do health check em: [http://localhost:8000/health](http://localhost:8000/health) ou a documentação interativa em [http://localhost:8000/docs](http://localhost:8000/docs).

### Frontend (React + TypeScript + Vite)

1. Entre no diretório do frontend:
   ```bash
   cd frontend
   ```
2. Instale as dependências:
   ```bash
   npm install
   ```
3. Execute o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```
4. Acesse a aplicação no navegador em: [http://localhost:5173](http://localhost:5173).

---

## 🧪 Testes Automatizados

Para rodar a suite de testes no backend:
```bash
cd backend
python -m pytest tests/
```

---

## 📈 Status do Cronograma (Checklist)

- [x] **Fase 1 — Estrutura** (Concluído)
  - [x] Estrutura de arquivos e diretórios iniciada.
  - [x] Configuração de `.env.example` e `.gitignore`.
  - [x] Servidor FastAPI inicial configurado com `/health`.
  - [x] Projeto React + Vite + TypeScript inicializado.
- [ ] **Fase 2 — DuckDB**
- [ ] **Fase 3 — Upload**
- [ ] **Fase 4 — LLM**
- [ ] **Fase 5 — SQL Security**
- [ ] **Fase 6 — Orchestrator**
- [ ] **Fase 7 — Frontend**
- [ ] **Fase 8 — Docker**
- [ ] **Fase 9 — Testes e documentação**
