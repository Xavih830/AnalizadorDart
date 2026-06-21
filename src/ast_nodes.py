# -*- coding: utf-8 -*-
"""
Módulo que define los nodos del Árbol de Sintaxis Abstracta (AST) 
para el lenguaje Dart.
"""

class ASTNode:
    """Clase base para todos los nodos del AST."""
    def to_string(self, indent=0):
        raise NotImplementedError("Cada nodo debe implementar el método to_string")

    def __str__(self):
        return self.to_string(0)


class Program(ASTNode):
    """Nodo que representa el programa completo (una lista de declaraciones/sentencias)."""
    def __init__(self, statements):
        self.statements = statements

    def to_string(self, indent=0):
        spacing = "  " * indent
        result = f"{spacing}Program\n"
        for stmt in self.statements:
            if stmt:
                result += stmt.to_string(indent + 1) + "\n"
        return result.rstrip()


class VarDeclaration(ASTNode):
    """Declaración de variable (con var, tipo explícito, final o const)."""
    def __init__(self, name, var_type, value, is_final=False, is_const=False, line=0):
        self.name = name
        self.var_type = var_type  # Puede ser 'var', 'int', 'String', etc.
        self.value = value        # Nodo expresión
        self.is_final = is_final
        self.is_const = is_const
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        modifier = ""
        if self.is_const:
            modifier = "const "
        elif self.is_final:
            modifier = "final "
        
        type_str = self.var_type if self.var_type else "dynamic"
        val_str = self.value.to_string(0) if self.value else "null"
        return f"{spacing}VarDeclaration: {modifier}{type_str} {self.name} = {val_str} (linea {self.line})"


class Block(ASTNode):
    """Bloque de código encerrado entre llaves."""
    def __init__(self, statements):
        self.statements = statements

    def to_string(self, indent=0):
        spacing = "  " * indent
        result = f"{spacing}Block\n"
        for stmt in self.statements:
            if stmt:
                result += stmt.to_string(indent + 1) + "\n"
        return result.rstrip()


class IfStatement(ASTNode):
    """Estructura condicional if / else if / else."""
    def __init__(self, condition, then_branch, else_branch=None, line=0):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        result = f"{spacing}IfStatement (linea {self.line})\n"
        result += f"{spacing}  Condition:\n" + self.condition.to_string(indent + 2) + "\n"
        result += f"{spacing}  Then:\n" + self.then_branch.to_string(indent + 2)
        if self.else_branch:
            result += f"\n{spacing}  Else:\n" + self.else_branch.to_string(indent + 2)
        return result


class ForStatement(ASTNode):
    """Bucle for clásico."""
    def __init__(self, init, condition, update, body, line=0):
        self.init = init            # Declaración o expresión de inicialización
        self.condition = condition  # Expresión booleana
        self.update = update        # Expresión de actualización (e.g. x++)
        self.body = body            # Sentencia o bloque
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        init_str = self.init.to_string(0) if self.init else "none"
        cond_str = self.condition.to_string(0) if self.condition else "none"
        up_str = self.update.to_string(0) if self.update else "none"
        result = f"{spacing}ForStatement (linea {self.line}) [Init: {init_str}, Cond: {cond_str}, Update: {up_str}]\n"
        result += self.body.to_string(indent + 1)
        return result


class ForInStatement(ASTNode):
    """Bucle for-in para iterar colecciones."""
    def __init__(self, var_type, var_name, iterable, body, line=0):
        self.var_type = var_type
        self.var_name = var_name
        self.iterable = iterable
        self.body = body
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        iter_str = self.iterable.to_string(0)
        type_str = self.var_type if self.var_type else "var"
        result = f"{spacing}ForInStatement (linea {self.line}) [Iterate: {type_str} {self.var_name} in {iter_str}]\n"
        result += self.body.to_string(indent + 1)
        return result


class WhileStatement(ASTNode):
    """Bucle while."""
    def __init__(self, condition, body, line=0):
        self.condition = condition
        self.body = body
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        result = f"{spacing}WhileStatement (linea {self.line})\n"
        result += f"{spacing}  Condition:\n" + self.condition.to_string(indent + 2) + "\n"
        result += f"{spacing}  Body:\n" + self.body.to_string(indent + 2)
        return result


class DoWhileStatement(ASTNode):
    """Bucle do-while."""
    def __init__(self, body, condition, line=0):
        self.body = body
        self.condition = condition
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        result = f"{spacing}DoWhileStatement (linea {self.line})\n"
        result += f"{spacing}  Body:\n" + self.body.to_string(indent + 2) + "\n"
        result += f"{spacing}  Condition:\n" + self.condition.to_string(indent + 2)
        return result


