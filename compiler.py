class Compiler:
    def __init__(self):
        # Таблица опкодов инструкций (без BANK)
        self.opcodes = {
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
            'LOADRR': 0x1F
        }
        
        # Регистры
        self.registers = {
            'R1': 0x01,
            'R2': 0x02,
            'R3': 0x03,
            'R4': 0x04,
            'R5': 0x05,
            'R6': 0x06
        }
        
        # Добавляем словарь для хранения меток
        self.labels = {}
        self.program_size = 0
        self.current_line = 0  # Добавляем отслеживание текущей строки
        self.current_bank = 0  # Добавляем отслеживание текущего банка в компиляторе
        
        # Добавляем только словарь для констант
        self.defines = {}
        self.current_db_address = 0x80

    def get_bank_and_addr(self, full_addr):
        # Вспомогательная функция для разделения адреса
        bank = full_addr // 256
        addr = full_addr % 256
        return bank, addr

    def first_pass(self, lines):
        """Первый проход - собираем метки и их адреса"""
        current_address = 0
        
        for line in lines:
            line = line.split(';')[0].strip()
            if not line:
                continue
                
            # Добавляем только обработку директив
            if line.startswith('.'):
                parts = line.split()
                directive = parts[0].upper()
                
                if directive == '.DB':
                    values = ' '.join(parts[1:]).split(',')
                    for value in values:
                        value = value.strip()
                        current_address += 3
                    continue
                    
                elif directive == '.DEFINE':
                    if len(parts) == 3:
                        name = parts[1]
                        try:
                            #print(parts[2])
                            if parts[2].startswith('0x'):
                                value = int(parts[2], 16)
                            else:
                                value = int(parts[2])
                            self.defines[name] = value
                        except ValueError:
                            pass
                    continue
            
            # Проверяем, является ли строка меткой
            if line.startswith(':'):
                label_name = line[1:].strip().upper()  # Преобразуем метку в верхний регистр
                self.labels[label_name] = current_address
                continue
                
            # Считаем байты инструкции
            parts = line.upper().split()
            instruction = parts[0]
            
            if instruction in self.opcodes:
                # Считаем размер инструкции (опкод + операнды)
                instruction_size = 1  # опкод
                operands = parts[1:]
                instruction_size += len(operands)  # добавляем размер операндов
                current_address += instruction_size

    def compile(self, source_file, output_file):
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Первый проход - собираем метки
            self.first_pass(lines)

            #print(self.defines)
            
            machine_code = []
            
            # Второй проход - генерируем код
            for line_num, line in enumerate(lines, 1):
                original_line = line.strip()  # Сохраняем оригинальную строку
                line = line.split(';')[0].strip()
                if not line or line.startswith(':'):
                    continue
                    
                # Добавляем только обработку директив
                if line.startswith('.'):
                    parts = line.split()
                    directive = parts[0].upper()
                    
                    if directive == '.DB':
                        values = ' '.join(parts[1:]).split(',')
                        for value in values:
                            value = value.strip()
                            # Добавляем STOREV
                            machine_code.append(self.opcodes['STOREV'])
                            # Добавляем адрес
                            machine_code.append(self.current_db_address)
                            # Добавляем значение
                            if value in self.defines:
                                machine_code.append(self.defines[value])
                            else:
                                    machine_code.append(int(value))
                            self.current_db_address += 1
                        continue
                    elif directive == '.DEFINE':
                        continue

                parts = line.upper().split()
                instruction = parts[0]
                
                # Отслеживаем текущий банк
                if instruction == 'BANK':
                    self.current_bank = int(parts[1], 16) if parts[1].startswith('0X') else int(parts[1])
                    machine_code.append(self.opcodes['BANK'])
                    machine_code.append(self.current_bank)
                    continue

                # Проверяем инструкции перехода
                if instruction in ['JMP', 'JE', 'JNE', 'CALL']:
                    label = parts[1]
                    if label in self.labels:
                        target_addr = self.labels[label]
                        bank, addr = self.get_bank_and_addr(target_addr)
                        
                        # Если адрес в другом банке, проверяем наличие BANK перед этой инструкцией
                        if bank != self.current_bank:
                            # Ищем предыдущую инструкцию BANK
                            prev_line = None
                            for prev_num in range(line_num-2, -1, -1):
                                if prev_num < 0:
                                    break
                                prev_line = lines[prev_num].split(';')[0].strip().upper()
                                if prev_line and not prev_line.startswith(':'):
                                    break
                            
                            if not prev_line or not prev_line.startswith('BANK'):
                                raise ValueError(
                                    f"Строка {line_num}: Переход на адрес в другом банке без указания BANK\n"
                                    f"{original_line}\n"
                                    f"Подсказка: Добавьте перед этой строкой:\n"
                                    f"BANK {bank}"
                                )

                        # Добавляем инструкцию перехода с обрезанным адресом
                        machine_code.append(self.opcodes[instruction])
                        machine_code.append(addr)  # addr уже обрезан до размера банка
                    else:
                        raise ValueError(f"Строка {line_num}: Метка не найдена: {label}")
                else:
                    # Обычные инструкции
                    machine_code.append(self.opcodes[instruction])
                    
                    # Обрабатываем операнды
                    operands = parts[1:]
                    for operand in operands:
                        # Проверяем регистры
                        if operand in self.registers:
                            machine_code.append(self.registers[operand])
                        else:
                            # Проверяем определенные константы
                            if operand in self.defines:
                                machine_code.append(self.defines[operand])
                                continue
                                
                            # Пробуем как число
                            try:
                                value = int(operand, 16) if operand.startswith('0X') else int(operand)
                                if value > 255:
                                    raise ValueError(
                                        f"Строка {line_num}: Значение {value} превышает размер байта\n"
                                        f"{original_line}"
                                    )
                                machine_code.append(value)
                            except ValueError as e:
                                if operand in self.labels:
                                    addr = self.labels[operand]
                                    if addr > 255:
                                        bank, local_addr = self.get_bank_and_addr(addr)
                                        raise ValueError(
                                            f"Строка {line_num}: Адрес метки {operand} ({hex(addr)}) превышает размер банка\n"
                                            f"{original_line}\n"
                                            f"Подсказка: Разделите программу на банки. Для этого адреса используйте:\n"
                                            f"BANK {bank}\n"
                                            f"{instruction} {hex(local_addr)}"
                                        )
                                    machine_code.append(addr)
                                else:
                                    raise ValueError(
                                        f"Строка {line_num}: Неверный операнд: {operand}\n"
                                        f"{original_line}"
                                    )

            self.program_size = len(machine_code)
            print(f"\nРазмер программы: {self.program_size} байт")
            
            # Выводим адреса всех меток
            print("\nАдреса меток:")
            print("-" * 40)
            print(f"{'Метка':<20} {'Адрес':<8} {'Банк:Смещение'}")
            print("-" * 40)
            for label, addr in sorted(self.labels.items()):
                bank, offset = self.get_bank_and_addr(addr)
                print(f"{label:<20} {addr:<8} {bank}:{hex(offset)}")
            print("-" * 40)

            # Записываем машинный код в файл
            with open(output_file, 'w', encoding='utf-8') as f:
                for byte in machine_code:
                    f.write(f"{byte:02x} ")

            return True

        except Exception as e:
            print(f"Ошибка компиляции: {str(e)}")
            return False 