#Representación del arbol de derivaciones

from lark import Tree, Token
from typing import List, Optional, Any
import json

class TreeNode:
    #Nodo del árbol de derivación
    
    def __init__(self, name: str, children: Optional[list['TreeNode']] = None, value: Optional[Any] = None):
        self.name = name
        self.children = children if children else []
        self.value = value

    def is_terminal(self) -> bool:
        #Verifica si el nodo es terminal (hoja)
        return len(self.children) == 0 and self.value is not None
    
    def is_nonterminal(self) -> bool:
        #Verifica si el nodo es no terminal
        return len(self.children) > 0
    
    def __repr__(self):
        if self.is_terminal():
            return f"TreeNode({self.name}={self.value})"
        return f"TreeNode({self.name}, children={len(self.children)})"

class ParseTree:
    #Árbol de derivación con funcionalidades

    def __init__(self, lark_tree: Tree, original_query: str, is_ambiguous: bool = False):
        """
        Inicializa el árbol de derivación.
        
        Args:
            lark_tree (Tree): Árbol de Lark
            original_query (str): Consulta SQL original
            is_ambiguous (bool): Si el árbol contiene ambigüedad
        """
        self.lark_tree = lark_tree
        self.original_query = original_query
        
        # Detectar ambigüedad buscando nodos _ambig
        self.is_ambiguous = self._detect_ambiguity(lark_tree)
        self.trees = self._extract_ambiguous_trees(lark_tree)
    

    def _detect_ambiguity(self, tree) -> bool:
        """Detecta si hay nodos _ambig en el árbol"""
        if isinstance(tree, Tree):
            if tree.data == '_ambig':
                return True
            for child in tree.children:
                if self._detect_ambiguity(child):
                    return True
        return False

    def _extract_ambiguous_trees(self, tree) -> List[Tree]:
        """Extrae todos los árboles alternativos si hay ambigüedad"""
        # Buscar el primer nodo _ambig
        ambig_node = self._find_ambig_node(tree)
        
        if ambig_node and ambig_node.data == '_ambig':
            # Los hijos de _ambig son las diferentes derivaciones
            return list(ambig_node.children)
        else:
            return [tree]

    def _find_ambig_node(self, tree):
        """Encuentra el primer nodo _ambig"""
        if isinstance(tree, Tree):
            if tree.data == '_ambig':
                return tree
            for child in tree.children:
                result = self._find_ambig_node(child)
                if result:
                    return result
        return None

    def get_derivation_count(self) -> int:
        #Retorna el número de derivaciones posibles
        return len(self.trees)
    
    def get_pretty_string(self, tree_index: int = 0) -> str:
        """
        Retorna una representación legible del árbol.
        
        Args:
            tree_index (int): Índice del árbol (si hay ambigüedad)
            
        Returns:
            str: Representación en texto del árbol
        """
        if tree_index >= len(self.trees):
            return f"Error: índice {tree_index} fuera de rango (hay {len(self.trees)} árboles)"
        
        return self.trees[tree_index].pretty()
    
    def get_all_pretty_strings(self) -> List[str]:
        #Retorna representaciones de todos los árboles (en caso de ambigüedad)
        return [tree.pretty() for tree in self.trees]
    
    def to_dict(self, tree_index: int = 0) -> dict:
        """
        Convierte el árbol a diccionario.
        
        Args:
            tree_index (int): Índice del árbol
            
        Returns:
            dict: Representación en diccionario
        """
        if tree_index >= len(self.trees):
            return {"error": f"Índice {tree_index} fuera de rango"}
        
        return {
            "query": self.original_query,
            "is_ambiguous": self.is_ambiguous,
            "derivation_count": self.get_derivation_count(),
            "tree": self._tree_to_dict(self.trees[tree_index])
        }
    
    def _tree_to_dict(self, node) -> dict:
        #Convierte un nodo de Lark a diccionario recursivamente
        if isinstance(node, Token):
            return {
                "type": "token",
                "name": node.type,
                "value": str(node)
            }
        elif isinstance(node, Tree):
            return {
                "type": "tree",
                "name": node.data,
                "children": [self._tree_to_dict(child) for child in node.children]
            }
        else:
            return {"type": "unknown", "value": str(node)}
        
    def to_json(self, tree_index: int = 0, indent: int = 2) -> str:
        #Convierte el árbol a JSON
        return json.dumps(self.to_dict(tree_index), indent=indent, ensure_ascii=False)
    
    def get_depth(self, tree_index: int = 0) -> int:
        #Calcula la profundidad del árbol
        if tree_index >= len(self.trees):
            return 0
        return self._calculate_depth(self.trees[tree_index])
    
    def _calculate_depth(self, node, current_depth: int = 0) -> int:
        #Calcula profundidad recursivamente
        if isinstance(node, Token):
            return current_depth
        elif isinstance(node, Tree):
            if not node.children:
                return current_depth
            return max(self._calculate_depth(child, current_depth + 1) 
                      for child in node.children)
        return current_depth
    
    def get_node_count(self, tree_index: int = 0) -> int:
        #Cuenta el número total de nodos en el árbol
        if tree_index >= len(self.trees):
            return 0
        return self._count_nodes(self.trees[tree_index])
    
    def _count_nodes(self, node) -> int:
        #Cuenta nodos recursivamente
        if isinstance(node, Token):
            return 1
        elif isinstance(node, Tree):
            return 1 + sum(self._count_nodes(child) for child in node.children)
        return 0
    
    def extract_columns(self, tree_index: int = 0) -> List[str]:
        #Extrae los nombres de columnas del SELECT únicamente
        columns = []
        tree = self.trees[tree_index] if tree_index < len(self.trees) else None
        if tree:
            # Buscar solo dentro del nodo 'columns'
            self._extract_columns_from_select(tree, columns)
        return columns
        
    def _extract_columns_from_select(self, node, columns: List[str]):
    #Extrae columnas SOLO del SELECT, no del ORDER BY"""
        if isinstance(node, Tree):
            # Solo procesar si estamos en el nodo 'columns' del SELECT
            if node.data == 'columns':
                for child in node.children:
                    if isinstance(child, Tree) and child.data == 'column':
                        for subchild in child.children:
                            if isinstance(subchild, Token):
                                columns.append(str(subchild))
                return  # No seguir buscando fuera de 'columns'
            
            # Continuar búsqueda solo hasta encontrar 'columns'
            if node.data != 'order_clause':  # Evitar ORDER BY
                for child in node.children:
                    self._extract_columns_from_select(child, columns)

    def extract_table(self, tree_index: int = 0) -> Optional[str]:
        #Extrae el nombre de la tabla
        tree = self.trees[tree_index] if tree_index < len(self.trees) else None
        if tree:
            return self._extract_table_recursive(tree)
        return None
    
    def _extract_table_recursive(self, node) -> Optional[str]:
        #Extrae tabla recursivamente
        if isinstance(node, Tree):
            if node.data == 'table':
                for child in node.children:
                    if isinstance(child, Token):
                        return str(child)
            for child in node.children:
                result = self._extract_table_recursive(child)
                if result:
                    return result
        return None
    
    def __str__(self):
        return self.get_pretty_string(0)
    
    def __repr__(self):
        return f"ParseTree(query='{self.original_query}', derivations={self.get_derivation_count()}, ambiguous={self.is_ambiguous})"
    



