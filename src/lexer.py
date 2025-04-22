class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '/':
            # Single-line comment
            self.advance()  # Skip first /
            self.advance()  # Skip second /
            
            # Skip until end of line or EOF
            while self.current_char and self.current_char != '\n':
                self.advance()
            
            # Skip the newline if present
            if self.current_char == '\n':
                self.advance()
                
        elif self.current_char == '/' and self.peek() == '*':
            # Multi-line comment
            self.advance()  # Skip /
            self.advance()  # Skip *
            
            while self.current_char:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()  # Skip *
                    self.advance()  # Skip /
                    break
                self.advance()

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def number(self):
        """Parse a number (integer or float)"""
        result = ''
        has_dot = False
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if has_dot:
                    break  # Second dot, not part of the number
                has_dot = True
            result += self.current_char
            self.advance()
            
        if has_dot:
            return float(result)
        else:
            return int(result)

    def identifier(self):
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def string(self):
        # Skip the opening quote
        self.advance()
        
        # Collect string parts and any interpolation tokens
        string_parts = []
        current_string = ''
        
        while self.current_char and self.current_char != '"':
            # Check for interpolation syntax
            if self.current_char == '$' and self.peek() == '{':
                # Save any accumulated string part
                if current_string:
                    string_parts.append(Token('STRING_LITERAL', current_string))
                    current_string = ''
                
                # Skip $ and {
                self.advance()
                self.advance()
                
                # Create a new lexer for the interpolated expression and get tokens
                # (We'll need to find the matching closing brace)
                expr_start = self.pos
                expr_brace_count = 1
                
                while expr_brace_count > 0 and self.current_char:
                    if self.current_char == '{':
                        expr_brace_count += 1
                    elif self.current_char == '}':
                        expr_brace_count -= 1
                    
                    if expr_brace_count > 0:
                        self.advance()
                
                if not self.current_char:
                    raise Exception("Unterminated string interpolation")
                
                expr_end = self.pos
                expr_text = self.text[expr_start:expr_end]
                
                # Add the interpolation token
                string_parts.append(Token('INTERPOLATION', expr_text))
                
                # Skip the closing brace
                self.advance()
            else:
                current_string += self.current_char
                self.advance()
        
        # Save any remaining string part
        if current_string:
            string_parts.append(Token('STRING_LITERAL', current_string))
        
        # Skip the closing quote
        if self.current_char == '"':
            self.advance()
        else:
            raise Exception('Unterminated string')
        
        # If there's just one string part with no interpolation, return a regular STRING token
        if len(string_parts) == 1 and string_parts[0].type == 'STRING_LITERAL':
            return Token('STRING', string_parts[0].value)
        
        # Otherwise, return a token for the interpolated string
        return Token('STRING_INTERPOLATION', string_parts)

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment()
                continue

            if self.current_char.isdigit() or self.current_char == '.':
                number_value = self.number()
                if isinstance(number_value, int):
                    return Token('INTEGER', number_value)
                else:
                    return Token('FLOAT', number_value)

            if self.current_char.isalpha() or self.current_char == '_':
                identifier = self.identifier()
                # Keywords
                if identifier == 'print':
                    return Token('PRINT')
                if identifier == 'var':
                    return Token('VAR')
                if identifier == 'if':
                    return Token('IF')
                if identifier == 'else':
                    return Token('ELSE')
                if identifier == 'while':
                    return Token('WHILE')
                if identifier == 'true':
                    return Token('BOOLEAN', True)
                if identifier == 'false':
                    return Token('BOOLEAN', False)
                return Token('IDENTIFIER', identifier)

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('EQUALS')
                return Token('ASSIGN')

            if self.current_char == '+':
                self.advance()
                return Token('PLUS')

            if self.current_char == '-':
                self.advance()
                return Token('MINUS')

            if self.current_char == '*':
                self.advance()
                return Token('MULTIPLY')

            if self.current_char == '/':
                self.advance()
                return Token('DIVIDE')

            if self.current_char == '(':
                self.advance()
                return Token('LPAREN')

            if self.current_char == ')':
                self.advance()
                return Token('RPAREN')

            if self.current_char == '{':
                self.advance()
                return Token('LBRACE')

            if self.current_char == '}':
                self.advance()
                return Token('RBRACE')

            if self.current_char == ';':
                self.advance()
                return Token('SEMICOLON')

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('LESS_EQUAL')
                return Token('LESS')

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('GREATER_EQUAL')
                return Token('GREATER')

            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('NOT_EQUALS')
                return Token('NOT')

            if self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    self.advance()
                    return Token('AND')
                raise Exception("Expected & after &")

            if self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    self.advance()
                    return Token('OR')
                raise Exception("Expected | after |")

            if self.current_char == '"':
                return self.string()

            raise Exception(f'Invalid character: {self.current_char}')

        return Token('EOF') 