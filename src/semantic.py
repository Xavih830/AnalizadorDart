# -*- coding: utf-8 -*-
"""
Analizador Semántico para el lenguaje Dart.
Implementado de forma colaborativa por:
- Xavier Camacho (Xavih830)
- Manuel Matute (ManuelMatute)
- Johan Veloz (johegvel)
"""
from src.ast_nodes import Identifier

class SymbolTable:
    """Tabla de Símbolos con soporte de ámbitos (scoping)."""
    def __init__(self):
        # La pila de ámbitos. El primero es el ámbito global.
        self.scopes = [{}]

    def push(self):
        """Entra a un nuevo ámbito léxico."""
        self.scopes.append({})

    def pop(self):
        """Sale del ámbito léxico actual."""
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, name, symbol_type, kind='variable'):
        """Declara un símbolo en el ámbito actual."""
        self.scopes[-1][name] = {'type': symbol_type, 'kind': kind}

    def lookup(self, name):
        """Busca un símbolo en todos los ámbitos activos, desde el interno al global."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None


class SemanticAnalyzer:
    """Implementa el analisis semantico de las reglas SE-01 a SE-06."""
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function = None  # Almacena el nodo de la función actual
        self.loop_depth = 0           # Cuenta la profundidad de bucles activos

    def analyze(self, ast):
        """
        Punto de entrada principal para realizar el análisis semántico.
        Retorna la lista de errores semánticos detectados.
        """
        self.errors = []
        self.symbol_table = SymbolTable()
        self.current_function = None
        self.loop_depth = 0
        
        # Pre-registrar funciones estándar incorporadas de Dart para evitar falsos positivos
        self.symbol_table.declare('print', 'void', 'function')
        
        self.visit(ast)
        return self.errors

    def visit(self, node):
        """Llama al método visit_NombreNodo correspondiente."""
        if not node:
            return 'dynamic'
        
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Visita por defecto para nodos sin manejador explícito."""
        # Se recorren todos los atributos del nodo buscando otros nodos del AST
        for attr in dir(node):
            if attr.startswith('_'):
                continue
            val = getattr(node, attr)
            if isinstance(val, list):
                for item in val:
                    if hasattr(item, 'to_string'): # Es un nodo del AST
                        self.visit(item)
            elif hasattr(val, 'to_string'):
                self.visit(val)
        return 'dynamic'

    # --- Utilidades Semánticas ---

    def is_compatible(self, t_val, t_decl):
        """Verifica compatibilidad de tipos (Covarianza básica y Null Safety)."""
        if not t_val or not t_decl:
            return True
        if t_decl == 'dynamic' or t_val == 'dynamic':
            return True
        if t_decl == 'var':
            return True
        if t_decl == t_val:
            return True

        # Soporte básico para Null Safety
        if t_val == 'Null':
            if t_decl.endswith('?'):
                return True
            if t_decl in ['Null', 'dynamic', 'Object']:
                return True
            return False

        # Quitar comodines de opcionalidad (?)
        t_decl_clean = t_decl[:-1] if t_decl.endswith('?') else t_decl
        t_val_clean = t_val[:-1] if t_val.endswith('?') else t_val

        if t_decl_clean == t_val_clean:
            return True

        # Jerarquía Numérica en Dart (int y double heredan de num)
        if t_val_clean in ['int', 'double'] and t_decl_clean == 'num':
            return True
        # En Dart moderno, se permite casting implícito de int a double en asignaciones literales
        if t_val_clean == 'int' and t_decl_clean == 'double':
            return True

        # Object es ancestro común de todos los tipos no-nulos
        if t_decl_clean == 'Object':
            return True

        return False

    def is_castable(self, t_orig, t_dest):
        """Verifica si es posible realizar un casting con el operador 'as' (SE-06)."""
        if t_orig == 'dynamic' or t_dest == 'dynamic':
            return True
        if t_orig == 'Object' or t_dest == 'Object':
            return True
        if t_orig == t_dest:
            return True

        o = t_orig[:-1] if t_orig.endswith('?') else t_orig
        d = t_dest[:-1] if t_dest.endswith('?') else t_dest

        if o == d:
            return True

        # Permitir casting entre tipos numéricos (downcast/upcast)
        if o in ['int', 'double', 'num'] and d in ['int', 'double', 'num']:
            return True

        # Permitir casting entre la misma estructura genérica (ej. List<dynamic> as List<int>)
        if (o.startswith('List') and d.startswith('List')) or \
           (o.startswith('Map') and d.startswith('Map')) or \
           (o.startswith('Set') and d.startswith('Set')):
            return True

        return False

    # --- Manejadores de Nodos del AST ---

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)
        return 'void'

    def visit_ImportStatement(self, node):
        return 'void'

    def visit_VarDeclaration(self, node):
        # Primero evaluamos el valor para evitar autorreferencias no declaradas en la inicialización
        val_type = 'Null'
        if node.value:
            val_type = self.visit(node.value)

        decl_type = node.var_type or 'dynamic'
        
        # Inferencia de tipo con var, final o const sin tipo explícito
        if decl_type in ['var', 'final', 'const'] or decl_type is None:
            decl_type = val_type

        # Registrar en la tabla de símbolos
        self.symbol_table.declare(node.name, decl_type, 'variable')

        # Regla SE-02: incompatibilidad de tipo en asignación
        if node.value and val_type != 'dynamic' and decl_type != 'dynamic':
            if not self.is_compatible(val_type, decl_type):
                err_msg = f"ERROR_TIPO: no se puede asignar '{val_type}' a la variable '{node.name}' de tipo '{decl_type}' (linea {node.line})"
                self.errors.append({
                    'phase': 'Semántico',
                    'category': 'ERROR_TIPO',
                    'message': err_msg,
                    'line': node.line,
                    'lexeme': node.name
                })
        return 'void'

    def visit_Block(self, node):
        self.symbol_table.push()
        for stmt in node.statements:
            self.visit(stmt)
        self.symbol_table.pop()
        return 'void'

    def visit_ExpressionStatement(self, node):
        return self.visit(node.expression)

    def visit_BinaryOp(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        # Regla SE-02 en asignaciones
        if node.op in ['=', '+=', '-=', '*=', '/=', '~/=', '%=', '??=']:
            if isinstance(node.left, Identifier):
                # Verificar asignación a variables no declaradas
                self.visit(node.left) 
                
                # Para asignación directa, verificar compatibilidad de tipo
                if node.op == '=' and left_type != 'dynamic' and right_type != 'dynamic':
                    if not self.is_compatible(right_type, left_type):
                        err_msg = f"ERROR_TIPO: no se puede asignar '{right_type}' a la variable '{node.left.name}' de tipo '{left_type}' (linea {node.line})"
                        self.errors.append({
                            'phase': 'Semántico',
                            'category': 'ERROR_TIPO',
                            'message': err_msg,
                            'line': node.line,
                            'lexeme': node.left.name
                        })
            return left_type

        # Regla SE-03: incompatibilidad entre operandos aritméticos
        arithmetic_ops = ['+', '-', '*', '/', '~/', '%']
        if node.op in arithmetic_ops:
            # Caso especial: Concatenación de cadenas en Dart es válida
            if node.op == '+' and left_type == 'String' and right_type == 'String':
                return 'String'

            is_left_num = left_type in ['int', 'double', 'num', 'dynamic']
            is_right_num = right_type in ['int', 'double', 'num', 'dynamic']

            if not is_left_num or not is_right_num:
                err_msg = f"ERROR_OPERACION: el operador '{node.op}' no es aplicable entre '{left_type}' y '{right_type}' (linea {node.line})"
                self.errors.append({
                    'phase': 'Semántico',
                    'category': 'ERROR_OPERACION',
                    'message': err_msg,
                    'line': node.line,
                    'lexeme': node.op
                })
                return 'dynamic'

            # Determinar tipo de retorno aritmético
            if node.op == '/':
                return 'double'
            if node.op == '~/':
                return 'int'
            if left_type == 'double' or right_type == 'double':
                return 'double'
            if left_type == 'num' or right_type == 'num':
                return 'num'
            return 'int'

        # Operaciones Relacionales y Lógicas devuelven booleanos
        if node.op in ['==', '!=', '<', '>', '<=', '>=']:
            return 'bool'
        if node.op in ['&&', '||']:
            return 'bool'
        
        # Operador de fusión nula ??
        if node.op == '??':
            return left_type if left_type != 'Null' else right_type

        return 'dynamic'

    def visit_UnaryOp(self, node):
        operand_type = self.visit(node.operand)
        
        if node.op in ['++', '--']:
            if operand_type not in ['int', 'double', 'num', 'dynamic']:
                err_msg = f"ERROR_OPERACION: el operador '{node.op}' no es aplicable a un tipo '{operand_type}' (linea {node.line})"
                self.errors.append({
                    'phase': 'Semántico',
                    'category': 'ERROR_OPERACION',
                    'message': err_msg,
                    'line': node.line,
                    'lexeme': node.op
                })
            return operand_type
            
        if node.op == '!':
            return 'bool'
            
        # Postfix assert ! (e.g. valor!) remueve la nulabilidad
        if node.op == '!' and node.is_postfix:
            if operand_type.endswith('?'):
                return operand_type[:-1]
            return operand_type

        return operand_type

    def visit_TernaryOp(self, node):
        self.visit(node.condition)
        true_t = self.visit(node.true_val)
        false_t = self.visit(node.false_val)
        return true_t if true_t == false_t else 'dynamic'

    def visit_CastExpression(self, node):
        expr_type = self.visit(node.expression)
        target_type = node.target_type

        # Regla SE-06: casting entre tipos incompatibles
        if expr_type != 'dynamic' and target_type != 'dynamic':
            if not self.is_castable(expr_type, target_type):
                err_msg = f"ERROR_TIPO: no es posible convertir '{expr_type}' a '{target_type}' con casting (linea {node.line})"
                self.errors.append({
                    'phase': 'Semántico',
                    'category': 'ERROR_TIPO',
                    'message': err_msg,
                    'line': node.line,
                    'lexeme': 'as'
                })
                return 'dynamic'
        return target_type

    def visit_TypeTest(self, node):
        self.visit(node.expression)
        return 'bool'

    def visit_Identifier(self, node):
        # Regla SE-01: uso de variable no declarada
        sym = self.symbol_table.lookup(node.name)
        if not sym:
            err_msg = f"ERROR_IDENTIFICADOR: la variable '{node.name}' no ha sido declarada en el ambito actual (linea {node.line})"
            self.errors.append({
                'phase': 'Semántico',
                'category': 'ERROR_IDENTIFICADOR',
                'message': err_msg,
                'line': node.line,
                'lexeme': node.name
            })
            return 'dynamic'
        return sym['type']

    def visit_Literal(self, node):
        return node.literal_type

    def visit_ListLiteral(self, node):
        for elem in node.elements:
            self.visit(elem)
        return f"List<{node.type_param or 'dynamic'}>"

    def visit_MapLiteral(self, node):
        for k, v in node.key_values:
            self.visit(k)
            self.visit(v)
        k_t = node.key_type or 'dynamic'
        v_t = node.value_type or 'dynamic'
        return f"Map<{k_t}, {v_t}>"

    def visit_SetLiteral(self, node):
        for elem in node.elements:
            self.visit(elem)
        return f"Set<{node.type_param or 'dynamic'}>"

    def visit_IndexAccess(self, node):
        self.visit(node.collection)
        self.visit(node.index)
        return 'dynamic'

    def visit_MemberAccess(self, node):
        self.visit(node.obj)
        # Retornamos dynamic para simplificar accesos a campos
        return 'dynamic'

    def visit_FunctionCall(self, node):
        # Evaluar argumentos
        for arg in node.args:
            if hasattr(arg, 'value'): # Named argument
                self.visit(arg.value)
            else:
                self.visit(arg)

        # Buscar el tipo de retorno de la función
        if isinstance(node.name_node, Identifier):
            sym = self.symbol_table.lookup(node.name_node.name)
            if sym and sym['kind'] in ['function', 'method']:
                return sym['type']
        return 'dynamic'

    def visit_FunctionDeclaration(self, node):
        # Declarar la función antes de evaluar el cuerpo (permite llamadas recursivas)
        ret_type = node.return_type or 'dynamic'
        self.symbol_table.declare(node.name, ret_type, 'function')

        old_func = self.current_function
        self.current_function = node

        self.symbol_table.push()
        for param in node.params:
            p_type = param.param_type or 'dynamic'
            self.symbol_table.declare(param.name, p_type, 'variable')

        body_type = self.visit(node.body)

        # Regla SE-05 en funciones flecha directamente
        if node.is_arrow and ret_type != 'void' and ret_type != 'dynamic':
            if not self.is_compatible(body_type, ret_type):
                err_msg = f"ERROR_RETORNO: la funcion '{node.name}' declara tipo '{ret_type}' pero retorna '{body_type}' (linea {node.line})"
                self.errors.append({
                    'phase': 'Semántico',
                    'category': 'ERROR_RETORNO',
                    'message': err_msg,
                    'line': node.line,
                    'lexeme': node.name
                })

        self.symbol_table.pop()
        self.current_function = old_func
        return 'void'

    def visit_ReturnStatement(self, node):
        ret_type = 'void'
        if node.expression:
            ret_type = self.visit(node.expression)

        # Regla SE-05: tipo de retorno incompatible
        if self.current_function:
            decl_type = self.current_function.return_type or 'void'
            if decl_type != 'void' and decl_type != 'dynamic' and ret_type != 'dynamic':
                if not self.is_compatible(ret_type, decl_type):
                    err_msg = f"ERROR_RETORNO: la funcion '{self.current_function.name}' declara tipo '{decl_type}' pero retorna '{ret_type}' (linea {node.line})"
                    self.errors.append({
                        'phase': 'Semántico',
                        'category': 'ERROR_RETORNO',
                        'message': err_msg,
                        'line': node.line,
                        'lexeme': self.current_function.name
                    })
        return 'void'

    def visit_BreakStatement(self, node):
        # Regla SE-04: break fuera de bucle o switch
        if self.loop_depth <= 0:
            err_msg = f"ERROR_CONTROL: 'break' no esta dentro de un bucle o switch (linea {node.line})"
            self.errors.append({
                'phase': 'Semántico',
                'category': 'ERROR_CONTROL',
                'message': err_msg,
                'line': node.line,
                'lexeme': 'break'
            })
        return 'void'

    def visit_IfStatement(self, node):
        self.visit(node.condition)
        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)
        return 'void'

    def visit_ForStatement(self, node):
        self.symbol_table.push()
        self.loop_depth += 1
        
        if node.init:
            self.visit(node.init)
        if node.condition:
            self.visit(node.condition)
        if node.update:
            self.visit(node.update)
            
        self.visit(node.body)
        
        self.loop_depth -= 1
        self.symbol_table.pop()
        return 'void'

    def visit_ForInStatement(self, node):
        self.symbol_table.push()
        self.loop_depth += 1
        
        self.symbol_table.declare(node.var_name, node.var_type or 'dynamic', 'variable')
        self.visit(node.iterable)
        self.visit(node.body)
        
        self.loop_depth -= 1
        self.symbol_table.pop()
        return 'void'

    def visit_WhileStatement(self, node):
        self.loop_depth += 1
        self.visit(node.condition)
        self.visit(node.body)
        self.loop_depth -= 1
        return 'void'

    def visit_DoWhileStatement(self, node):
        self.loop_depth += 1
        self.visit(node.body)
        self.visit(node.condition)
        self.loop_depth -= 1
        return 'void'

    def visit_ClassDeclaration(self, node):
        # Registrar tipo de clase
        self.symbol_table.declare(node.name, node.name, 'class')
        
        self.symbol_table.push()
        for member in node.members:
            self.visit(member)
        self.symbol_table.pop()
        return 'void'

    def visit_FieldDeclaration(self, node):
        self.symbol_table.declare(node.name, node.field_type or 'dynamic', 'field')
        return 'void'

    def visit_ConstructorDeclaration(self, node):
        self.symbol_table.push()
        for param in node.params:
            self.symbol_table.declare(param.name, param.param_type or 'dynamic', 'variable')
        if node.body:
            self.visit(node.body)
        self.symbol_table.pop()
        return 'void'

    def visit_MethodDeclaration(self, node):
        ret_type = node.return_type or 'dynamic'
        self.symbol_table.declare(node.name, ret_type, 'method')

        old_func = self.current_function
        self.current_function = node

        self.symbol_table.push()
        for param in node.params:
            p_type = param.param_type or 'dynamic'
            self.symbol_table.declare(param.name, p_type, 'variable')
            
        self.visit(node.body)
        
        self.symbol_table.pop()
        self.current_function = old_func
        return 'void'

    def visit_GetterDeclaration(self, node):
        ret_type = node.return_type or 'dynamic'
        self.symbol_table.declare(node.name, ret_type, 'getter')

        old_func = self.current_function
        self.current_function = node

        self.symbol_table.push()
        self.visit(node.body)
        self.symbol_table.pop()
        
        self.current_function = old_func
        return 'void'

    def visit_CascadeExpression(self, node):
        self.visit(node.target)
        for op in node.operations:
            self.visit(op)
        return 'dynamic'

    def visit_MultiVarDeclaration(self, node):
        for decl in node.declarations:
            self.visit(decl)
        return 'void'

