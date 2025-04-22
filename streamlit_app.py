import streamlit as st
import os
import sys
import io
import time
from contextlib import redirect_stdout
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.bytecode import BytecodeCompiler, VirtualMachine

# Set page config
st.set_page_config(
    page_title="Simple Language Compiler",
    page_icon="🚀",
    layout="wide"
)

# Main title
st.title("Simple Language Compiler")
st.markdown("A basic programming language with interpreter and bytecode compiler")

# Function to get all example files
def get_example_files():
    examples_dir = "examples"
    examples = []
    for file in os.listdir(examples_dir):
        if file.endswith(".txt"):
            examples.append(file)
    return sorted(examples)

# Function to get example description
def get_example_description(filename):
    descriptions = {
        "arithmetic.txt": "Basic arithmetic operations",
        "conditionals.txt": "If/else statements and boolean logic",
        "loops.txt": "While loops and control flow",
        "strings.txt": "String manipulation",
        "data_types.txt": "Various data types including booleans and floats",
        "fizzbuzz.txt": "Classic FizzBuzz problem",
        "primes.txt": "Find prime numbers up to 50",
        "string_interpolation.txt": "String interpolation with expressions",
        "benchmark.txt": "Performance benchmark"
    }
    return descriptions.get(filename, "No description available")

# Function to read file content
def read_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

# Function to execute code
def execute_code(code, mode="bytecode"):
    # Capture stdout
    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        try:
            # Measure execution time
            start_time = time.time()
            
            lexer = Lexer(code)
            parser = Parser(lexer)
            
            parse_time = time.time()
            parse_duration = parse_time - start_time
            
            ast = parser.parse()
            
            if mode == "interpret":
                interpreter = Interpreter()
                interpreter.interpret(ast)
                end_time = time.time()
                execution_duration = end_time - parse_time
                total_duration = end_time - start_time
                
                # Add performance info
                print(f"\n--- Performance Metrics ---")
                print(f"Parse time: {parse_duration:.6f} seconds")
                print(f"Execution time: {execution_duration:.6f} seconds")
                print(f"Total time: {total_duration:.6f} seconds")
                
            else:  # bytecode
                compile_start = time.time()
                compiler = BytecodeCompiler()
                bytecode = compiler.compile_ast(ast)
                compile_end = time.time()
                compile_duration = compile_end - compile_start
                
                vm = VirtualMachine(bytecode)
                vm.run()
                end_time = time.time()
                
                execution_duration = end_time - compile_end
                total_duration = end_time - start_time
                
                # Add performance info
                print(f"\n--- Performance Metrics ---")
                print(f"Parse time: {parse_duration:.6f} seconds")
                print(f"Compile time: {compile_duration:.6f} seconds")
                print(f"Execution time: {execution_duration:.6f} seconds")
                print(f"Total time: {total_duration:.6f} seconds")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    return output_buffer.getvalue()

# Sidebar for selecting examples
st.sidebar.header("Select an Example")
example_files = get_example_files()

# Add descriptions to display options
example_options = {f"{file} - {get_example_description(file)}": file for file in example_files}
selected_option = st.sidebar.selectbox("Choose an example:", list(example_options.keys()))
selected_example = example_options[selected_option]

# Read the selected example
file_path = os.path.join("examples", selected_example)
code = read_file(file_path)

# Main area - split into code and output sections
col1, col2 = st.columns(2)

with col1:
    st.header("Code Editor")
    
    # Add option to edit code
    use_custom = st.checkbox("Edit code")
    if use_custom:
        edited_code = st.text_area("", value=code, height=400)
        code = edited_code
    else:
        st.code(code, language="python")
    
    # Execution options
    st.subheader("Execution Options")
    execution_mode = st.radio(
        "Select execution mode:",
        ["Bytecode Compilation", "AST Interpretation"],
        horizontal=True
    )
    
    mode = "bytecode" if execution_mode == "Bytecode Compilation" else "interpret"
    
    # Execute button
    if st.button("Run Program", type="primary"):
        with st.spinner('Executing...'):
            output = execute_code(code, mode)
            st.session_state.output = output
            st.session_state.mode = mode

with col2:
    st.header("Output")
    
    # Display output if available
    if 'output' in st.session_state:
        st.text_area("Program Output:", st.session_state.output, height=400)
        
        # Display execution mode used
        used_mode = "Bytecode Compilation" if st.session_state.mode == "bytecode" else "AST Interpretation"
        st.success(f"Executed using: {used_mode}")
    else:
        st.info("Click 'Run Program' to see the output")

# Language explanation
with st.expander("Language Features"):
    st.markdown("""
    ### Data Types
    - **Integers**: `var x = 42;`
    - **Floating-point**: `var pi = 3.14159;`
    - **Strings**: `var greeting = "Hello, World!";`
    - **Booleans**: `var isTrue = true;`
    
    ### Operators
    - **Arithmetic**: `+`, `-`, `*`, `/`
    - **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
    - **Logical**: `!`, `&&`, `||`
    
    ### Control Flow
    - **If/Else**: 
    ```
    if (condition) {
        statements;
    } else {
        statements;
    }
    ```
    
    - **While**: 
    ```
    while (condition) {
        statements;
    }
    ```
    
    ### String Interpolation
    ```
    var name = "World";
    print "Hello, ${name}!";  // Outputs: Hello, World!
    ```
    
    ### Comments
    ```
    // Single-line comment
    
    /* 
       Multi-line
       comment
    */
    ```
    """)

# Footer
st.markdown("---")
st.markdown("### About")
st.markdown("""
This is a simple programming language and compiler built in Python with two execution modes:
1. **AST Interpretation** - Directly interprets the abstract syntax tree
2. **Bytecode Compilation** - Compiles to bytecode and runs on a virtual machine (faster)

Try different examples to see how the language works and compare performance between the two execution modes!
""")

# Add a debug section
with st.expander("Advanced - Debug Bytecode"):
    if st.button("Generate Bytecode"):
        try:
            lexer = Lexer(code)
            parser = Parser(lexer)
            ast = parser.parse()
            compiler = BytecodeCompiler()
            bytecode = compiler.compile_ast(ast)
            
            # Display bytecode
            st.subheader("Instructions")
            for i, instruction in enumerate(bytecode['instructions']):
                st.code(f"{i}: {instruction}")
                
            st.subheader("Constants")
            for i, constant in enumerate(bytecode['constants']):
                st.code(f"{i}: {constant}")
                
            st.subheader("Variables")
            var_by_idx = {v: k for k, v in bytecode['variables'].items()}
            for i in range(len(var_by_idx)):
                st.code(f"{i}: {var_by_idx.get(i)}")
                
        except Exception as e:
            st.error(f"Error generating bytecode: {str(e)}") 