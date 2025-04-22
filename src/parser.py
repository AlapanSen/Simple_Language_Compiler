from src.lexer import Token, Lexer

# AST Nodes
class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Number:
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Float:
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Boolean:
    def __init__(self, token):
        self.token = token
        self.value = token.value

class String:
    def __init__(self, token):
        self.token = token
        self.value = token.value

class StringInterpolation:
    def __init__(self, parts):
        self.parts = parts

class UnaryOp:
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class Variable:
    def __init__(self, token):
        self.token = token
        self.value = token.value

class VarDecl:
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

class Assign:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Print:
    def __init__(self, expr):
        self.expr = expr

class If:
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Compound:
    def __init__(self):
        self.statements = []

class NoOp:
    pass

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message="Invalid syntax"):
        raise Exception(message)

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")

    def parse_interpolation(self, expr_text):
        # Create a new lexer and parser for the interpolated expression
        interpolation_lexer = Lexer(expr_text)
        interpolation_parser = Parser(interpolation_lexer)
        # Parse the expression
        return interpolation_parser.expr()

    def factor(self):
        token = self.current_token
        if token.type == 'INTEGER':
            self.eat('INTEGER')
            return Number(token)
        elif token.type == 'FLOAT':
            self.eat('FLOAT')
            return Float(token)
        elif token.type == 'BOOLEAN':
            self.eat('BOOLEAN')
            return Boolean(token)
        elif token.type == 'STRING':
            self.eat('STRING')
            return String(token)
        elif token.type == 'STRING_INTERPOLATION':
            # Process string interpolation
            parts = []
            string_parts = token.value  # This is a list of tokens
            
            for part in string_parts:
                if part.type == 'STRING_LITERAL':
                    parts.append(String(Token('STRING', part.value)))
                elif part.type == 'INTERPOLATION':
                    expr_node = self.parse_interpolation(part.value)
                    parts.append(expr_node)
            
            self.eat('STRING_INTERPOLATION')
            return StringInterpolation(parts)
        elif token.type == 'IDENTIFIER':
            self.eat('IDENTIFIER')
            return Variable(token)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        elif token.type in ('PLUS', 'MINUS', 'NOT'):
            self.eat(token.type)
            return UnaryOp(token, self.factor())
        self.error()

    def term(self):
        node = self.factor()

        while self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            token = self.current_token
            if token.type == 'MULTIPLY':
                self.eat('MULTIPLY')
            elif token.type == 'DIVIDE':
                self.eat('DIVIDE')
            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        node = self.term()

        while self.current_token.type in ('PLUS', 'MINUS', 'EQUALS', 'NOT_EQUALS', 'LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL', 'AND', 'OR'):
            token = self.current_token
            if token.type == 'PLUS':
                self.eat('PLUS')
            elif token.type == 'MINUS':
                self.eat('MINUS')
            elif token.type == 'EQUALS':
                self.eat('EQUALS')
            elif token.type == 'NOT_EQUALS':
                self.eat('NOT_EQUALS')
            elif token.type == 'LESS':
                self.eat('LESS')
            elif token.type == 'GREATER':
                self.eat('GREATER')
            elif token.type == 'LESS_EQUAL':
                self.eat('LESS_EQUAL')
            elif token.type == 'GREATER_EQUAL':
                self.eat('GREATER_EQUAL')
            elif token.type == 'AND':
                self.eat('AND')
            elif token.type == 'OR':
                self.eat('OR')
            node = BinOp(left=node, op=token, right=self.term())

        return node

    def statement(self):
        if self.current_token.type == 'VAR':
            self.eat('VAR')
            var_node = Variable(self.current_token)
            self.eat('IDENTIFIER')
            self.eat('ASSIGN')
            value_node = self.expr()
            self.eat('SEMICOLON')
            return VarDecl(var_node, value_node)
        elif self.current_token.type == 'IDENTIFIER':
            var_node = Variable(self.current_token)
            self.eat('IDENTIFIER')
            self.eat('ASSIGN')
            value_node = self.expr()
            self.eat('SEMICOLON')
            return Assign(var_node, value_node)
        elif self.current_token.type == 'PRINT':
            self.eat('PRINT')
            expr_node = self.expr()
            self.eat('SEMICOLON')
            return Print(expr_node)
        elif self.current_token.type == 'IF':
            self.eat('IF')
            self.eat('LPAREN')
            condition = self.expr()
            self.eat('RPAREN')
            
            # Handle if body
            if self.current_token.type == 'LBRACE':
                body = self.compound_statement()
            else:
                body = self.statement()
                
            # Handle else part if present
            else_body = None
            if self.current_token.type == 'ELSE':
                self.eat('ELSE')
                if self.current_token.type == 'LBRACE':
                    else_body = self.compound_statement()
                else:
                    else_body = self.statement()
                
            return If(condition, body, else_body)
        elif self.current_token.type == 'WHILE':
            self.eat('WHILE')
            self.eat('LPAREN')
            condition = self.expr()
            self.eat('RPAREN')
            
            # Handle while body
            if self.current_token.type == 'LBRACE':
                body = self.compound_statement()
            else:
                body = self.statement()
                
            return While(condition, body)
        elif self.current_token.type == 'LBRACE':
            return self.compound_statement()
        else:
            return self.empty()

    def statement_list(self):
        node = Compound()
        node.statements.append(self.statement())

        while self.current_token.type not in ('RBRACE', 'EOF'):
            node.statements.append(self.statement())

        return node

    def compound_statement(self):
        self.eat('LBRACE')
        nodes = self.statement_list()
        self.eat('RBRACE')
        return nodes

    def empty(self):
        return NoOp()

    def program(self):
        if self.current_token.type == 'LBRACE':
            node = self.compound_statement()
        else:
            node = self.statement_list()
            
        if self.current_token.type != 'EOF':
            self.error()
        return node

    def parse(self):
        node = self.program()
        return node 