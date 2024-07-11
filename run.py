from parserTest2 import *
from Code_Generation import *
import subprocess
from Default_Functions_and_Types import default_funcs

def hulk_compile(program_code: str):
    AST = parser.parse(program_code, lexer=lexer)
    AST.func_list.extend(default_funcs)
    return program_to_MIPS(AST.main_expression, AST.func_list, AST.type_list)

i_file = open("./test.hulk", mode = "r")
o_file = open("./compiled.asm", mode = "w")
o_file.write(hulk_compile(i_file.read()))
o_file.close()
subprocess.run("qtspim -f compiled.asm")