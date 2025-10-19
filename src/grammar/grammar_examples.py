"""
Ejemplos de consultas SQL para testing y demostración
"""

# Consultas válidas básicas
VALID_QUERIES = [
    "SELECT * FROM users WHERE (age > 18 AND status = 'active') OR role = 'admin'",
    "SELECT name FROM users ORDER BY name ASC",
    "SELECT * FROM products WHERE price > 50 ORDER BY price DESC",
]

# Consultas para demostrar ambigüedad
AMBIGUOUS_QUERIES = [
     "SELECT * FROM users WHERE a = 1 AND b = 2 AND c = 3 OR d = 4",
    "SELECT * FROM users WHERE NOT status = 'banned' AND age > 18",
    "SELECT * FROM users WHERE price > 100 OR category = 'electronics' AND stock > 0",
]

# Consultas inválidas (para testing de errores)
INVALID_QUERIES = [
    "SELECT * users",  # Falta FROM
    "SELECT * FROM",  # Falta tabla
    "SELECT * FROM users WHERE",  # WHERE incompleto
    "SELECT * FROM users WHERE age >",  # Condición incompleta
    "SELECT name, FROM users",  # Coma extra
]

# Consultas complejas
COMPLEX_QUERIES = [
    "SELECT name, age, email FROM users WHERE (age >= 18 AND status = 'active') OR role = 'admin' ORDER BY name ASC",
    "SELECT * FROM products WHERE (price > 100 AND category = 'electronics') OR (price < 50 AND category = 'books')",
    "SELECT id FROM orders WHERE NOT (status = 'cancelled' OR status = 'refunded') AND total > 1000",
]


def get_examples_by_category():
    """Retorna ejemplos organizados por categoría"""
    return {
        "valid": VALID_QUERIES,
        "ambiguous": AMBIGUOUS_QUERIES,
        "invalid": INVALID_QUERIES,
        "complex": COMPLEX_QUERIES,
    }


def get_all_examples():
    """Retorna todos los ejemplos"""
    return (
        VALID_QUERIES + 
        AMBIGUOUS_QUERIES + 
        INVALID_QUERIES + 
        COMPLEX_QUERIES
    )
