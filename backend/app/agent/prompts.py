def sql_prompt(question: str, schema: str) -> str:
    return f"""Você é um analista de dados.

Transforme a pergunta do usuário em uma consulta SQL compatível com DuckDB.

=== INSTRUÇÕES CRÍTICAS ===

1. A tabela se chama EXATAMENTE: data
2. NÃO confunda nomes de colunas com nomes de tabelas.
3. NUNCA use o nome de uma coluna como nome de tabela.
4. NUNCA invente tabelas. Use APENAS: data
5. NUNCA invente colunas. Use APENAS as colunas listadas no schema abaixo.

=== SCHEMA DA TABELA "data" ===
{schema}

=== EXEMPLOS CORRETOS ===

Se o schema é: id (INTEGER), data (DATE), produto (VARCHAR), valor (DOUBLE)

Pergunta: "Qual foi o faturamento total?"
SQL correto: SELECT SUM(valor) AS faturamento_total FROM data

Pergunta: "Mostre as vendas por produto"
SQL correto: SELECT produto, SUM(valor) AS total FROM data GROUP BY produto

Pergunta: "Vendas de janeiro"
SQL correto: SELECT * FROM data WHERE data >= '2025-01-01' AND data <= '2025-01-31'

Pergunta: "Qual produto mais vendeu?"
SQL correto: SELECT produto, SUM(valor) AS total FROM data GROUP BY produto ORDER BY total DESC LIMIT 1

=== PERGUNTA DO USUÁRIO ===
{question}

=== REGRAS ===
- Gere SOMENTE o SQL, sem explicações adicionais.
- A tabela SEMPRE se chama "data".
- Consultas de leitura APENAS (SELECT ou WITH).
- Não use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE.
- Não invente colunas que não existem no schema.
- Não invente tabelas.
- Se os dados não permitirem responder, gere um SELECT vazio: SELECT NULL WHERE 1=0"""


def explanation_prompt(question: str, sql: str, result: str) -> str:
    return f"""Você é um analista de dados.

Responda à pergunta do usuário de forma BREVE e DIRETA, em no máximo 2-3 frases.
Use os números dos resultados. Seja conciso.

Pergunta:
{question}

SQL executado:
{sql}

Resultados:
{result}"""
