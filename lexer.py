def preprocess_line(line):
    """Удаляет комментарии и лишние пробелы."""
    line = line.split(';')[0].strip()
    return line

def tokenize_line(line):
    """Разделяет строку на токены."""
    return line.upper().split()