# Analizador léxico para la P1 de Lava utilizando PLY, que define:
# - El conjunto de tokens del lenguaje
# - Las reglas léxicas mediante expresiones regulares 
# - El tratamiento de palabras reservadas
# - La gestión de comentarios y espacios en blanco

import ply.lex as lex
from ply.lex import TOKEN


# ===== Palabras reservadas =====
reserved = (
    "TRUE",
    "BOOLEAN",
    "DO",
    "FALSE",
    "VOID",
    "WHILE",
    "INT",
    "RETURN",
    "PRINT",
    "FLOAT",
    "IF",
    "NEW",
    "CHAR",
    "ELSE",
    "RECORD",
    "BREAK",
)

reserved_map = {}
for r_type in reserved:
    reserved_map[r_type.lower()] = r_type


# ===== Tokens =====

tokens = reserved + (
    # Identificadores y literales
    "ID",
    "INT_VALUE",
    "FLOAT_VALUE",
    "CHAR_VALUE",
    # Operadores (comparación / booleanos / aritmética)
    "ASSIGN",   # =
    "EQ",       # ==
    "GT",       # >
    "GE",       # >=
    "LT",       # <
    "LE",       # <=
    "PLUS",     # +
    "MINUS",    # -
    "TIMES",    # *
    "DIVIDE",   # /
    "AND",      # &&
    "OR",       # ||
    "NOT",      # !
    # Separadores / puntuación
    "LPAREN",   # (
    "RPAREN",   # )
    "LBRACE",   # {
    "RBRACE",   # }
    "COMMA",    # ,
    "SEMICOLON",# ;
    "DOT",      # .
) 


# ===== Reglas simples =====

# Comparación (orden importante: >= antes que >, etc.)
t_GE = r">="
t_LE = r"<="
t_EQ  = r"=="
t_GT  = r">"
t_LT  = r"<"
t_ASSIGN = r"="

# Lógicos
t_AND = r"&&"
t_OR  = r"\|\|"
t_NOT = r"!"

# Aritméticos
t_PLUS  = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"

# Separadores 
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COMMA = r","
t_SEMICOLON = r";"
t_DOT = r"\."



# ===== Ignorar espacios y tabs =====
t_ignore = " \t"



# ===== Ignorar comentarios =====
# // ... fin de línea
# /* ... */ multilínea 

def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

# Comentarios de una línea
def t_LINE_COMMENT(_):
    r"//[^\n]*"
    return None

states = (("comment", "exclusive"),)

# Comentarios multi-línea (estado exclusivo para evitar expresión regular grande)
def t_MLCOMMENT_START(t):
    r"/\*"
    t.lexer.comment_start_line = t.lineno
    t.lexer.begin("comment")

def t_comment_END(t):
    r"\*/"
    t.lexer.begin("INITIAL")

def t_comment_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

def t_comment_content(_):
    r"[^*\n]+|\*+[^*/\n]*"

t_comment_ignore = ""

def t_comment_error(t):
    t.lexer.skip(1)

def t_comment_eof(t):
    start = getattr(t.lexer, "comment_start_line", t.lexer.lineno)
    print(f"Unterminated comment starting at line {start}")
    return None


# ===== Literales =====
# Se combinan las distintas bases en una expresión mediante grupos no capturadores (?:) para simplificar la definición del token entero

# Enteros
_int_dec = r'(0|[1-9][0-9]*)'
_int_bin = r'0b[01]+'
_int_oct = r'0[0-7]+'
_int_hex = r'0x[0-9A-F]+'
_int_value = rf'(?:{_int_bin}|{_int_hex}|{_int_oct}|{_int_dec})'

# Reales
_float_dot = rf'(?:{_int_dec})\.[0-9]+'
# Se permite notación científica con 'e' o 'E' para mayor robustez, aunque el enunciado solo ejemplifica la 'e' minúscula
_float_sci = rf'(?:{_float_dot}|{_int_dec})[eE][+\-]?{_int_dec}'
_float_value = rf'(?:{_float_sci}|{_float_dot})'

# Floats
@TOKEN(_float_value)
def t_FLOAT_VALUE(t):
    t.value = float(t.value)
    return t

# INT
# La conversión se hace manualmente, ya que Python no interpreta automáticamente ciertas formas
@TOKEN(_int_value)
def t_INT_VALUE(t):
    s = t.value

    if s.startswith('0b'):
        t.value = int(s[2:], 2)

    elif s.startswith('0x'):
        t.value = int(s[2:], 16)

    elif len(s) > 1 and s.startswith('0') and all(c in '01234567' for c in s[1:]):
        # octal
        t.value = int(s[1:], 8)

    else:
        # decimal
        t.value = int(s, 10)

    return t


# CHAR
# Literal CHAR entre comillas simples. Se permiten los escapes comunes \n, \t, \r, \', \\
def t_CHAR_VALUE(t):
    r"\'([^\\\n]|(\\.))\'"

    raw = t.value[1:-1]  # sin comillas

    if raw.startswith('\\'):
        esc = raw[1:]

        if esc == 'n':
            t.value = '\n'
        elif esc == 't':
            t.value = '\t'
        elif esc == 'r':
            t.value = '\r'
        elif esc == "'":
            t.value = "'"
        elif esc == '\\':
            t.value = '\\'
        else:
            # escape no reconocido → tomar el carácter literal
            t.value = esc[0]
    else:
        t.value = raw

    return t

def t_ID(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved_map.get(t.value, "ID")
    return t


# ===== Manejo de errores =====

def t_error(t):
    print(f"Illegal character {t.value[0]!r} at line {t.lineno}")
    t.lexer.skip(1)

def build_lexer(**kwargs):
    return lex.lex(**kwargs)