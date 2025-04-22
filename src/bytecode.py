# Bytecode operation codes
class OpCode:
    # Stack operations
    LOAD_CONST = 1    # Push constant onto stack
    LOAD_VAR = 2      # Push variable value onto stack
    STORE_VAR = 3     # Store top of stack in variable
    POP = 4           # Discard top of stack
    
    # Arithmetic operations
    ADD = 10
    SUBTRACT = 11
    MULTIPLY = 12
    DIVIDE = 13
    UNARY_PLUS = 14
    UNARY_MINUS = 15
    
    # Logical operations
    NOT = 16
    AND = 17
    OR = 18
    
    # String operations
    CONCAT = 19       # Concatenate two strings
    TO_STRING = 23    # Convert top of stack to string
    
    # Comparison operations
    EQUALS = 20
    NOT_EQUALS = 21
    LESS_THAN = 22
    GREATER_THAN = 23
    LESS_EQUAL = 24
    GREATER_EQUAL = 25
    
    # Control flow
    JUMP = 30         # Unconditional jump
    JUMP_IF_FALSE = 31 # Jump if top of stack is false
    
    # I/O operations
    PRINT = 40
    
    # Program structure
    HALT = 255        # End program execution


class Instruction:
    def __init__(self, opcode, operand=None):
        self.opcode = opcode
        self.operand = operand
    
    def __repr__(self):
        if self.operand is not None:
            return f"Instruction({self.opcode}, {self.operand})"
        return f"Instruction({self.opcode})"


