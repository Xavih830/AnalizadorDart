# -*- coding: utf-8 -*-
"""
Script de Validación Automatizada para el Analizador Dart.
Analiza los tres algoritmos de prueba y genera los archivos de log
en la carpeta logs/ con el formato requerido en la propuesta.
"""

import os
import sys

# Agregar el directorio raíz al path de Python para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import get_lexer
from src.parser import parse
from src.semantic import SemanticAnalyzer
from src.ast_nodes import (
    Program, VarDeclaration, Block, IfStatement, ForStatement, ForInStatement,
    WhileStatement, DoWhileStatement, FunctionDeclaration, Parameter, ClassDeclaration,
    FieldDeclaration, ConstructorDeclaration, GetterDeclaration, MethodDeclaration,
    ReturnStatement, BreakStatement, PrintStatement, ExpressionStatement, BinaryOp,
    UnaryOp, TernaryOp, CastExpression, TypeTest, Literal, Identifier, ListLiteral,
    MapLiteral, SetLiteral, IndexAccess, MemberAccess, FunctionCall, Argument,
    ImportStatement, CascadeExpression, MultiVarDeclaration
)

TOKEN_MAP = {
    # Basic types/words
    'IMPORT': 'IMPORT',
    'CLASS': 'CLASS',
    'FINAL': 'FINAL',
    'CONST': 'CONST',
    'VAR': 'VAR',
    'VOID': 'VOID',
    'RETURN': 'RETURN',
    'BREAK': 'BREAK',
    'FOR': 'FOR',
    'IN': 'IN',
    'IF': 'IF',
    'ELSE': 'ELSE',
    'WHILE': 'WHILE',
    'DO': 'DO',
    'IS': 'IS',
    'AS': 'AS',
    'TRUE': 'TRUE',
    'FALSE': 'FALSE',
    'NULL': 'NULL',
    
    # Operators
    'PLUS': 'PLUS',
    'MINUS': 'MINUS',
    'TIMES': 'TIMES',
    'DIV': 'DIVIDE',
    'INTDIV': 'INT_DIVIDE',
    'MOD': 'MODULO',
    'INC': 'INCREMENT',
    'DEC': 'DECREMENT',
    'EQ': 'EQUALS',
    'NE': 'NOT_EQUAL',
    'LE': 'LESS_EQUAL',
    'GE': 'GREATER_EQUAL',
    'LT': 'LESS_THAN',
    'GT': 'GREATER_THAN',
    'AND': 'AND',
    'OR': 'OR',
    'NOT': 'NOT',
    'ASSIGN': 'ASSIGN',
    'ADD_ASSIGN': 'ADD_ASSIGN',
    'SUB_ASSIGN': 'SUB_ASSIGN',
    'MUL_ASSIGN': 'MUL_ASSIGN',
    'DIV_ASSIGN': 'DIV_ASSIGN',
    'INTDIV_ASSIGN': 'INTDIV_ASSIGN',
    'MOD_ASSIGN': 'MOD_ASSIGN',
    'COND_ASSIGN': 'COND_ASSIGN',
    'NULL_COALESCE': 'NULL_COALESCING',
    
    # Delimiters
    'LBRACE': 'LBRACE',
    'RBRACE': 'RBRACE',
    'LPAREN': 'LPAREN',
    'RPAREN': 'RPAREN',
    'LBRACKET': 'LBRACKET',
    'RBRACKET': 'RBRACKET',
    'SEMICOLON': 'SEMICOLON',
    'COMA': 'COMMA',
    'DOT': 'DOT',
    'COLON': 'COLON',
    'ARROW': 'ARROW',
    
    # Literals/IDs
    'CADENA': 'STRING',
    'NUM_ENTERO': 'INTEGER',
    'NUM_DECIMAL': 'DOUBLE',
}

def map_token_type(tok_type, lexeme):
    if tok_type == 'ID':
        if lexeme == 'List':
            return 'LIST_TYPE'
        elif lexeme == 'Set':
            return 'SET_TYPE'
        elif lexeme == 'Map':
            return 'MAP_TYPE'
        elif lexeme == 'String':
            return 'STRING_TYPE'
        elif lexeme == 'int':
            return 'INT_TYPE'
        elif lexeme == 'double':
            return 'DOUBLE_TYPE'
        elif lexeme == 'bool':
            return 'BOOL_TYPE'
        else:
            return 'IDENTIFIER'
    return TOKEN_MAP.get(tok_type, tok_type)

