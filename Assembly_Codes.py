ASSEMBLY_TEXT_PREAMBLE = """
.text
.globl main

get_string_length:
    #Set base
    move $fp, $sp

    #Load argument
    lw $a0, 0($fp)

    #Loop
    ori $v0, $0, 0
    _slw1:
        ori $a1, $0, 0
        lb $a1, 0($a0)
        beqz $a1, _slw1e
        addi $v0, $v0, 1
        addi $a0, $a0, 1
        j _slw1
    _slw1e:

    #Return
    j $ra

concat_strings:
    #Set base
    move $fp, $sp

    #Load first string
    lw $a0, 0($fp)

    ############ Compute Length of First String

    #Push fp and ra
    addi $sp, $sp, -4
    sw $fp, 0($sp)

    addi $sp, $sp, -4
    sw $ra, 0($sp)
    
    #Push argument
    addi $sp, $sp, -4
    sw $a0, 0($sp)

    #Call
    jal get_string_length

    #Pop argument
    addi $sp, $sp, 4

    #Pop ra and fp
    lw $ra, 0($sp)
    addi $sp, $sp, 4

    lw $fp, 0($sp)
    addi $sp, $sp, 4

    ############

    #Push string 1 length
    addi $sp, $sp, -4
    sw $v0, 0($sp)

    #Load second string
    lw $a0, 4($fp)

    ############ Compute Length of Second String

    #Push fp and ra
    addi $sp, $sp, -4
    sw $fp, 0($sp)

    addi $sp, $sp, -4
    sw $ra, 0($sp)
    
    #Push argument
    addi $sp, $sp, -4
    sw $a0, 0($sp)

    #Call
    jal get_string_length

    #Pop argument
    addi $sp, $sp, 4

    #Pop ra and fp
    lw $ra, 0($sp)
    addi $sp, $sp, 4

    lw $fp, 0($sp)
    addi $sp, $sp, 4

    ############
    
    #Compute total length
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    add $a0, $a0, $v0

    #Reserve Memory
    addi $a0, $a0, 1
    ori $v0, $0, 9
    syscall

    #Loop over first string
    lw $a0, 0($fp) # a0 <- old_string1_pointer
    ori $a1, $v0, 0 # a1 <- new_string_pointer
    _scw1:
        ori $a2, $0, 0
        lb $a2, 0($a0)
        beqz $a2, _scw1e
        sb $a2, 0($a1)
        addi $a0, $a0, 1
        addi $a1, $a1, 1
        j _scw1
    _scw1e:

    #Loop over second string
    lw $a0, 4($fp) # a0 <- old_string2_pointer
    _scw2:
        ori $a2, $0, 0
        lb $a2, 0($a0)
        beqz $a2, _scw2e
        sb $a2, 0($a1)
        addi $a0, $a0, 1
        addi $a1, $a1, 1
        j _scw2
    _scw2e:
    
    sb $0, 0($a1)

    #Return
    j $ra

string_cmp:
    #Set base
    move $fp, $sp

    #Load arguments
    lw $a2, 0($fp)
    lw $a3, 4($fp)

    #Loop
    _sccw1:
        ori $a0, $0, 0
        lb $a0, 0($a2)
        ori $a1, $0, 0
        lb $a1, 0($a3)
        bne $a0, $a1, _sccw1e_false

        beqz $a0, _sccw1e_true
        
        addi $a2, $a2, 1
        addi $a3, $a3, 1
        j _sccw1
    _sccw1e_true:
        ori $v0, $0, 1
        j _sccw1e
    _sccw1e_false:
        ori $v0, $0, 0
    _sccw1e:

    #Return
    j $ra
"""