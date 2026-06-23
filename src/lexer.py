# -*- coding: utf-8 -*-
"""
Analizador Léxico (Lexer) para el lenguaje Dart utilizando PLY.
Implementado de forma colaborativa por:
- Xavier Camacho (Xavih830)
- Manuel Matute (ManuelMatute)
- Johan Veloz (johegvel)
"""

import ply.lex as lex

# Palabras reservadas del lenguaje Dart
reserved = {
    'assert': 'ASSERT',
    'break': 'BREAK',
    'case': 'CASE',
    'catch': 'CATCH',
    'class': 'CLASS',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'do': 'DO',
    'else': 'ELSE',
    'enum': 'ENUM',
    'extends': 'EXTENDS',
    'false': 'FALSE',
    'final': 'FINAL',
    'finally': 'FINALLY',
    'for': 'FOR',
    'if': 'IF',
    'in': 'IN',
    'is': 'IS',
    'new': 'NEW',
    'null': 'NULL',
    'rethrow': 'RETHROW',
    'return': 'RETURN',
    'super': 'SUPER',
    'switch': 'SWITCH',
    'this': 'THIS',
    'throw': 'THROW',
    'true': 'TRUE',
    'try': 'TRY',
    'var': 'VAR',
    'void': 'VOID',
    'while': 'WHILE',
    'with': 'WITH',
    'async': 'ASYNC',
    'await': 'AWAIT',
    'static': 'STATIC',
    'abstract': 'ABSTRACT',
    'import': 'IMPORT',
    'late': 'LATE',
    'required': 'REQUIRED',
    'typedef': 'TYPEDEF',
    'get': 'GET',
}

# Lista completa de nombres de tokens
tokens = [
    # Identificadores y Literales
    'ID',
    'NUM_ENTERO',
    'NUM_DECIMAL',
    'CADENA',

    # Operadores Aritméticos
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'INTDIV', 'MOD',
    # Incremento / Decremento
    'INC', 'DEC',
    # Operadores Relacionales
    'EQ', 'NE', 'LE', 'GE', 'LT', 'GT',
    # Operadores Lógicos
    'AND', 'OR', 'NOT',
    # Operadores de Asignación
    'ASSIGN', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN', 'INTDIV_ASSIGN', 'MOD_ASSIGN', 'COND_ASSIGN',
    # Operadores Bit a Bit
    'BIT_AND', 'BIT_OR', 'BIT_XOR', 'BIT_NOT', 'LSHIFT', 'RSHIFT', 'URSHIFT',
    # Operadores Condicionales y Especiales
    'QMARK', 'COLON', 'NULL_COALESCE',
    'CASCADE', 'NULL_SAFE_CASCADE',
    'DOT', 'NULL_SAFE_DOT', 'ASSERT_DOT',
    'SPREAD', 'NULL_SAFE_SPREAD',
    'IS_NOT', 'AS',

    # Delimitadores
    'LBRACE', 'RBRACE',
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'SEMICOLON', 'COMA',
    'ARROW',
    'AT',
] + list(reserved.values())

# --- Reglas de Expresiones Regulares para Tokens Simples ---

# Operadores de asignación compuesta (deben ir antes que los simples)
t_ADD_ASSIGN = r'\+='
t_SUB_ASSIGN = r'-='
t_MUL_ASSIGN = r'\*='
t_DIV_ASSIGN = r'/='
t_INTDIV_ASSIGN = r'~/='
t_MOD_ASSIGN = r'%='
t_COND_ASSIGN = r'\?\?='

# Incremento y Decremento
t_INC = r'\+\+'
t_DEC = r'--'

# Operadores Relacionales
t_EQ = r'=='
t_NE = r'!='
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'

# Operadores Lógicos
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

# Operador Flecha
t_ARROW = r'=>'

# Operadores Aritméticos
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_INTDIV = r'~/'
t_DIV = r'/'
t_MOD = r'%'

