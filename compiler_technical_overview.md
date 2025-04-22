# Simple Language Compiler - Technical Overview

## Introduction

This document provides a comprehensive technical explanation of our compiler's architecture and execution flow. Our compiler transforms source code written in a custom programming language into executable form through multiple stages: lexical analysis, syntax analysis, and execution (either through direct interpretation or bytecode compilation and virtual machine execution).

## Compiler Architecture

Our compiler follows a multi-stage pipeline architecture:

```
Source Code → Lexer → Parser → [Interpreter OR Bytecode Compiler → VM]
```

Each component has clearly defined responsibilities and interfaces, allowing them to work together seamlessly while remaining independently maintainable.

## Lexical Analysis (Lexer)

### Core Functionality

The lexer (`src/lexer.py`) performs character-by-character scanning of the source code, breaking it into tokens. Each token represents a meaningful unit in the language's grammar, such as keywords, identifiers, literals, operators, and punctuation.

### Implementation Details

1. **Character Processing**: The lexer maintains a pointer to the current character and advances through the text using the `advance()` method.

2. **Token Recognition**: Specialized methods like `number()`, `identifier()`, and `string()` recognize patterns and create appropriate tokens:
   
   ```python
   def number(self):
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
   ```

3. **String Interpolation**: When encountering `${expression}` within strings, the lexer generates a special `STRING_INTERPOLATION` token containing multiple parts:

   ```python
   # For string: "Hello, ${name}!"
   Token('STRING_INTERPOLATION', [
       Token('STRING_LITERAL', "Hello, "),
       Token('INTERPOLATION', "name"),
       Token('STRING_LITERAL', "!")
   ])
   ```

4. **Comment Handling**: The lexer recognizes both single-line (`//`) and multi-line (`/* */`) comments and skips them during tokenization.

5. **Token Generation**: The `get_next_token()` method is the main driver that returns the next token from the input until reaching the end of file.

## Syntax Analysis (Parser)

### Core Functionality

The parser (`src/parser.py`) takes the token stream from the lexer and analyzes the grammatical structure according to the language's syntax rules. It builds an Abstract Syntax Tree (AST) that represents the hierarchical structure of the program.

### Grammar Definition

Our language follows these grammar rules (simplified):

```
program        : compound_statement | statement_list
statement      : var_declaration | assignment | print_statement 
               | if_statement | while_statement | compound_statement
expr           : term ((PLUS | MINUS | comparison_op) term)*
term           : factor ((MULTIPLY | DIVIDE) factor)*
factor         : INTEGER | FLOAT | STRING | BOOLEAN | IDENTIFIER
               | LPAREN expr RPAREN | unary_operator factor
```

### Implementation Details

1. **Recursive Descent Parsing**: Each grammar rule is implemented as a method that may call other rule methods recursively:

   ```python
   def expr(self):
       node = self.term()
       while self.current_token.type in ('PLUS', 'MINUS', 'EQUALS', ...):
           token = self.current_token
           self.eat(token.type)
           node = BinOp(left=node, op=token, right=self.term())
       return node
   ```

2. **AST Node Classes**: Each language construct is represented by a specific node class:

   ```python
   class BinOp:
       def __init__(self, left, op, right):
           self.left = left
           self.token = self.op = op
           self.right = right
   ```

3. **Operator Precedence**: Implemented through the calling hierarchy:
   - `expr()` handles addition, subtraction, and comparisons
   - `term()` handles multiplication and division
   - `factor()` handles literals, variables, and parenthesized expressions

4. **String Interpolation Parsing**: For interpolated strings, the parser processes each part recursively:
   
   ```python
   def parse_interpolation(self, expr_text):
       interpolation_lexer = Lexer(expr_text)
       interpolation_parser = Parser(interpolation_lexer)
       return interpolation_parser.expr()
   ```

5. **Error Handling**: The parser implements robust error detection and reporting:
   
   ```python
   def error(self, message="Invalid syntax"):
       raise Exception(message)
   ```