class FunctionDeclaration(ASTNode):
    """Declaración de una función."""
    def __init__(self, name, return_type, params, body, is_arrow=False, line=0):
        self.name = name
        self.return_type = return_type
        self.params = params  # Lista de Parameter
        self.body = body      # Bloque o Expresión (si es función flecha)
        self.is_arrow = is_arrow
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        arrow_str = " =>" if self.is_arrow else ""
        ret_str = self.return_type if self.return_type else "dynamic"
        params_str = ", ".join([f"{p.param_type} {p.name}" + (" (required)" if p.is_required else "") for p in self.params])
        result = f"{spacing}FunctionDeclaration: {ret_str} {self.name}({params_str}){arrow_str} (linea {self.line})\n"
        result += self.body.to_string(indent + 1)
        return result


class Parameter(ASTNode):
    """Parámetro de función o constructor."""
    def __init__(self, name, param_type, is_required=False, default_value=None, is_named=False, is_this=False):
        self.name = name
        self.param_type = param_type  # Puede ser int, String, dynamic, etc.
        self.is_required = is_required
        self.default_value = default_value  # Expresión por defecto
        self.is_named = is_named
        self.is_this = is_this  # Para constructors 'this.nombre'


class ClassDeclaration(ASTNode):
    """Declaración de una clase."""
    def __init__(self, name, members, line=0):
        self.name = name
        self.members = members  # Lista de campos, constructores, métodos
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        result = f"{spacing}ClassDeclaration: class {self.name} (linea {self.line})\n"
        for member in self.members:
            if member:
                result += member.to_string(indent + 1) + "\n"
        return result.rstrip()


class FieldDeclaration(ASTNode):
    """Declaración de un campo de clase."""
    def __init__(self, name, field_type, is_final=False, line=0):
        self.name = name
        self.field_type = field_type
        self.is_final = is_final
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        final_str = "final " if self.is_final else ""
        return f"{spacing}Field: {final_str}{self.field_type} {self.name} (linea {self.line})"


class ConstructorDeclaration(ASTNode):
    """Declaración de un constructor."""
    def __init__(self, class_name, params, initializers=None, body=None, line=0):
        self.class_name = class_name
        self.params = params  # Lista de Parameter
        self.initializers = initializers
        self.body = body      # Bloque o Arrow o None
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        params_str = []
        for p in self.params:
            prefix = "this." if p.is_this else ""
            req = "required " if p.is_required else ""
            default = f" = {p.default_value}" if p.default_value else ""
            params_str.append(f"{req}{prefix}{p.name}{default}")
        params_formatted = ", ".join(params_str)
        result = f"{spacing}Constructor: {self.class_name}({params_formatted}) (linea {self.line})"
        if self.body:
            result += "\n" + self.body.to_string(indent + 1)
        return result


class GetterDeclaration(ASTNode):
    """Declaración de un Getter de clase."""
    def __init__(self, name, return_type, body, line=0):
        self.name = name
        self.return_type = return_type
        self.body = body
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        ret = self.return_type if self.return_type else "dynamic"
        result = f"{spacing}Getter: {ret} get {self.name} (linea {self.line})\n"
        result += self.body.to_string(indent + 1)
        return result


class MethodDeclaration(ASTNode):
    """Declaración de un método de clase."""
    def __init__(self, name, return_type, params, body, annotations=None, line=0):
        self.name = name
        self.return_type = return_type
        self.params = params
        self.body = body
        self.annotations = annotations or []  # e.g., '@override'
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        ann_str = "".join([f"{a} " for a in self.annotations])
        ret = self.return_type if self.return_type else "dynamic"
        params_str = ", ".join([f"{p.param_type} {p.name}" for p in self.params])
        result = f"{spacing}Method: {ann_str}{ret} {self.name}({params_str}) (linea {self.line})\n"
        result += self.body.to_string(indent + 1)
        return result


class ReturnStatement(ASTNode):
    """Instrucción de retorno."""
    def __init__(self, expression, line=0):
        self.expression = expression  # Nodo expresión o None
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        val = self.expression.to_string(0) if self.expression else "void"
        return f"{spacing}ReturnStatement: return {val} (linea {self.line})"


class BreakStatement(ASTNode):
    """Instrucción break."""
    def __init__(self, line=0):
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        return f"{spacing}BreakStatement (linea {self.line})"


class PrintStatement(ASTNode):
    """Instrucción print()."""
    def __init__(self, expression, line=0):
        self.expression = expression
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        return f"{spacing}PrintStatement: print({self.expression.to_string(0)}) (linea {self.line})"


class ImportStatement(ASTNode):
    """Instrucción import '...';"""
    def __init__(self, uri, line=0):
        self.uri = uri
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        return f"{spacing}ImportStatement: import '{self.uri}' (linea {self.line})"


class ExpressionStatement(ASTNode):
    """Sentencia compuesta de una sola expresión."""
    def __init__(self, expression, line=0):
        self.expression = expression
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        return f"{spacing}ExpressionStatement: {self.expression.to_string(0)} (linea {self.line})"


