# -*- coding: utf-8 -*-
"""
Interfaz Gráfica de Usuario (GUI) para el Analizador Dart.
Desarrollada en PyQt6.
Implementado de forma colaborativa por:
- Xavier Camacho (Xavih830)
- Manuel Matute (ManuelMatute)
- Johan Veloz (johegvel)
"""

import sys
import os

# Ajuste dinámico de sys.path para permitir la ejecución autónoma desde cualquier directorio
_current_dir = os.path.dirname(os.path.abspath(__file__)) # src/gui
_src_dir = os.path.dirname(_current_dir) # src
_project_root = os.path.dirname(_src_dir) # root
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QTextEdit, QLabel, QFileDialog, QSplitter, QStatusBar,
    QMessageBox
)
from PyQt6.QtGui import QFont, QColor, QIcon, QTextFormat, QPainter
from PyQt6.QtCore import Qt, QSize, QRect

from src.lexer import get_lexer
from src.parser import parse
from src.semantic import SemanticAnalyzer

# --- Área e Implementación de Números de Línea en PyQt6 ---

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    def lineNumberAreaWidth(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num /= 10
            digits += 1

        space = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        
        # Color de fondo del área de números (gris oscuro muy elegante)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                
                # Resaltar la línea actual con color blanco brillante, las otras con gris
                is_current = (block == self.textCursor().block())
                painter.setPen(QColor("#ffffff") if is_current else QColor("#757575"))
                
                # Dibujar el número alineado a la derecha
                painter.drawText(
                    0, top, 
                    self.lineNumberArea.width() - 5, 
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, 
                    number
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            # Color de fondo sutil para la línea en la que se encuentra el cursor
            lineColor = QColor("#1c2d3d")
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)


# Estilo QSS Oscuro Premium
DARK_STYLESHEET = """
QMainWindow {
    background-color: #121212;
}
QWidget {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QPlainTextEdit, QTextEdit {
    background-color: #1e1e1e;
    color: #dcdcdc;
    border: 1px solid #333333;
    border-radius: 4px;
}
QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #1e1e1e;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #1a1a1a;
    color: #888888;
    padding: 8px 16px;
    border: 1px solid #333333;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #ffffff;
    border-bottom: 2px solid #007acc;
}
QTableWidget {
    background-color: #1e1e1e;
    color: #dcdcdc;
    gridline-color: #333333;
    border: 1px solid #333333;
}
QHeaderView::section {
    background-color: #1a1a1a;
    color: #e0e0e0;
    padding: 6px;
    border: 1px solid #333333;
}
QPushButton {
    background-color: #007acc;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0098ff;
}
QPushButton:pressed {
    background-color: #005999;
}
QPushButton#btn_clear {
    background-color: #3e3e3e;
}
QPushButton#btn_clear:hover {
    background-color: #4e4e4e;
}
QPushButton#btn_open {
    background-color: #2e7d32;
}
QPushButton#btn_open:hover {
    background-color: #388e3c;
}
QStatusBar {
    background-color: #1a1a1a;
    color: #888888;
    border-top: 1px solid #333333;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador de Dart - Compiladores")
        self.resize(1100, 750)
        self.setStyleSheet(DARK_STYLESHEET)
        
        # Inicializar componentes principales
        self.setup_ui()
        self.setup_statusbar()
        
    def setup_ui(self):
        # Widget central y layout horizontal principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Splitter principal para redimensionamiento interactivo
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # --- Panel Izquierdo: Editor de Código y Controles ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 5, 0)
        
        lbl_code = QLabel("Código Fuente de Dart:")
        lbl_code.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        left_layout.addWidget(lbl_code)
        
        self.code_editor = CodeEditor()
        self.code_editor.setFont(QFont("Consolas", 11))
        # Autotab / tab size
        self.code_editor.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 16)
        left_layout.addWidget(self.code_editor)
        
        # Controles
        ctrl_layout = QHBoxLayout()
        
        self.btn_open = QPushButton("Abrir Archivo")
        self.btn_open.setObjectName("btn_open")
        self.btn_open.clicked.connect(self.open_file)
        ctrl_layout.addWidget(self.btn_open)
        
        self.btn_analyze = QPushButton("Analizar Código")
        self.btn_analyze.clicked.connect(self.run_analysis)
        ctrl_layout.addWidget(self.btn_analyze)
        
        self.btn_clear = QPushButton("Limpiar")
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.clicked.connect(self.clear_all)
        ctrl_layout.addWidget(self.btn_clear)
        
        left_layout.addLayout(ctrl_layout)
        
        splitter.addWidget(left_panel)
        
        # --- Panel Derecho: Tabs de Resultados ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 0, 0, 0)
        
        lbl_results = QLabel("Resultados del Análisis:")
        lbl_results.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        right_layout.addWidget(lbl_results)
        
        self.tabs = QTabWidget()
        right_layout.addWidget(self.tabs)
        
        # Tab 1: Léxico
        self.tab_lex = QWidget()
        tab_lex_layout = QVBoxLayout(self.tab_lex)
        self.table_tokens = QTableWidget(0, 4)
        self.table_tokens.setHorizontalHeaderLabels(["Token", "Lexema", "Línea", "Posición"])
        self.table_tokens.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tab_lex_layout.addWidget(self.table_tokens)
        self.tabs.addTab(self.tab_lex, "Léxico (Tokens)")
        
        # Tab 2: Sintáctico (AST o errores)
        self.tab_sin = QWidget()
        tab_sin_layout = QVBoxLayout(self.tab_sin)
        self.txt_ast = QTextEdit()
        self.txt_ast.setReadOnly(True)
        self.txt_ast.setFont(QFont("Consolas", 10))
        tab_sin_layout.addWidget(self.txt_ast)
        self.tabs.addTab(self.tab_sin, "Sintáctico (AST)")
        
        # Tab 3: Semántico
        self.tab_sem = QWidget()
        tab_sem_layout = QVBoxLayout(self.tab_sem)
        self.txt_semantic = QTextEdit()
        self.txt_semantic.setReadOnly(True)
        self.txt_semantic.setFont(QFont("Segoe UI", 10))
        tab_sem_layout.addWidget(self.txt_semantic)
        self.tabs.addTab(self.tab_sem, "Semántico")
        
        # Tab 4: Consola / Reporte
        self.tab_report = QWidget()
        tab_report_layout = QVBoxLayout(self.tab_report)
        self.txt_report = QTextEdit()
        self.txt_report.setReadOnly(True)
        self.txt_report.setFont(QFont("Consolas", 9))
        tab_report_layout.addWidget(self.txt_report)
        
        self.btn_save_log = QPushButton("Guardar Log de Salida")
        self.btn_save_log.clicked.connect(self.save_log_dialog)
        tab_report_layout.addWidget(self.btn_save_log)
        
        self.tabs.addTab(self.tab_report, "Consola de Compilación")
        
        splitter.addWidget(right_panel)
        
        # Ajustar proporciones iniciales (50% editor, 50% resultados)
        splitter.setSizes([550, 550])
 
    def setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo para analizar.")
 
    # --- Acciones y Lógica de Negocio ---
 
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Abrir Código Dart", "", "Archivos Dart (*.dart);;Archivos de Texto (*.txt)"
        )
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    self.code_editor.setPlainText(f.read())
                self.status_bar.showMessage(f"Archivo cargado: {os.path.basename(file_name)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo leer el archivo:\n{str(e)}")
 
    def clear_all(self):
        self.code_editor.clear()
        self.table_tokens.setRowCount(0)
        self.txt_ast.clear()
        self.txt_semantic.clear()
        self.txt_report.clear()
        self.status_bar.showMessage("Limpio.")
 
    def run_analysis(self):
        code = self.code_editor.toPlainText()
        if not code.strip():
            self.status_bar.showMessage("Editor vacío, nada que analizar.")
            return
 
        # 1. Análisis Léxico manual para recolectar tokens individuales
        lexer = get_lexer()
        lexer.input(code)
        tokens = []
        while True:
            try:
                tok = lexer.token()
                if not tok:
                    break
                tokens.append(tok)
            except Exception as e:
                break
 
        # Cargar tabla léxica
        self.table_tokens.setRowCount(len(tokens))
        for row, tok in enumerate(tokens):
            self.table_tokens.setItem(row, 0, QTableWidgetItem(str(tok.type)))
            self.table_tokens.setItem(row, 1, QTableWidgetItem(str(tok.value)))
            self.table_tokens.setItem(row, 2, QTableWidgetItem(str(tok.lineno)))
            self.table_tokens.setItem(row, 3, QTableWidgetItem(str(tok.lexpos)))
 
        # 2. Análisis Sintáctico (Genera AST y captura errores)
        ast, syntactic_errors = parse(code)
        lex_errors = lexer.errors
        
        # 3. Análisis Semántico (solo si el AST es válido)
        semantic_errors = []
        if ast:
            analyzer = SemanticAnalyzer()
            semantic_errors = analyzer.analyze(ast)
            
            # Formatear AST
            self.txt_ast.setHtml(self.format_ast_html(ast.to_string()))
        else:
            self.txt_ast.setHtml("<span style='color:#f44336; font-weight:bold;'>Error: No se pudo generar el AST debido a errores sintácticos.</span>")
 
        # 4. Formatear Resultados Semánticos
        if not ast:
            self.txt_semantic.setHtml("<span style='color:#f44336; font-weight:bold;'>Análisis semántico omitido debido a fallas sintácticas primarias.</span>")
        elif len(semantic_errors) == 0:
            self.txt_semantic.setHtml("<span style='color:#4caf50; font-weight:bold;'>✔ Análisis semántico completado exitosamente sin errores.</span>")
        else:
            sem_html = "<b>Errores Semánticos Encontrados:</b><br><br>"
            for err in semantic_errors:
                sem_html += f"<span style='color:#f44336;'>• {err['message']}</span><br>"
            self.txt_semantic.setHtml(sem_html)
 
        # 5. Generar reporte consolidado (Consola de compilación)
        total_lex = len(lex_errors)
        total_sin = len(syntactic_errors)
        total_sem = len(semantic_errors)
        total_errors = total_lex + total_sin + total_sem
        
        report = "==================================================\n"
        report += "          REPORTE DE COMPILACIÓN DART\n"
        report += "==================================================\n"
        report += f"Resumen:\n"
        report += f" - Errores Léxicos: {total_lex}\n"
        report += f" - Errores Sintácticos: {total_sin}\n"
        report += f" - Errores Semánticos: {total_sem}\n"
        report += f" - Total de Errores: {total_errors}\n"
        report += "--------------------------------------------------\n\n"
        
        if total_errors == 0:
            report += "✔ COMPILACIÓN EXITOSA. El programa está bien estructurado.\n"
        else:
            report += "✘ COMPILACIÓN FALLIDA. Detalles de los errores:\n\n"
            
            if total_lex > 0:
                report += "[Fase 1: Análisis Léxico]\n"
                for err in lex_errors:
                    report += f" - Línea {err['line']}: {err['message']} (Lexema: '{err['lexeme']}')\n"
                report += "\n"
                
            if total_sin > 0:
                report += "[Fase 2: Análisis Sintáctico]\n"
                for err in syntactic_errors:
                    report += f" - Línea {err['line']}: {err['message']}\n"
                report += "\n"
                
            if total_sem > 0:
                report += "[Fase 3: Análisis Semántico]\n"
                for err in semantic_errors:
                    report += f" - Línea {err['line']}: {err['message']}\n"
                report += "\n"
                
        self.txt_report.setPlainText(report)
        
        # Guardar reporte en variable temporal para poder exportarlo
        self.last_report = report
        
        # Actualizar barra de estado
        if total_errors == 0:
            self.status_bar.showMessage("Análisis completado: 0 errores detectados.")
        else:
            self.status_bar.showMessage(f"Análisis completado: {total_errors} errores encontrados.")
 
    def format_ast_html(self, ast_text):
        """Aplica colores a la salida del AST para que sea más legible en HTML."""
        lines = ast_text.split('\n')
        formatted_lines = []
        for line in lines:
            # Reemplazar espacios de indentación con &nbsp;
            spaces = len(line) - len(line.lstrip(' '))
            content = line.strip()
            if not content:
                continue
            indent = "&nbsp;" * spaces
            
            # Clasificar y colorear tipos de nodos
            if content.startswith("Program") or content.startswith("Block"):
                content = f"<span style='color:#569cd6; font-weight:bold;'>{content}</span>"
            elif content.startswith("ImportStatement"):
                content = f"<span style='color:#ce9178;'>{content}</span>"
            elif content.startswith("FunctionDeclaration") or content.startswith("MethodDeclaration"):
                content = f"<span style='color:#4fc1ff; font-weight:bold;'>{content}</span>"
            elif content.startswith("VarDeclaration"):
                content = f"<span style='color:#4ec9b0;'>{content}</span>"
            elif content.startswith("IfStatement") or content.startswith("ForStatement") or content.startswith("WhileStatement") or content.startswith("DoWhileStatement"):
                content = f"<span style='color:#c586c0; font-weight:bold;'>{content}</span>"
            elif content.startswith("ReturnStatement"):
                content = f"<span style='color:#c586c0;'>{content}</span>"
            else:
                content = f"<span style='color:#dcdcdc;'>{content}</span>"
                
            formatted_lines.append(f"{indent}{content}")
            
        return "<br>".join(formatted_lines)
 
    def save_log_dialog(self):
        if not hasattr(self, 'last_report') or not self.last_report:
            QMessageBox.warning(self, "Advertencia", "No hay ningún reporte generado para guardar.")
            return
            
        # Nombre por defecto del log: analizador-desarrollador-DD-MM-YYYY-HH-MM.txt
        import datetime
        now = datetime.datetime.now()
        date_str = now.strftime("%d-%m-%Y-%H-%M")
        default_name = f"analizador-ManuelMatute-{date_str}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Log de Compilación", default_name, "Archivos de Texto (*.txt)"
        )
        
        if file_path:
            try:
                # Si la carpeta logs no existe, la crea
                logs_dir = os.path.dirname(file_path)
                if logs_dir and not os.path.exists(logs_dir):
                    os.makedirs(logs_dir)
                    
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.last_report)
                self.status_bar.showMessage(f"Log guardado en: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el log:\n{str(e)}")
 
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
