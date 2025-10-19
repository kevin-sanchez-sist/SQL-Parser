# Cargador y Validador de gramaticas

from lark import Lark
from lark.exceptions import GrammarError
from typing import Optional
import logging

logger = logging.getLogger(__name__)

#clase para cargar y validar gramaticas para el parser
class GrammarLoader:

    def __init__(self):
        self._cached_parsers = {}

    def load_grammar(self, grammar_string: str, start_symbol: str = "query") -> Optional[Lark]:
        """
        Carga una gramática desde un string.
        Args:
            grammar_string (str): Definición de la gramática
            start_symbol (str): Símbolo inicial de la gramática 
        Returns: Lark: Parser configurado, o None si hay error
        """
        cache_key = hash(grammar_string + start_symbol)

        if cache_key in self._cached_parsers:
            logger.debug("Usando gramática en caché")
            return self._cached_parsers[cache_key]
        
        try:
            parser = Lark(
                grammar_string,
                start=start_symbol,
                parser='earley',  # Earley maneja ambigüedad
                ambiguity='explicit'  # Detecta ambigüedad
            )
            self._cached_parsers[cache_key] = parser
            logger.info(f"Gramática cargada exitosamente (símbolo inicial: {start_symbol})")
            return parser
        except GrammarError as e:
            logger.error(f"Error en la gramática: {e}")
            return None
        
    def validate_grammar(self, grammar_string: str) -> tuple[bool, str]:
        """
        Valida si una gramática es sintácticamente correcta.
        Args: grammar_string (str): Definición de la gramática   
        Returns: tuple: (es_valida, mensaje)
        """
        try:
            Lark(grammar_string, start="start")
            return True, "Gramatica válida"
        except GrammarError as e:
            return False, f"Error de gramática: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"