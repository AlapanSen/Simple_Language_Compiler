import sys
from src.main import main

if __name__ == "__main__":
    sys.argv = [sys.argv[0]] + sys.argv[1:]
    main() 