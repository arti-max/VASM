class Disassembler:
    def __init__(self):
        # Таблица опкодов (обратная таблице в компиляторе)
        self.opcodes = {
            0x00: 'NOP',
            0x01: 'SET',
            0x02: 'MOV',
            0x03: 'ADD',
            0x04: 'SUB',
            0x05: 'AND',
            0x06: 'OR',
            0x07: 'XOR',
            0x08: 'JMP',
            0x09: 'STOREV',
            0x0A: 'STORER',
            0x0B: 'STOREM',
            0x0C: 'LOADR',
            0x0D: 'JE',
            0x0E: 'JNE',
            0x0F: 'CMP',
            0x10: 'PUSH',
            0x11: 'POP',
            0x12: 'MUL',
            0x13: 'DIV',
            0x14: 'SETPX',
            0x15: 'CLRPX',
            0x16: 'DIGIT',
            0x17: 'CLEAR',
            0x18: 'GETKEY',
            0x19: 'CALL',
            0x1A: 'RET',
            0x1B: 'RND',
            0x1C: 'BANK',
            0x1D: 'SAVKEY',
            0x1E: 'BRIGHT',
            0x1F: 'LOADRR',
            0xFF: 'HLT'
        }
        
        # Обратная таблица регистров
        self.registers = {
            0x01: 'R1',
            0x02: 'R2',
            0x03: 'R3',
            0x04: 'R4',
            0x05: 'R5',
            0x06: 'R6'
        }
        
        # Размер операндов для каждой инструкции
        self.operand_sizes = {
            'NOP': 0,
            'SET': 2,    # регистр + значение
            'MOV': 2,    # регистр + регистр
            'ADD': 2,    # регистр + регистр
            'SUB': 2,
            'AND': 2,
            'OR': 2,
            'XOR': 2,
            'JMP': 1,    # адрес
            'STOREV': 2, # адрес + значение
            'STORER': 2, # адрес + регистр
            'STOREM': 2,
            'LOADR': 2,  # регистр + адрес
            'JE': 1,     # адрес
            'JNE': 1,    # адрес
            'CMP': 2,    # регистр + регистр
            'PUSH': 1,   # регистр
            'POP': 1,    # регистр
            'MUL': 2,
            'DIV': 2,
            'SETPX': 3,  # x + y + яркость
            'CLRPX': 2,  # x + y
            'DIGIT': 2,  # позиция + значение
            'CLEAR': 0,
            'GETKEY': 1, # регистр
            'CALL': 1,   # адрес
            'RET': 0,
            'RND': 2,    # регистр + максимум
            'BANK': 1,   # номер банка
            'SAVKEY': 1, # адрес
            'BRIGHT': 1, # яркость
            'LOADRR': 2, # регистр + регистр
            'HLT': 0
        }

    def disassemble(self, binary_file, output_file=None):
        try:
            # Читаем бинарный файл
            with open(binary_file, 'r') as f:
                data = f.read().strip().split()
                program = [int(x, 16) for x in data]

            current_bank = 0
            address = 0
            result = []
            i = 0

            while i < len(program):
                # Получаем текущий опкод
                opcode = program[i]
                if opcode not in self.opcodes:
                    result.append(f"; Неизвестный опкод: {hex(opcode)}")
                    i += 1
                    continue

                instruction = self.opcodes[opcode]
                operand_size = self.operand_sizes[instruction]
                operands = program[i+1:i+1+operand_size]
                
                # Форматируем инструкцию
                if instruction == 'BANK':
                    current_bank = operands[0]
                    result.append(f"\nBANK {operands[0]}    ; Банк {operands[0]}")
                elif instruction in ['JMP', 'JE', 'JNE', 'CALL']:
                    addr = operands[0]
                    result.append(f"{instruction} {hex(addr)}    ; Переход на адрес {hex(addr)}")
                elif instruction in ['SET', 'RND']:
                    reg = self.registers.get(operands[0], f"R{operands[0]}")
                    result.append(f"{instruction} {reg} {hex(operands[1])}    ; {reg} = {operands[1]}")
                elif instruction in ['MOV', 'ADD', 'SUB', 'AND', 'OR', 'XOR', 'CMP', 'MUL', 'DIV']:
                    reg1 = self.registers.get(operands[0], f"R{operands[0]}")
                    reg2 = self.registers.get(operands[1], f"R{operands[1]}")
                    result.append(f"{instruction} {reg1} {reg2}")
                elif instruction in ['STOREV']:
                    result.append(f"{instruction} {hex(operands[0])} {hex(operands[1])}    ; MEM[{hex(operands[0])}] = {hex(operands[1])}")
                elif instruction in ['STORER', 'LOADR']:
                    reg = self.registers.get(operands[1], f"R{operands[1]}")
                    result.append(f"{instruction} {hex(operands[0])} {reg}")
                else:
                    operands_str = ' '.join(hex(op) for op in operands)
                    if operands_str:
                        result.append(f"{instruction} {operands_str}")
                    else:
                        result.append(instruction)

                i += 1 + operand_size

            # Записываем результат
            if output_file:
                with open(output_file, 'w') as f:
                    f.write('\n'.join(result))
            else:
                print('\n'.join(result))

            return True

        except Exception as e:
            print(f"Ошибка дизассемблирования: {str(e)}")
            return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Использование: python disassembly.py input.bin [output.asm]")
        sys.exit(1)

    disassembler = Disassembler()
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    disassembler.disassemble(input_file, output_file) 