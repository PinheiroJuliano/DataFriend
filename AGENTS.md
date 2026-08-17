# AGENTS.md — DataFriend MVP

## Objetivo

Construir um MVP de um **DataFriend** capaz de:

1. Receber CSV ou XLSX.
2. Carregar o dataset no DuckDB.
3. Identificar e exibir o schema.
4. Receber perguntas em linguagem natural.
5. Enviar pergunta + schema para um LLM.
6. Gerar SQL somente leitura.
7. Validar o SQL antes da execução.
8. Executar a consulta no DuckDB.
9. Enviar o resultado de volta ao LLM.
10. Retornar uma resposta em linguagem natural.
11. Exibir pergunta, resposta, SQL e resultado tabular no frontend.

Fluxo:

```text
Usuário → React → FastAPI → Orchestrator → LLM
                                      ↓
                                    SQL
                                      ↓
                                  Validação
                                      ↓
                                   DuckDB
                                      ↓
                                   Resultado
                                      ↓
                                    LLM
                                      ↓
                                  Resposta
```

## Stack

### Backend
- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic
- DuckDB
- SDK oficial do provedor de LLM
- pytest

### Frontend
- React
- Vite
- TypeScript
- CSS simples ou Tailwind
- Recharts somente quando a funcionalidade de gráficos for implementada

### Infraestrutura
- Docker
- Docker Compose
- `.env`
- `.env.example`

## Escopo do MVP

Implementar:

- upload CSV/XLSX;
- descoberta de schema;
- perguntas em linguagem natural;
- geração de SQL pelo LLM;
- validação de SQL;
- execução no DuckDB;
- explicação dos resultados pelo LLM;
- exibição do SQL;
- exibição do resultado em tabela;
- tratamento de erros;
- testes;
- Docker Compose.

Não implementar ainda:

- autenticação;
- múltiplos usuários;
- PostgreSQL para persistência;
- RAG;
- embeddings;
- vector database;
- Databricks;
- Delta Lake;
- agentes autônomos complexos;
- execução de Python gerado pela IA;
- escrita/modificação dos datasets;
- Kubernetes.

## Estrutura

```text
DataFriend/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── upload.py
│   │   │   └── datasets.py
│   │   ├── agent/
│   │   │   ├── orchestrator.py
│   │   │   ├── prompts.py
│   │   │   └── sql_validator.py
│   │   ├── data/
│   │   │   ├── duckdb.py
│   │   │   └── loader.py
│   │   ├── llm/
│   │   │   ├── provider.py
│   │   │   └── provider_impl.py
│   │   └── models/
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── types/
├── data/
├── uploads/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── AGENTS.md
```

Manter HTTP/API, LLM, orquestração e DuckDB separados. Não colocar toda a lógica nos endpoints.

## DuckDB

A tabela lógica padrão deve ser:

```text
data
```

Exemplo:

```sql
SELECT estado, SUM(valor) AS faturamento
FROM data
GROUP BY estado
ORDER BY faturamento DESC;
```

O DuckDB deve rodar localmente no backend. Não usar banco externo no MVP.

## LLM

Criar uma abstração:

```python
class LLMProvider:
    async def generate_sql(self, question: str, schema: str) -> str:
        ...

    async def explain_result(
        self,
        question: str,
        sql: str,
        result: str
    ) -> str:
        ...
```

Configuração via ambiente:

```env
LLM_PROVIDER=anthropic
LLM_API_KEY=
LLM_MODEL=
```

Nunca colocar API Key no código.

O provider concreto deve ficar separado do orchestrator para permitir troca futura de modelo/provedor.

## Prompt de SQL

O prompt deve informar:

- tabela disponível: `data`;
- schema;
- pergunta;
- sintaxe DuckDB;
- somente leitura;
- proibição de comandos destrutivos;
- proibição de tabelas/colunas inventadas.

Exemplo:

```text
Você é um analista de dados.

Transforme a pergunta do usuário em uma consulta SQL
compatível com DuckDB.

Tabela disponível:
data

Schema:
{schema}

Pergunta:
{question}

Regras:
- Gere somente SQL.
- Utilize somente a tabela data.
- Gere somente consultas de leitura.
- Não use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE ou TRUNCATE.
- Não invente colunas.
- Não invente tabelas.
- Se os dados não permitirem responder, informe isso.
```

A saída do LLM nunca deve ser executada diretamente.

## Validação SQL

Antes de executar:

