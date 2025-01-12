# code_generator.py

from typing import List
from errors import CompilationError

def generate_db_code(compiler, values, machine_code, line_num, original_line):
    """Генерирует код для директивы .DB."""
    for value in values:
        value = value.strip()
        # Добавляем STOREV
        machine_code.append(compiler.opcodes['STOREV'])
        # Добавляем адрес
        machine_code.append(compiler.current_db_address)
        # Добавляем значение
        if value in compiler.defines:
            machine_code.append(compiler.defines[value])
        else:
            try:
                machine_code.append(int(value))
            except ValueError:
                raise CompilationError(
                    f"Строка {line_num}: Неверное значение для .DB: {value}\n"
                    f"{original_line}"
                )
        compiler.current_db_address += 1
    return machine_code

def generate_bank_code(compiler, parts, machine_code):
    """Генерирует код для инструкции BANK."""
    compiler.current_bank = int(parts[1], 16) if parts[1].startswith('0X') else int(parts[1])
    machine_code.append(compiler.opcodes['BANK'])
    machine_code.append(compiler.current_bank)
    return machine_code

def generate_transition_code(compiler, instruction, target_addr, machine_code, line_num, original_line):
    """Генерирует код для инструкций перехода."""
    bank, addr = compiler.get_bank_and_addr(target_addr)
    
    print(f"CBT: {line_num} : {bank} : {addr} : {compiler.lines}")
    compiler._check_bank_transition(line_num, compiler.lines, original_line, bank, compiler.current_bank)
    
    machine_code.append(compiler.opcodes[instruction])
    machine_code.append(addr)
    return machine_code

def generate_instruction_code(compiler, instruction, operands, machine_code, line_num, original_line):
    """Генерирует код для обычных инструкций."""
    machine_code.append(compiler.opcodes[instruction])
    
    for operand in operands:
        if operand in compiler.registers:
            machine_code.append(compiler.registers[operand])
        elif operand in compiler.defines:
            machine_code.append(compiler.defines[operand])
        else:
            try:
                value = int(operand, 16) if operand.startswith('0X') else int(operand)
                if value > 255:
                    raise CompilationError(
                        f"Строка {line_num}: Значение {value} превышает размер байта\n"
                        f"{original_line}"
                    )
                machine_code.append(value)
            except ValueError:
                if operand in compiler.labels:
                    addr = compiler.labels[operand]
                    if addr > 255:
                        bank, local_addr = compiler.get_bank_and_addr(addr)
                        raise CompilationError(
                            f"Строка {line_num}: Адрес метки {operand} ({hex(addr)}) превышает размер банка\n"
                            f"{original_line}\n"
                            f"Подсказка: Разделите программу на банки. Для этого адреса используйте:\n"
                            f"BANK {bank}\n"
                            f"{instruction} {hex(local_addr)}"
                        )
                    machine_code.append(addr)
                else:
                    raise CompilationError(
                        f"Строка {line_num}: Неверный операнд: {operand}\n"
                        f"{original_line}"
                    )
    return machine_code