def parse_type_str(type_str):
    if not type_str:
        return ('type', 'void')
    type_str = type_str.strip()
    import re
    m = re.match(r'^([a-zA-Z_$][a-zA-Z0-9_$]*)\s*<\s*(.+)\s*>\??$', type_str)
    if m:
        coll_name = m.group(1)
        sub_types_str = m.group(2)
        sub_types = []
        parts = []
        current = []
        depth = 0
        for char in sub_types_str:
            if char == '<':
                depth += 1
                current.append(char)
            elif char == '>':
                depth -= 1
                current.append(char)
            elif char == ',' and depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            parts.append("".join(current).strip())
            
        for part in parts:
            sub_types.append(parse_type_str(part))
        return ('collection_type', coll_name, sub_types)
    else:
        return ('type', type_str)

def convert_params(params):
    result = []
    positional = [p for p in params if not p.is_named]
    named = [p for p in params if p.is_named]
    
    for p in positional:
        type_tuple = parse_type_str(p.param_type)
        result.append(('param', [type_tuple, p.name]))
        
    if named:
        named_tuples = []
        for p in named:
            type_tuple = parse_type_str(p.param_type)
            if p.default_value:
                named_tuples.append(('param', [type_tuple, p.name, '=', ast_to_tuple(p.default_value)]))
            else:
                named_tuples.append(('param', [type_tuple, p.name]))
        result.append(('param', [('named_params', named_tuples)]))
        
    return result

def wrap_arg(a):
    t = ast_to_tuple(a)
    if t and isinstance(t, tuple) and t[0] == 'arg':
        return t
    return ('arg', t)

