import sys
import time
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.bytecode import BytecodeCompiler, VirtualMachine

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename> [--interpret|--bytecode]")
        sys.exit(1)

    filename = sys.argv[1]
    # Default to bytecode execution
    mode = 'bytecode' if len(sys.argv) <= 2 else sys.argv[2].lstrip('-')
    
    try:
        with open(filename, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)

    lexer = Lexer(text)
    parser = Parser(lexer)
    
    try:
        ast = parser.parse()
    except Exception as e:
        print(f"Parsing error: {e}")
        sys.exit(1)
    
    if mode == 'interpret':
        print("Running with direct AST interpretation:")
        start_time = time.time()
        
        interpreter = Interpreter()
        try:
            interpreter.interpret(ast)
        except Exception as e:
            print(f"Runtime error: {e}")
            sys.exit(1)
            
        end_time = time.time()
        print(f"\nExecution time: {end_time - start_time:.6f} seconds")
        
    elif mode == 'bytecode':
        print("Running with bytecode compilation and VM execution:")
        
        # Compilation phase
        start_compile = time.time()
        compiler = BytecodeCompiler()
        bytecode = compiler.compile_ast(ast)
        end_compile = time.time()
        
        # Display bytecode if requested
        if len(sys.argv) > 3 and sys.argv[3] == '--debug':
            print("\nBytecode:")
            for i, instruction in enumerate(bytecode['instructions']):
                print(f"{i}: {instruction}")
            print("\nConstants:")
            for i, constant in enumerate(bytecode['constants']):
                print(f"{i}: {constant}")
            print("\nVariables:")
            var_by_idx = {v: k for k, v in bytecode['variables'].items()}
            for i in range(len(var_by_idx)):
                print(f"{i}: {var_by_idx.get(i)}")
            print()
        
        # Execution phase
        start_exec = time.time()
        vm = VirtualMachine(bytecode)
        try:
            vm.run()
        except Exception as e:
            print(f"VM runtime error: {e}")
            sys.exit(1)
        end_exec = time.time()
        
        # Print timing information
        compile_time = end_compile - start_compile
        exec_time = end_exec - start_exec
        total_time = compile_time + exec_time
        
        print(f"\nCompile time: {compile_time:.6f} seconds")
        print(f"Execution time: {exec_time:.6f} seconds")
        print(f"Total time: {total_time:.6f} seconds")
    
    else:
        print(f"Unknown execution mode: {mode}")
        print("Available modes: --interpret, --bytecode")
        sys.exit(1)

if __name__ == "__main__":
    main() 