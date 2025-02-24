# Документация по Ассемблеру для VCPU

Добро пожаловать в документацию по ассемблеру для **VCPU** — виртуального 8-битного процессора, реализованного на языке Python. Эта документация охватывает основные аспекты использования ассемблера, включая синтаксис, доступные инструкции, директивы, регистры, управление банками памяти и процесс компиляции.

## Содержание

1. [Введение](#введение)
2. [Требования](#требования)
3. [Установка](#установка)
4. [Синтаксис Ассемблера](#синтаксис-ассемблера)
    - [Структура Программы](#структура-программы)
    - [Комментарии](#комментарии)
    - [метки (Labels)](#метки-labels)
    - [Директивы](#директивы)
5. [Регистры](#регистрrы)
6. [Банковая Схема Памяти](#банковая-схема-памяти)
7. [Инструкции](#инструкции)
    - [Общие Инструкции](#общие-инструкции)
    - [Управление Потоком Выполнения](#управление-потоком-выполнения)
    - [Работа с Памятью](#работа-с-памятью)
    - [Ввод/Вывод](#вводвывод)
    - [Работа с Кассетами](#работа-с-кассетами)
8. [Командная Строка Компилятора](#командная-строка-компилятора)
    - [Основное Использование](#основное-использование)
    - [Опции](#опции)
9. [Процесс Загрузки Программы](#процесс-загрузки-программы)
10. [Примеры Программ](#примеры-программ)
    - [Простой Пример](#простой-пример)
    - [Использование Директив](#использование-директив)
    - [Работа с Кассетами](#работа-с-кассетами)
11. [Отладка и Ошибки](#отладка-и-ошибки)
12. [Дополнительные Возможности](#дополнительные-возможности)
    - [Константы и Определения](#константы-и-определения)
13. [Заключение](#заключение)

---

## Введение

**VCPU** — это виртуальный 8-битный процессор, реализованный на языке Python. Ассемблер для VCPU позволяет писать низкоуровневый код, который компилируется в машинный код, исполняемый виртуальным процессором. Эта документация поможет вам начать работу с ассемблером, ознакомиться с доступными инструкциями и особенностями компиляции.

## Требования

- **Python 3.6+**: Убедитесь, что Python установлен на вашем компьютере.
- **Библиотеки Python**: Некоторые библиотеки, такие как `pickle`, используются для работы с кассетами.

## Установка

1. **Клонируйте Репозиторий**:
    ```bash
    git clone https://github.com/your-repo/vcpu-assembler.git
    cd vcpu-assembler
    ```

2. **Установите Зависимости**:
    Если есть файл `requirements.txt`, установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

3. **Проверьте Установку**:
    Убедитесь, что все файлы на месте и готовы к использованию.

## Синтаксис Ассемблера

### Структура Программы

Программа на ассемблере для VCPU состоит из последовательности инструкций, директив и ярлыков. Пример структуры:

```assembly
.DEFINE MAX_VALUE 0xFF

:START
    SET R1 10
    MOV R2 R1
    ADD R2 R1
    HLT
```

### Комментарии

Комментарии начинаются с символа `;` и продолжаются до конца строки.

```assembly
; Это комментарий
SET R1 10 ; Установка регистра R1
```

### Метки (Labels)

Метки используются для обозначения адресов в коде и обозначаются двоеточием (`:`) перед именем.

```assembly
:LOOP
    SET R1 20
    JMP LOOP
```

### Директивы

Директивы начинаются с точки (`.`) и используются для задания данных или определений.

- **.DB**: Определение байтов данных.
    ```assembly
    .DB 0x1A, 0x2B, 0x3C
    ```
  
- **.DEFINE**: Определение констант.
    ```assembly
    .DEFINE BUFFER_SIZE 256
    ```

## Регистры

VCPU поддерживает 6 регистров общего назначения:

- `R1` — 0x01
- `R2` — 0x02
- `R3` — 0x03
- `R4` — 0x04
- `R5` — 0x05
- `R6` — 0x06

### Специальные Регистры

- **IP (Instruction Pointer)**: Указывает текущую инструкцию.
- **Flags**: Флаги состояния процессора (например, `ZF` — флаг нуля).

## Банковая Схема Памяти

VCPU использует банковую схему памяти для управления большим количеством данных, разделяя память на банки по 256 байт. Банки позволяют эффективно управлять данными, обеспечивая доступ к различным сегментам памяти.

Всего банков: `8 (2048 байт)`

### Использование Банков

Банки памяти необходимы только для работы с данными (`STORE` и `LOAD`), а также для команд перехода (`JMP`, `CALL`).  Компилятор подскажет в ошибке компиляции, куда надо вставить инструкцию `BANK` перед командами, и с каким дначением

**Пример переключения банка для работы с данными:**

```assembly
BANK 1
STOREV 0x10 R1 ; загружает в адрес 16 значение ищ регистра 1
LOADR R2 0x10 ; загружает в регистр 2 данные из памяти по адресу 16
```

### Управление Банками в Компиляторе

Компилятор сам отслеживает текущий банк и сообщает о нём, если вы неправильно их указали `BANK`, чтобы обеспечить корректный доступ к данным или переходам между различными банками памяти.

## Инструкции

### Общие Инструкции

#### NOP
**NOP** — No Operation. Делает ничего.

```assembly
NOP
```

#### SET
**SET REG VAL** — Устанавливает значение `VAL` в регистр `REG`.

```assembly
SET R1 10
```

#### MOV
**MOV REG1 REG2** — Копирует значение из `REG2` в `REG1`.

```assembly
MOV R2 R1
```

#### ADD
**ADD REG1 REG2** — Добавляет значение `REG2` к `REG1`. Результат сохраняется в `REG1`.

```assembly
ADD R1 R2
```

#### SUB
**SUB REG1 REG2** — Вычитает значение `REG2` из `REG1`. Результат сохраняется в `REG1`.

```assembly
SUB R1 R2
```

#### AND, OR, XOR
Логические операции над регистрами.

```assembly
AND R1 R2
OR R1 R2
XOR R1 R2
```

### Управление Потоком Выполнения

#### JMP
**JMP ADDR** — Безусловный переход по адресу `ADDR`.

```assembly
JMP LOOP
```

#### JE
**JE ADDR** — Переход к `ADDR`, если флаг `ZF` установлен.

```assembly
JE END
```

#### JNE
**JNE ADDR** — Переход к `ADDR`, если флаг `ZF` не установлен.

```assembly
JNE LOOP
```

#### CALL
**CALL ADDR** — Вызов подпрограммы по адресу `ADDR`.

```assembly
CALL FUNCTION
```

#### RET
**RET** — Возврат из подпрограммы.

```assembly
RET
```

#### CMP
**CMP REG1 REG2** — Сравнивает `REG1` и `REG2`, устанавливает флаг `ZF`.

```assembly
CMP R1 R2
```

### Работа с Памятью

#### STOREV
**STOREV ADDR VAL** — Сохраняет значение `VAL` по адресу `ADDR`.

```assembly
STOREV 0x10 R1
```

#### STORER
**STORER ADDR REG** — Сохраняет значение из `REG` по адресу `ADDR`.

```assembly
STORER 0x20 R2
```

#### STOREM
**STOREM ADDR1 ADDR2** — Сохраняет значение из `ADDR2` по адресу `ADDR1`.

```assembly
STOREM 0x30 0x40
```

#### LOADR
**LOADR REG ADDR** — Загружает значение из `ADDR` в `REG`.

```assembly
LOADR R1 0x50
```

### Ввод/Вывод

### Пиксельный дисплей
- Разрешение: 16x16 пикселей
- Каждый пиксель:
  - Может быть включен/выключен
  - Имеет настраиваемую яркость (0-255)
- Координаты:
  - X: 0-15 (слева направо)
  - Y: 0-15 (сверху вниз)

### Семисегментный дисплей
- 8 разрядов
- Поддерживаемые символы:
  - Цифры: 0-9
  - Специальные символы:
    - Минус (код 10)
    - Подчеркивание (код 11)
    - Пробел (код 12)
    - E/ESC (код 13)
    - d/DEL (код 14)
    - n/ENTER (код 15)
    - Стрелки (коды 16-19)
- Режимы вывода:
  - Одиночный символ: указываем позицию (1-7) и значение
  - Полное число: позиция 0, число дополняется нулями слева

### Клавиатура
- Поддерживаемые клавиши и их коды:
  - Цифры: 0-9 (коды 0-9)
  - ESC: код 13
  - DEL: код 14
  - ENTER: код 15
  - Стрелки:
    - Вверх: код 16
    - Вниз: код 17
    - Вправо: код 18
    - Влево: код 19
- Два режима работы:
  - Активный опрос (GETKEY)
  - Автосохранение в память (SAVKEY)

#### SETPX
**SETPX REG1 REG2 REG3** — Устанавливает пиксель на координатах `(x, y)` с яркостью из `REG3`.

```assembly
SETPX R1 R2 R3
```

#### CLRPX
**CLRPX REG1 REG2** — Очищает пиксель на координатах `(x, y)`.

```assembly
CLRPX R1 R2
```

#### DIGIT
**DIGIT REG1 REG2** — Выводит число на сегментный дисплей на позиции из `REG1` со значением из `REG2`. Позиция 0 включает автоматическое выравнивание цифр по правой стороне.

```assembly
DIGIT R1 R2
```

#### CLEAR
**CLEAR** — Очищает весь дисплей.

```assembly
CLEAR
```

#### GETKEY
**GETKEY REG** — Считывает нажатую клавишу и записывает ASCII код в `REG`.

```assembly
GETKEY R1
```

### Работа с Кассетами

#### CREAD
**CREAD REG1 REG2** — Загружает секцию кассеты из `REG2` начиная с адреса `REG1`.

```assembly
CREAD R1 R2
```

#### CWRITE
**CWRITE REG1 REG2** — Записывает данные из памяти начиная с `REG1` в секцию кассеты `REG2`.

```assembly
CWRITE R1 R2
```

#### CSTAT
**CSTAT REG** — Записывает статус кассеты (0 — отсутствует, 1 — вставлена) в `REG`.

```assembly
CSTAT R1
```

#### CINFO
**CINFO REG1 REG2** — Получает информацию о кассете. Тип информации задается в `REG1`, результат записывается в `REG2`.

```assembly
CINFO R1 R2
```

#### SAVKEY
**SAVKEY ADDR** — Устанавливает адрес для сохранения нажатий клавиш.

```assembly
SAVKEY R1
```

#### BRIGHT
**BRIGHT REG** — Устанавливает яркость экрана из значения в регистре `REG`.

```assembly
BRIGHT R1
```

#### RND
**RND REG LIMIT** — Генерирует случайное число от 0 до `LIMIT` и сохраняет его в `REG`.

```assembly
RND R1 100
```

## Командная Строка Компилятора

### Основное Использование

Компилятор VCPU реализован в файлах `main.py` и `compiler.py`. Для компиляции программы используйте следующую команду:

```bash
python main.py [--cassette <section_number>] <output_file> <input_file>
```

### Опции

- `--cassette <section_number>`: Указывает, что вывод будет записан в кассету в определенную секцию.

#### Примеры

1. **Компиляция в файл**:

    ```bash
    python main.py program.bin program.asm
    ```

2. **Компиляция в кассету**:

    ```bash
    python main.py --cassette 2 cassette.cas program.asm
    ```

### Обработка Ошибок

При ошибках компиляции компилятор выведет сообщение с указанием строки и причины ошибки. Например:

```
Ошибка: неверный формат команды --cassette. Используйте --cassette <section_number> <output_file> <input_file>
```

## Процесс Загрузки Программы

Программа автоматически загружается в память процессора с помощью модуля `loader.py`. Загрузка происходит из файла `boot.bin`, который содержит скомпилированный машинный код.

## Примеры Программ

### Простой Пример

Программа, которая устанавливает в `R1` число 10, копирует его в `R2`, добавляет `R1` к `R2` и завершает выполнение.

```assembly
:START
    SET R1 10
    MOV R2 R1
    ADD R2 R1
    HLT
```

### Использование Директив

Пример с использованием директив `.DEFINE` и `.DB`.

```assembly
.DEFINE MAX_COUNT 0x0A

.DB 0x01, 0x02, 0x03, MAX_COUNT

:START
    SET R1 MAX_COUNT
    MOV R2 R1
    ; Остальной код
    HLT
```

### Работа с Кассетами

Пример записи данных в кассету.

```assembly
:START
    ; Установка адреса сохранения
    SET R1 0x80
    SAVKEY R1

    ; Запись данных из памяти в кассету
    CWRITE R1 R2

    HLT
```

## Отладка и Ошибки

### Общие Ошибки

- **Синтаксические Ошибки**: Неправильный синтаксис инструкции или директивы.
- **Неверные Опернды**: Использование несуществующих регистров или констант.
- **Переходы Между Банками**: Если переход осуществляется в другой банк без инструкции `BANK`.
- **Переполнение Стека**: Когда стек заполняется до предела.

### Отладка

Используйте вывод компилятора для определения размеров программы и адресов меток:

```
Размер программы: 15 байт

Адреса меток:
----------------------------------------
Метка                 Адрес    Банк:Смещение
----------------------------------------
START                 0x00     0:0x0
LOOP                  0x05     0:0x5
----------------------------------------
```

## Дополнительные Возможности

### Константы и Определения

Используйте директиву `.DEFINE` для определения констант, которые можно использовать в коде.

```assembly
.DEFINE BUFFER_SIZE 256
.DEFINE START_ADDRESS 0x80

:START
    SET R1 BUFFER_SIZE
    ; Остальной код
    HLT
```

## Заключение

Ассемблер для VCPU предоставляет мощные инструменты для создания низкоуровневых программ для виртуального 8-битного процессора. Изучив эту документацию, вы сможете эффективно использовать доступные инструкции, директивы и возможности компилятора для реализации своих проектов. Не бойтесь экспериментировать и создавать собственные программы — возможности ограничены только вашим воображением!

Если у вас возникли вопросы или предложения, пожалуйста, обратитесь к [репозиторию проекта](https://github.com/arti-max/VCPU) или свяжитесь с авторами.

---

**Приятного кодирования!**
