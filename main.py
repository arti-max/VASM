from compiler import Compiler
import sys

def main():
    if len(sys.argv) != 3:
        print("Использование: python main.py input.asm output.bin")
        return
        
    source_file = sys.argv[1]
    output_file = sys.argv[2]
    
    compiler = Compiler()
    if compiler.compile(source_file, output_file):
        print(f"Компиляция успешно завершена. Результат сохранен в {output_file}")
    else:
        print("Ошибка при компиляции")

if __name__ == "__main__":
    main() 