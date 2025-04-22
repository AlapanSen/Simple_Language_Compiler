from src.parser import (
    BinOp, Number, Float, Boolean, String, StringInterpolation, UnaryOp, Variable,
    VarDecl, Assign, Print, If, While,
    Compound, NoOp
)

class NodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

class Interpreter(NodeVisitor):
    def __init__(self):
        self.global_scope = {}

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.op.type == 'PLUS':
            return left + right
        elif node.op.type == 'MINUS':
            return left - right
        elif node.op.type == 'MULTIPLY':
            return left * right
        elif node.op.type == 'DIVIDE':
            # Handle division differently for integers vs floats
            if isinstance(left, int) and isinstance(right, int):
                return left // right  # Integer division
            else:
                return left / right   # Float division
        elif node.op.type == 'EQUALS':
            return left == right
        elif node.op.type == 'NOT_EQUALS':
            return left != right
        elif node.op.type == 'LESS':
            return left < right
        elif node.op.type == 'GREATER':
            return left > right
        elif node.op.type == 'LESS_EQUAL':
            return left <= right
        elif node.op.type == 'GREATER_EQUAL':
            return left >= right
        elif node.op.type == 'AND':
            return left and right
        elif node.op.type == 'OR':
            return left or right

    def visit_UnaryOp(self, node):
        expr = self.visit(node.expr)
        
        if node.op.type == 'PLUS':
            return +expr
        elif node.op.type == 'MINUS':
            return -expr
        elif node.op.type == 'NOT':
            return not expr

    def visit_Number(self, node):
        return node.value

    def visit_Float(self, node):
        return node.value
        
    def visit_Boolean(self, node):
        return node.value

    def visit_String(self, node):
        return node.value
    
    def visit_StringInterpolation(self, node):
        # Evaluate each part and concatenate the results
        result = ""
        for part in node.parts:
            # Convert each part to string and concatenate
            part_value = self.visit(part)
            result += str(part_value)
        return result

    def visit_Variable(self, node):
        var_name = node.value
        if var_name not in self.global_scope:
            raise Exception(f"Variable '{var_name}' not defined")
        return self.global_scope[var_name]

    def visit_VarDecl(self, node):
        var_name = node.variable.value
        var_value = self.visit(node.value)
        self.global_scope[var_name] = var_value

    def visit_Assign(self, node):
        var_name = node.left.value
        if var_name not in self.global_scope:
            raise Exception(f"Cannot assign to undeclared variable '{var_name}'")
        var_value = self.visit(node.right)
        self.global_scope[var_name] = var_value

    def visit_Print(self, node):
        value = self.visit(node.expr)
        print(value)
        return value

    def visit_If(self, node):
        condition = self.visit(node.condition)
        if condition:
            return self.visit(node.body)
        elif node.else_body:
            return self.visit(node.else_body)

    def visit_While(self, node):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_Compound(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_NoOp(self, node):
        pass

    def interpret(self, tree):
        return self.visit(tree) 