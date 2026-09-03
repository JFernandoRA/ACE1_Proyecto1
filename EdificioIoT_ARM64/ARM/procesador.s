/*
 * procesador.s
 * Módulo de procesamiento en ensamblador AArch64 (ARM64) para el proyecto
 * "Edificio Inteligente IoT". Escrito con syscalls de Linux directas
 * (sin libc), para poder ensamblarse y enlazarse solo con 'as' y 'ld'.
 *
 * Qué hace:
 *   1. Lee el archivo "datos.txt" (generado por Python).
 *   2. Interpreta números enteros separados por saltos de línea.
 *   3. Detecta el carácter '$' como finalizador de los datos.
 *   4. Calcula máximo, mínimo, promedio entero (truncado) y cantidad de
 *      datos procesados.
 *   5. Escribe el resultado en "resultado.txt" con el formato:
 *        MÁX=<valor>
 *        MIN=<valor>
 *        AVG=<valor>
 *        COUNT=<valor>
 *
 * Compilar (en la Raspberry Pi, arquitectura aarch64 nativa):
 *   as -g -o procesador.o procesador.s
 *   ld -o procesador procesador.o
 *   (o simplemente: make)
 *
 * Ejecutar:
 *   ./procesador
 */

    .global _start
    .text

// ---------------------------------------------------------------------
// _start: punto de entrada. Orquesta todo el proceso.
// ---------------------------------------------------------------------
_start:
    // ---- abrir datos.txt para lectura ----
    mov     x0, #-100               // AT_FDCWD (directorio actual)
    adr     x1, ruta_entrada
    mov     x2, #0                  // O_RDONLY
    mov     x3, #0
    mov     x8, #56                 // syscall: openat
    svc     #0
    cmp     x0, #0
    b.lt    error_abrir_entrada
    mov     x19, x0                 // x19 = fd de entrada

    // ---- leer el contenido completo a buffer_entrada ----
    mov     x0, x19
    adr     x1, buffer_entrada
    mov     x2, #16384
    mov     x8, #63                 // syscall: read
    svc     #0
    cmp     x0, #0
    b.lt    error_leer_entrada
    mov     x20, x0                 // x20 = cantidad de bytes leídos

    // ---- cerrar datos.txt ----
    mov     x0, x19
    mov     x8, #57                 // syscall: close
    svc     #0

    // =======================================================================
    // FASE 1: interpretar los números de buffer_entrada
    //   x9  = puntero de lectura (avanza por el buffer)
    //   x10 = puntero límite (fin del buffer, por si no aparece '$')
    //   x11 = count  (cantidad de números procesados)
    //   x12 = suma acumulada (64 bits, para no desbordar)
    //   x13 = máximo actual
    //   x14 = mínimo actual
    //   x15 = bandera: 1 si ya se procesó al menos un número
    // =======================================================================
    adr     x9, buffer_entrada
    add     x10, x9, x20
    mov     x11, #0
    mov     x12, #0
    mov     x13, #0
    mov     x14, #0
    mov     x15, #0

parse_loop:
    cmp     x9, x10
    b.ge    parse_fin                // se acabó el buffer sin encontrar '$'

    ldrb    w16, [x9]
    cmp     w16, #'$'
    b.eq    parse_fin                // encontramos el finalizador obligatorio

    cmp     w16, #'\n'
    b.eq    parse_siguiente
    cmp     w16, #'\r'
    b.eq    parse_siguiente
    cmp     w16, #' '
    b.eq    parse_siguiente

    // Si llegamos aquí, este carácter inicia un número (con signo opcional)
    mov     x17, #0                  // x17 = valor acumulado del número actual
    mov     x21, #0                  // x21 = 1 si el número es negativo

    cmp     w16, #'-'
    b.ne    num_digitos
    mov     x21, #1
    add     x9, x9, #1
    cmp     x9, x10
    b.ge    parse_fin
    ldrb    w16, [x9]

num_digitos:
    cmp     w16, #'0'
    b.lt    num_terminado
    cmp     w16, #'9'
    b.gt    num_terminado

    sub     w16, w16, #'0'           // carácter -> dígito numérico
    mov     x22, x17
    mov     x23, #10
    mul     x17, x22, x23            // x17 = x17 * 10
    add     x17, x17, w16, uxtw      // x17 = x17 + dígito

    add     x9, x9, #1
    cmp     x9, x10
    b.ge    num_terminado
    ldrb    w16, [x9]
    b       num_digitos

