# main.py
# Uso: python main.py <file>
# Genera <mismo_nombre>.token con formato:
# TIPO, VALOR, LINEA, COLUMNA-INICIO, COLUMNA-FIN

import os
import sys

import lexer as lava_lexer


def token_to_line(tok, lexdata: str, lexer) -> str:
    # columna inicio: 0-based
    col_start = lava_lexer.find_column(lexer, tok.lexpos)

    # columna fin: exclusiva (como en el ejemplo del PDF)
    # Para que sea exacta, usamos la longitud del lexema que PLY ha guardado en tok.value (string)
    # En palabras reservadas/operadores también es string.
    lexeme = tok.value
    # Por seguridad, si algún token tuviera value no-str (no debería aquí), lo convertimos:
    if not isinstance(lexeme, str):
        lexeme = str(lexeme)

    col_end = col_start + len(lexeme)

    return f"{tok.type}, {lexeme}, {tok.lineno}, {col_start}, {col_end}"


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python main.py <file>")
        return 1

    in_path = sys.argv[1]
    if not os.path.isfile(in_path):
        print(f"Error: no existe el fichero: {in_path}")
        return 1

    with open(in_path, "r", encoding="utf-8") as f:
        data = f.read()

    # Normalizamos CRLF -> LF para consistencia en columnas/líneas
    data = data.replace("\r\n", "\n")

    lexr = lava_lexer.make_lexer()
    lexr.input(data)

    base, _ext = os.path.splitext(in_path)
    out_path = base + ".token"

    with open(out_path, "w", encoding="utf-8") as out:
        for tok in lexr:
            out.write(token_to_line(tok, data, lexr) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
