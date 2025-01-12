from typing import Tuple

class Utils:

    def __init__(self, lines, labels, current_bank):
        self.lines = lines
        self.labels = labels
        self.current_bank = current_bank
        
    def get_bank_and_addr(self, full_addr: int) -> Tuple[int, int]:
        """Разделяет полный адрес на банк и адрес в банке."""
        bank = full_addr // 256
        addr = full_addr % 256
        return bank, addr

    def _check_bank_transition(self, line_num, lines, original_line, bank, current_bank):
        """Проверяет наличие инструкции BANK перед переходом в другой банк."""
        if bank != current_bank:
            prev_line = None
            for prev_num in range(line_num - 2, -1, -1):
                if prev_num < 0:
                    break
                prev_line = lines[prev_num].split(';')[0].strip().upper()
                if prev_line and not prev_line.startswith(':'):
                    break
            if not prev_line or not prev_line.startswith('BANK'):
                from errors import CompilationError
                raise CompilationError(
                    f"Строка {line_num}: Переход на адрес в другом банке без указания BANK\n"
                    f"{original_line}\n"
                    f"Подсказка: Добавьте перед этой строкой:\n"
                    f"BANK {bank}"
                )