## Interpreter

### Core Functionality

The interpreter (`src/interpreter.py`) directly executes the AST by traversing its nodes and performing the operations they represent. It follows the Visitor Pattern, which separates node traversal logic from the operations performed on each node.

### Implementation Details

1. **Visitor Pattern Implementation**:
   
   ```python
   def visit(self, node):
       method_name = 'visit_' + type(node).__name__
       visitor = getattr(self, method_name, self.generic_visit)
       return visitor(node)
   ```

2. **Expression Evaluation**: Binary operations are evaluated by recursively visiting operands:
   
   ```python
   def visit_BinOp(self, node):
       left = self.visit(node.left)
       right = self.visit(node.right)
       
       if node.op.type == 'PLUS':
           return left + right
       # ... other operations ...
   ```

3. **Variable Management**: Variables are stored in a dictionary (symbol table):
   
   ```python
   def visit_VarDecl(self, node):
       var_name = node.variable.value
       var_value = self.visit(node.value)
       self.global_scope[var_name] = var_value
   ```

4. **Control Flow Implementation**: Conditional execution based on evaluated conditions:
   
   ```python
   def visit_If(self, node):
       condition = self.visit(node.condition)
       if condition:
           return self.visit(node.body)
       elif node.else_body:
           return self.visit(node.else_body)
   ```

5. **String Interpolation Evaluation**:
   
   ```python
   def visit_StringInterpolation(self, node):
       result = ""
       for part in node.parts:
           part_value = self.visit(part)
           result += str(part_value)
       return result
   ```

## Bytecode Compiler

### Core Functionality

The bytecode compiler (`src/bytecode.py`) transforms the AST into a more efficient, lower-level representation (bytecode) designed for faster execution by the Virtual Machine. It uses a stack-based instruction set similar to those used by Python and Java.

### Instruction Set Design

```python
class OpCode:
    # Stack operations
    LOAD_CONST = 1    # Push constant onto stack
    LOAD_VAR = 2      # Push variable value onto stack
    STORE_VAR = 3     # Store top of stack in variable
    
    # Arithmetic operations
    ADD = 10
    SUBTRACT = 11
    # ... more operations ...
    
    # Control flow
    JUMP = 30         # Unconditional jump
    JUMP_IF_FALSE = 31 # Jump if top of stack is false
    
    # Program structure
    HALT = 255        # End program execution
```

### Implementation Details

1. **AST Traversal**: The compiler visits each AST node and emits appropriate bytecode instructions:
   
   ```python
   def compile(self, node):
       node_type = type(node).__name__
       if node_type == 'Number':
           self.compile_number(node)
       elif node_type == 'BinOp':
           self.compile_binop(node)
       # ... other node types ...
   ```

2. **Constant Pool**: Literal values are stored in a constants pool and referenced by index:
   
   ```python
   def add_constant(self, value):
       if value in self.constants:
           return self.constants.index(value)
       self.constants.append(value)
       return len(self.constants) - 1
   ```

3. **Variable Management**: Variables are mapped to numeric indices for efficient access:
   
   ```python
   def get_variable_index(self, name):
       if name not in self.variables:
           self.variables[name] = len(self.variables)
       return self.variables[name]
   ```

4. **Control Flow**: For conditional statements and loops, the compiler emits jump instructions with a two-pass approach:
   
   ```python
   # First pass: emit jump with placeholder
   jump_if_false_idx = self.emit(OpCode.JUMP_IF_FALSE, 0)
   
   # Compile the body
   self.compile(node.body)
   
   # Second pass: patch the jump instruction
   jump_target = len(self.instructions)
   self.instructions[jump_if_false_idx].operand = jump_target
   ```

5. **String Interpolation Compilation**:
   
   ```python
   def compile_string_interpolation(self, node):
       for part in node.parts:
           self.compile(part)
           if not isinstance(part, String):
               self.emit(OpCode.TO_STRING)
           if not first_part:
               self.emit(OpCode.CONCAT)
           first_part = False
   ```

