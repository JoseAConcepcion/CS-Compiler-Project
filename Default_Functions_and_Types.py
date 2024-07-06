from AST_Nodes import *

#--- Default Functions ---#
print_str_func = Function_Definition("print_str", ["str"], Expression_Block([
    ASSEMBLY_INSERT(
        """
        lw $4, 0($fp)
        ori $2, $0, 4
        syscall
        """
    ),
    Identifier("str")
]))

print_flt_func = Function_Definition("print_flt", ["flt"], Expression_Block([
    ASSEMBLY_INSERT(
        """
        l.s $f12, 0($fp)
        ori $2, $0, 2
        syscall
        """
    ),
    Identifier("flt")
]))

default_funcs = [print_str_func, print_flt_func]

#--- Default Types ---#
default_types = []