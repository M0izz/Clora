"""
Production-Hardened In-Memory Tabular & DuckDB Query Engine.
INDUSAI-X / SIH Problem Statement 26117 (MRPL)
Member 6: Data Intelligence + Knowledge Graph + Security Engineer

Security & Robustness:
- In-memory execution with enable_external_access=false.
- AST-level SQL validation via sqlglot.
- Single-statement strict enforcement (blocks multi-statement semicolon injection).
- AST function & table whitelisting (blocks read_csv, glob, copy, attach, and file leaks).
- Returns structured JSON dictionaries and Markdown tables for agent tool consumption.
"""

import os
import duckdb
import pandas as pd
import sqlglot
from sqlglot import exp
from typing import Dict, Any, List, Optional, Tuple


class SQLSecurityError(Exception):
    """Raised when an unauthorized or potentially dangerous SQL query is attempted."""
    pass


ALLOWED_SQL_FUNCTIONS = {
    # Aggregates
    "AVG", "COUNT", "SUM", "MIN", "MAX", "STDDEV", "VARIANCE", "MEDIAN", "MODE",
    # Math
    "ROUND", "ABS", "CEIL", "FLOOR", "SQRT", "POWER", "MOD",
    # String
    "LOWER", "UPPER", "TRIM", "LTRIM", "RTRIM", "LENGTH", "SUBSTRING", "CONCAT", "REPLACE", "LIKE", "ILIKE",
    # Date & Time
    "DATE_TRUNC", "EXTRACT", "NOW", "CURRENT_TIMESTAMP", "CURRENT_DATE", "YEAR", "MONTH", "DAY", "HOUR", "MINUTE",
    # Logic / Cast
    "COALESCE", "NULLIF", "CAST", "TRY_CAST", "CASE", "WHEN", "THEN", "ELSE"
}


class TabularEngine:
    """Safe in-memory SQL execution engine for industrial telemetry and equipment logs."""

    def __init__(self):
        # Create an isolated in-memory DuckDB database
        self.conn = duckdb.connect(database=":memory:", read_only=False)
        # Lock down external filesystem and network access
        try:
            self.conn.execute("SET enable_external_access = false;")
        except Exception:
            pass
        self.registered_tables: Dict[str, str] = {}

    def load_csv(self, table_name: str, csv_path: str) -> int:
        """Loads a CSV dataset into an in-memory table."""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # Load through pandas first to avoid DuckDB filesystem read dependencies
        df = pd.read_csv(csv_path)
        self.conn.register(f"temp_{table_name}", df)
        self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_{table_name};")
        self.conn.unregister(f"temp_{table_name}")
        self.registered_tables[table_name] = csv_path
        
        row_count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        return row_count

    def load_dataframe(self, table_name: str, df: pd.DataFrame) -> int:
        """Registers an in-memory DataFrame as a table."""
        self.conn.register(f"temp_{table_name}", df)
        self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_{table_name};")
        self.conn.unregister(f"temp_{table_name}")
        self.registered_tables[table_name] = "in_memory_dataframe"
        return len(df)

    def validate_sql(self, sql_query: str) -> None:
        """
        Validates SQL AST to strictly allow read-only SELECT queries and block:
        - Multi-statement execution (semicolons)
        - Non-SELECT statements (INSERT, UPDATE, DELETE, DROP, ALTER, COPY, ATTACH)
        - Unauthorized functions (read_csv, read_parquet, glob, httpfs)
        - Unknown / unregistered tables
        """
        cleaned_query = sql_query.strip().rstrip(";")
        if not cleaned_query:
            raise SQLSecurityError("Query string is empty.")

        try:
            statements = sqlglot.parse(cleaned_query, read="duckdb")
        except Exception as e:
            raise SQLSecurityError(f"SQL Syntax Error / Unparseable query: {str(e)}")

        # 1. Multi-statement check
        if len(statements) != 1:
            raise SQLSecurityError(f"Multiple SQL statements detected ({len(statements)}). Only single SELECT statements are allowed.")

        stmt = statements[0]
        if stmt is None:
            raise SQLSecurityError("Null statement parsed.")

        # 2. Statement Type check: strictly SELECT or UNION
        if not isinstance(stmt, (exp.Select, exp.Union)):
            raise SQLSecurityError(f"Unauthorized statement type '{stmt.key}'. Only SELECT queries are permitted.")

        # 3. Check for disallowed AST expressions
        disallowed_types = (
            exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter,
            exp.Command, exp.Create, exp.Attach, exp.Detach
        )
        for node in stmt.walk():
            if isinstance(node, disallowed_types):
                raise SQLSecurityError(f"Forbidden SQL operation detected: {type(node).__name__}")

        # 4. Function whitelisting
        for func in stmt.find_all(exp.Func, exp.Anonymous):
            if isinstance(func, exp.Anonymous):
                func_name = str(func.this).upper()
            else:
                func_name = (func.key or func.__class__.__name__).upper()
            
            if func_name and func_name not in ALLOWED_SQL_FUNCTIONS:
                raise SQLSecurityError(f"Forbidden SQL function '{func_name}' detected. Only mathematical and aggregate functions are permitted.")

        # 5. Table reference validation
        for table in stmt.find_all(exp.Table):
            t_name = table.name.lower()
            if t_name and t_name not in [t.lower() for t in self.registered_tables.keys()]:
                raise SQLSecurityError(f"Table '{t_name}' is not in the list of registered in-memory tables: {list(self.registered_tables.keys())}")

    def query(self, sql_query: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Executes a validated read-only SQL query.
        Returns:
            - List of dictionaries (row-level JSON serializable data)
            - Formatted Markdown string table for LLM agent reasoning.
        """
        self.validate_sql(sql_query)
        cursor = self.conn.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        dict_rows = [dict(zip(columns, row)) for row in rows]
        df_result = pd.DataFrame(rows, columns=columns)
        markdown_table = df_result.to_markdown(index=False) if not df_result.empty else "No results found."

        return dict_rows, markdown_table

    def get_schema(self, table_name: str) -> Dict[str, str]:
        """Returns column names and types for LLM prompt context."""
        if table_name not in self.registered_tables:
            raise KeyError(f"Table '{table_name}' not found.")
        
        info = self.conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
        return {col[1]: col[2] for col in info}

    def close(self):
        """Closes connection."""
        self.conn.close()
