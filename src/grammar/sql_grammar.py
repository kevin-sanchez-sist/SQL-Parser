'''
Definiciones de gramaticas de SQL para el analizador con gramaticas ambiguas y solucionando el problema
'''


#Grámatica ambigua: AND y OR sin precedencia definida
SQL_GRAMMAR_AMBIGUOUS = r"""
?start: query
query: "SELECT" columns "FROM" table where_clause? order_clause?
columns: "*" | column ("," column)*
column: CNAME
table: CNAME
where_clause: "WHERE" condition

// PROBLEMA: ambigüedad en expresiones lógicas
?condition: condition "AND" condition
           | condition "OR" condition
           | "NOT" condition
           | "(" condition ")"
           | predicate

predicate: value comp value

comp: "=" | "<>" | "!=" | "<" | ">" | "<=" | ">="

value: CNAME | NUMBER | STRING | SINGLE_STRING
order_clause: "ORDER" "BY" column ("ASC" | "DESC")?
SINGLE_STRING: /'[^']*'/

%import common.CNAME
%import common.NUMBER
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
"""

# Gramática NO AMBIGUA: precedencia OR < AND < NOT
SQL_GRAMMAR_UNAMBIGUOUS = r"""
?start: query
query: "SELECT" columns "FROM" table where_clause? order_clause?
columns: "*" | column ("," column)*
column: CNAME
table: CNAME
where_clause: "WHERE" condition

// SOLUCIÓN: jerarquía de precedencia
?condition: or_expr
?or_expr: and_expr ("OR" and_expr)*
?and_expr: not_expr ("AND" not_expr)*
?not_expr: "NOT" not_expr | "(" or_expr ")" | predicate

predicate: value comp value

comp: "=" | "<>" | "!=" | "<" | ">" | "<=" | ">="

value: CNAME | NUMBER | STRING | SINGLE_STRING
order_clause: "ORDER" "BY" column ("ASC" | "DESC")?
SINGLE_STRING: /'[^']*'/

%import common.CNAME
%import common.NUMBER
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
"""

def get_grammar(ambiguous=False):
    #Retorna la gramática ambigua o no ambigua.
    return SQL_GRAMMAR_AMBIGUOUS if ambiguous else SQL_GRAMMAR_UNAMBIGUOUS