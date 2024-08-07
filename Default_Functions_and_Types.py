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

print_int_func = Function_Definition("print_int", ["int"], Expression_Block([
    ASSEMBLY_INSERT(
        """
        lw $4, 0($fp)
        ori $2, $0, 1
        syscall
        """
    ),
    Identifier("int")
]))

print_type_func = Function_Definition("print_type", ["instance"], Expression_Block([
    ASSEMBLY_INSERT(
        """
        la $a0, _str1
        ori $v0, $0, 4
        syscall

        lw $a0, 0($sp)
        lw $a0, 0($a0)
        ori $v0, $0, 1
        syscall
        """
    ),
    Identifier("instance")
]))

print_array_func = Function_Definition("print_array", ["arr"], Expression_Block([
    ASSEMBLY_INSERT(
        """
        la $a0, _str2
        ori $v0, $0, 4
        syscall
        """
    ),
    Identifier("arr")
]))

print_bool_func = Function_Definition("print_bool", ["arr"], Expression_Block([
    ASSEMBLY_INSERT(
        """
        lw $a0, 0($fp)
        
        bnez $a0, _______w
        la $a0, _str3
        j ______x
        
        _______w:
        la $a0, _str4
        
        ______x:
        ori $v0, $0, 4
        syscall
        """
    ),
    Identifier("arr")
]))

#--- Se reserva $s0 para el estado random
rand_func = Function_Definition("rand", [], Expression_Block([
    ASSEMBLY_INSERT(
        """
        #Next int value
        li $a0, 75
        li $a1, 65537
        mul $s0, $s0, $a0
        addi $s0, $s0, 74
        rem $s0, $s0, $a1
        move $v0, $s0

        #To [0,1)
        mtc1 $s0, $f0
        mtc1 $a1, $f1
        cvt.s.w $f0, $f0
        cvt.s.w $f1, $f1
        div.s $f0, $f0, $f1
        mfc1 $v0, $f0

        addi $sp, $sp, -4
        sw $v0, 0($sp)
        """
    ),
]))

rand_seed_func = Function_Definition("rand_seed", [], Expression_Block([
    ASSEMBLY_INSERT(
        """
        lw $a0, 0($fp)
        mtc1 $a0, $f0
        abs.s $f0, $f0
        cvt.w.s $f0, $f0
        mfc1 $s0, $f0
        
        addi $sp, $sp, -4
        sw $s0, 0($sp)
        """
    ),
]))


default_funcs = [print_str_func, print_flt_func, print_int_func, print_type_func, print_array_func, print_bool_func, 
                 rand_func, rand_seed_func]

#--- Default Types ---#
default_types = []