#Parser principal para consultas SQL
#Maneja el parsing, detección de ambigüedad y generación de árboles

from lark import Lark, Tree
from lark.exceptions import LarkError, UnexpectedInput, UnexpectedCharacters
from typing import Optional, List, Tuple
import logging

from ..grammar.sql_grammar import get_grammar
from .parse_tree import ParseTree

logger = logging.getLogger(__name__)

class SQLParser:
    #Analizador de consultas SQL con soporte para detección de ambigüedades

    def __init__(self, ambiguous: bool = False, detect_ambiguity: bool = False):
        """
        Inicializa el parser SQL.
        
        Args:
            ambiguous (bool): Si True, usa la gramática ambigua
            detect_ambiguity (bool): Si True, detecta múltiples derivaciones
        """
        self.ambiguous = ambiguous
        self.detect_ambiguity = detect_ambiguity
        self._grammar_string = get_grammar(ambiguous=ambiguous)
        self._parser = self._create_parser()

    def _create_parser(self) -> Optional[Lark]:
        #Crea el parser de Lark con la configuración apropiada
        try:
            parser_config = {
                'start': 'query',
                'parser': 'earley',  # Earley puede manejar ambigüedad
            }
            
            # Si queremos detectar ambigüedad explícitamente
            if self.detect_ambiguity:
                parser_config['ambiguity'] = 'explicit'
            
            parser = Lark(self._grammar_string, **parser_config)
            logger.info(f"Parser creado (ambiguo={self.ambiguous}, detectar_ambigüedad={self.detect_ambiguity})")
            return parser
            
        except Exception as e:
            logger.error(f"Error al crear parser: {e}")
            return None
        
    def parse(self, query: str) -> Optional[ParseTree]:
        """
        Parsea una consulta SQL.
        
        Args:
            query (str): Consulta SQL a parsear
            
        Returns:
            ParseTree: Árbol de derivación, o None si hay error
        """
        if not self._parser:
            logger.error("Parser no inicializado")
            return None
        
        if not query or not query.strip():
            logger.error("Consulta vacía")
            return None
        
        try:
            tree = self._parser.parse(query)
            
            # Verificar si hay ambigüedad detectada
            is_ambiguous = hasattr(tree, 'data') and tree.data == '_ambig'
            
            if is_ambiguous:
                logger.info(f"Ambigüedad detectada: {len(tree.children)} derivaciones")
                # Crear ParseTree para cada derivación
                return ParseTree(tree, query, is_ambiguous=True)
            else:
                logger.info("Consulta parseada exitosamente")
                return ParseTree(tree, query, is_ambiguous=False)
                
        except UnexpectedCharacters as e:
            logger.error(f"Carácter inesperado en posición {e.pos_in_stream}: '{e.char}'")
            return None
            
        except UnexpectedInput as e:
            logger.error(f"Entrada inesperada: {e}")
            return None
            
        except LarkError as e:
            logger.error(f"Error de parsing: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Error inesperado: {type(e).__name__}: {e}")
            return None
        
    def parse_multiple(self, queries: List[str]) -> List[Tuple[str, Optional[ParseTree]]]:
        """
        Parsea múltiples consultas.
        
        Args:
            queries (List[str]): Lista de consultas SQL
            
        Returns:
            List[Tuple[str, Optional[ParseTree]]]: Lista de (query, árbol)
        """
        results = []
        for query in queries:
            tree = self.parse(query)
            results.append((query, tree))
        return results
    
    def validate_syntax(self, query: str) -> Tuple[bool, str]:
        """
        Valida únicamente la sintaxis sin generar el árbol completo.
        
        Args:
            query (str): Consulta SQL
            
        Returns:
            Tuple[bool, str]: (es_válida, mensaje)
        """
        try:
            self._parser.parse(query)
            return True, "Sintaxis válida"
        except UnexpectedCharacters as e:
            return False, f"Carácter inesperado '{e.char}' en posición {e.pos_in_stream}"
        except UnexpectedInput as e:
            return False, f"Entrada inesperada: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_grammar(self) -> str:
        #Retorna la gramática actual como string
        return self._grammar_string
    
    def is_ambiguous_grammar(self) -> bool:
        #Retorna si se está usando la gramática ambigua
        return self.ambiguous