1. Remover blocos Markdown como ```sql.
2. Normalizar o SQL.
3. Verificar múltiplas instruções.
4. Permitir somente consultas de leitura.
5. Bloquear comandos destrutivos.
6. Impedir acesso a tabelas diferentes de `data`.
7. Aplicar limites de segurança quando apropriado.
8. Capturar erros do DuckDB.

Bloquear pelo menos:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
TRUNCATE
ATTACH
COPY
EXPORT
INSTALL
LOAD
PRAGMA
```

Implementar em:

```text
backend/app/agent/sql_validator.py
```

Não confiar apenas em regex para segurança. Combinar validação textual com parsing/validação do DuckDB quando possível.

## Orchestrator

Fluxo:

```text
question
  ↓
schema
  ↓
LLM.generate_sql()
  ↓
validate_sql()
  ↓
DuckDB.execute()
  ↓
result
  ↓
LLM.explain_result()
  ↓
final response
```

Exemplo conceitual:

```python
async def process_question(question, dataset):
    schema = dataset.get_schema()

    sql = await llm.generate_sql(
        question=question,
        schema=schema
    )

    validated_sql = validate_sql(sql)
    result = dataset.execute(validated_sql)

    answer = await llm.explain_result(
        question=question,
        sql=validated_sql,
        result=result
    )

    return {
        "answer": answer,
        "sql": validated_sql,
        "result": result
    }
```

O orchestrator não deve conhecer detalhes do React ou HTTP.

## API

### POST `/api/datasets/upload`

Recebe `multipart/form-data` com `file`.

Retorna nome, linhas, colunas e schema.

### GET `/api/datasets/{dataset_id}`

Retorna metadados do dataset.

### POST `/api/chat`

Entrada:

```json
{
  "dataset_id": "uuid",
  "question": "Qual estado teve maior faturamento?"
}
```

Saída:

```json
{
  "answer": "São Paulo teve o maior faturamento...",
  "sql": "SELECT ...",
  "columns": ["estado", "faturamento"],
  "rows": [
    ["SP", 8420000],
    ["MG", 5210000]
  ]
}
```

### GET `/health`

Retornar:

```json
{
  "status": "ok"
}
```

## Frontend

Criar uma página principal contendo:

- upload;
- nome do dataset;
- quantidade de registros;
- quantidade de colunas;
- schema;
- campo de pergunta;
- botão de análise;
- resposta;
- SQL gerado;
- tabela de resultados;
- loading;
- mensagens de erro.

Não criar uma interface excessivamente complexa no MVP.

## Tratamento de erros

Cobrir:

- formato inválido;
- arquivo vazio;
- erro de leitura;
- erro do LLM;
- SQL inválido;
- SQL bloqueado;
- erro DuckDB;
- pergunta sem resposta possível;
- timeout.

Não exibir stack trace para o usuário.

## Testes

Criar testes para:

### SQL Validator
Aceitar:

```sql
SELECT * FROM data;
```

Bloquear:

```sql
DROP TABLE data;
DELETE FROM data;
UPDATE data SET valor = 0;
INSERT INTO data VALUES (...);
ALTER TABLE data ...
```

### DuckDB
Testar:

- CSV;
- XLSX;
- schema;
- SELECT;
- erros.

### Orchestrator
Mockar o LLM e testar:

```text
pergunta → SQL → validação → DuckDB → resultado → resposta
```

Não fazer chamadas reais ao LLM nos testes unitários.

## Docker

Criar:

```text
docker-compose.yml
```

com:

```text
frontend
backend
```

Não criar container separado para DuckDB.

Frontend:

```env
VITE_API_URL=http://localhost:8000
```

Backend:

```env
CORS_ORIGINS=http://localhost:5173
```

## Execução local

Backend:

```bash
cd backend
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar:

```bash
pip install -r requirements.txt
```

Executar:

```bash
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Execução com Docker

```bash
docker compose up --build
```

URLs esperadas:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
Swagger:  http://localhost:8000/docs
```

## `.env.example`

```env
LLM_PROVIDER=anthropic
LLM_API_KEY=
LLM_MODEL=

CORS_ORIGINS=http://localhost:5173