num_terminado:
    cbz     x21, num_actualizar_stats
    neg     x17, x17                 // aplicar el signo negativo

num_actualizar_stats:
    add     x11, x11, #1             // count++
    add     x12, x12, x17            // suma += valor

    cbnz    x15, num_no_es_primero
    mov     x13, x17                 // primer dato: max = valor
    mov     x14, x17                 // primer dato: min = valor
    mov     x15, #1
    b       parse_loop

num_no_es_primero:
    cmp     x17, x13
    b.le    num_revisar_min
    mov     x13, x17                 // actualizar máximo
num_revisar_min:
    cmp     x17, x14
    b.ge    parse_loop
    mov     x14, x17                 // actualizar mínimo
    b       parse_loop

parse_siguiente:
    add     x9, x9, #1
    b       parse_loop

parse_fin:
    // ---- calcular promedio truncado (división entera con signo) ----
    cbz     x11, promedio_es_cero
    sdiv    x24, x12, x11            // x24 = suma / count, truncado hacia 0
    b       promedio_listo
promedio_es_cero:
    mov     x24, #0
promedio_listo:

    // =======================================================================
    // FASE 2: formatear el resultado en buffer_salida
    //   Movemos los 4 resultados a x19-x22 porque nuestras subrutinas
    //   convertir_entero/copiar_bytes preservan ese rango de registros.
    // =======================================================================
    mov     x19, x13                 // max
    mov     x20, x14                 // min
    mov     x21, x24                 // avg
    mov     x22, x11                 // count

    adr     x25, buffer_salida       // puntero de escritura, avanza con cada pieza

    // "MÁX="  (Á en UTF-8 son los bytes 0xC3 0x81)
    adr     x0, etiqueta_max
    mov     x1, x25
    mov     x2, #ETIQUETA_MAX_LEN
    bl      copiar_bytes
    mov     x25, x0

    mov     x0, x19
    mov     x1, x25
    bl      convertir_entero
    mov     x25, x0

    // "\nMIN="
    adr     x0, etiqueta_min
    mov     x1, x25
    mov     x2, #ETIQUETA_MIN_LEN
    bl      copiar_bytes
    mov     x25, x0

    mov     x0, x20
    mov     x1, x25
    bl      convertir_entero
    mov     x25, x0

    // "\nAVG="
    adr     x0, etiqueta_avg
    mov     x1, x25
    mov     x2, #ETIQUETA_AVG_LEN
    bl      copiar_bytes
    mov     x25, x0

    mov     x0, x21
    mov     x1, x25
    bl      convertir_entero
    mov     x25, x0

    // "\nCOUNT="
    adr     x0, etiqueta_count
    mov     x1, x25
    mov     x2, #ETIQUETA_COUNT_LEN
    bl      copiar_bytes
    mov     x25, x0

    mov     x0, x22
    mov     x1, x25
    bl      convertir_entero
    mov     x25, x0

    // "\n" final
    adr     x0, etiqueta_final
    mov     x1, x25
    mov     x2, #1
    bl      copiar_bytes
    mov     x25, x0

    // longitud total del texto generado
    adr     x26, buffer_salida
    sub     x27, x25, x26

    // =======================================================================
    // FASE 3: escribir resultado.txt
    // =======================================================================
    mov     x0, #-100                // AT_FDCWD
    adr     x1, ruta_salida
    mov     x2, #0x241               // O_WRONLY | O_CREAT | O_TRUNC
    mov     x3, #0x1A4               // modo 0644
    mov     x8, #56                  // syscall: openat
    svc     #0
    cmp     x0, #0
    b.lt    error_abrir_salida
    mov     x28, x0                  // fd de salida

    mov     x0, x28
    adr     x1, buffer_salida
    mov     x2, x27
    mov     x8, #64                  // syscall: write
    svc     #0

    mov     x0, x28
    mov     x8, #57                  // syscall: close
    svc     #0

    mov     x0, #0                   // código de salida 0 = éxito
    mov     x8, #94                  // syscall: exit_group
    svc     #0