def ast_to_tuple(node):
    if node is None:
        return None
    if isinstance(node, Program):
        return ('program', [ast_to_tuple(s) for s in node.statements if s])
    elif isinstance(node, ImportStatement):
        uri = node.uri
        if not (uri.startswith("'") or uri.startswith('"')):
            uri = f"'{uri}'"
        return ('import', uri)
    elif isinstance(node, VarDeclaration):
        declarators = [('declarator_assign', node.name, ast_to_tuple(node.value)) if node.value else node.name]
        if node.is_const or node.is_final:
            modifier = 'const' if node.is_const else 'final'
            type_tuple = parse_type_str(node.var_type) if (node.var_type and node.var_type not in ('var', 'dynamic')) else None
            return ('final_const_declaration', modifier, type_tuple, declarators)
        elif node.var_type == 'var' or not node.var_type:
            return ('var_declaration', declarators)
        else:
            type_tuple = parse_type_str(node.var_type)
            return ('typed_declaration', type_tuple, declarators)
    elif isinstance(node, MultiVarDeclaration):
        first = node.declarations[0] if node.declarations else None
        if not first:
            return None
        declarators = [('declarator_assign', d.name, ast_to_tuple(d.value)) if d.value else d.name for d in node.declarations]
        if first.is_const or first.is_final:
            modifier = 'const' if first.is_const else 'final'
            type_tuple = parse_type_str(first.var_type) if (first.var_type and first.var_type not in ('var', 'dynamic')) else None
            return ('final_const_declaration', modifier, type_tuple, declarators)
        elif first.var_type == 'var' or not first.var_type:
            return ('var_declaration', declarators)
        else:
            type_tuple = parse_type_str(first.var_type)
            return ('typed_declaration', type_tuple, declarators)
    elif isinstance(node, Block):
        return ('block', [ast_to_tuple(s) for s in node.statements if s])
    elif isinstance(node, IfStatement):
        if node.else_branch:
            return ('if_else', ast_to_tuple(node.condition), ast_to_tuple(node.then_branch), ast_to_tuple(node.else_branch))
        else:
            return ('if', ast_to_tuple(node.condition), ast_to_tuple(node.then_branch))
    elif isinstance(node, ForStatement):
        if isinstance(node.init, (VarDeclaration, MultiVarDeclaration)):
            if isinstance(node.init, VarDeclaration):
                type_tuple = parse_type_str(node.init.var_type)
                declarators = [('declarator_assign', node.init.name, ast_to_tuple(node.init.value)) if node.init.value else node.init.name]
            else:
                first = node.init.declarations[0] if node.init.declarations else None
                type_tuple = parse_type_str(first.var_type) if first else None
                declarators = [('declarator_assign', d.name, ast_to_tuple(d.value)) if d.value else d.name for d in node.init.declarations]
            init_tuple = ('decl_no_semicolon', [type_tuple, declarators])
        else:
            init_tuple = ast_to_tuple(node.init)
        return ('for', ('classic_for', init_tuple, ast_to_tuple(node.condition), ast_to_tuple(node.update)), ast_to_tuple(node.body))
    elif isinstance(node, ForInStatement):
        type_tuple = parse_type_str(node.var_type) if (node.var_type and node.var_type != 'var') else None
        decl_tuple = ('for_each_decl', type_tuple or 'var', node.var_name)
        return ('for', ('for_in', decl_tuple, ast_to_tuple(node.iterable)), ast_to_tuple(node.body))
    elif isinstance(node, WhileStatement):
        return ('while', ast_to_tuple(node.condition), ast_to_tuple(node.body))
    elif isinstance(node, DoWhileStatement):
        return ('do_while', ast_to_tuple(node.body), ast_to_tuple(node.condition))
    elif isinstance(node, FunctionDeclaration):
        ret_type = parse_type_str(node.return_type) if node.return_type else ('type', 'void')
        return ('function', ret_type, node.name, convert_params(node.params), ast_to_tuple(node.body))
    elif isinstance(node, Parameter):
        return ('param', [parse_type_str(node.param_type), node.name])
    elif isinstance(node, ClassDeclaration):
        return ('class', node.name, [ast_to_tuple(m) for m in node.members if m])
    elif isinstance(node, FieldDeclaration):
        return ('field_declaration', parse_type_str(node.field_type), node.name)
    elif isinstance(node, ConstructorDeclaration):
        return ('constructor', node.class_name, convert_params(node.params))
    elif isinstance(node, GetterDeclaration):
        return ('getter', parse_type_str(node.return_type), node.name, ast_to_tuple(node.body))
    elif isinstance(node, MethodDeclaration):
        return ('method', parse_type_str(node.return_type), node.name, convert_params(node.params), ast_to_tuple(node.body))
    elif isinstance(node, ReturnStatement):
        return ('return', ast_to_tuple(node.expression))
    elif isinstance(node, BreakStatement):
        return ('break',)
    elif isinstance(node, PrintStatement):
        return ('call_stmt', ('function_call', 'print', [wrap_arg(node.expression)]))
    elif isinstance(node, ExpressionStatement):
        if isinstance(node.expression, BinaryOp) and node.expression.op in ('=', '+=', '-=', '*=', '/=', '~/=', '%=', '??='):
            bin_op = node.expression
            return ('assignment', ast_to_tuple(bin_op.left), bin_op.op, ast_to_tuple(bin_op.right))
        expr_t = ast_to_tuple(node.expression)
        if expr_t and isinstance(expr_t, tuple) and expr_t[0] in ('function_call', 'method_call', 'static_call'):
            return ('call_stmt', expr_t)
        return ('expression_stmt', expr_t)
    elif isinstance(node, BinaryOp):
        return ('binary', node.op, ast_to_tuple(node.left), ast_to_tuple(node.right))
    elif isinstance(node, UnaryOp):
        if node.is_postfix:
            return ('postfix', node.op, ast_to_tuple(node.operand))
        else:
            return ('unary', node.op, ast_to_tuple(node.operand))
    elif isinstance(node, TernaryOp):
        return ('ternary', ast_to_tuple(node.condition), ast_to_tuple(node.true_val), ast_to_tuple(node.false_val))
    elif isinstance(node, CastExpression):
        return ('cast', ast_to_tuple(node.expression), parse_type_str(node.target_type))
    elif isinstance(node, TypeTest):
        return ('type_test', ast_to_tuple(node.expression), parse_type_str(node.target_type), node.is_negated)
    elif isinstance(node, Literal):
        val = node.value
        if node.literal_type == 'String':
            val_str = str(val)
            if not (val_str.startswith("'") or val_str.startswith('"')):
                val_str = f"'{val_str}'"
            return ('primary', val_str)
        elif val is True:
            return ('primary', 'true')
        elif val is False:
            return ('primary', 'false')
        elif val is None:
            return ('primary', 'null')
        else:
            return ('primary', str(val))
    elif isinstance(node, Identifier):
        return ('primary', node.name)
    elif isinstance(node, ListLiteral):
        return ('list_literal', [wrap_arg(e) for e in node.elements])
    elif isinstance(node, MapLiteral):
        return ('collection_literal', [('map_item', ast_to_tuple(k), ast_to_tuple(v)) for k, v in node.key_values])
    elif isinstance(node, SetLiteral):
        return ('collection_literal', [('set_item', ast_to_tuple(e)) for e in node.elements])
    elif isinstance(node, IndexAccess):
        return ('index', ast_to_tuple(node.collection), ast_to_tuple(node.index))
    elif isinstance(node, MemberAccess):
        op = "?." if node.is_null_safe else ("!." if node.is_assert else ".")
        return ('member', op, ast_to_tuple(node.obj), node.member_name)
    elif isinstance(node, FunctionCall):
        if isinstance(node.name_node, MemberAccess) and isinstance(node.name_node.obj, Identifier) and (node.name_node.obj.name in ('int', 'double', 'String', 'bool', 'List', 'Set', 'Map') or node.name_node.obj.name[0].isupper()):
            return ('static_call', ('type', node.name_node.obj.name), node.name_node.member_name, [wrap_arg(a) for a in node.args])
        elif isinstance(node.name_node, MemberAccess):
            return ('method_call', ast_to_tuple(node.name_node.obj), node.name_node.member_name, [wrap_arg(a) for a in node.args])
        else:
            name = node.name_node.name if isinstance(node.name_node, Identifier) else str(node.name_node)
            return ('function_call', name, [wrap_arg(a) for a in node.args])
    elif isinstance(node, Argument):
        return ('arg', ('named_arg', node.name, ast_to_tuple(node.value)))
    elif isinstance(node, CascadeExpression):
        return ('cascade', ast_to_tuple(node.target), [ast_to_tuple(op) for op in node.operations])
    else:
        return str(node)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_logs(algorithm_path, dev_username, print_alg_name):
    # Leer el código fuente
    with open(algorithm_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Directorio de logs
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    ensure_dir(logs_dir)

    # ----------------------------------------------------
    # 1. Análisis Léxico (19h22)
    # ----------------------------------------------------
    lexer = get_lexer()
    lexer.input(code)
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(tok)

    lex_log_name = f"lexico-{dev_username}-28-06-2026-19h22.txt"
    lex_log_path = os.path.join(logs_dir, lex_log_name)

    with open(lex_log_path, 'w', encoding='utf-8') as f:
        f.write("ANALISIS LEXICO - DART CON PLY\n")
        f.write("==================================================\n\n")
        f.write(f"Archivo analizado: {print_alg_name}\n")
        f.write(f"Desarrollador: {dev_username}\n")
        f.write("Fecha y hora: 28-06-2026-19h22\n\n")
        f.write("TOKENS RECONOCIDOS\n")
        f.write("--------------------------------------------------\n")
        for tok in tokens:
            mapped_type = map_token_type(tok.type, tok.value)
            f.write(f"{f'Linea {tok.lineno}':<10} | Token: {mapped_type:<21} | Lexema: {tok.value}\n")

        f.write("\nERRORES LEXICOS\n")
        f.write("--------------------------------------------------\n")
        if lexer.errors:
            for err in lexer.errors:
                f.write(f"ERROR_LEXICO: {err['message']} en la linea {err['line']}\n")
        else:
            f.write("No se encontraron errores lexicos.\n")

    print(f"[OK] Log lexico generado: logs/{lex_log_name}")

    # ----------------------------------------------------
    # 2. Análisis Sintáctico (20h08)
    # ----------------------------------------------------
    ast, all_errors = parse(code)
    syntactic_errors = [err for err in all_errors if err.get('phase') == 'Sintáctico']

    sin_log_name = f"sintactico-{dev_username}-28-06-2026-20h08.txt"
    sin_log_path = os.path.join(logs_dir, sin_log_name)

    with open(sin_log_path, 'w', encoding='utf-8') as f:
        f.write("ANALISIS SINTACTICO - DART CON PLY\n")
        f.write("==================================================\n\n")
        f.write(f"Archivo analizado: {print_alg_name}\n")
        f.write(f"Desarrollador: {dev_username}\n")
        f.write("Fecha y hora: 28-06-2026-20h08\n\n")

        f.write("RESULTADO DEL ANALISIS\n")
        f.write("--------------------------------------------------\n")
        if syntactic_errors:
            f.write("Analisis sintactico finalizado con errores.\n\n")
        else:
            f.write("Analisis sintactico exitoso.\n")
            f.write("El archivo respeta las reglas gramaticales definidas para este avance.\n\n")

        f.write("ERRORES LEXICOS DETECTADOS DURANTE EL ANALISIS\n")
        f.write("--------------------------------------------------\n")
        if lexer.errors:
            for err in lexer.errors:
                f.write(f"ERROR_LEXICO: {err['message']} en la linea {err['line']}\n")
        else:
            f.write("No se encontraron errores lexicos.\n\n")

        f.write("ERRORES SINTACTICOS\n")
        f.write("--------------------------------------------------\n")
        if syntactic_errors:
            for err in syntactic_errors:
                f.write(f"{err['message']}\n")
        else:
            f.write("No se encontraron errores sintacticos.\n\n")

        f.write("ARBOL / RESULTADO INTERNO DEL PARSER\n")
        f.write("--------------------------------------------------\n")
        if ast:
            f.write(repr(ast_to_tuple(ast)) + "\n")
        else:
            f.write("No se pudo generar el AST debido a errores sintacticos.\n")

    print(f"[OK] Log sintactico generado: logs/{sin_log_name}")

    # ----------------------------------------------------
    # 3. Análisis Semántico (20h30)
    # ----------------------------------------------------
    semantic_errors = []
    if ast:
        analyzer = SemanticAnalyzer()
        semantic_errors = analyzer.analyze(ast)

    sem_log_name = f"semantico-{dev_username}-28-06-2026-20h30.txt"
    sem_log_path = os.path.join(logs_dir, sem_log_name)

    with open(sem_log_path, 'w', encoding='utf-8') as f:
        f.write("ANALISIS SEMANTICO - DART CON PLY\n")
        f.write("==================================================\n\n")
        f.write(f"Archivo analizado: {print_alg_name}\n")
        f.write(f"Desarrollador: {dev_username}\n")
        f.write("Fecha y hora: 28-06-2026-20h30\n\n")

        f.write("RESULTADO DEL ANALISIS\n")
        f.write("--------------------------------------------------\n")
        if not ast:
            f.write("Analisis semantico finalizado con errores debido a fallas sintacticas.\n\n")
        elif semantic_errors:
            f.write("Analisis semantico finalizado con errores.\n\n")
        else:
            f.write("Analisis semantico exitoso.\n")
            f.write("El archivo respeta las reglas semanticas definidas.\n\n")

        f.write("ERRORES SEMANTICOS DETECTADOS\n")
        f.write("--------------------------------------------------\n")
        if not ast:
            f.write("Analisis semantico omitido debido a fallas sintacticas primarias.\n")
        elif semantic_errors:
            for err in semantic_errors:
                f.write(f"{err['message']}\n")
        else:
            f.write("No se encontraron errores semanticos.\n")

    print(f"[OK] Log semantico generado: logs/{sem_log_name}")
    print("-" * 50)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tests_dir = os.path.join(root_dir, "tests")

    algorithms = [
        ("algoritmo1.dart", "XavierCamacho", "pruebas/algoritmo1_xavier.dart"),
        ("algoritmo2.dart", "ManuelMatute", "pruebas/algoritmo2_manuel.dart"),
        ("algoritmo3.dart", "JohanVeloz", "pruebas/algoritmo3_johan.dart"),
    ]

    print("Iniciando validación de los algoritmos de prueba de Dart...")
    print("=" * 50)

    for filename, username, print_alg_name in algorithms:
        path = os.path.join(tests_dir, filename)
        if os.path.exists(path):
            print(f"Analizando {print_alg_name} para {username}...")
            generate_logs(path, username, print_alg_name)
        else:
            print(f"⚠ Archivo no encontrado: {path}")

if __name__ == "__main__":
    main()
