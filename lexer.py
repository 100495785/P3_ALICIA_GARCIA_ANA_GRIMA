# lexer.py
# Analizador léxico para Lava (P1) usando PLY (ply.lex)

import ply.lex as lex

# -------------------------
# Palabras reservadas (PDF)
# -------------------------
# En el PDF se listan como reservadas (en minúsculas):
# true false int float char boolean void return if else do while print new record
# (Se menciona 'break' en el while; lo añadimos para robustez.)

# Las palabras reservadas se escriben en minúscula en el lenguaje, pero sus tipos de token se definen en MAYÚSCULA por convención en PLY.
reserved = {
    "true": "TRUE",
    "false": "FALSE",
    "int": "INT",
    "float": "FLOAT",
    "char": "CHAR",
    "boolean": "BOOLEAN",
    "void": "VOID",
    "return": "RETURN",
    "if": "IF",
    "else": "ELSE",
    "do": "DO",
    "while": "WHILE",
    "print": "PRINT",
    "new": "NEW",
    "record": "RECORD",
    "break": "BREAK",
}

# -------------------------
# Tokens
# -------------------------
tokens = (
    # Identificadores y literales
    "ID",
    "INT_VALUE",
    "FLOAT_VALUE",
    "CHAR_VALUE",

    # Operadores
    "ASSIGN",   # =
    "EQ",       # ==
    "GT",       # >
    "GTE",      # >=
    "LT",       # <
    "LTE",      # <=
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
) + tuple(set(reserved.values()))

# -------------------------
# Estados para comentarios multi-línea
# -------------------------
states = (
    ("comment", "exclusive"),
)

# -------------------------
# Reglas simples (1-línea)
# -------------------------
t_GTE = r">="
t_LTE = r"<="
t_EQ  = r"=="
t_GT  = r">"
t_LT  = r"<"

t_AND = r"&&"
t_OR  = r"\|\|"
t_NOT = r"!"

t_ASSIGN = r"="

t_PLUS  = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"

t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COMMA = r","
t_SEMICOLON = r";"
t_DOT = r"\."

# Ignorados (pero cuentan para columnas vía lexpos)
t_ignore = " \t"

# -------------------------
# Saltos de línea (soporta LF y CRLF)
# -------------------------
def t_NEWLINE(t):
    r"\r?\n+"
    t.lexer.lineno += t.value.count("\n")

# -------------------------
# Comentarios de una línea: // ... \n
# -------------------------
def t_LINE_COMMENT(t):
    r"//[^\n]*"
    # Se ignora por completo
    pass

# -------------------------
# Comentarios multi-línea: /* ... */
# Usamos estado exclusivo para evitar regex enormes y para contar líneas.
# -------------------------
def t_MLCOMMENT_START(t):
    r"/\*"
    t.lexer.begin("comment")

def t_comment_END(t):
    r"\*/"
    t.lexer.begin("INITIAL")

def t_comment_NEWLINE(t):
    r"\r?\n+"
    t.lexer.lineno += t.value.count("\n")

def t_comment_CONTENT(t):
    r"[^*\n]+|\*+[^*/\n]*"
    # Consumimos contenido sin producir tokens
    pass

t_comment_ignore = ""

def t_comment_error(t):
    # Consumir 1 carácter para evitar bucle infinito
    t.lexer.skip(1)

# -------------------------
# Literales numéricos
# -------------------------
# INT:
# - decimal: 0 o [1-9][0-9]* (sin ceros a la izquierda)
# - binario: 0b[01]+
# - octal: 0[0-7]+  (nota: "0" solo ya es decimal 0)
# - hex: 0x[0-9A-F]+ (según PDF A-F en mayúsculas; aceptamos también a-f por robustez)
#
# FLOAT:
# - dot notation: entero '.' decimales (ambas partes presentes)
# - scientific: base (entera o decimal) + e/E + exponente entero con signo opcional

_dec_int = r"(?:0|[1-9][0-9]*)"
_bin_int = r"(?:0b[01]+)"
_oct_int = r"(?:0[0-7]+)"
_hex_int = r"(?:0x[0-9A-Fa-f]+)"

_dot_float = rf"(?:{_dec_int})\.(?:[0-9]+)"
_sci_float = rf"(?:{_dec_int})(?:\.(?:[0-9]+))?[eE][\+\-]?(?:{_dec_int})"

def t_FLOAT_VALUE(t):
    rf"{_sci_float}|{_dot_float}"
    # Mantener lexema tal cual (string) para que columna-fin sea exacta
    return t

def t_INT_VALUE(t):
    rf"{_bin_int}|{_hex_int}|{_oct_int}|{_dec_int}"
    # Mantener lexema tal cual
    return t

# -------------------------
# CHAR literal: 'x' o escapes simples tipo '\n', '\'', '\\', etc.
# PDF: ASCII-extendido entre comillas simples.
# -------------------------
def t_CHAR_VALUE(t):
    r"\'([^\\\n\']|\\.)\'"
    return t

# -------------------------
# Identificadores y reserved words
# -------------------------
def t_ID(t):
    r"[a-zA-Z][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "ID")
    return t

# -------------------------
# Error
# -------------------------
def t_error(t):
    # No imprimimos warnings PLY; esto es error léxico de entrada
    # Puedes adaptar el formato si tu profe exige algo concreto.
    line = t.lineno
    col = find_column(t.lexer, t.lexpos)
    print(f"Illegal character {t.value[0]!r} at line {line}, column {col}")
    t.lexer.skip(1)

# -------------------------
# Helpers de posición
# -------------------------
def find_column(lexer, lexpos: int) -> int:
    """
    Devuelve columna 0-based calculada desde el último '\n' en lexer.lexdata.
    """
    data = lexer.lexdata
    last_nl = data.rfind("\n", 0, lexpos)
    if last_nl < 0:
        return lexpos
    return lexpos - (last_nl + 1)

def make_lexer(**kwargs):
    """
    Factory para construir el lexer desde main.py
    """
    return lex.lex(**kwargs)
