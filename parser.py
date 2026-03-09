# Analizador sintáctico para una primera versión de la P2 de Lava utilizando PLY, que define:
# - Una gramática simplificada pero alineada con el lenguaje del enunciado
# - Las reglas de precedencia y asociatividad de los operadores
# - La estructura básica del programa, sentencias, bloques y funciones
# - El manejo básico de errores sintácticos

import ply.yacc as yacc
import lexer as lava_lexer


# ===== Tokens =====

tokens = lava_lexer.tokens

# Símbolo inicial de la gramática
start = "program"


# ===== Precedencia =====
# Se define la precedencia de operadores para evitar ambigüedades:
# - else por encima del if sin else para resolver el dangling else
# - || por debajo de &&
# - comparaciones por debajo de suma/resta
# - suma/resta por debajo de multiplicación/división
# - operadores unarios con mayor precedencia que los binarios

precedence = (
    ("nonassoc", "IFX"),
    ("nonassoc", "ELSE"),
    ("left", "OR"),
    ("left", "AND"),
    ("nonassoc", "EQ", "GT", "GE", "LT", "LE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "NOT", "UPLUS", "UMINUS"),
)


# ===== Reglas auxiliares =====

# Producción vacía
def p_empty(p):
    "empty :"
    pass


# ===== Estructura global del programa =====
# Un programa es una secuencia de elementos de nivel superior.
# En esta versión simplificada se permiten:
# - sentencias vacías ';'
# - declaraciones de variables
# - asignaciones
# - llamadas a función como sentencia
# - print y return
# - sentencias compuestas
# - declaraciones de funciones

def p_program(p):
    "program : top_list"
    pass


def p_top_list_recursive(p):
    "top_list : top_list top_item"
    pass


def p_top_list_empty(p):
    "top_list : empty"
    pass


def p_top_item_empty_stmt(p):
    "top_item : SEMICOLON"
    pass


# Elementos de nivel superior que empiezan por tipo + identificador.
# Permiten distinguir entre:
# - declaración: int a;
# - declaración con inicialización: int a = 3;
# - función: int suma(int x, int y) { ... }
def p_top_item_typed(p):
    "top_item : type_spec_or_void ID top_typed_tail"
    pass


# Elementos de nivel superior que no empiezan por tipo.
# Se aceptan como sentencias terminadas en ';'
def p_top_item_non_typed_stmt(p):
    "top_item : non_typed_simple_statement SEMICOLON"
    pass


def p_top_item_compound_stmt(p):
    "top_item : compound_statement"
    pass


# ===== Continuación de elementos tipados en nivel superior =====
# Tras haber leído 'tipo ID', se puede tener:
# - una función: (...) { ... }
# - una declaración: ;   , ... ;   = ... ;

def p_top_typed_tail_function(p):
    "top_typed_tail : LPAREN parameter_list_opt RPAREN block"
    pass


def p_top_typed_tail_decl(p):
    "top_typed_tail : top_decl_tail SEMICOLON"
    pass


# Tras haber leído 'tipo ID', se permite:
# - declaración simple: int a;
# - lista de variables: int a, b, c;
# - inicialización: int a = 3;
def p_top_decl_tail_init(p):
    "top_decl_tail : ASSIGN expression"
    pass


def p_top_decl_tail_list(p):
    "top_decl_tail : id_list_tail"
    pass


# ===== Bloques =====
# Un bloque contiene una secuencia de elementos internos.
# Dentro del bloque se permiten:
# - sentencias vacías ';'
# - sentencias simples acabadas en ';'
# - sentencias compuestas

def p_block(p):
    "block : LBRACE block_item_list RBRACE"
    pass


def p_block_item_list_recursive(p):
    "block_item_list : block_item_list block_item"
    pass


def p_block_item_list_empty(p):
    "block_item_list : empty"
    pass


def p_block_item_empty_stmt(p):
    "block_item : SEMICOLON"
    pass


def p_block_item_simple_stmt(p):
    "block_item : simple_statement SEMICOLON"
    pass


def p_block_item_compound_stmt(p):
    "block_item : compound_statement"
    pass


# ===== Tipos =====
# En esta versión simplificada se aceptan tipos básicos y void.
# Más adelante se podrá ampliar con ID para tipos de record.

def p_type_spec(p):
    """type_spec : INT
                 | FLOAT
                 | CHAR
                 | BOOLEAN"""
    pass


def p_type_spec_or_void(p):
    """type_spec_or_void : type_spec
                         | VOID"""
    pass


# ===== Sentencias simples =====
# Son las sentencias que terminan en ';'

def p_simple_statement(p):
    """simple_statement : declaration_statement
                        | non_typed_simple_statement"""
    pass


# ===== Sentencias simples sin tipo al principio =====
# Se separan para evitar ambigüedad entre:
# - declaraciones que empiezan por tipo
# - funciones que empiezan por tipo
# en el nivel superior

def p_non_typed_simple_statement(p):
    """non_typed_simple_statement : assignment_statement
                                  | call_statement
                                  | print_statement
                                  | return_statement"""
    pass


# ===== Sentencias compuestas =====
# Son sentencias que no requieren ';' externo

def p_compound_statement(p):
    """compound_statement : block
                          | if_statement
                          | while_statement"""
    pass


# ===== Declaraciones =====
# Se permite:
# - int a;
# - int a, b, c;
# - int a = 3;
# No se permite multideclaración con asignación mezclada

def p_declaration_statement(p):
    "declaration_statement : type_spec ID declaration_suffix"
    pass


def p_declaration_suffix_init(p):
    "declaration_suffix : ASSIGN expression"
    pass


def p_declaration_suffix_list(p):
    "declaration_suffix : id_list_tail"
    pass


# Continúa una lista de identificadores después del primero:
# - vacío  -> int a;
# - coma   -> int a, b, c;
def p_id_list_tail_empty(p):
    "id_list_tail : empty"
    pass


def p_id_list_tail_recursive(p):
    "id_list_tail : COMMA ID id_list_tail"
    pass


# ===== Asignación =====
# En esta versión simplificada la parte izquierda es solo un identificador

def p_assignment_statement(p):
    "assignment_statement : ID ASSIGN expression"
    pass


# ===== Llamada a función como sentencia =====
# Se permite una llamada a función terminada en ';'

def p_call_statement(p):
    "call_statement : ID LPAREN argument_list_opt RPAREN"
    pass


# ===== Print / return =====

def p_print_statement(p):
    "print_statement : PRINT LPAREN argument_list_opt RPAREN"
    pass


def p_return_statement(p):
    "return_statement : RETURN expression"
    pass


# ===== If / while =====

def p_if_statement_if(p):
    "if_statement : IF LPAREN expression RPAREN block %prec IFX"
    pass


def p_if_statement_if_else(p):
    "if_statement : IF LPAREN expression RPAREN block ELSE block"
    pass


def p_while_statement(p):
    "while_statement : WHILE LPAREN expression RPAREN block"
    pass


# ===== Parámetros =====
# Se usan en la definición de funciones

def p_parameter_list_opt_list(p):
    "parameter_list_opt : parameter_list"
    pass


def p_parameter_list_opt_empty(p):
    "parameter_list_opt : empty"
    pass


def p_parameter_list_single(p):
    "parameter_list : parameter"
    pass


def p_parameter_list_multiple(p):
    "parameter_list : parameter_list COMMA parameter"
    pass


def p_parameter(p):
    "parameter : type_spec ID"
    pass


# ===== Argumentos =====
# Se reutilizan para llamadas a función y print(...)

def p_argument_list_opt_list(p):
    "argument_list_opt : argument_list"
    pass


def p_argument_list_opt_empty(p):
    "argument_list_opt : empty"
    pass


def p_argument_list_single(p):
    "argument_list : expression"
    pass


def p_argument_list_multiple(p):
    "argument_list : argument_list COMMA expression"
    pass


# ===== Expresiones =====
# En esta primera versión se incluyen:
# - literales
# - identificadores
# - llamadas a función
# - operadores aritméticos, booleanos y comparativos
# - paréntesis

def p_expression_binary(p):
    """expression : expression OR expression
                  | expression AND expression
                  | expression EQ expression
                  | expression GT expression
                  | expression GE expression
                  | expression LT expression
                  | expression LE expression
                  | expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression"""
    pass


def p_expression_unary_not(p):
    "expression : NOT expression"
    pass


def p_expression_unary_plus(p):
    "expression : PLUS expression %prec UPLUS"
    pass


def p_expression_unary_minus(p):
    "expression : MINUS expression %prec UMINUS"
    pass


def p_expression_primary(p):
    "expression : primary_expression"
    pass


# ===== Expresiones primarias =====
# Elementos base de una expresión:
# - identificadores
# - llamadas a función
# - literales
# - expresiones entre paréntesis

def p_primary_expression_group(p):
    "primary_expression : LPAREN expression RPAREN"
    pass


def p_primary_expression_literal(p):
    """primary_expression : INT_VALUE
                          | FLOAT_VALUE
                          | CHAR_VALUE
                          | TRUE
                          | FALSE"""
    pass


def p_primary_expression_id(p):
    "primary_expression : ID"
    pass


def p_primary_expression_call(p):
    "primary_expression : ID LPAREN argument_list_opt RPAREN"
    pass


# ===== Manejo de errores =====

def p_error(p):
    if p is None:
        print("[ERROR] Fin de fichero inesperado")
    else:
        print(f"[ERROR] Token '{p.type}' inesperado en la línea {p.lineno}")


# ===== Construcción del parser =====

def build_parser(**kwargs):
    return yacc.yacc(**kwargs)