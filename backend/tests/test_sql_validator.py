import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agent.sql_validator import validate_sql
import pytest


class TestSQLValidatorAccepts:
    def test_select_star(self):
        result = validate_sql("SELECT * FROM data;")
        assert result == "SELECT * FROM data"

    def test_select_with_alias(self):
        result = validate_sql("SELECT estado AS uf, SUM(valor) AS total FROM data GROUP BY estado")
        assert "estado" in result
        assert "data" in result

    def test_with_cte(self):
        result = validate_sql(
            "WITH totals AS (SELECT estado, SUM(valor) AS total FROM data GROUP BY estado) "
            "SELECT * FROM totals ORDER BY total DESC"
        )
        assert "WITH" in result
        assert "totals" in result

    def test_strips_markdown(self):
        result = validate_sql("```sql\nSELECT id FROM data\n```")
        assert result == "SELECT id FROM data"

    def test_strips_markdown_no_label(self):
        result = validate_sql("```\nSELECT id FROM data\n```")
        assert result == "SELECT id FROM data"

    def test_normalizes_whitespace(self):
        result = validate_sql("  SELECT id FROM data  ;  ")
        assert result == "SELECT id FROM data"


class TestSQLValidatorBlocks:
    def test_empty_sql(self):
        with pytest.raises(ValueError, match="não gerou"):
            validate_sql("")

    def test_multiple_statements(self):
        with pytest.raises(ValueError, match="Múltiplas"):
            validate_sql("SELECT * FROM data; SELECT id FROM data")

    def test_insert(self):
        with pytest.raises(ValueError, match="INSERT"):
            validate_sql("INSERT INTO data VALUES (1, 'a')")

    def test_update(self):
        with pytest.raises(ValueError, match="UPDATE"):
            validate_sql("UPDATE data SET valor = 0")

    def test_delete(self):
        with pytest.raises(ValueError, match="DELETE"):
            validate_sql("DELETE FROM data WHERE id = 1")

    def test_drop(self):
        with pytest.raises(ValueError, match="DROP"):
            validate_sql("DROP TABLE data")

    def test_alter(self):
        with pytest.raises(ValueError, match="ALTER"):
            validate_sql("ALTER TABLE data ADD COLUMN test INT")

    def test_create(self):
        with pytest.raises(ValueError, match="CREATE"):
            validate_sql("CREATE TABLE data (id INT)")

    def test_truncate(self):
        with pytest.raises(ValueError, match="TRUNCATE"):
            validate_sql("TRUNCATE TABLE data")

    def test_attach(self):
        with pytest.raises(ValueError, match="ATTACH"):
            validate_sql("ATTACH DATABASE 'test.db' AS db")

    def test_copy(self):
        with pytest.raises(ValueError, match="COPY"):
            validate_sql("COPY data TO 'output.csv'")

    def test_pragma(self):
        with pytest.raises(ValueError, match="PRAGMA"):
            validate_sql("PRAGMA table_info(data)")

    def test_non_select_first_word(self):
        with pytest.raises(ValueError, match="não suportado"):
            validate_sql("EXPLAIN SELECT * FROM data")

    def test_other_table_from(self):
        with pytest.raises(ValueError, match="tabela 'other_table'"):
            validate_sql("SELECT * FROM other_table")

    def test_other_table_join(self):
        with pytest.raises(ValueError, match="tabela 'users'"):
            validate_sql("SELECT * FROM data JOIN users ON data.id = users.id")

    def test_other_table_into(self):
        with pytest.raises(ValueError, match="tabela 'backup'"):
            validate_sql("SELECT * INTO backup FROM data")
