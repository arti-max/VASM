import sys
import struct
import pickle
import os
from pathlib import Path
from typing import Dict, List, Tuple

from lexer import preprocess_line, tokenize_line
from parser import Parser
from code_generator import generate_db_code, generate_bank_code, generate_transition_code, generate_instruction_code
from utils import Utils
from errors import CompilationError

DATA_START_ADDRESS = 0x80  # Константа для начального адреса данных

class Compiler:
    
    def __init__(self):
        # Таблица опкодов инструкций (без BANK)
        self.opcodes: Dict[str, int] = {
            'NOP':    0x00,
            'SET':    0x01,
            'MOV':    0x02,
            'ADD':    0x03,
            'SUB':    0x04,
            'AND':    0x05,
            'OR':     0x06,
            'XOR':    0x07,
            'JMP':    0x08,
            'STOREV': 0x09,
            'STORER': 0x0A,
            'STOREM': 0x0B,
            'LOADR':  0x0C,
            'JE':     0x0D,
            'JNE':    0x0E,
            'CMP':    0x0F,
            'PUSH':   0x10,
            'POP':    0x11,
            'MUL':    0x12,
            'DIV':    0x13,
            'SETPX':  0x14,    # Установить пиксель (x, y)
            'CLRPX':  0x15,    # Очистить пиксель (x, y)
            'DIGIT':  0x16,    # Вывести число на сегментный дисплей (позиция, значение)
            'CLEAR':  0x17,    # Очистить весь дисплей
            'GETKEY': 0x18,    # Новая инструкция для чтения клавиши
            'CALL':   0x19,    # Вызов подпрограммы
            'RET':    0x1A,
            'RND':    0x1B,    # Случайное число в регистр
            'HLT':    0xFF,
            'BANK':   0x1C,    # Переключение банка
            'SAVKEY': 0x1D,
            'BRIGHT': 0x1E,    # Новая инструкция для установки яркости
            'LOADRR': 0x1F,
            'CREAD':  0x20,    # Чтение секции кассеты
            'CWRITE': 0x21,    # Запись секции кассеты
            'CSTAT':  0x22,    # Проверка статуса кассеты
            'CINFO':  0x23,    # Получение информации о кассете
        }
        
        # Регистры
        self.registers: Dict[str, int] = {
            'R1': 0x01,
            'R2': 0x02,
            'R3': 0x03,
            'R4': 0x04,
            'R5': 0x05,
            'R6': 0x06
        }
        
        # Добавляем словарь для хранения меток
        self.labels: Dict[str, int] = {}
        self.program_size: int = 0
        self.current_line: int = 0  # Добавляем отслеживание текущей строки
        self.current_bank: int = 0  # Добавляем отслеживание текущего банка в компиляторе
        
        # Добавляем только словарь для констант
        self.defines: Dict[str, int] = {}
        self.current_db_address: int = DATA_START_ADDRESS
        self.lines : List[str] = []
        self.included_files : List[Path] = [] #Список для отслеживания импортированных файлов
        self.current_directory = Path('.')

    def get_bank_and_addr(self, full_addr: int) -> Tuple[int, int]:
            """Разделяет полный адрес на банк и адрес в банке."""
            bank = full_addr // 256
            addr = full_addr % 256
            return bank, addr

    def _check_bank_transition(self, line_num, lines, original_line, bank, current_bank):
        """Проверяет наличие инструкции BANK перед переходом в другой банк."""
        if bank != current_bank:
            prev_line = None
            # print(f"LINE_NUM: {line_num}")
            for prev_num in range(line_num - 2, -1, -1):
                if prev_num < 0:
                    break
                print(f"PREV_NUM: {prev_num} : {lines}")
                prev_line = lines[prev_num].split(';')[0].strip().upper()
                if prev_line and not prev_line.startswith(':'):
                    break
            if not prev_line or not prev_line.startswith('BANK'):
                raise CompilationError(
                    f"Строка {line_num}: Переход на адрес в другом банке без указания BANK\n"
                    f"{original_line}\n"
                    f"Подсказка: Добавьте перед этой строкой:\n"
                    f"BANK {bank}"
                )
    
    def _process_include(self, file_path: str):
        """Включает содержимое файла в текущую программу."""
        file_path_obj = (self.current_directory / file_path).resolve()  # Получаем абсолютный путь

        normalized_file_path = str(file_path_obj).lower()

        #print("NORMFILE: ",normalized_file_path)
        
        # if normalized_file_path in [str(path).lower() for path in self.included_files]:
        #         return [], current_address
        
        self.included_files.append(normalized_file_path)
        
        try:
            with open(normalized_file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            raise CompilationError(f"Файл не найден: {file_path}")
        
    def preprocess_includes(self, lines):
        """Заменяет директивы INCLUDE содержимым файлов."""
        processed_lines = []
        
        parser = Parser(self.opcodes, self.registers, self.labels, self.defines, self.current_bank, self.program_size, self.current_db_address)
        
        for line in lines:
            line = preprocess_line(line)
            if not line:
                continue
            
            if parser.is_directive(line) and parser.get_directive(line) == '.INCLUDE':
                file_path = parser.get_directive_values(line)[0]
                included_lines = self._process_include(file_path)
                if included_lines:
                    processed_lines.extend(included_lines)
            else:
                processed_lines.append(line)
        return processed_lines
        
    def first_pass(self, lines):
        """Первый проход - собираем метки и их адреса"""
        current_address = 0
        
        parser = Parser(self.opcodes, self.registers, self.labels, self.defines, self.current_bank, self.program_size, self.current_db_address)
        conditional_stack = []
        is_wr = True

        for line in lines:
            line = preprocess_line(line)
            if not line:
                continue

            print(current_address)
                
            if parser.is_directive(line):
                directive = parser.get_directive(line)
                
                if directive == '.IFNDEF':
                    parts = tokenize_line(line)
                    if len(parts) != 2:
                       raise CompilationError("Неверный формат .IFNDEF")
                    symbol = parts[1]
                    conditional_stack.append(symbol not in self.defines)
                    is_wr = all(conditional_stack)
                    continue
                elif directive == '.ENDIF':
                     if not conditional_stack:
                         raise CompilationError("Директива .ENDIF без соотв. .IFNDEF")
                     is_wr = not all(conditional_stack) if conditional_stack else True
                     conditional_stack.pop()
                     continue
                # elif not is_wr:
                #     print(f"SKIP: {current_address}")
                #     continue
                elif directive == '.DB' and is_wr:
                    values = parser.get_directive_values(line)
                    for value in values:
                        value = value.strip()
                        current_address += 3
                    continue
                elif directive == '.DEFINE' and is_wr:
                    parts = tokenize_line(line)
                    if len(parts) == 3:
                        name = parts[1]
                        try:
                            if parts[2].startswith('0x'):
                                value = int(parts[2], 16)
                            else:
                                value = int(parts[2])
                            self.defines[name] = value
                        except ValueError:
                            pass
                    continue
                
            # Проверяем, является ли строка меткой
            if parser.is_label(line) and is_wr:
                label_name = parser.get_label_name(line)  # Преобразуем метку в верхний регистр
                self.labels[label_name] = current_address
                continue
                
            # Считаем байты инструкции
            instruction, operands = parser.parse_instruction(line, 0, line)
            
            if instruction in self.opcodes and is_wr:
                # Считаем размер инструкции (опкод + операнды)
                instruction_size = 1  # опкод
                instruction_size += len(operands)  # добавляем размер операндов
                current_address += instruction_size
        #self.program_size = current_address #Сохраняем размер
        if conditional_stack:
           raise CompilationError("Незакрытые директивы .IFNDEF")
   
    def compile(self, source_file, output_file, use_cassette=False, section_number=0):
        # try:
            self.current_directory = Path(source_file).parent # Получаем текущий каталог
            with open(source_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Препроцессинг - заменяем INCLUDE
            lines = self.preprocess_includes(lines)
            
            # Первый проход - собираем метки
            self.first_pass(lines)
            self.lines = lines
            
            machine_code = []
            
            utils = Utils(lines, self.labels, self.current_bank)
            
            self.defines = {} #Очищаем self.defines
            
            parser = Parser(self.opcodes, self.registers, self.labels, self.defines, self.current_bank, self.program_size, self.current_db_address)
            
            conditional_stack = []
            write_code = True #Флаг записи
           
            # Второй проход - генерируем код
            for line_num, line in enumerate(lines, 1):
                original_line = line.strip()
                
                if parser.is_label(line) or not parser.process_conditional_directive(line, self.defines):
                    continue
                
                 # Проверяем директивы
                if parser.is_directive(line):
                    directive = parser.get_directive(line)
                    
                    if directive == '.IFNDEF':
                         parts = tokenize_line(line)
                         if len(parts) != 2:
                            raise CompilationError("Неверный формат .IFNDEF")
                         symbol = parts[1]
                         conditional_stack.append(symbol not in self.defines)
                         write_code = all(conditional_stack)
                         print(f"WR: {write_code} CS: {conditional_stack} S: {symbol} DEF: {self.defines}")
                         continue
                    elif directive == '.ENDIF':
                         if not conditional_stack:
                              raise CompilationError("Директива .ENDIF без соотв. .IFNDEF")
                         conditional_stack.pop()
                         write_code = all(conditional_stack) if conditional_stack else True
                         continue
                    elif directive == '.INCLUDE':
                         continue #Пропускаем Include, т.к. он уже был обработан
                    elif directive == '.DEFINE':
                        parts = tokenize_line(line)
                        if len(parts) == 3:
                            name = parts[1]
                            try:
                                if parts[2].startswith('0x'):
                                    value = int(parts[2], 16)
                                else:
                                    value = int(parts[2])
                                self.defines[name] = value
                            except ValueError:
                                pass
                        continue
                    elif directive == '.DB':
                        values = parser.get_directive_values(line)
                        if write_code:
                            machine_code = generate_db_code(self, values, machine_code, line_num, original_line)
                        continue
                
                instruction, operands = parser.parse_instruction(line, line_num, original_line)
                
                if instruction is None:
                    continue #Если instruction None, ничего не делаем

                # Отслеживаем текущий банк
                if instruction == 'BANK':
                     if write_code:
                        machine_code = generate_bank_code(self, tokenize_line(line), machine_code)
                     continue

                # Проверяем инструкции перехода
                if instruction in ['JMP', 'JE', 'JNE', 'CALL']:
                    label = operands[0]
                    print(label)
                    if label in self.labels:
                        print(f"IS LABEL: {label} {self.labels}")
                        target_addr = self.labels[label]
                    else:
                        print(f"NOT IS LABEL {label} : CODE {machine_code}")
                        try:
                            target_addr = int(label, 16) if label.startswith('0X') else int(label)
                        except ValueError:
                            raise CompilationError(f"Неверный адрес перехода: {label} в строке {line_num}")

                    if write_code:
                       print("wrL")
                       machine_code = generate_transition_code(self, instruction, target_addr, machine_code, line_num, original_line)
                else:
                    # Обычные инструкции
                    if write_code:
                       print("wrI")
                       machine_code = generate_instruction_code(self, instruction, operands, machine_code, line_num, original_line)
    
            if conditional_stack:
               raise CompilationError("Незакрытые директивы .IFNDEF")
            
            self.program_size = len(machine_code)
               
            print(f"\nРазмер программы: {self.program_size} байт")
            
           # Выводим адреса всех меток
            print("\nАдреса меток:")
            print("-" * 40)
            print(f"{'Метка':<20} {'Адрес':<8} {'Банк:Смещение'}")
            print("-" * 40)
            for label, addr in sorted(self.labels.items(), key=lambda item: item[1]):
                bank, offset = self.get_bank_and_addr(addr)
                print(f"{label:<20} {addr:<8} {bank}:{hex(offset)}")
            print("-" * 40)
            # Записываем машинный код в файл или кассету

            if use_cassette:
                if not self._write_to_cassette(output_file, machine_code, section_number):
                   return False
            else:
                if not self._write_to_file(output_file, machine_code):
                    return False
            return True

        # except CompilationError as e:
        #     print(f"Ошибка компиляции: {str(e)}")
        #     return False
        # except Exception as e:
        #     print(f"Неизвестная ошибка компиляции: {str(e)}")
        #     return False
    
    def _write_to_file(self, output_file, machine_code):
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for byte in machine_code:
                    f.write(f"{byte:02x} ")
            print(f"Код успешно записан в файл: '{output_file}'")
            return True
        except Exception as e:
            print(f"Ошибка записи в файл: {str(e)}")
            return False

    def _write_to_cassette(self, output_file, machine_code, section_number):
        try:
            with open(output_file, 'rb+') as f:
                try:
                    loaded_data = pickle.load(f)  # загружаем данные с помощью pickle
                except Exception as e:
                    print(f"Ошибка: Невозможно десериализовать данные кассеты, возможно файл не зашифрован с помощью pickle: {e}")
                    return False
                cassette_data = loaded_data['data']
                
                start_byte = section_number * 256
                end_byte = start_byte + len(machine_code)
                
                if end_byte > len(cassette_data):
                    print("Ошибка: бинарный код слишком велик для выбранной секции кассеты.")
                    return False

                cassette_data[start_byte:end_byte] = machine_code # записываем код в нужную секцию
                loaded_data['data'] = cassette_data # обновляем данные
                f.seek(0) # устанавливаем курсор в начало файла
                pickle.dump(loaded_data, f) # перезаписываем данные
                print(f"Код успешно записан в секцию {section_number} файла кассеты '{output_file}'")
                return True
        except FileNotFoundError:
                print(f"Ошибка: Файл кассеты '{output_file}' не найден")
                return False
        except Exception as e:
                 print(f"Ошибка записи в кассету: {str(e)}")
                 return False