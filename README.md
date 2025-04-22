# Simple Language Compiler

A basic programming language and compiler built in Python.

## Language Features

- **Data Types**:
  - Integers
  - Floating-point numbers
  - Strings (with interpolation)
  - Booleans
- **Operators**:
  - Arithmetic: +, -, *, /
  - Comparison: ==, !=, <, >, <=, >=
  - Logical: !, &&, ||
- Control flow (if/else, while loops)
- Variables and assignments
- Print statement
- Single-line and multi-line comments
- String interpolation with `${expression}` syntax

## Execution Modes

This compiler supports two execution modes:

1. **AST Interpretation** - Directly interprets the abstract syntax tree
2. **Bytecode Compilation** - Compiles to bytecode and runs on a virtual machine (faster)

## Syntax

### Variable Declaration
```
var name = value;
```

### Assignment
```
name = value;
```

### Print Statement
```
print expression;
```

### If Statement
```
if (condition) {
    statements;
} else {
    statements;
}
```

### While Loop
```
while (condition) {
    statements;
}
```

### Compound Statements
```
{
    statement1;
    statement2;
    ...
}
```

### Comments
```
// Single-line comment

/* 
   Multi-line
   comment
*/
```

### Data Types
```
// Integers
var a = 42;

// Floating-point numbers
var pi = 3.14159;

// Strings
var greeting = "Hello, World!";

// Booleans
var isTrue = true;
var isFalse = false;
```

### String Interpolation
```
var name = "World";
print "Hello, ${name}!";  // Outputs: Hello, World!

var a = 10;
var b = 20;
print "The sum of ${a} and ${b} is ${a + b}";  // Outputs: The sum of 10 and 20 is 30

// Complex expressions are supported
var x = 5;
print "The square of ${x} is ${x * x}";  // Outputs: The square of 5 is 25
```

### Operators
```
// Arithmetic operators
var sum = a + b;
var difference = a - b;
var product = a * b;
var quotient = a / b;

// Comparison operators
var isEqual = a == b;
var isNotEqual = a != b;
var isLess = a < b;
var isGreater = a > b;
var isLessOrEqual = a <= b;
var isGreaterOrEqual = a >= b;

// Logical operators
var not = !isTrue;
var and = isTrue && isTrue;
var or = isTrue || isFalse;
```

## Running a Program

Run with bytecode compilation (default and faster):
```
python run.py examples/sample.txt
```

Run with AST interpretation:
```
python run.py examples/sample.txt --interpret
```

Debug bytecode:
```
python run.py examples/sample.txt --bytecode --debug
```

## Example Programs

Several example programs are included in the `examples/` directory to demonstrate language features:

- `arithmetic.txt` - Basic arithmetic operations
- `strings.txt` - String manipulation
- `conditionals.txt` - If/else statements
- `loops.txt` - While loops
- `fizzbuzz.txt` - Classic FizzBuzz problem
- `primes.txt` - Find prime numbers
- `data_types.txt` - Demonstrate boolean and float types
- `string_interpolation.txt` - Examples of string interpolation

## Bytecode Compilation

The bytecode compiler translates the AST into a sequence of stack-based instructions that can be executed by the virtual machine. This provides:

1. **Better performance** - Bytecode execution is faster than AST interpretation
2. **Smaller memory footprint** - Bytecode is more compact than the AST
3. **Potential for optimization** - Bytecode can be optimized before execution

The bytecode includes:
- Operation codes (opcodes) for each instruction
- A constants pool for literals (numbers, strings)
- Variable storage indexed by name 