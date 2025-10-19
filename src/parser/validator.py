"""
Validador de consultas SQL
Realiza validaciones sintácticas y semánticas
"""

from typing import List, Tuple, Optional
import logging
from .sql_parser import SQLParser
from .parse_tree import ParseTree

logger = logging.getLogger(__name__)


class SQLValidator:
    #Validador de consultas SQL con análisis sintáctico y semántico
    
    def __init__(self):
        self.parser = SQLParser(ambiguous=False)
    
    def validate_query(self, query: str) -> Tuple[bool, List[str], Optional[ParseTree]]:
        """
        Valida una consulta SQL completa.
        
        Args:
            query (str): Consulta SQL
            
        Returns:
            Tuple[bool, List[str], Optional[ParseTree]]: 
                (es_válida, lista_errores/warnings, árbol)
        """
        errors = []
        warnings = []
        
        # Validación básica
        if not query or not query.strip():
            errors.append("Consulta vacía")
            return False, errors, None
        
        # Validar sintaxis
        tree = self.parser.parse(query)
        if not tree:
            errors.append("Error de sintaxis en la consulta")
            return False, errors, None
        
        # Validaciones semánticas
        semantic_errors = self._validate_semantics(tree, query)
        errors.extend(semantic_errors)
        
        # Validaciones de estilo
        style_warnings = self._validate_style(query)
        warnings.extend(style_warnings)
        
        is_valid = len(errors) == 0
        all_messages = errors + warnings
        
        return is_valid, all_messages, tree
    
    def _validate_semantics(self, tree: ParseTree, query: str) -> List[str]:
        #Validaciones semánticas
        errors = []
        
        # Validar que SELECT tenga al menos una columna
        columns = tree.extract_columns()
        if not columns and '*' not in query:
            errors.append("SELECT debe especificar al menos una columna")
        
        # Validar que haya una tabla
        table = tree.extract_table()
        if not table:
            errors.append("Debe especificar una tabla en FROM")
        
        # Validar duplicados en SELECT
        if len(columns) != len(set(columns)):
            duplicates = [col for col in columns if columns.count(col) > 1]
            errors.append(f"Columnas duplicadas en SELECT: {', '.join(set(duplicates))}")
        
        return errors
    
    def _validate_style(self, query: str) -> List[str]:
        """Validaciones de estilo (warnings)"""
        warnings = []
        
        # Verificar uso de palabras clave en mayúsculas (recomendado)
        keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'ORDER', 'BY']
        query_upper = query.upper()
        
        for keyword in keywords:
            if keyword.lower() in query.lower() and keyword not in query_upper:
                warnings.append(f"Recomendación: usar '{keyword}' en mayúsculas")
                break  # Solo un warning general
        
        # Verificar longitud excesiva
        if len(query) > 500:
            warnings.append("Query muy larga, considere dividirla")
        
        return warnings
    
    def validate_batch(self, queries: List[str]) -> List[Tuple[str, bool, List[str]]]:
        """
        Valida múltiples consultas.
        
        Args:
            queries (List[str]): Lista de consultas
            
        Returns:
            List[Tuple[str, bool, List[str]]]: Lista de (query, es_válida, errores)
        """
        results = []
        for query in queries:
            is_valid, messages, _ = self.validate_query(query)
            results.append((query, is_valid, messages))
        return results
    
    def check_ambiguity(self, query: str) -> Tuple[bool, int]:
        """
        Verifica si una consulta es ambigua.
        
        Args:
            query (str): Consulta SQL
            
        Returns:
            Tuple[bool, int]: (es_ambigua, número_de_derivaciones)
        """
        ambiguous_parser = SQLParser(ambiguous=True, detect_ambiguity=True)
        tree = ambiguous_parser.parse(query)
        
        if not tree:
            return False, 0
        
        return tree.is_ambiguous, tree.get_derivation_count()