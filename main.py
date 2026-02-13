# main.py
import sys
import os
import ply.lex as lex
import lexer  # tu lexer.py (el archivo debe llamarse lexer.py)


def main():
    # Validación de argumentos
    if len(sys.argv) != 2:
        print("Uso: python main.py <file>")
        sys.exit(1)

    input_path = sys.argv[1]

    # Leer fichero de entrada
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: no se encuentra el fichero '{input_path}'")
        sys.exit(1)

    # Construir lexer
    lx = lex.lex(module=lexer)
    lx.input(data)

    # Nombre de salida: mismo nombre + extensión .token
    # (si el input era example.lava -> example.token)
    base, _ = os.path.splitext(input_path)
    output_path = base + ".token"

    # Tokenizar y escribir salida
    with open(output_path, "w", encoding="utf-8") as out:
        while True:
            tok = lx.token()
            if not tok:
                break

            line = tok.lineno
            col_start = lexer.find_column(data, tok)
            col_end = col_start + len(str(tok.value))

            out.write(f"{tok.type}, {tok.value}, {line}, {col_start}, {col_end}\n")


if __name__ == "__main__":
    main()