class BytecodeCompiler:
    def __init__(self):
        self.constants = []  # Constants pool (numbers, strings)
        self.instructions = []  # Bytecode instructions
        self.variables = {}  # Variable names to index mapping
    
    def add_constant(self, value):
        """Add a constant to the constants pool and return its index."""
        if value in self.constants:
            return self.constants.index(value)
        self.constants.append(value)
        return len(self.constants) - 1
    
    def get_variable_index(self, name):
        """Get variable index, creating it if needed."""
        if name not in self.variables:
            self.variables[name] = len(self.variables)
        return self.variables[name]
    
    def emit(self, opcode, operand=None):
        """Add an instruction to the bytecode."""
        self.instructions.append(Instruction(opcode, operand))
        return len(self.instructions) - 1
    
    def compile_number(self, node):
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.LOAD_CONST, const_idx)
    
    def compile_float(self, node):
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.LOAD_CONST, const_idx)
    
    def compile_boolean(self, node):
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.LOAD_CONST, const_idx)
    
    def compile_string(self, node):
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.LOAD_CONST, const_idx)
    
    def compile_string_interpolation(self, node):
        # Empty string to start
        if len(node.parts) > 0:
            # Compile each part of the interpolation
            first_part = True
            for part in node.parts:
                # Compile the expression
                self.compile(part)
                
                # If it's not a string, convert it to string
                if not (isinstance(part, String) or
                        isinstance(part, StringInterpolation)):
                    self.emit(OpCode.TO_STRING)
                
                # If not the first part, concatenate with the existing result
                if not first_part:
                    self.emit(OpCode.CONCAT)
                first_part = False
        else:
            # If there are no parts, push an empty string
            const_idx = self.add_constant("")
            self.emit(OpCode.LOAD_CONST, const_idx)
    
    def compile_unaryop(self, node):
        # Compile the expression
        self.compile(node.expr)
        
        # Emit the unary operation
        if node.op.type == 'PLUS':
            self.emit(OpCode.UNARY_PLUS)
        elif node.op.type == 'MINUS':
            self.emit(OpCode.UNARY_MINUS)
        elif node.op.type == 'NOT':
            self.emit(OpCode.NOT)
    
    def compile_binop(self, node):
        # Compile left and right operands
        self.compile(node.left)
        self.compile(node.right)
        
        # Emit the operation instruction
        if node.op.type == 'PLUS':
            self.emit(OpCode.ADD)
        elif node.op.type == 'MINUS':
            self.emit(OpCode.SUBTRACT)
        elif node.op.type == 'MULTIPLY':
            self.emit(OpCode.MULTIPLY)
        elif node.op.type == 'DIVIDE':
            self.emit(OpCode.DIVIDE)
        elif node.op.type == 'EQUALS':
            self.emit(OpCode.EQUALS)
        elif node.op.type == 'NOT_EQUALS':
            self.emit(OpCode.NOT_EQUALS)
        elif node.op.type == 'LESS':
            self.emit(OpCode.LESS_THAN)
        elif node.op.type == 'GREATER':
            self.emit(OpCode.GREATER_THAN)
        elif node.op.type == 'LESS_EQUAL':
            self.emit(OpCode.LESS_EQUAL)
        elif node.op.type == 'GREATER_EQUAL':
            self.emit(OpCode.GREATER_EQUAL)
        elif node.op.type == 'AND':
            self.emit(OpCode.AND)
        elif node.op.type == 'OR':
            self.emit(OpCode.OR)
    
    def compile_variable(self, node):
        var_idx = self.get_variable_index(node.value)
        self.emit(OpCode.LOAD_VAR, var_idx)
    
    def compile_vardecl(self, node):
        # Compile the initial value
        self.compile(node.value)
        
        # Store it in the variable
        var_idx = self.get_variable_index(node.variable.value)
        self.emit(OpCode.STORE_VAR, var_idx)
    
    def compile_assign(self, node):
        # Compile the value
        self.compile(node.right)
        
        # Store it in the variable
        var_idx = self.get_variable_index(node.left.value)
        self.emit(OpCode.STORE_VAR, var_idx)
    
    def compile_print(self, node):
        # Compile the expression to print
        self.compile(node.expr)
        
        # Emit print instruction
        self.emit(OpCode.PRINT)
    
    def compile_if(self, node):
        # Compile condition
        self.compile(node.condition)
        
        # Emit conditional jump (to be patched)
        jump_if_false_idx = self.emit(OpCode.JUMP_IF_FALSE, 0)
        
        # Compile if-body
        self.compile(node.body)
        
        if node.else_body:
            # Emit jump to skip else part 
            jump_idx = self.emit(OpCode.JUMP, 0)
            
            # Patch the conditional jump to point to the else-body
            jump_target = len(self.instructions)
            self.instructions[jump_if_false_idx].operand = jump_target
            
            # Compile else-body
            self.compile(node.else_body)
            
            # Patch the unconditional jump to point after the else-body
            jump_target = len(self.instructions)
            self.instructions[jump_idx].operand = jump_target
        else:
            # Patch the conditional jump to point after the if-body
            jump_target = len(self.instructions)
            self.instructions[jump_if_false_idx].operand = jump_target
    
    def compile_while(self, node):
        # Remember start of loop condition
        loop_start = len(self.instructions)
        
        # Compile condition
        self.compile(node.condition)
        
        # Emit conditional jump (to be patched)
        jump_if_false_idx = self.emit(OpCode.JUMP_IF_FALSE, 0)
        
        # Compile loop body
        self.compile(node.body)
        
        # Emit jump back to loop condition
        self.emit(OpCode.JUMP, loop_start)
        
        # Patch the conditional jump to point after the loop
        jump_target = len(self.instructions)
        self.instructions[jump_if_false_idx].operand = jump_target
    
    def compile_compound(self, node):
        for statement in node.statements:
            self.compile(statement)
    
    def compile_noop(self, node):
        pass
    
    def compile(self, node):
        """Compile an AST node to bytecode."""
        node_type = type(node).__name__
        
        if node_type == 'Number':
            self.compile_number(node)
        elif node_type == 'Float':
            self.compile_float(node)
        elif node_type == 'Boolean':
            self.compile_boolean(node)
        elif node_type == 'String':
            self.compile_string(node)
        elif node_type == 'StringInterpolation':
            self.compile_string_interpolation(node)
        elif node_type == 'UnaryOp':
            self.compile_unaryop(node)
        elif node_type == 'BinOp':
            self.compile_binop(node)
        elif node_type == 'Variable':
            self.compile_variable(node)
        elif node_type == 'VarDecl':
            self.compile_vardecl(node)
        elif node_type == 'Assign':
            self.compile_assign(node)
        elif node_type == 'Print':
            self.compile_print(node)
        elif node_type == 'If':
            self.compile_if(node)
        elif node_type == 'While':
            self.compile_while(node)
        elif node_type == 'Compound':
            self.compile_compound(node)
        elif node_type == 'NoOp':
            self.compile_noop(node)
        else:
            raise Exception(f"Unknown node type: {node_type}")
    
    def compile_ast(self, ast):
        """Compile an AST to bytecode."""
        self.compile(ast)
        self.emit(OpCode.HALT)
        return {
            'constants': self.constants,
            'instructions': self.instructions,
            'variables': self.variables
        }


