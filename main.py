from compiler import Compiler
import sys

def main():
    if len(sys.argv) < 3:
        print("Использование: python main.py [--cassette <section_number>] <output_file> <input_file>")
        return

    use_cassette = False
    section_number = 0
    output_file = ""
    input_file = ""


    if "--cassette" in sys.argv:
        use_cassette = True
        try:
            cassette_index = sys.argv.index("--cassette")
            section_number = int(sys.argv[cassette_index + 1])
            if section_number < 0:
              raise Exception()
            output_file = sys.argv[cassette_index+2]
            input_file = sys.argv[-1]
        except (ValueError, IndexError, Exception):
            print("Ошибка: неверный формат команды --cassette. Используйте --cassette <section_number> <output_file> <input_file>")
            return

    elif  len(sys.argv) == 3:
        output_file = sys.argv[1]
        input_file = sys.argv[2]
    else:
         print("Ошибка: неверный формат команды. Используйте [--cassette <section_number>] <output_file> <input_file>")
         return
    
    compiler = Compiler()
    if compiler.compile(input_file, output_file, use_cassette, section_number):
         print("Компиляция прошла успешно")
    else:
         print("Компиляция не удалась")

if __name__ == "__main__":
    main()