UPLOAD_DIR=./uploads
DUCKDB_PATH=./data/datafriend.duckdb
```

Nunca versionar:

```text
.env
uploads/
*.duckdb
.venv/
node_modules/
__pycache__/
```

## Ordem de implementação

### Fase 1 — Estrutura

- [ ] Criar estrutura.
- [ ] Configurar FastAPI.
- [ ] Configurar React + Vite + TypeScript.
- [ ] Criar `.env.example`.
- [ ] Criar `.gitignore`.
- [ ] Criar `/health`.

### Fase 2 — DuckDB

- [ ] CSV.
- [ ] XLSX.
- [ ] Tabela `data`.
- [ ] Schema.
- [ ] SELECT.
- [ ] Testes.

### Fase 3 — Upload

- [ ] `/api/datasets/upload`.
- [ ] Validação.
- [ ] `dataset_id`.
- [ ] Metadados.

### Fase 4 — LLM

- [ ] Interface `LLMProvider`.
- [ ] Provider concreto.
- [ ] Prompt SQL.
- [ ] Prompt de explicação.
- [ ] API Key via ambiente.

### Fase 5 — SQL Security

- [ ] `sql_validator.py`.
- [ ] Somente leitura.
- [ ] Bloqueio destrutivo.
- [ ] Bloqueio de múltiplas instruções.
- [ ] Testes.

### Fase 6 — Orchestrator

- [ ] Integrar LLM.
- [ ] Integrar DuckDB.
- [ ] Implementar fluxo completo.
- [ ] Retornar SQL + resultado + resposta.

### Fase 7 — Frontend

- [ ] Upload.
- [ ] Dataset.
- [ ] Schema.
- [ ] Pergunta.
- [ ] Resposta.
- [ ] SQL.
- [ ] Resultado.
- [ ] Loading/erro.

### Fase 8 — Docker

- [ ] Dockerfile backend.
- [ ] Dockerfile frontend.
- [ ] docker-compose.
- [ ] Testar execução completa.

### Fase 9 — Testes e documentação

- [ ] Testes unitários.
- [ ] Testes de integração.
- [ ] README.
- [ ] Dataset de exemplo.
- [ ] Exemplos de perguntas.
- [ ] Documentação da arquitetura.

## Critérios de aceite

O MVP está concluído quando:

1. A aplicação abre no navegador.
2. CSV pode ser enviado.
3. XLSX pode ser enviado.
4. Schema é exibido.
5. Perguntas em linguagem natural funcionam.
6. O LLM gera SQL.
7. SQL é validado antes da execução.
8. DuckDB executa a consulta.
9. Resultado aparece em tabela.
10. O LLM explica o resultado.
11. SQL gerado é exibido.
12. Consultas destrutivas são bloqueadas.
13. Docker Compose executa o sistema.
14. Testes principais passam.
15. Nenhuma API Key está no código.

## Dataset de demonstração

Criar:

```text
data/sample_sales.csv
```

Colunas:

```text
id
data
produto
categoria
estado
quantidade
valor
```

Exemplo:

```csv
id,data,produto,categoria,estado,quantidade,valor
1,2025-01-10,Notebook,Eletronicos,SP,2,8000
2,2025-01-12,Mouse,Perifericos,MG,10,1500
3,2025-02-03,Notebook,Eletronicos,MG,1,4000
4,2025-02-15,Monitor,Eletronicos,SP,4,6000
5,2025-03-01,Mouse,Perifericos,RJ,20,3000
```

Perguntas de demonstração:

```text
Qual estado teve maior faturamento?
Qual produto vendeu mais unidades?
Qual foi o faturamento total?
Qual categoria teve maior faturamento?
Mostre o faturamento por estado.
Qual foi o mês com maior faturamento?
```

## Princípios para o agente de desenvolvimento

1. Não implementar tudo de uma vez.
2. Trabalhar por fases.
3. Manter frontend e backend desacoplados.
4. Não colocar regras de negócio diretamente nos endpoints.
5. Não colocar API Keys no código.
6. Nunca executar SQL gerado pela IA sem validação.
7. Criar testes antes de considerar uma funcionalidade concluída.
8. Preferir código simples no MVP.
9. Não adicionar dependências sem necessidade.
10. Não implementar funcionalidades fora do escopo sem solicitação.
11. Atualizar o README conforme as funcionalidades forem concluídas.
12. Manter o projeto executável após cada fase.

## Definition of Done

```text
[ ] Código implementado
[ ] Tratamento de erro implementado
[ ] Teste criado quando aplicável
[ ] Código executando localmente
[ ] Sem secrets no código
[ ] README atualizado quando necessário
[ ] Nenhuma funcionalidade existente quebrada
```

## Próxima ação

Começar pela **Fase 1 — Estrutura**.

Não implementar LLM, DuckDB ou frontend completo antes de estabelecer a estrutura inicial.

Seguir sequencialmente:

```text
Fase 1 → Estrutura
Fase 2 → DuckDB
Fase 3 → Upload
Fase 4 → LLM
Fase 5 → SQL Security
Fase 6 → Orchestrator
Fase 7 → Frontend
Fase 8 → Docker
Fase 9 → Testes e documentação
```
