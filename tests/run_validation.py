# -*- coding: utf-8 -*-
"""
Script de Validación Automatizada para el Analizador Dart.
Analiza los tres algoritmos de prueba y genera los archivos de log
en la carpeta logs/ con el formato requerido en la propuesta.
"""

import os
import datetime
import sys

# Agregar el directorio raíz al path de Python para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import get_lexer
from src.parser import parse
from src.semantic import SemanticAnalyzer

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_logs(algorithm_path, algorithm_name):
    # Leer el código fuente
    with open(algorithm_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Fecha y hora actual
    now = datetime.datetime.now()
    # Para el nombre del archivo: DD-MM-YYYY-HH-MM
    # Nota: Windows no permite ':' en nombres de archivos, por lo que usamos '-'
    datetime_str = now.strftime("%d-%m-%Y-%H-%M")
    
    # Directorio de logs
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    ensure_dir(logs_dir)

    # ----------------------------------------------------
    # 1. Análisis Léxico (Xavier Camacho / Xavih830)
    # ----------------------------------------------------
    lexer = get_lexer()
    lexer.input(code)
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(tok)
    
    lex_log_name = f"lexico-Xavih830-{datetime_str}.txt"
    lex_log_path = os.path.join(logs_dir, lex_log_name)
    
    with open(lex_log_path, 'w', encoding='utf-8') as f:
        f.write("==================================================\n")
        f.write("          LOG DE ANÁLISIS LÉXICO (DART)\n")
        f.write("==================================================\n")
        f.write(f"Desarrollador: Xavier Camacho (Xavih830)\n")
        f.write(f"Fecha y Hora:  {now.strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Archivo Origen: {algorithm_name}\n")
        f.write("--------------------------------------------------\n")
        f.write(f"Tokens detectados: {len(tokens)}\n")
        f.write(f"Errores léxicos:   {len(lexer.errors)}\n")
        f.write("--------------------------------------------------\n")
        f.write(f"{'TIPO TOKEN':<20} | {'LEXEMA':<25} | {'LÍNEA':<5} | {'POSICIÓN':<8}\n")
        f.write("-" * 68 + "\n")
        for tok in tokens:
            f.write(f"{tok.type:<20} | {repr(tok.value):<25} | {tok.lineno:<5} | {tok.lexpos:<8}\n")
        
        if lex_errors := lexer.errors:
            f.write("\n--- ERRORES LÉXICOS ---\n")
            for err in lex_errors:
                f.write(f"- Linea {err['line']}: {err['message']} (Lexema: '{err['lexeme']}')\n")
                
    print(f"[OK] Log lexico generado: logs/{lex_log_name}")

    # ----------------------------------------------------
    # 2. Análisis Sintáctico (Manuel Matute / ManuelMatute)
    # ----------------------------------------------------
    ast, syntactic_errors = parse(code)
    
    sin_log_name = f"sintactico-ManuelMatute-{datetime_str}.txt"
    sin_log_path = os.path.join(logs_dir, sin_log_name)
    
    with open(sin_log_path, 'w', encoding='utf-8') as f:
        f.write("==================================================\n")
        f.write("        LOG DE ANÁLISIS SINTÁCTICO (DART)\n")
        f.write("==================================================\n")
        f.write(f"Desarrollador: Manuel Matute (ManuelMatute)\n")
        f.write(f"Fecha y Hora:  {now.strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Archivo Origen: {algorithm_name}\n")
        f.write("--------------------------------------------------\n")
        f.write(f"Errores sintácticos: {len(syntactic_errors)}\n")
        f.write("--------------------------------------------------\n\n")
        
        if ast:
            f.write("--- Árbol de Sintaxis Abstracta (AST) ---\n")
            f.write(ast.to_string())
        else:
            f.write("[ERROR] ERROR: No se pudo generar el AST debido a fallas en el análisis sintáctico.\n")
            
        if syntactic_errors:
            f.write("\n\n--- DETALLE DE ERRORES SINTÁCTICOS ---\n")
            for err in syntactic_errors:
                f.write(f"- Linea {err['line']}: {err['message']} (Lexema: '{err['lexeme']}')\n")
                
    print(f"[OK] Log sintactico generado: logs/{sin_log_name}")

    # ----------------------------------------------------
    # 3. Análisis Semántico (Johan Veloz / johegvel)
    # ----------------------------------------------------
    semantic_errors = []
    if ast:
        analyzer = SemanticAnalyzer()
        semantic_errors = analyzer.analyze(ast)
        
    sem_log_name = f"semantico-johegvel-{datetime_str}.txt"
    sem_log_path = os.path.join(logs_dir, sem_log_name)
    
    with open(sem_log_path, 'w', encoding='utf-8') as f:
        f.write("==================================================\n")
        f.write("         LOG DE ANÁLISIS SEMÁNTICO (DART)\n")
        f.write("==================================================\n")
        f.write(f"Desarrollador: Johan Veloz (johegvel)\n")
        f.write(f"Fecha y Hora:  {now.strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Archivo Origen: {algorithm_name}\n")
        f.write("--------------------------------------------------\n")
        f.write(f"Errores semánticos: {len(semantic_errors)}\n")
        f.write("--------------------------------------------------\n\n")
        
        if not ast:
            f.write("[ERROR] ERROR: Análisis semántico omitido debido a fallas sintácticas primarias.\n")
        elif len(semantic_errors) == 0:
            f.write("[SUCCESS] EXITO: El análisis semántico completó exitosamente sin detectar errores.\n")
        else:
            f.write("--- DETALLE DE ERRORES SEMÁNTICOS ---\n")
            for err in semantic_errors:
                f.write(f"- Linea {err['line']}: {err['message']} (Lexema: '{err['lexeme']}')\n")
                
    print(f"[OK] Log semantico generado: logs/{sem_log_name}")
    print("-" * 50)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tests_dir = os.path.join(root_dir, "tests")
    
    algorithms = [
        ("algoritmo1.dart", "Algoritmo 1 - Búsqueda y Ordenamiento"),
        ("algoritmo2.dart", "Algoritmo 2 - Gestión de Inventario"),
        ("algoritmo3.dart", "Algoritmo 3 - Análisis de Texto"),
    ]
    
    print("Iniciando validación de los algoritmos de prueba de Dart...")
    print("=" * 50)
    
    for filename, desc in algorithms:
        path = os.path.join(tests_dir, filename)
        if os.path.exists(path):
            print(f"Analizando {desc} ({filename})...")
            generate_logs(path, filename)
        else:
            print(f"⚠ Archivo no encontrado: {path}")

if __name__ == "__main__":
    main()