error_abrir_entrada:
    mov     x0, #1
    mov     x8, #94
    svc     #0

error_leer_entrada:
    mov     x0, #2
    mov     x8, #94
    svc     #0

error_abrir_salida:
    mov     x0, #3
    mov     x8, #94
    svc     #0


// ---------------------------------------------------------------------
// copiar_bytes(x0=origen, x1=destino, x2=longitud) -> x0=destino avanzado
// Función auxiliar (hoja) para copiar texto literal al buffer de salida.
// No necesita guardar registros: solo usa x0-x3, todos "caller-saved".
// ---------------------------------------------------------------------
copiar_bytes:
    cbz     x2, cb_fin
cb_loop:
    ldrb    w3, [x0], #1
    strb    w3, [x1], #1
    subs    x2, x2, #1
    b.ne    cb_loop
cb_fin:
    mov     x0, x1
    ret


// ---------------------------------------------------------------------
// convertir_entero(x0=valor con signo, x1=destino) -> x0=destino avanzado
// Convierte un entero de 64 bits a su representación ASCII decimal,
// incluyendo el signo '-' si es negativo. Escribe en [x1] y devuelve el
// puntero justo después del último carácter escrito.
//
// Usa x19-x24 como registros de trabajo, guardándolos y restaurándolos,
// por eso es seguro que el código que la llama (_start) guarde valores
// persistentes en ese mismo rango de registros: sobreviven a la llamada.
// ---------------------------------------------------------------------
convertir_entero:
    stp     x29, x30, [sp, #-96]!
    mov     x29, sp
    stp     x19, x20, [sp, #16]
    stp     x21, x22, [sp, #32]
    stp     x23, x24, [sp, #48]
    // offsets [sp,#64] a [sp,#95]: área temporal para los dígitos invertidos

    mov     x19, x1                  // puntero de escritura (avanza)
    mov     x20, x0                  // magnitud de trabajo
    mov     x21, #0                  // bandera: 1 si es negativo

    cmp     x20, #0
    b.ge    ce_sin_signo
    mov     x21, #1
    neg     x20, x20
ce_sin_signo:
    cbz     x21, ce_valor
    mov     w2, #'-'
    strb    w2, [x19]
    add     x19, x19, #1
ce_valor:
    cbnz    x20, ce_extraer
    mov     w2, #'0'
    strb    w2, [x19]
    add     x19, x19, #1
    b       ce_fin

ce_extraer:
    mov     x22, #0                  // cantidad de dígitos extraídos
ce_digito_loop:
    cbz     x20, ce_copiar
    mov     x23, #10
    udiv    x24, x20, x23
    msub    x2, x24, x23, x20        // x2 = resto = x20 % 10
    add     w2, w2, #'0'
    add     x4, x22, #64
    strb    w2, [sp, x4]             // guardamos en el área temporal (invertido)
    add     x22, x22, #1
    mov     x20, x24
    b       ce_digito_loop

ce_copiar:
    cbz     x22, ce_fin
    sub     x22, x22, #1
    add     x4, x22, #64
    ldrb    w2, [sp, x4]
    strb    w2, [x19]
    add     x19, x19, #1
    b       ce_copiar

ce_fin:
    mov     x0, x19
    ldp     x23, x24, [sp, #48]
    ldp     x21, x22, [sp, #32]
    ldp     x19, x20, [sp, #16]
    ldp     x29, x30, [sp], #96
    ret


    .data
ruta_entrada:
    .asciz  "datos.txt"
ruta_salida:
    .asciz  "resultado.txt"

etiqueta_max:
    .ascii  "M"
    .byte   0xC3, 0x81               // "Á" en UTF-8
    .ascii  "X="
    ETIQUETA_MAX_LEN = . - etiqueta_max

etiqueta_min:
    .ascii  "\nMIN="
    ETIQUETA_MIN_LEN = . - etiqueta_min

etiqueta_avg:
    .ascii  "\nAVG="
    ETIQUETA_AVG_LEN = . - etiqueta_avg

etiqueta_count:
    .ascii  "\nCOUNT="
    ETIQUETA_COUNT_LEN = . - etiqueta_count

etiqueta_final:
    .ascii  "\n"


    .bss
    .align 4
buffer_entrada:
    .skip   16384
buffer_salida:
    .skip   256