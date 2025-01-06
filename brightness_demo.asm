; Демонстрация работы с яркостью отдельных пикселей

.DEFINE MAX_BRIGHT 0xFF
.DEFINE MIN_BRIGHT 0x10
.DEFINE SIZE 0x0F
.DEFINE ESC 27

BANK 0
JMP SETUP

:SETUP
    CLEAR                   ; Очищаем экран
    SET R1 0                ; X координата
    SET R2 8                ; Y координата (середина экрана)
    SET R3 MAX_BRIGHT       ; Начальная яркость
    SET R4 MIN_BRIGHT       ; Шаг уменьшения яркости

:DRAW_LINE
    SETPX R1 R2 R3  ; Рисуем пиксель с яркостью из R3
    
    ; Уменьшаем яркость
    SUB R3 R4       ; R3 -= 16
    
    ; Переходим к следующему X
    SET R4 1
    ADD R1 R4               ; R1 += 1
    SET R4 MIN_BRIGHT       ; Возвращаем шаг яркости
    
    ; Проверяем конец экрана
    SET R4 SIZE
    CMP R1 R4
    JNE DRAW_LINE   ; Если не достигли края, продолжаем

:LOOP
    ; Ждем нажатия ESC
    GETKEY R4
    SET R3 ESC       ; Код ESC
    CMP R4 R3
    JNE LOOP

:END
    HLT 