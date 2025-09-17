# CS-Compiler-Project

Este proyecto implementa un compilador educativo para el lenguaje HULK, realizado para una clase de compiladores. El compilador toma código fuente escrito en HULK y lo traduce a instrucciones MIPS, permitiendo su ejecución en simuladores como qtspim.

## Informe breve sobre el funcionamiento

### ¿Qué hace el proyecto?

- **Compilación a MIPS:** El archivo principal `run.py` lee código HULK desde `test.hulk`, lo procesa con un parser para generar su AST, extiende las funciones con utilidades por defecto y traduce todo a código ensamblador MIPS, ejecutable en qtspim.
- **Definiciones personalizadas:** Permite definir tipos de datos, funciones y protocolos propios, soportando inicializadores y métodos asociados.
- **Generación de bajo nivel:** Incluye rutinas en MIPS para operaciones como manejo de arrays, concatenación de strings, y manipulación de datos complejos.
- **Parsing y gramáticas:** Utiliza módulos para definir gramáticas y procesar sintáctica y semánticamente el código fuente HULK, generando estructuras intermedias.
- **Ejemplos matemáticos y gráficos:** Incluye ejemplos de uso con funciones matemáticas y rutinas gráficas, mostrando versatilidad y aplicación más allá del compilador base.

### Resumen técnico

El proyecto abarca desde el análisis léxico, sintáctico y semántico del código fuente HULK, hasta la generación final de ensamblador MIPS, permitiendo definir estructuras y funciones personalizadas, con utilidades para manipulación y visualización de resultados.