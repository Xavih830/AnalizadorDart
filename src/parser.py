# -*- coding: utf-8 -*-
"""
Analizador Sintáctico (Parser) para el lenguaje Dart utilizando PLY.
Implementado de forma colaborativa por:
- Xavier Camacho (Xavih830)
- Manuel Matute (ManuelMatute)
- Johan Veloz (johegvel)
"""

import ply.yacc as yacc
from src.lexer import tokens, reserved
from src.ast_nodes import (
    Program, VarDeclaration, Block, IfStatement, ForStatement, ForInStatement,
    WhileStatement, DoWhileStatement, FunctionDeclaration, Parameter, ClassDeclaration,
    FieldDeclaration, ConstructorDeclaration, GetterDeclaration, MethodDeclaration,
    ReturnStatement, BreakStatement, ExpressionStatement, BinaryOp, UnaryOp, TernaryOp,
    CastExpression, TypeTest, Literal, Identifier, ListLiteral, MapLiteral, SetLiteral,
    IndexAccess, MemberAccess, FunctionCall, Argument, ImportStatement, CascadeExpression,
    MultiVarDeclaration
)

# Reglas de precedencia y asociatividad de operadores (Tabla 4 y precedencia Dart)
precedence = (
    ('right', 'ASSIGN', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN', 'INTDIV_ASSIGN', 'MOD_ASSIGN', 'COND_ASSIGN'),
    ('left', 'NULL_COALESCE'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'BIT_OR'),
    ('left', 'BIT_XOR'),
    ('left', 'BIT_AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'LE', 'GT', 'GE', 'IS', 'IS_NOT', 'AS'),
    ('left', 'LSHIFT', 'RSHIFT', 'URSHIFT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIV', 'INTDIV', 'MOD'),
    ('right', 'NOT', 'BIT_NOT', 'UNARY_MINUS', 'UNARY_PLUS'),
    ('left', 'INC', 'DEC', 'ASSERT_POSTFIX'), 
    ('left', 'DOT', 'NULL_SAFE_DOT', 'ASSERT_DOT', 'LBRACKET'),
)

_current_parser_errors = []
_current_parser = None

# --- Reglas Gramaticales ---

def p_program(p):
    '''program : top_level_statement_list
               | empty'''
    p[0] = Program(p[1] if p[1] is not None else [])

def p_top_level_statement_list(p):
    '''top_level_statement_list : top_level_statement_list top_level_statement
                               | top_level_statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_top_level_statement(p):
    '''top_level_statement : import_statement
                           | class_declaration
                           | function_declaration
                           | variable_declaration
                           | assignment_statement
                           | if_statement
                           | for_statement
                           | for_in_statement
                           | while_statement
                           | do_while_statement
                           | expression_statement
                           | block'''
    p[0] = p[1]

def p_block_statement_list(p):
    '''block_statement_list : block_statement_list block_statement
                            | block_statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_block_statement(p):
    '''block_statement : import_statement
                       | class_declaration
                       | variable_declaration
                       | assignment_statement
                       | if_statement
                       | for_statement
                       | for_in_statement
                       | while_statement
                       | do_while_statement
                       | return_statement
                       | break_statement
                       | expression_statement
                       | block'''
    p[0] = p[1]

# 1. Sentencia de Importación (Xavih830)
def p_import_statement(p):
    '''import_statement : IMPORT CADENA SEMICOLON'''
    uri = p[2][1:-1]
    p[0] = ImportStatement(uri, line=p.lineno(1))

# 2. Declaración de Variables con tipos inlined para evitar conflictos LALR (Xavier, Manuel y Johan)
def p_variable_declaration(p):
    '''variable_declaration : ID ID ASSIGN expression SEMICOLON
                            | ID ID SEMICOLON
                            | ID QMARK ID ASSIGN expression SEMICOLON
                            | ID QMARK ID SEMICOLON
                            | ID LT type_list GT ID ASSIGN expression SEMICOLON
                            | ID LT type_list GT ID SEMICOLON
                            | ID LT type_list GT QMARK ID ASSIGN expression SEMICOLON
                            | ID LT type_list GT QMARK ID SEMICOLON
                            | VAR ID ASSIGN expression SEMICOLON
                            | FINAL ID ASSIGN expression SEMICOLON
                            | FINAL ID ID ASSIGN expression SEMICOLON
                            | FINAL ID QMARK ID ASSIGN expression SEMICOLON
                            | FINAL ID LT type_list GT ID ASSIGN expression SEMICOLON
                            | FINAL ID LT type_list GT QMARK ID ASSIGN expression SEMICOLON
                            | CONST ID ASSIGN expression SEMICOLON
                            | CONST ID ID ASSIGN expression SEMICOLON
                            | CONST ID QMARK ID ASSIGN expression SEMICOLON
                            | CONST ID LT type_list GT ID ASSIGN expression SEMICOLON
                            | CONST ID LT type_list GT QMARK ID ASSIGN expression SEMICOLON
                            | ID ID ASSIGN expression COMA ID ASSIGN expression SEMICOLON'''
    if len(p) == 4:
        p[0] = VarDeclaration(p[2], p[1], None, line=p.lineno(2))
    elif len(p) == 5:
        p[0] = VarDeclaration(p[3], f"{p[1]}?", None, line=p.lineno(3))
    elif len(p) == 6:
        if p[1] == 'var':
            p[0] = VarDeclaration(p[2], 'var', p[4], line=p.lineno(2))
        elif p[1] == 'final':
            p[0] = VarDeclaration(p[2], None, p[4], is_final=True, line=p.lineno(2))
        elif p[1] == 'const':
            p[0] = VarDeclaration(p[2], None, p[4], is_const=True, line=p.lineno(2))
        else:
            p[0] = VarDeclaration(p[2], p[1], p[4], line=p.lineno(2))
    elif len(p) == 7:
        if p[2] == '?':
            p[0] = VarDeclaration(p[3], f"{p[1]}?", p[5], line=p.lineno(3))
        elif p[4] == '>':
            p[0] = VarDeclaration(p[5], f"{p[1]}<{p[3]}>", None, line=p.lineno(5))
        elif p[1] == 'final':
            p[0] = VarDeclaration(p[3], p[2], p[5], is_final=True, line=p.lineno(3))
        else:
            p[0] = VarDeclaration(p[3], p[2], p[5], is_const=True, line=p.lineno(3))
    elif len(p) == 8:
        if p[5] == '?':
            p[0] = VarDeclaration(p[6], f"{p[1]}<{p[3]}>?", None, line=p.lineno(6))
        elif p[1] == 'final':
            p[0] = VarDeclaration(p[4], f"{p[2]}?", p[6], is_final=True, line=p.lineno(4))
        else:
            p[0] = VarDeclaration(p[4], f"{p[2]}?", p[6], is_const=True, line=p.lineno(4))
    elif len(p) == 9:
        p[0] = VarDeclaration(p[5], f"{p[1]}<{p[3]}>", p[7], line=p.lineno(5))
    elif len(p) == 10:
        if p[5] == ',':
            decl1 = VarDeclaration(p[2], p[1], p[4], line=p.lineno(2))
            decl2 = VarDeclaration(p[6], p[1], p[8], line=p.lineno(6))
            p[0] = MultiVarDeclaration([decl1, decl2], line=p.lineno(2))
        elif p[5] == '?':
            p[0] = VarDeclaration(p[6], f"{p[1]}<{p[3]}>?", p[8], line=p.lineno(6))
        elif p[1] == 'final':
            p[0] = VarDeclaration(p[6], f"{p[2]}<{p[4]}>", p[8], is_final=True, line=p.lineno(6))
        else:
            p[0] = VarDeclaration(p[6], f"{p[2]}<{p[4]}>", p[8], is_const=True, line=p.lineno(6))
    elif len(p) == 11:
        if p[1] == 'final':
            p[0] = VarDeclaration(p[7], f"{p[2]}<{p[4]}>?", p[9], is_final=True, line=p.lineno(7))
        else:
            p[0] = VarDeclaration(p[7], f"{p[2]}<{p[4]}>?", p[9], is_const=True, line=p.lineno(7))


# 3. Sentencia de Asignación Directa o Compuesta (ManuelMatute)
def p_assignment_statement(p):
    '''assignment_statement : expression ASSIGN expression SEMICOLON
                            | expression ADD_ASSIGN expression SEMICOLON
                            | expression SUB_ASSIGN expression SEMICOLON
                            | expression MUL_ASSIGN expression SEMICOLON
                            | expression DIV_ASSIGN expression SEMICOLON
                            | expression INTDIV_ASSIGN expression SEMICOLON
                            | expression MOD_ASSIGN expression SEMICOLON
                            | expression COND_ASSIGN expression SEMICOLON'''
    p[0] = ExpressionStatement(BinaryOp(p[1], p[2], p[3], line=p.lineno(2)), line=p.lineno(2))

# 4. Estructuras de Control: Condicional If/Else (Xavih830)
def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN block_statement
                    | IF LPAREN expression RPAREN block_statement ELSE block_statement'''
    if len(p) == 6:
        p[0] = IfStatement(p[3], p[5], line=p.lineno(1))
    else:
        p[0] = IfStatement(p[3], p[5], p[7], line=p.lineno(1))

# 5. Estructuras de Control: Bucles For y For-in (ManuelMatute)
def p_for_statement(p):
    '''for_statement : FOR LPAREN variable_declaration expression SEMICOLON expression RPAREN block_statement
                     | FOR LPAREN expression_statement expression SEMICOLON expression RPAREN block_statement
                     | FOR LPAREN SEMICOLON expression SEMICOLON expression RPAREN block_statement'''
    if len(p) == 9:
        p[0] = ForStatement(p[3], p[4], p[6], p[8], line=p.lineno(1))
    else:
        p[0] = ForStatement(None, p[4], p[6], p[8], line=p.lineno(1))

def p_for_in_statement(p):
    '''for_in_statement : FOR LPAREN ID ID IN expression RPAREN block_statement
                        | FOR LPAREN ID LT type_list GT ID IN expression RPAREN block_statement
                        | FOR LPAREN VAR ID IN expression RPAREN block_statement
                        | FOR LPAREN ID IN expression RPAREN block_statement'''
    if len(p) == 9:
        if p[3] == 'var':
            p[0] = ForInStatement('var', p[4], p[6], p[8], line=p.lineno(1))
        else:
            p[0] = ForInStatement(p[3], p[4], p[6], p[8], line=p.lineno(1))
    elif len(p) == 8:
        p[0] = ForInStatement(None, p[3], p[5], p[7], line=p.lineno(1))
    else: # len == 12: generic type for-in (e.g. MapEntry<String, Producto> e in ...)
        p[0] = ForInStatement(f"{p[3]}<{p[5]}>", p[7], p[9], p[11], line=p.lineno(1))

# 6. Estructuras de Control: Bucle While y Do-While (johegvel)
def p_while_statement(p):
    '''while_statement : WHILE LPAREN expression RPAREN block_statement'''
    p[0] = WhileStatement(p[3], p[5], line=p.lineno(1))

def p_do_while_statement(p):
    '''do_while_statement : DO block_statement WHILE LPAREN expression RPAREN SEMICOLON'''
    p[0] = DoWhileStatement(p[2], p[5], line=p.lineno(1))

# 7. Sentencias de Retorno y Control de Bucle
def p_return_statement(p):
    '''return_statement : RETURN expression SEMICOLON
                        | RETURN SEMICOLON'''
    if len(p) == 4:
        p[0] = ReturnStatement(p[2], line=p.lineno(1))
    else:
        p[0] = ReturnStatement(None, line=p.lineno(1))

def p_break_statement(p):
    '''break_statement : BREAK SEMICOLON'''
    p[0] = BreakStatement(line=p.lineno(1))

# 8. Sentencia de Expresión Única
def p_expression_statement(p):
    '''expression_statement : expression SEMICOLON'''
    p[0] = ExpressionStatement(p[1], line=p.lineno(2))

def p_block(p):
    '''block : LBRACE block_statement_list RBRACE
             | LBRACE RBRACE'''
    if len(p) == 4:
        p[0] = Block(p[2])
    else:
        p[0] = Block([])


# --- Declaraciones de Funciones con inlining de tipos para LALR ---

def p_function_declaration(p):
    '''function_declaration : ID ID LPAREN parameter_list RPAREN block
                            | ID ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                            | ID QMARK ID LPAREN parameter_list RPAREN block
                            | ID QMARK ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                            | ID LT type_list GT ID LPAREN parameter_list RPAREN block
                            | ID LT type_list GT ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                            | ID LT type_list GT QMARK ID LPAREN parameter_list RPAREN block
                            | ID LT type_list GT QMARK ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                            | VOID ID LPAREN parameter_list RPAREN block
                            | VOID ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                            | ID LPAREN parameter_list RPAREN block
                            | ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON'''
    if len(p) == 6:
        p[0] = FunctionDeclaration(p[1], None, p[3], p[5], is_arrow=False, line=p.lineno(1))
    elif len(p) == 7:
        if p[1] == 'void':
            p[0] = FunctionDeclaration(p[2], 'void', p[4], p[6], is_arrow=False, line=p.lineno(2))
        else:
            p[0] = FunctionDeclaration(p[2], p[1], p[4], p[6], is_arrow=False, line=p.lineno(2))
    elif len(p) == 8:
        if p[2] == '?':
            p[0] = FunctionDeclaration(p[3], f"{p[1]}?", p[5], p[7], is_arrow=False, line=p.lineno(3))
        else:
            p[0] = FunctionDeclaration(p[1], None, p[3], p[6], is_arrow=True, line=p.lineno(1))
    elif len(p) == 9:
        if p[1] == 'void':
            p[0] = FunctionDeclaration(p[2], 'void', p[4], p[7], is_arrow=True, line=p.lineno(2))
        else:
            p[0] = FunctionDeclaration(p[2], p[1], p[4], p[7], is_arrow=True, line=p.lineno(2))
    elif len(p) == 10:
        if p[2] == '?':
            p[0] = FunctionDeclaration(p[3], f"{p[1]}?", p[5], p[8], is_arrow=True, line=p.lineno(3))
        else:
            p[0] = FunctionDeclaration(p[5], f"{p[1]}<{p[3]}>", p[7], p[9], is_arrow=False, line=p.lineno(5))
    elif len(p) == 11:
        p[0] = FunctionDeclaration(p[6], f"{p[1]}<{p[3]}>?", p[8], p[10], is_arrow=False, line=p.lineno(6))
    elif len(p) == 12:
        p[0] = FunctionDeclaration(p[5], f"{p[1]}<{p[3]}>", p[7], p[10], is_arrow=True, line=p.lineno(5))
    elif len(p) == 13:
        p[0] = FunctionDeclaration(p[6], f"{p[1]}<{p[3]}>?", p[8], p[11], is_arrow=True, line=p.lineno(6))


# Manejo de Listas sin conflictos de reducción de vacíos
def p_parameter_list(p):
    '''parameter_list : parameter_list_not_empty
                      | empty'''
    p[0] = p[1] if p[1] is not None else []

def p_parameter_list_not_empty(p):
    '''parameter_list_not_empty : positional_parameters
                                | positional_parameters COMA named_parameters
                                | named_parameters'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[3]

def p_positional_parameters(p):
    '''positional_parameters : positional_parameters COMA parameter
                             | parameter'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_named_parameters(p):
    '''named_parameters : LBRACE named_parameter_list RBRACE'''
    p[0] = p[2]

def p_named_parameter_list(p):
    '''named_parameter_list : named_parameter_list COMA named_parameter
                            | named_parameter'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# Parámetros inlined
def p_parameter(p):
    '''parameter : ID ID
                 | ID
                 | ID LT type_list GT ID
                 | ID QMARK ID
                 | ID LT type_list GT QMARK ID
                 | THIS DOT ID
                 | REQUIRED THIS DOT ID
                 | REQUIRED ID ID
                 | REQUIRED ID
                 | REQUIRED ID LT type_list GT ID
                 | REQUIRED ID QMARK ID
                 | REQUIRED ID LT type_list GT QMARK ID'''
    if len(p) == 2:
        p[0] = Parameter(p[1], None)
    elif len(p) == 3:
        if p[1] == 'required':
            p[0] = Parameter(p[2], None, is_required=True)
        else:
            p[0] = Parameter(p[2], p[1])
    elif len(p) == 4:
        if p[1] == 'this':
            p[0] = Parameter(p[3], None, is_this=True)
        elif p[1] == 'required':
            p[0] = Parameter(p[3], p[2], is_required=True)
        elif p[2] == '?':
            p[0] = Parameter(p[3], f"{p[1]}?", is_required=False)
    elif len(p) == 5:
        if p[2] == 'this':
            p[0] = Parameter(p[4], None, is_required=True, is_this=True)
        else:
            p[0] = Parameter(p[4], f"{p[2]}?", is_required=True)
    elif len(p) == 6:
        p[0] = Parameter(p[5], f"{p[1]}<{p[3]}>")
    elif len(p) == 7:
        if p[1] == 'required':
            p[0] = Parameter(p[6], f"{p[2]}<{p[4]}>", is_required=True)
        else:
            p[0] = Parameter(p[6], f"{p[1]}<{p[3]}>?")
    elif len(p) == 8:
        p[0] = Parameter(p[7], f"{p[2]}<{p[4]}>?", is_required=True)

def p_named_parameter(p):
    '''named_parameter : parameter
                       | parameter ASSIGN expression
                       | REQUIRED parameter
                       | REQUIRED parameter ASSIGN expression'''
    if len(p) == 2:
        p[1].is_named = True
        p[0] = p[1]
    elif len(p) == 3:
        if p[1] == 'required':
            p[2].is_required = True
            p[2].is_named = True
            p[0] = p[2]
        else:
            p[1].default_value = p[3]
            p[1].is_named = True
            p[0] = p[1]
    else:
        p[2].is_required = True
        p[2].default_value = p[4]
        p[2].is_named = True
        p[0] = p[2]


# --- Estructuras de Clases (johegvel) ---

def p_class_declaration(p):
    '''class_declaration : CLASS ID LBRACE class_member_list RBRACE'''
    p[0] = ClassDeclaration(p[2], p[4], line=p.lineno(1))

def p_class_member_list(p):
    '''class_member_list : class_member_list class_member
                         | empty'''
    if len(p) == 3:
        if p[1] is None:
            p[0] = [p[2]]
        else:
            p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_class_member(p):
    '''class_member : field_declaration
                    | constructor_declaration
                    | getter_declaration
                    | method_declaration'''
    p[0] = p[1]

def p_field_declaration(p):
    '''field_declaration : ID ID SEMICOLON
                         | ID QMARK ID SEMICOLON
                         | ID LT type_list GT ID SEMICOLON
                         | ID LT type_list GT QMARK ID SEMICOLON
                         | FINAL ID ID SEMICOLON
                         | FINAL ID QMARK ID SEMICOLON
                         | FINAL ID LT type_list GT ID SEMICOLON
                         | FINAL ID LT type_list GT QMARK ID SEMICOLON
                         | VAR ID ASSIGN expression SEMICOLON'''
    if len(p) == 4:
        if p[1] == 'var':
            p[0] = FieldDeclaration(p[2], 'var', line=p.lineno(2))
        else:
            p[0] = FieldDeclaration(p[2], p[1], line=p.lineno(2))
    elif len(p) == 5:
        if p[1] == 'final':
            p[0] = FieldDeclaration(p[3], p[2], is_final=True, line=p.lineno(3))
        else: # ID QMARK ID SEMICOLON
            p[0] = FieldDeclaration(p[3], f"{p[1]}?", line=p.lineno(3))
    elif len(p) == 6:
        if p[1] == 'final':
            p[0] = FieldDeclaration(p[4], f"{p[2]}?", is_final=True, line=p.lineno(4))
        else: # ID LT type_list GT ID SEMICOLON
            p[0] = FieldDeclaration(p[5], f"{p[1]}<{p[3]}>", line=p.lineno(5))
    elif len(p) == 7:
        if p[1] == 'final':
            p[0] = FieldDeclaration(p[6], f"{p[2]}<{p[4]}>", is_final=True, line=p.lineno(6))
        else: # ID LT type_list GT QMARK ID SEMICOLON
            p[0] = FieldDeclaration(p[6], f"{p[1]}<{p[3]}>?", line=p.lineno(6))
    else: # len(p) == 8
        p[0] = FieldDeclaration(p[7], f"{p[2]}<{p[4]}>?", is_final=True, line=p.lineno(7))

def p_constructor_declaration(p):
    '''constructor_declaration : ID LPAREN parameter_list RPAREN block
                               | ID LPAREN parameter_list RPAREN SEMICOLON'''
    if len(p) == 6:
        p[0] = ConstructorDeclaration(p[1], p[3], body=p[5], line=p.lineno(1))
    else:
        p[0] = ConstructorDeclaration(p[1], p[3], body=None, line=p.lineno(1))

def p_getter_declaration(p):
    '''getter_declaration : ID GET ID ARROW expression SEMICOLON
                          | ID LT type_list GT GET ID ARROW expression SEMICOLON
                          | GET ID ARROW expression SEMICOLON'''
    if len(p) == 7:
        p[0] = GetterDeclaration(p[3], p[1], p[5], line=p.lineno(3))
    elif len(p) == 9:
        p[0] = GetterDeclaration(p[6], f"{p[1]}<{p[3]}>", p[8], line=p.lineno(6))
    else:
        p[0] = GetterDeclaration(p[2], None, p[4], line=p.lineno(2))

def p_method_declaration(p):
    '''method_declaration : method_modifier ID ID LPAREN parameter_list RPAREN block
                          | method_modifier ID ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | method_modifier ID QMARK ID LPAREN parameter_list RPAREN block
                          | method_modifier ID QMARK ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | method_modifier ID LT type_list GT ID LPAREN parameter_list RPAREN block
                          | method_modifier ID LT type_list GT ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | method_modifier ID LT type_list GT QMARK ID LPAREN parameter_list RPAREN block
                          | method_modifier ID LT type_list GT QMARK ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | method_modifier VOID ID LPAREN parameter_list RPAREN block
                          | method_modifier VOID ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | method_modifier ID LPAREN parameter_list RPAREN block
                          | method_modifier ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | ID ID LPAREN parameter_list RPAREN block
                          | ID ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | ID QMARK ID LPAREN parameter_list RPAREN block
                          | ID QMARK ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | ID LT type_list GT ID LPAREN parameter_list RPAREN block
                          | ID LT type_list GT ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | ID LT type_list GT QMARK ID LPAREN parameter_list RPAREN block
                          | ID LT type_list GT QMARK ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | VOID ID LPAREN parameter_list RPAREN block
                          | VOID ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON
                          | ID LPAREN parameter_list RPAREN block
                          | ID LPAREN parameter_list RPAREN ARROW expression SEMICOLON'''
    # Para simplificar la decodificación de las 24 combinaciones (con/sin anotación, tipo retorno, arrow/block):
    # Determinamos la anotación, el tipo de retorno y dónde empiezan los parámetros.
    offset = 0
    annotation = None
    
    if isinstance(p[1], str) and p[1].startswith('@'):
        annotation = [p[1]]
        offset = 1
        
    # Desplazamos los índices basándonos en si tiene anotación
    t_ret = p[1 + offset]
    p_name = p[2 + offset]
    
    if p_name == '(':
        # Método sin tipo de retorno declarador (e.g. main())
        name = p[1 + offset]
        params = p[3 + offset]
        body = p[5 + offset]
        p[0] = MethodDeclaration(name, None, params, body, annotations=annotation, line=p.lineno(1+offset))
    elif p[3 + offset] == '(':
        # Método con tipo simple o void (e.g. String toString() o void show())
        name = p[2 + offset]
        params = p[4 + offset]
        body = p[6 + offset]
        p[0] = MethodDeclaration(name, t_ret, params, body, annotations=annotation, line=p.lineno(2+offset))
    elif p[3 + offset] == '?':
        # Tipo opcional (e.g. int? getVal())
        name = p[4 + offset]
        params = p[6 + offset]
        body = p[8 + offset]
        p[0] = MethodDeclaration(name, f"{t_ret}?", params, body, annotations=annotation, line=p.lineno(4+offset))
    else: # Genéricos (e.g. List<int> getList())
        # p[3+offset] es LT, p[4+offset] es type_list, p[5+offset] es GT, p[6+offset] es ID (nombre)
        name = p[6 + offset]
        
        if p[7 + offset] == '?':
            # Genérico nullable
            params = p[9 + offset]
            body = p[11 + offset]
            p[0] = MethodDeclaration(name, f"{t_ret}<{p[4+offset]}>?", params, body, annotations=annotation, line=p.lineno(6+offset))
        else:
            params = p[8 + offset]
            body = p[10 + offset]
            p[0] = MethodDeclaration(name, f"{t_ret}<{p[4+offset]}>", params, body, annotations=annotation, line=p.lineno(6+offset))

def p_method_modifier(p):
    '''method_modifier : AT ID'''
    p[0] = f"@{p[2]}"


# --- Tipos de Datos Genéricos ---

def p_type(p):
    '''type : ID
            | ID LT type_list GT
            | type QMARK'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3: # type QMARK
        p[0] = f"{p[1]}?"
    else: # ID LT type_list GT
        p[0] = f"{p[1]}<{p[3]}>"

def p_type_list(p):
    '''type_list : type_list COMA type
                 | type'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]}, {p[3]}"


# --- Expresiones (Aritméticas, Booleanas, Colecciones, Lambdas) ---

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIV expression
                  | expression INTDIV expression
                  | expression MOD expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression AND expression
                  | expression OR expression
                  | expression BIT_AND expression
                  | expression BIT_OR expression
                  | expression BIT_XOR expression
                  | expression LSHIFT expression
                  | expression RSHIFT expression
                  | expression URSHIFT expression
                  | expression NULL_COALESCE expression'''
    p[0] = BinaryOp(p[1], p[2], p[3], line=p.lineno(2))

def p_expression_unop_prefix(p):
    '''expression : INC expression
                  | DEC expression
                  | MINUS expression %prec UNARY_MINUS
                  | PLUS expression %prec UNARY_PLUS
                  | NOT expression
                  | BIT_NOT expression'''
    p[0] = UnaryOp(p[1], p[2], is_postfix=False, line=p.lineno(1))

def p_expression_unop_postfix(p):
    '''expression : expression INC
                  | expression DEC
                  | expression NOT %prec ASSERT_POSTFIX'''
    p[0] = UnaryOp(p[2], p[1], is_postfix=True, line=p.lineno(2))

def p_expression_ternary(p):
    '''expression : expression QMARK expression COLON expression'''
    p[0] = TernaryOp(p[1], p[3], p[5], line=p.lineno(2))

def p_expression_cast(p):
    '''expression : expression AS type'''
    p[0] = CastExpression(p[1], p[3], line=p.lineno(2))

def p_expression_type_test(p):
    '''expression : expression IS type
                  | expression IS_NOT type'''
    is_neg = (p[2] == 'is!')
    p[0] = TypeTest(p[1], p[3], is_negated=is_neg, line=p.lineno(2))

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_identifier(p):
    '''expression : ID'''
    p[0] = Identifier(p[1], line=p.lineno(1))

# Literales Básicos
def p_expression_literal(p):
    '''expression : NUM_ENTERO
                  | NUM_DECIMAL
                  | CADENA
                  | TRUE
                  | FALSE
                  | NULL'''
    if p[1] == 'true':
        p[0] = Literal(True, 'bool', line=p.lineno(1))
    elif p[1] == 'false':
        p[0] = Literal(False, 'bool', line=p.lineno(1))
    elif p[1] == 'null':
        p[0] = Literal(None, 'Null', line=p.lineno(1))
    elif isinstance(p[1], str):
        p[0] = Literal(p[1][1:-1], 'String', line=p.lineno(1))
    elif isinstance(p[1], float):
        p[0] = Literal(p[1], 'double', line=p.lineno(1))
    else:
        p[0] = Literal(p[1], 'int', line=p.lineno(1))

# Colección: List Literal
def p_expression_list_literal(p):
    '''expression : LBRACKET expression_list RBRACKET
                  | LBRACKET expression_list COMA RBRACKET
                  | LT type GT LBRACKET expression_list RBRACKET
                  | LT type GT LBRACKET expression_list COMA RBRACKET'''
    if len(p) in (4, 5):
        p[0] = ListLiteral(p[2], line=p.lineno(1))
    else:
        p[0] = ListLiteral(p[5], type_param=p[2], line=p.lineno(4))

# Colección: Map y Set Literales (Sin conflictos LALR de reducción de vacío)
def p_expression_map_or_set_literal(p):
    '''expression : LBRACE RBRACE
                  | LBRACE key_value_list_not_empty RBRACE
                  | LBRACE key_value_list_not_empty COMA RBRACE
                  | LBRACE expression_list_not_empty RBRACE
                  | LBRACE expression_list_not_empty COMA RBRACE
                  | LT type_list GT LBRACE RBRACE
                  | LT type_list GT LBRACE key_value_list_not_empty RBRACE
                  | LT type_list GT LBRACE key_value_list_not_empty COMA RBRACE
                  | LT type_list GT LBRACE expression_list_not_empty RBRACE
                  | LT type_list GT LBRACE expression_list_not_empty COMA RBRACE'''
    if len(p) in (3, 4, 5):
        if len(p) == 3:
            p[0] = MapLiteral([], line=p.lineno(1))
        else:
            entries = p[2]
            if isinstance(entries[0], tuple):
                p[0] = MapLiteral(entries, line=p.lineno(1))
            else:
                p[0] = SetLiteral(entries, line=p.lineno(1))
    else:
        types = p[2].split(",")
        entries = p[5] if len(p) in (7, 8) else []
        if len(types) >= 2:
            p[0] = MapLiteral(entries or [], key_type=types[0].strip(), value_type=types[1].strip(), line=p.lineno(4))
        else:
            p[0] = SetLiteral(entries or [], type_param=types[0].strip(), line=p.lineno(4))

def p_key_value_list_not_empty(p):
    '''key_value_list_not_empty : key_value_list_not_empty COMA key_value
                                 | key_value'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_key_value(p):
    '''key_value : expression COLON expression'''
    p[0] = (p[1], p[3])

def p_expression_list(p):
    '''expression_list : expression_list_not_empty
                       | empty'''
    p[0] = p[1] if p[1] is not None else []

def p_expression_list_not_empty(p):
    '''expression_list_not_empty : expression_list_not_empty COMA expression
                                 | expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# Acceso por índice e invocación (Xavier, Manuel y Johan)
def p_expression_index_access(p):
    '''expression : expression LBRACKET expression RBRACKET'''
    p[0] = IndexAccess(p[1], p[3], line=p.lineno(2))

def p_expression_member_access(p):
    '''expression : expression DOT ID
                  | expression NULL_SAFE_DOT ID
                  | expression ASSERT_DOT ID'''
    is_ns = (p[2] == '?.')
    is_as = (p[2] == '!.')
    p[0] = MemberAccess(p[1], p[3], is_null_safe=is_ns, is_assert=is_as, line=p.lineno(3))

def p_expression_function_call(p):
    '''expression : expression LPAREN argument_list RPAREN'''
    p[0] = FunctionCall(p[1], p[3], line=p.lineno(2))

def p_argument_list(p):
    '''argument_list : argument_list_not_empty
                     | empty'''
    p[0] = p[1] if p[1] is not None else []

def p_argument_list_not_empty(p):
    '''argument_list_not_empty : argument_list_not_empty COMA argument
                               | argument'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_argument(p):
    '''argument : expression
                | ID COLON expression'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Argument(p[1], p[3])

# Invocación de Cascadas (.. y ?..)
def p_expression_cascade(p):
    '''expression : expression CASCADE cascade_section
                  | expression NULL_SAFE_CASCADE cascade_section'''
    p[0] = CascadeExpression(p[1], p[3], line=p.lineno(2))

def p_cascade_section(p):
    '''cascade_section : cascade_section CASCADE cascade_operation
                       | cascade_operation'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_cascade_operation(p):
    '''cascade_operation : ID LPAREN argument_list RPAREN
                         | ID ASSIGN expression
                         | ID'''
    if len(p) == 5:
        p[0] = FunctionCall(Identifier(p[1]), p[3])
    elif len(p) == 4:
        p[0] = BinaryOp(Identifier(p[1]), '=', p[3])
    else:
        p[0] = Identifier(p[1])

# Funciones Anónimas / Lambdas (johegvel)
def p_expression_lambda(p):
    '''expression : LPAREN parameter_list RPAREN ARROW expression
                  | LPAREN parameter_list RPAREN block'''
    is_arr = (p[4] == '=>')
    body_node = p[5] if is_arr else p[4]
    p[0] = FunctionDeclaration("anonymous", None, p[2], body_node, is_arrow=is_arr, line=p.lineno(1))


# --- Auxiliares ---

def p_empty(p):
    '''empty :'''
    p[0] = None


# --- Manejo de Errores Sintácticos (p_error) ---

def p_error(p):
    global _current_parser_errors
    if p:
        error_msg = f"ERROR_SINTACTICO: token inesperado '{p.value}' de tipo {p.type} en la linea {p.lineno}"
        err = {
            'phase': 'Sintáctico',
            'category': 'ERROR_SINTACTICO',
            'message': error_msg,
            'line': p.lineno,
            'lexeme': str(p.value)
        }
        _current_parser_errors.append(err)
        global _current_parser
        if _current_parser:
            _current_parser.errok()
    else:
        error_msg = "ERROR_SINTACTICO: fin de archivo inesperado (EOF)"
        err = {
            'phase': 'Sintáctico',
            'category': 'ERROR_SINTACTICO',
            'message': error_msg,
            'line': 0,
            'lexeme': 'EOF'
        }
        _current_parser_errors.append(err)


# --- API Pública ---

def get_parser():
    """Genera e inicializa una instancia del parser yacc."""
    return yacc.yacc(write_tables=False, debug=False)

def parse(code):
    """
    Parsea una cadena de código fuente de Dart.
    Retorna una tupla: (árbol AST, lista de errores sintácticos).
    """
    global _current_parser_errors, _current_parser
    _current_parser_errors = []
    
    from src.lexer import get_lexer
    lexer = get_lexer()
    
    parser = get_parser()
    _current_parser = parser
    
    try:
        ast = parser.parse(code, lexer=lexer)
        lex_errors = lexer.errors
        all_errors = lex_errors + _current_parser_errors
        return ast, all_errors
    except Exception as e:
        all_errors = _current_parser_errors + [{
            'phase': 'Sintáctico',
            'category': 'FATAL',
            'message': f"Error interno del parser: {str(e)}",
            'line': 0,
            'lexeme': ''
        }]
        return None, all_errors
