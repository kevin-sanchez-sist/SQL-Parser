# test_parser.py
from src.parser import SQLParser, SQLValidator
from src.grammar.grammar_examples import VALID_QUERIES, INVALID_QUERIES

print("="*70)
print("TEST DEL PARSER")
print("="*70)

# Test 1: Parser básico
parser = SQLParser()
query = "SELECT name, age FROM users WHERE age > 18"
tree = parser.parse(query)

if tree:
    print(f"\n✅ Query parseada: {query}")
    print(f"   Derivaciones: {tree.get_derivation_count()}")
    print(f"   Profundidad: {tree.get_depth()}")
    print(f"   Nodos: {tree.get_node_count()}")
    print(f"   Columnas: {tree.extract_columns()}")
    print(f"   Tabla: {tree.extract_table()}")
    print(f"\nÁrbol:\n{tree.get_pretty_string()}")

# Test 2: Validador
print("\n" + "="*70)
print("TEST DEL VALIDADOR")
print("="*70)

validator = SQLValidator()

for query in VALID_QUERIES[:3]:
    is_valid, messages, tree = validator.validate_query(query)
    status = "✅" if is_valid else "❌"
    print(f"\n{status} {query}")
    if messages:
        for msg in messages:
            print(f"   - {msg}")

# Test 3: Ambigüedad
print("\n" + "="*70)
print("TEST DE AMBIGÜEDAD")
print("="*70)

ambiguous_query = "SELECT * FROM users WHERE a = 1 AND b = 2 OR c = 3"
is_ambiguous, count = validator.check_ambiguity(ambiguous_query)
print(f"\nQuery: {ambiguous_query}")
print(f"¿Es ambigua?: {is_ambiguous}")
print(f"Derivaciones: {count}")