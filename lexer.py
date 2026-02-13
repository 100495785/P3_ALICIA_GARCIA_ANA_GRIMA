# lexer.py
import ply.lex as lex

# ----------------------------
# Palabras reservadas
# ----------------------------
reserved = {
    'true': 'TRUE',
    'false': 'FALSE',
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'boolean': 'BOOLEAN',
    'void': 'VOID',
    'return': 'RETURN',
    'if': 'IF',
    'else': 'ELSE',
    'do': 'DO',
    'while': 'WHILE',
    'print': 'PRINT',
    'new': 'NEW',
    'record': 'RECORD',
    'break': 'BREAK',
}

# ----------------------------
# Lista de tokens
# ----------------------------
tokens = [
    # Identificadores
    'ID',

    # Literales
    'INT_VALUE',
    'FLOAT_VALUE',
    'CHAR_VALUE',

    # Operadores aritméticos
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',

    # Operadores booleanos
    'AND', 'OR', 'NOT',

    # Operadores comparativos
    'GE', 'GT', 'LE', 'LT', 'EQ',

    # Asignación
    'ASSIGN',

    # Delimitadores
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'SEMICOLON',
    'COMMA',
    'DOT',
] + list(reserved.values())

# ----------------------------
# Ignorados (espacios/tab)
# ----------------------------
t_ignore = ' \t'

# ----------------------------
# Tokens simples (regex directas)
# IMPORTANTE: poner compuestos antes que simples
# ----------------------------

# Comparativos compuestos antes que simples
t_GE = r'>='
t_LE = r'<='
t_EQ = r'=='

t_GT = r'>'
t_LT = r'<'

# Booleanos
t_AND = r'&&'
t_OR  = r'\|\|'
t_NOT = r'!'

# Aritméticos
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'

# Asignación (después de ==)
t_ASSIGN = r'='

# Delimitadores
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_SEMICOLON = r';'
t_COMMA     = r','
t_DOT       = r'\.'

# ----------------------------
# Comentarios
# ----------------------------

def t_COMMENT_SINGLE(t):
    r'//[^\n]*'
    # Se ignora por completo
    pass

def t_COMMENT_MULTI(t):
    r'/\*[\s\S]*?\*/'
    # Ajuste de líneas si hay saltos dentro del comentario
    t.lexer.lineno += t.value.count('\n')
    pass

# ----------------------------
# Saltos de línea
# ----------------------------

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# ----------------------------
# Literales
# ----------------------------

def t_FLOAT_VALUE(t):
    r'([0-9]+\.[0-9]+([eE][+-]?[0-9]+)?)|([0-9]+[eE][+-]?[0-9]+)'
    return t

def t_INT_VALUE(t):
    r'0b[01]+|0x[0-9A-F]+|0[0-7]+|[1-9][0-9]*|0'
    return t

def t_CHAR_VALUE(t):
    r"\'(.|\n)\'"
    # Si quisieras prohibir salto de línea dentro del char, cambia a r"\'[^\n]\'"
    # Pero el PDF dice “cualquier carácter”, y los comentarios multilínea ya lo cubren.
    return t

# ----------------------------
# Identificadores / Reservadas
# ----------------------------

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# ----------------------------
# Columna (utilidad para main.py)
# ----------------------------

def find_column(input_text: str, token) -> int:
    """
    Devuelve columna (0-index) del inicio del token.
    """
    last_cr = input_text.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = -1
    return token.lexpos - last_cr - 1

# ----------------------------
# Error léxico
# ----------------------------

def t_error(t):
    # Mantener simple en P1: reporta y avanza
    # (No aborta, permite sacar más tokens)
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)