from src.parser import String, StringInterpolation

class VirtualMachine:
    def __init__(self, bytecode):
        self.constants = bytecode['constants']
        self.instructions = bytecode['instructions']
        self.variables = [None] * len(bytecode['variables'])
        self.stack = []
        self.pc = 0  # Program counter
    
    def push(self, value):
        self.stack.append(value)
    
    def pop(self):
        return self.stack.pop()
    
    def run(self):
        while True:
            # Fetch instruction
            if self.pc >= len(self.instructions):
                break
                
            instruction = self.instructions[self.pc]
            self.pc += 1
            
            # Execute instruction
            if instruction.opcode == OpCode.LOAD_CONST:
                self.push(self.constants[instruction.operand])
            
            elif instruction.opcode == OpCode.LOAD_VAR:
                value = self.variables[instruction.operand]
                if value is None:
                    raise Exception(f"Variable at index {instruction.operand} not initialized")
                self.push(value)
            
            elif instruction.opcode == OpCode.STORE_VAR:
                self.variables[instruction.operand] = self.pop()
            
            elif instruction.opcode == OpCode.POP:
                self.pop()
            
            elif instruction.opcode == OpCode.UNARY_PLUS:
                value = self.pop()
                self.push(+value)
                
            elif instruction.opcode == OpCode.UNARY_MINUS:
                value = self.pop()
                self.push(-value)
                
            elif instruction.opcode == OpCode.NOT:
                value = self.pop()
                self.push(not value)
            
            elif instruction.opcode == OpCode.ADD:
                right = self.pop()
                left = self.pop()
                self.push(left + right)
            
            elif instruction.opcode == OpCode.SUBTRACT:
                right = self.pop()
                left = self.pop()
                self.push(left - right)
            
            elif instruction.opcode == OpCode.MULTIPLY:
                right = self.pop()
                left = self.pop()
                self.push(left * right)
            
            elif instruction.opcode == OpCode.DIVIDE:
                right = self.pop()
                left = self.pop()
                if isinstance(left, int) and isinstance(right, int):
                    self.push(left // right)  # Integer division
                else:
                    self.push(left / right)   # Float division
                    
            elif instruction.opcode == OpCode.CONCAT:
                right = self.pop()
                left = self.pop()
                self.push(left + right)
                
            elif instruction.opcode == OpCode.TO_STRING:
                value = self.pop()
                self.push(str(value))
            
            elif instruction.opcode == OpCode.EQUALS:
                right = self.pop()
                left = self.pop()
                self.push(left == right)
                
            elif instruction.opcode == OpCode.NOT_EQUALS:
                right = self.pop()
                left = self.pop()
                self.push(left != right)
            
            elif instruction.opcode == OpCode.LESS_THAN:
                right = self.pop()
                left = self.pop()
                self.push(left < right)
            
            elif instruction.opcode == OpCode.GREATER_THAN:
                right = self.pop()
                left = self.pop()
                self.push(left > right)
                
            elif instruction.opcode == OpCode.LESS_EQUAL:
                right = self.pop()
                left = self.pop()
                self.push(left <= right)
                
            elif instruction.opcode == OpCode.GREATER_EQUAL:
                right = self.pop()
                left = self.pop()
                self.push(left >= right)
                
            elif instruction.opcode == OpCode.AND:
                right = self.pop()
                left = self.pop()
                self.push(left and right)
                
            elif instruction.opcode == OpCode.OR:
                right = self.pop()
                left = self.pop()
                self.push(left or right)
            
            elif instruction.opcode == OpCode.JUMP:
                self.pc = instruction.operand
            
            elif instruction.opcode == OpCode.JUMP_IF_FALSE:
                condition = self.pop()
                if not condition:
                    self.pc = instruction.operand
            
            elif instruction.opcode == OpCode.PRINT:
                value = self.pop()
                print(value)
            
            elif instruction.opcode == OpCode.HALT:
                break
            
            else:
                raise Exception(f"Unknown opcode: {instruction.opcode}")
        
        return True 