# --- Expresiones ---

class BinaryOp(ASTNode):
    """Operación binaria (aritmética, relacional, lógica, asignación)."""
    def __init__(self, left, op, right, line=0):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        # Si indent es 0, hacemos representación lineal simple para legibilidad
        if indent == 0:
            return f"({self.left.to_string(0)} {self.op} {self.right.to_string(0)})"
        result = f"{spacing}BinaryOp: {self.op} (linea {self.line})\n"
        result += self.left.to_string(indent + 1) + "\n"
        result += self.right.to_string(indent + 1)
        return result


class UnaryOp(ASTNode):
    """Operación unaria (prefijo o postfijo, incremento, decremento, negación)."""
    def __init__(self, op, operand, is_postfix=False, line=0):
        self.op = op
        self.operand = operand
        self.is_postfix = is_postfix
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        if indent == 0:
            if self.is_postfix:
                return f"{self.operand.to_string(0)}{self.op}"
            else:
                return f"{self.op}{self.operand.to_string(0)}"
        
        pos = "Postfix" if self.is_postfix else "Prefix"
        result = f"{spacing}UnaryOp: {self.op} ({pos}, linea {self.line})\n"
        result += self.operand.to_string(indent + 1)
        return result


class TernaryOp(ASTNode):
    """Operación condicional ternaria (cond ? true_expr : false_expr)."""
    def __init__(self, condition, true_val, false_val, line=0):
        self.condition = condition
        self.true_val = true_val
        self.false_val = false_val
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        if indent == 0:
            return f"({self.condition.to_string(0)} ? {self.true_val.to_string(0)} : {self.false_val.to_string(0)})"
        result = f"{spacing}TernaryOp (linea {self.line})\n"
        result += f"{spacing}  Cond: {self.condition.to_string(0)}\n"
        result += f"{spacing}  True: {self.true_val.to_string(0)}\n"
        result += f"{spacing}  False: {self.false_val.to_string(0)}"
        return result


class CastExpression(ASTNode):
    """Operación de casting: expr as Tipo."""
    def __init__(self, expression, target_type, line=0):
        self.expression = expression
        self.target_type = target_type
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        if indent == 0:
            return f"({self.expression.to_string(0)} as {self.target_type})"
        result = f"{spacing}CastExpression: as {self.target_type} (linea {self.line})\n"
        result += self.expression.to_string(indent + 1)
        return result


class TypeTest(ASTNode):
    """Operador de verificación de tipo: expr is Tipo o expr is! Tipo."""
    def __init__(self, expression, target_type, is_negated=False, line=0):
        self.expression = expression
        self.target_type = target_type
        self.is_negated = is_negated
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        op = "is!" if self.is_negated else "is"
        if indent == 0:
            return f"({self.expression.to_string(0)} {op} {self.target_type})"
        result = f"{spacing}TypeTest: {op} {self.target_type} (linea {self.line})\n"
        result += self.expression.to_string(indent + 1)
        return result


class Literal(ASTNode):
    """Valores literales (números, cadenas, booleanos, nulos)."""
    def __init__(self, value, literal_type, line=0):
        self.value = value
        self.literal_type = literal_type  # 'int', 'double', 'String', 'bool', 'Null'
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        val_str = f"'{self.value}'" if self.literal_type == 'String' else str(self.value)
        if indent == 0:
            return val_str
        return f"{spacing}Literal ({self.literal_type}): {val_str}"


class Identifier(ASTNode):
    """Identificadores de variables o funciones."""
    def __init__(self, name, line=0):
        self.name = name
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        if indent == 0:
            return self.name
        return f"{spacing}Identifier: {self.name}"


class ListLiteral(ASTNode):
    """Literal de Lista: [1, 2, 3] o <String>['a', 'b']."""
    def __init__(self, elements, type_param=None, line=0):
        self.elements = elements
        self.type_param = type_param  # Tipo genérico (e.g., 'int')
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        type_prefix = f"<{self.type_param}>" if self.type_param else ""
        elem_strs = [e.to_string(0) for e in self.elements]
        if indent == 0:
            return f"{type_prefix}[{', '.join(elem_strs)}]"
        result = f"{spacing}ListLiteral {type_prefix} (linea {self.line})\n"
        for elem in self.elements:
            result += elem.to_string(indent + 1) + "\n"
        return result.rstrip()


