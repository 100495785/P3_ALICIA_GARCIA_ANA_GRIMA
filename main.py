# Programa principal de la Práctica 1, que:
# - Lee el fichero fuente Lava proporcionado por línea de comandos
# - Ejecuta el analizador léxico implementado con PLY en lexer.py
# - Genera un fichero <nombre>.token con el listado de tokens (tipo, valor, línea y columnas)


import sys
from pathlib import Path
import lexer as lava_lexer

# Normaliza saltos de línea para evitar problemas en Windows (CRLF = \r\n)
def normalize_newlines(text: str) -> str:
    return text.replace('\r\n', '\n').replace('\r', '\n')

# Devuelve la posición del 1er carácter de la línea donde cae lexpos
def line_start_pos(text: str, lexpos: int) -> int:
    # índice del carácter posterior al último \n antes de lexpos
    return text.rfind('\n', 0, lexpos) + 1

# Calcula columna inicio y fin del token
def col_start_end(text: str, tok) -> tuple[int, int]:
    start = tok.lexpos - line_start_pos(text, tok.lexpos)
    end = start + len(str(tok.value) if tok.type in ('INT_LITERAL', 'FLOAT_LITERAL') else tok.lexeme)
    return start, end

# Devuelve el string (se imprime en el campo VALOR del token).
# Para literales numéricos, el lexer ya convierte a int/float y aquí los pasamos a string
# Para el resto (incluyendo CHAR), usamos el lexema original para que sea exacto
def token_value_str(tok) -> str:
    if tok.type in ('INT_LITERAL', 'FLOAT_LITERAL'):
        return str(tok.value)
    return tok.lexeme

def find_column(text: str, tok) -> tuple[int, int]:
    start = tok.lexpos - line_start_pos(text, tok.lexpos)
    end = start + len(tok.lexeme)
    return start, end

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <file.lava>")
        sys.exit(1)

    in_path = Path(sys.argv[1])
    if not in_path.exists():
        print(f"No existe el archivo: {in_path}")
        sys.exit(1)

    # Lee fichero completo
    raw = in_path.read_text(encoding="utf-8")
    data = normalize_newlines(raw)
    # Construir y ejecutar el lexer
    lx = lava_lexer.build_lexer()
    lx.lineno = 1
    lx.input(data)


    out_lines = []
    # Pedimos tokens hasta EOF 
    while True:
        tok = lx.token()
        if not tok:
            break
        # Guardar lexema original usando lexdata + posiciones
        lexeme = lx.lexdata[tok.lexpos:lx.lexpos]
        tok.lexeme = lexeme

        col_start, col_end = find_column(data, tok)
        out_lines.append(f"{tok.type}, {token_value_str(tok)}, {tok.lineno}, {col_start}, {col_end}")

    out_path = in_path.with_suffix(in_path.suffix + ".token")
    out_path.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")
    # print(f"Análisis léxico completado. Fichero generado: {out_path}")

if __name__ == "__main__":
    main()

