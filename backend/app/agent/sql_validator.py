import re
from typing import Set


BLOCKED_KEYWORDS: Set[str] = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "ATTACH",
    "COPY",
    "EXPORT",
    "INSTALL",
    "LOAD",
    "PRAGMA",
}

KNOWN_TABLES: Set[str] = {"DATA"}


def _strip_markdown(sql: str) -> str:
    sql = sql.strip()
    sql = re.sub(r"^```(?:sql)?\s*\n?", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\n?```\s*$", "", sql, flags=re.IGNORECASE)
    return sql.strip()


def _normalize(sql: str) -> str:
    sql = _strip_markdown(sql)
    sql = sql.rstrip(";").strip()
    return sql


def _remove_subqueries(sql_upper: str) -> str:
    """Remove subqueries and their aliases to avoid false positives on inner table refs."""
    result = sql_upper
    depth = 0
    start = -1
    chars = list(result)
    for i, c in enumerate(chars):
        if c == '(':
            if depth == 0:
                start = i
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0 and start >= 0:
                # Remove from ( to ) inclusive
                for j in range(start, i + 1):
                    chars[j] = ' '
                # Also remove the alias after ) if present
                k = i + 1
                while k < len(chars) and chars[k] == ' ':
                    k += 1
                if k < len(chars) and chars[k].isalpha():
                    while k < len(chars) and (chars[k].isalnum() or chars[k] == '_'):
                        chars[k] = ' '
                        k += 1
                start = -1
    return ''.join(chars)


def validate_sql(sql: str) -> str:
    """
    Validates and normalizes SQL from the LLM.
    Returns the cleaned SQL or raises ValueError with a reason.
    """
    sql = _normalize(sql)

    if not sql:
        raise ValueError("O LLM não gerou uma consulta SQL válida.")

    # Block multiple statements
    if ";" in sql:
        raise ValueError(
            "Múltiplas instruções SQL não são permitidas. Envie apenas uma consulta."
        )

    # Uppercase for keyword matching (preserving original)
    upper = sql.upper()

    # Block destructive commands
    for keyword in BLOCKED_KEYWORDS:
        pattern = r"\b" + keyword + r"\b"
        if re.search(pattern, upper):
            raise ValueError(
                f"Comando bloqueado: {keyword}. Somente consultas de leitura (SELECT, WITH) são permitidas."
            )

    # Must be a read-only statement (SELECT or WITH)
    first_word = upper.split()[0]
    if first_word not in ("SELECT", "WITH"):
        raise ValueError(
            f"Comando não suportado: '{first_word}'. Somente SELECT e WITH são permitidos."
        )

    # Collect CTE aliases (WITH ... AS <name>)
    cte_aliases = set()
    for match in re.finditer(r"\bWITH\b\s+(\w+)\s+AS\s*\(", upper):
        cte_aliases.add(match.group(1))

    # Remove subqueries before checking table references
    cleaned = _remove_subqueries(upper)

    # Block access to tables other than 'data' or CTE aliases
    table_refs = re.findall(
        r"\b(?:FROM|JOIN|INTO|TABLE)\s+([a-zA-Z_]\w*)",
        cleaned,
    )
    allowed = KNOWN_TABLES | cte_aliases
    for table in table_refs:
        if table not in allowed:
            raise ValueError(
                f"Tabela '{table.lower()}' não existe. Use apenas a tabela 'data'. "
                f"Colunas disponíveis estão no schema."
            )

    return sql
