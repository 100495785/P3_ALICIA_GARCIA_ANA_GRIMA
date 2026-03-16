#!/usr/bin/env python3
"""
Ejecuta todos los tests en tests_p2/*.lava secuencialmente.
Después de cada test borra cualquier directorio __pycache__ (recursivo),
y los archivos parser.out y parsetab.py en la raíz del proyecto.
"""
import sys
import os
import glob
import shutil
import subprocess


def remove_artifacts(root):
    # Remove parser.out and parsetab.py if present
    for name in ("parser.out", "parsetab.py"):
        path = os.path.join(root, name)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Warning: could not remove {path}: {e}")

    # Remove any __pycache__ directories recursively
    for dirpath, dirnames, _ in os.walk(root):
        if "__pycache__" in dirnames:
            full = os.path.join(dirpath, "__pycache__")
            try:
                shutil.rmtree(full)
            except Exception as e:
                print(f"Warning: could not remove {full}: {e}")


def run_tests(tests_dir="tests_p2"):
    pattern = os.path.join(tests_dir, "*.lava")
    tests = sorted(glob.glob(pattern))
    if not tests:
        print(f"No hay tests en {tests_dir}")
        return 1

    root = os.getcwd()

    # Master log for all tests
    master_log = os.path.join(root, f"{tests_dir}.log")
    try:
        master_fh = open(master_log, "w", encoding="utf-8")
    except Exception as e:
        print(f"Warning: could not open master log {master_log}: {e}")
        master_fh = None

    for t in tests:
        print('\n' + '=' * 60)
        print(f"Ejecutando: {t}")

        cmd = [sys.executable, "main.py", t]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Append output to master log and include test file content
        header = f"\n{'=' * 60}\nEjecutando: {t}\n"

        # Read test file content
        try:
            with open(t, "r", encoding="utf-8") as tf:
                test_content = tf.read()
        except Exception as e:
            test_content = f"Warning: could not read test file {t}: {e}\n"

        if master_fh:
            try:
                master_fh.write(header)
                master_fh.write("Contenido del test:\n")
                master_fh.write(test_content)
                master_fh.write("\n============================================================\n")
                master_fh.write(proc.stdout or "")
                master_fh.write(f"\nExit code: {proc.returncode}\n")
                master_fh.flush()
            except Exception as e:
                print(f"Warning: could not write to master log {master_log}: {e}")

        # Also print a short summary to the console
        print(f"Salida añadida a: {master_log}")
        print(f"Exit code: {proc.returncode}\n")

        # Cleanup before next test
        remove_artifacts(root)

    if master_fh:
        master_fh.close()
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
