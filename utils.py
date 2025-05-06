import re

def extract_sql(message):
    """Extract SQL code from a message."""
    sql_pattern = r"```sql\n(.*?)\n```"
    matches = re.findall(sql_pattern, message, re.DOTALL)
    return matches if matches else []

def escape_sql_for_js(sql):
    """Escape SQL code for JavaScript."""
    # Escape single quotes and double quotes for JavaScript
    return sql.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')