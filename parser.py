# parser.py
from typing import List, Dict, Union, Tuple
from errors import CompilationError
from lexer import tokenize_line

class Parser:
    def __init__(self, opcodes, registers, labels, defines, current_bank, program_size, current_db_address):
        self.opcodes = opcodes
        self.registers = registers
        self.labels = labels
        self.defines = defines
        self.current_bank = current_bank
        self.program_size = program_size
        self.current_db_address = current_db_address
        self.conditional_stack = []
        

    def get_directive(self, line: str) -> str:
        """Возвращает имя директивы (например, .INCLUDE) или None."""
        parts = tokenize_line(line)
        if parts and parts[0].startswith('.'):
            return parts[0].upper()
        return None

    def get_directive_values(self, line: str) -> List[str]:
        """Извлекает значения из директивы, удаляя кавычки."""
        parts = tokenize_line(line)
        values = ' '.join(parts[1:]).split(',')
        # Удаляем кавычки из каждого значения
        return [value.strip().strip('"') for value in values]
    
    def is_directive(self, line:str) -> bool:
        """Проверяет, является ли строка директивой."""
        return self.get_directive(line) is not None

    def is_label(self, line: str) -> bool:
        """Проверяет, является ли строка меткой."""
        return line.strip().startswith(":")

    def get_label_name(self, line: str) -> str:
        """Извлекает имя метки из строки, убирая двоеточие."""
        return line.strip()[1:].upper()

    def parse_instruction(self, line: str, line_num: int, original_line: str) -> Tuple[Union[str, None], List[str]]:
        """Парсит строку и возвращает инструкцию и операнды."""
        parts = tokenize_line(line)
        if not parts:
            return None, []
        instruction = parts[0]
        operands = parts[1:]
        return instruction, operands

    def process_conditional_directive(self, line:str, defines:Dict[str,int]) -> bool:
        """Проверяет, нужно ли компилировать строку"""
        if self.conditional_stack and not self.conditional_stack[-1]:
              return False
        return True