class MapLiteral(ASTNode):
    """Literal de Mapa (Map): {'clave': valor}."""
    def __init__(self, key_values, key_type=None, value_type=None, line=0):
        self.key_values = key_values  # Lista de tuplas (key_node, val_node)
        self.key_type = key_type
        self.value_type = value_type
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        type_prefix = f"<{self.key_type}, {self.value_type}>" if self.key_type else ""
        pair_strs = [f"{k.to_string(0)}: {v.to_string(0)}" for k, v in self.key_values]
        if indent == 0:
            return f"{type_prefix}{{{', '.join(pair_strs)}}}"
        result = f"{spacing}MapLiteral {type_prefix} (linea {self.line})\n"
        for k, v in self.key_values:
            result += f"{spacing}  Key: {k.to_string(0)} -> Value:\n{v.to_string(indent + 2)}\n"
        return result.rstrip()


class SetLiteral(ASTNode):
    """Literal de Conjunto (Set): {'elem1', 'elem2'}."""
    def __init__(self, elements, type_param=None, line=0):
        self.elements = elements
        self.type_param = type_param
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        type_prefix = f"<{self.type_param}>" if self.type_param else ""
        elem_strs = [e.to_string(0) for e in self.elements]
        if indent == 0:
            return f"{type_prefix}{{{', '.join(elem_strs)}}}"
        result = f"{spacing}SetLiteral {type_prefix} (linea {self.line})\n"
        for elem in self.elements:
            result += elem.to_string(indent + 1) + "\n"
        return result.rstrip()


class IndexAccess(ASTNode):
    """Acceso a colección por índice: lista[indice] o mapa[clave]."""
    def __init__(self, collection, index, line=0):
        self.collection = collection  # Nodo expresión (identificador, etc.)
        self.index = index            # Nodo expresión índice/clave
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        if indent == 0:
            return f"{self.collection.to_string(0)}[{self.index.to_string(0)}]"
        result = f"{spacing}IndexAccess (linea {self.line})\n"
        result += f"{spacing}  Collection: {self.collection.to_string(0)}\n"
        result += f"{spacing}  Index: {self.index.to_string(0)}"
        return result


class MemberAccess(ASTNode):
    """Acceso a miembro de un objeto: obj.prop, obj?.prop, obj!.prop."""
    def __init__(self, obj, member_name, is_null_safe=False, is_assert=False, line=0):
        self.obj = obj
        self.member_name = member_name
        self.is_null_safe = is_null_safe
        self.is_assert = is_assert
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        op = "?." if self.is_null_safe else ("!." if self.is_assert else ".")
        if indent == 0:
            return f"{self.obj.to_string(0)}{op}{self.member_name}"
        return f"{spacing}MemberAccess: {self.obj.to_string(0)}{op}{self.member_name} (linea {self.line})"


class FunctionCall(ASTNode):
    """Llamada a función o constructor: miFuncion(1, 2) o Clase(nombre: 'a')."""
    def __init__(self, name_node, args, line=0):
        self.name_node = name_node  # Puede ser Identifier o MemberAccess
        self.args = args            # Lista de argumentos (puede contener Argument)
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        arg_strs = []
        for arg in self.args:
            if isinstance(arg, Argument):
                arg_strs.append(f"{arg.name}: {arg.value.to_string(0)}")
            else:
                arg_strs.append(arg.to_string(0))
        name_str = self.name_node.to_string(0)
        if indent == 0:
            return f"{name_str}({', '.join(arg_strs)})"
        
        result = f"{spacing}FunctionCall: {name_str} (linea {self.line})\n"
        for arg in self.args:
            if isinstance(arg, Argument):
                result += f"{spacing}  NamedArg: {arg.name} = {arg.value.to_string(0)}\n"
            else:
                result += arg.to_string(indent + 1) + "\n"
        return result.rstrip()


class Argument(ASTNode):
    """Argumento nombrado de una función: nombre: valor."""
    def __init__(self, name, value):
        self.name = name
        self.value = value  # Nodo expresión


class CascadeExpression(ASTNode):
    """Expresión de cascada: obj..metodo()..prop = x."""
    def __init__(self, target, operations, line=0):
        self.target = target
        self.operations = operations  # Lista de operaciones encadenadas
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        op_strs = [op.to_string(0) for op in self.operations]
        if indent == 0:
            return f"{self.target.to_string(0)}..{r'..'.join(op_strs)}"
        result = f"{spacing}CascadeExpression (linea {self.line})\n"
        result += f"{spacing}  Target: {self.target.to_string(0)}\n"
        for op in self.operations:
            result += f"{spacing}  Op: {op.to_string(0)}\n"
        return result.rstrip()


class MultiVarDeclaration(ASTNode):
    """Declaración múltiple de variables (separadas por comas)."""
    def __init__(self, declarations, line=0):
        self.declarations = declarations  # Lista de VarDeclaration
        self.line = line

    def to_string(self, indent=0):
        spacing = "  " * indent
        result = f"{spacing}MultiVarDeclaration (linea {self.line})\n"
        for decl in self.declarations:
            result += decl.to_string(indent + 1) + "\n"
        return result.rstrip()