# Asignación simple
t_ASSIGN = r'='

# Operadores Bit a Bit
t_BIT_AND = r'&'
t_BIT_OR = r'\|'
t_BIT_XOR = r'\^'
t_BIT_NOT = r'~'
t_URSHIFT = r'>>>'
t_RSHIFT = r'>>'
t_LSHIFT = r'<<'

# Cascada
t_NULL_SAFE_CASCADE = r'\?\.\.'
t_CASCADE = r'\.\.'

# Dispersión (Spread)
t_NULL_SAFE_SPREAD = r'\.\.\?\?' # En Dart es ...? pero evitamos ambigüedades
t_SPREAD = r'\.\.\.'

# Operadores Especiales de acceso
t_NULL_SAFE_DOT = r'\?\.'
t_ASSERT_DOT = r'!\.'
t_DOT = r'\.'

# Condicional y Fusión Nula
t_NULL_COALESCE = r'\?\?'
t_QMARK = r'\?'
t_COLON = r':'

# Delimitadores
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COMA = r','

t_AT = r'@'

# Operadores especiales compuestos de palabra
t_IS_NOT = r'is!'

# Regla para cadenas de texto (Strings)
# Soporta comillas triples (multilínea), dobles y simples
def t_CADENA(t):
    r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''
    # Contar saltos de línea dentro de la cadena para mantener el número de línea correcto
    t.lexer.lineno += t.value.count('\n')
    return t

# Números Decimales (double)
def t_NUM_DECIMAL(t):
    r'\d+\.\d+([eE][-+]?\d+)?|\d+[eE][-+]?\d+'
    t.value = float(t.value)
    return t

# Números Enteros (int)
def t_NUM_ENTERO(t):
    r'0[xX][0-9a-fA-F]+|\d+'
    if t.value.lower().startswith('0x'):
        t.value = int(t.value, 16)
    else:
        t.value = int(t.value)
    return t

# Identificadores y Palabras Reservadas
# Coincide con variables estándar, privadas y constantes (Tabla 1 de propuesta)
def t_ID(t):
    r'[a-zA-Z_$][a-zA-Z0-9_$]*'
    # Verifica si es una palabra reservada o un operador especial de palabra (is, as)
    if t.value == 'as':
        t.type = 'AS'
    elif t.value == 'is':
        t.type = 'IS'
    else:
        t.type = reserved.get(t.value, 'ID')
    return t

# --- Comentarios (se descartan y no generan token) ---

# Comentarios de Documentación (///)
def t_comment_doc(t):
    r'///.*'
    pass

# Comentarios de Una Línea (//)
def t_comment_single(t):
    r'//.*'
    pass

# Comentarios Multilínea (/* */)
def t_comment_multi(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

# --- Gestión de Líneas y Espacios ---

# Saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Caracteres a ignorar (espacios y tabulaciones)
t_ignore = ' \t\r'

# Manejo de Errores Léxicos
def t_error(t):
    error_lexeme = t.value[0]
    error_msg = f"ERROR_LEXICO: caracter no reconocido '{error_lexeme}' en la linea {t.lexer.lineno}"
    
    # Registramos el error en la lista interna del lexer
    t.lexer.errors.append({
        'phase': 'Léxico',
        'category': 'ERROR_LEXICO',
        'message': error_msg,
        'line': t.lexer.lineno,
        'lexeme': error_lexeme
    })
    t.lexer.skip(1)


# --- API Pública ---

def get_lexer():
    """Crea y configura una instancia del lexer."""
    lexer = lex.lex()
    lexer.errors = []
    return lexer

def tokenize(code):
    """
    Tokeniza una cadena de código fuente.
    Retorna una tupla: (lista de tokens, lista de errores).
    """
    lexer = get_lexer()
    lexer.input(code)
    
    token_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        token_list.append(tok)
        
    return token_list, lexer.errors