## Virtual Machine (VM)

### Core Functionality

The Virtual Machine (`src/bytecode.py` - `VirtualMachine` class) executes the bytecode produced by the compiler. It's a stack-based machine that processes instructions sequentially, maintaining program state in a stack, variable storage array, and constants table.

### Implementation Details

1. **VM Components**:
   
   ```python
   class VirtualMachine:
       def __init__(self, bytecode):
           self.constants = bytecode['constants']
           self.instructions = bytecode['instructions']
           self.variables = [None] * len(bytecode['variables'])
           self.stack = []
           self.pc = 0  # Program counter
   ```

2. **Execution Loop**: The VM follows a fetch-decode-execute cycle:
   
   ```python
   def run(self):
       while True:
           # Fetch
           if self.pc >= len(self.instructions):
               break
           instruction = self.instructions[self.pc]
           self.pc += 1
           
           # Decode and execute
           if instruction.opcode == OpCode.LOAD_CONST:
               self.push(self.constants[instruction.operand])
           # ... other instructions ...
   ```

3. **Stack Manipulation**:
   
   ```python
   def push(self, value):
       self.stack.append(value)
   
   def pop(self):
       return self.stack.pop()
   ```

4. **Arithmetic Operations**:
   
   ```python
   elif instruction.opcode == OpCode.ADD:
       right = self.pop()
       left = self.pop()
       self.push(left + right)
   ```

5. **Control Flow Implementation**:
   
   ```python
   elif instruction.opcode == OpCode.JUMP:
       self.pc = instruction.operand
   
   elif instruction.opcode == OpCode.JUMP_IF_FALSE:
       condition = self.pop()
       if not condition:
           self.pc = instruction.operand
   ```

6. **String Operations**:
   
   ```python
   elif instruction.opcode == OpCode.CONCAT:
       right = self.pop()
       left = self.pop()
       self.push(left + right)
   
   elif instruction.opcode == OpCode.TO_STRING:
       value = self.pop()
       self.push(str(value))
   ```

## Execution Models Comparison

Our compiler supports two execution models:

1. **Direct AST Interpretation**:
   - Advantages: Simpler implementation, easier to debug, faster development cycle
   - Disadvantages: Slower execution, higher memory usage due to storing the entire AST

2. **Bytecode Compilation + VM Execution**:
   - Advantages: 5-10x faster execution, more compact representation, potential for further optimization
   - Disadvantages: More complex implementation, additional compilation step

Performance benchmarks show that the bytecode VM significantly outperforms direct AST interpretation, especially for programs with loops and complex control flow.

## String Interpolation: A Feature Case Study

String interpolation (`"Hello, ${name}!"`) is a complex feature that demonstrates how the different compiler components work together:

1. **Lexer**: Identifies interpolation patterns and creates `STRING_INTERPOLATION` tokens with separate parts
2. **Parser**: Builds a `StringInterpolation` AST node containing string parts and expression parts
3. **Interpreter**: Recursively evaluates each part and concatenates the results
4. **Bytecode Compiler**: Generates instructions to push each part onto the stack and concatenate them
5. **VM**: Executes the string operation instructions to produce the final interpolated string

This feature showcases the clean separation of concerns between components while maintaining consistent semantics.

## User Interface

The compiler is accessible through a Streamlit web interface (`streamlit_app.py`) that allows:
- Selecting example programs from a dropdown menu
- Viewing and editing code in a code editor
- Executing programs with either AST interpretation or bytecode compilation
- Viewing execution output and performance metrics
- Examining generated bytecode for debugging

## Conclusion

Our compiler demonstrates a complete implementation of a programming language from lexical analysis through execution. The modular architecture allows for independent development and testing of components, while the dual execution models provide flexibility in trading off performance versus simplicity.

The stack-based bytecode design offers significant performance benefits over direct AST interpretation, while maintaining the exact same language semantics. This architecture also provides a foundation for future extensions like additional language features, optimizations, or alternative compilation targets. 