from AST_Nodes import *
from Assembly_Codes import *

class Globals:
    def __init__(self):
        self.data_segment = """
            .data
            _fl0: .float 0.0
            _fl1: .float -1.0
            _str0: .asciiz \"\"
            _str1: .asciiz \"Instancia de objeto, de tipo dinamico con id interno: \"
            _str2: .asciiz \"Pues... un array...\"
            _str3: .asciiz \"False\"
            _str4: .asciiz \"True\"
        """
        self.next_float_id = 2
        self.next_str_id = 5
        self.next_while_id = 1
        self.next_comparison_id = 1
        self.next_if_id = 1
        self.next_func_id = 1
        self.FIRST_TYPE_ID = 10
        self.next_type_id = self.FIRST_TYPE_ID

        self.type_to_id = {} #(key, value) = (type_name, dynamic_type_id)
        self.func_to_id = {} #(key, value) = (function_name_in_code, corresponding_label_number_in_assembly)
        self.type_to_initializer = {} #(key, value) = (type_name_in_code, corresponding_label_number_in_assembly)
        self.type_and_function_to_id = {} #(key, value) = ((type_name_in_code, function_name_in_code), corresponding_label_number_in_assembly)
        self.type_and_member_to_offset = {} #(key, value) = ((type_name_in_code, member_name_in_code), offset_from_start_of_object)
        self.type_to_size = {} #(key, value) = (type_name, size_in_bytes)
        self.protocols_by_name = {} #(key, value) = (protocol_name, protocol_definition)

class Context:
    def __init__(self):
        self.sp_offset = 0 #Offset of $sp from $fp
        self.local_variables = {} #Offsets of the variable, for each variable name
    
    def push_from(self, register: str):
        self.sp_offset -= 4
        if register[1] == "f" and register[2] != "p":
            return f"\naddi $sp, $sp, -4\nswc1 {register}, 0($sp)\n"
        else:
            return f"\naddi $sp, $sp, -4\nsw {register}, 0($sp)\n"
        
    def pop_to(self, register: str):
        self.sp_offset += 4
        if register[1] == "f" and register[2] != "p":
            return f"\nl.s {register}, 0($sp)\naddi $sp, $sp, 4\n"
        else:
            return f"\nlw {register}, 0($sp)\naddi $sp, $sp, 4\n"

def function_to_mips(func: Function_Definition, g: Globals, func_id: int):
        t = ""
        t += f"\n_func{func_id}:\n"
        t += "move $fp, $sp\n"
        
        c = Context()
        for i in range(0, len(func.argument_names)):
            c.local_variables[func.argument_names[i]] = [4*(len(func.argument_names)-1-i)]

        t += __expression_to_MIPS(func.body, g, True, c)
        t += c.pop_to("$v0")
        t += "move $sp, $fp\n"
        t += "j $ra\n"
        return t

def program_to_MIPS(main_expr: Expression, global_funcs: List[Function_Definition], global_types: List[Type_Definition], global_protocols: List[Protocol_Definition]):
    
    #Preamble
    t = ASSEMBLY_TEXT_PREAMBLE
    g = Globals()
    
    #So you like functions and assembly? Name every function in assembly
    for func in global_funcs:
        g.func_to_id[func.name] = g.next_func_id
        g.next_func_id += 1
    
    #For each type, calculate ids, sizes, func_ids, offsets, etc.
    for type in global_types:
        g.type_to_size[type.name] = -1
    
    while True:
        all_types_processed = True
        for type in global_types:
            if g.type_to_size[type.name] == -1:
                all_types_processed = False
                if type.parent_name == None or g.type_to_size[type.parent_name] != -1:
                    
                    #Type to dynamic_type_id
                    g.type_to_id[type.name] = g.next_type_id
                    g.next_type_id += 1

                    #Initializer to func_id
                    g.type_to_initializer[type.name] = g.next_func_id
                    g.next_func_id += 1

                    #Member functions to func_id
                    for func in type.functions:
                        g.type_and_function_to_id[(type.name, func.name)] = g.next_func_id
                        g.next_func_id += 1
                    
                    #Member variable to offset
                    offset = 4
                    if type.parent_name != None:
                        offset = g.type_to_size[type.parent_name]
                    
                    for member_name in type.variable_names:
                        g.type_and_member_to_offset[(type.name, member_name)] = offset
                        offset += 4
                    
                    #Overloaded and inhereted functions to offset. Also, add the inhereted ones to corresponding list.
                    if type.parent_name != None:
                        for func_parent in type.parent.functions+type.parent.inhereted_functions:
                            g.type_and_member_to_offset[(type.name, func_parent.name)] = g.type_and_member_to_offset[(type.parent.name, func_parent.name)]
                            if func_parent.name not in [func.name for func in type.functions]: #HACK: should semmantic checker do this?
                                type.inhereted_functions.append(func_parent)

                    #New (not overloaded nor inhereted) functions to offset
                    for func in type.functions:
                        if (type.name, func.name) not in g.type_and_member_to_offset:
                            g.type_and_member_to_offset[(type.name, func.name)] = offset
                            offset += 4

                    g.type_to_size[type.name] = offset
        
        if all_types_processed: break

    #Type table
    g.data_segment += "\n"
    for type in global_types:
        is_table = f"_tpy{g.type_to_id[type.name]}_is: .word "

        parent = type
        while parent != None:
            is_table += f"{g.type_to_id[parent.name]}, "
            parent = parent.parent
        is_table += f"{0}\n"
        g.data_segment += is_table
    g.data_segment += "\n"

    g.data_segment += "_is_table_references: .word "
    for i in range(len(global_types)):
        g.data_segment += f"_tpy{g.FIRST_TYPE_ID+i}_is, "
    g.data_segment += "0 \n\n"

    #Calculate protocol stuff (type id, size, offset...)
    for protocol in global_protocols:
        g.protocols_by_name[protocol.name] = protocol
        
        g.type_to_id[protocol.name] = g.next_type_id
        g.next_type_id += 1

        offset = 4
        for func_name in protocol.func_names:
            g.type_and_member_to_offset[(protocol.name, func_name)] = offset
            offset += 4
        
        g.type_to_size[protocol.name] = offset

    #Translate the functions to assembly
    for func in global_funcs:
        t += function_to_mips(func, g, g.func_to_id[func.name])

    #Translate types to assembly
    for type in global_types:
        #--Build Initializer--##
        t += f"\n_func{g.type_to_initializer[type.name]}:\n"
        t += "move $fp, $sp\n"
        
        temp_c = Context()
        for i in range(0, len(type.initializer_parameters)):
            temp_c.local_variables[type.initializer_parameters[i]] = [4*(len(type.initializer_parameters)-i)]

        #Call parent initializer if exists
        if type.parent_name != None:
            t += temp_c.push_from("$fp")
            t += temp_c.push_from("$ra")

            for i in range(0, len(type.parent_initializer_expressions)):
                t += __expression_to_MIPS(type.parent_initializer_expressions[i], g, True, temp_c)
            
            t += "lw $a0, 0($fp)\n"
            t += temp_c.push_from("$a0")

            t += f"\njal _func{g.type_to_initializer[type.parent_name]}\n"
            
            for i in range(0, len(type.parent_initializer_expressions)):
                t += temp_c.pop_to("$a3")
            t += temp_c.pop_to("$a3")

            t += temp_c.pop_to("$ra")
            t += temp_c.pop_to("$fp")
        
        #Initialize members
        t += "lw $v0, 0($fp)\n"
        for func in type.functions:
            t += f"\nla $a0, _func{g.type_and_function_to_id[(type.name,func.name)]}\n"
            t += f"sw $a0, {g.type_and_member_to_offset[(type.name,func.name)]}($v0)\n"

        for i in range(0, len(type.variable_names)):
            t += temp_c.push_from("$v0")
            t += __expression_to_MIPS(type.initializer_expressions[i], g, True, temp_c)
            t += temp_c.pop_to("$a0")
            t += temp_c.pop_to("$v0")
            t += f"sw $a0, {g.type_and_member_to_offset[(type.name, type.variable_names[i])]}($v0)\n"
        
        t += "move $sp, $fp\n"
        t += "j $ra\n"

        #--Build Methods--##
        for func in type.functions:
            aux_function = Function_Definition("aux", func.argument_names+["self"], func.body)
            t += function_to_mips(aux_function, g, g.type_and_function_to_id[(type.name,func.name)])

    #Translate the main expression to assembly
    t += "\nmain:\nmove $fp, $sp\n"
    c = Context()
    t += __expression_to_MIPS(main_expr, g, True, c)

    #Exit
    t += """
        #Exit   
        ori $2, $0, 10
        syscall
    """

    return g.data_segment+t

#Uso: se mete la referencia a la instancia del tipo en $a3 antes de llamar a la funcion. La referencia al protocolo se retorna en $v0
def __type_to_protocol(type_name: str, protocol_name: str, g: Globals):
    t += f"""
        ori $a0, $0, {g.type_to_size[protocol_name]}
        ori $v0, $0, 9
        syscall
        
        sw $a3, 0($v0)
    """

    protocol = g.protocols_by_name[protocol_name]

    for func_name in protocol.func_names:
        t += f"la $a0, _func{g.type_and_function_to_id[(type_name, func_name)]}"
        t += f"sw $a3, {g.type_and_member_to_offset[(protocol_name, func_name)]}($v0)"

def __expression_to_MIPS(expr_node: Expression, g: Globals, is_result_used: bool, c: Context):
    t = ""
    
    if isinstance(expr_node, ASSEMBLY_INSERT):
        t += expr_node.ass
    
    elif isinstance(expr_node, Expression_Block):
        for i in range(len(expr_node.expressions)):
            t += __expression_to_MIPS(expr_node.expressions[i], g, ((i==len(expr_node.expressions)-1) and is_result_used), c)

    elif isinstance(expr_node, Is_Operator):
        t += c.push_from("$fp")
        t += c.push_from("$ra")
        
        t += f"li $a0, {g.type_to_id[expr_node.right.name]}"
        t += c.push_from("$a0")

        #Get left operand dynamic type
        t += __expression_to_MIPS(expr_node.left, g, True, c)
        t += c.pop_to("$a0")
        t += "lw $a0, 0($a0)\n"

        #Convert said type to offset from table
        t += f"addi $a0, $a0, -{g.FIRST_TYPE_ID}\n"
        t += "li $a1, 4\n"
        t += "mul $a0, $a0, $a1\n"

        #Index the table to get the reference to the wanted tpy_X_is array
        t += "la $a2, _is_table_references\n"
        t += "add $a2, $a2, $a0\n"
        t += "lw $a2, 0($a2)\n"
        t += c.push_from("$a2")

        t += f"\njal is_int_in_array_zero_ended\n"
        
        t += c.pop_to("$a3")
        t += c.pop_to("$a3")

        t += c.pop_to("$ra")
        t += c.pop_to("$fp")

        if is_result_used:
            t += c.push_from("$v0")

    elif isinstance(expr_node, As_Keyword):
        t += __expression_to_MIPS(expr_node.left, g, is_result_used, c)

    elif isinstance(expr_node, Dot_Operator):
        t += __expression_to_MIPS(expr_node.left, g, True, c)
        t += c.pop_to("$a0")
        
        if isinstance(expr_node.left.type, Array_Type):
            if expr_node.right.name == "length":
                t += "lw $a1, -4($a0)\n"
            if expr_node.right.name == "current":
                t += "la $a1, array_current"
            if expr_node.right.name == "next":
                t += "la $a1, array_next"
        elif expr_node.left.type.name == STRING_TYPE_NAME and expr_node.right.name == "length":
            t += c.push_from("$fp")
            t += c.push_from("$ra")
            
            t += c.push_from("$a0")

            t += f"\njal get_string_length\n"
            t += "mtc1 $v0, $f0\ncvt.s.w $f0, $f0\nmfc1 $v0, $f0\n"
            t += "move $a1, $v0\n"
            
            t += c.pop_to("$a0")

            t += c.pop_to("$ra")
            t += c.pop_to("$fp")
        else:
            t += f"lw $a1, {g.type_and_member_to_offset[(expr_node.left.type.name, expr_node.right.name)]}($a0)"
        
        if is_result_used:
            if expr_node.right_is_function_name:
                t += c.push_from("$a0")
            t += c.push_from("$a1")

    elif isinstance(expr_node, If):
        if_id = g.next_if_id
        current = expr_node
        if_sub_id = 0
        
        while current.next != None:
            t += f"_if{if_id}_{if_sub_id}:\n"
            t += __expression_to_MIPS(current.condition, g, True, c)
            t += c.pop_to("$a0")
            t += f"beqz $a0, _if{if_id}_{if_sub_id+1}\n"
            t += __expression_to_MIPS(current.body, g, is_result_used, c)
            t += f"j _if{if_id}e\n"
            if_sub_id += 1
            current = current.next

        t += f"_if{if_id}_{if_sub_id}:\n"
        t += __expression_to_MIPS(current.body, g, is_result_used, c)
        t += f"_if{if_id}e:\n"

    elif isinstance(expr_node, Function_Call):
        t += c.push_from("$fp")
        t += c.push_from("$ra")
        
        for i in range(0, len(expr_node.arguments)):
            t += __expression_to_MIPS(expr_node.arguments[i], g, True, c)

        if isinstance(expr_node.name, Identifier) and expr_node.name.name == "print":
            if isinstance(expr_node.arguments[0].type, Basic_or_Composite_Type):
                if expr_node.arguments[0].type.name == STRING_TYPE_NAME:
                    t += __expression_to_MIPS(Identifier("print_str"), g, True, c)
                elif expr_node.arguments[0].type.name == FLOAT_TYPE_NAME:
                    t += __expression_to_MIPS(Identifier("print_flt"), g, True, c)
                elif expr_node.arguments[0].type.name == BOOL_TYPE_NAME:
                    t += __expression_to_MIPS(Identifier("print_bool"), g, True, c)
                else:
                    t += __expression_to_MIPS(Identifier("print_type"), g, True, c)
            else:
                t += __expression_to_MIPS(Identifier("print_array"), g, True, c)
        else:
            t += __expression_to_MIPS(expr_node.name, g, True, c)
        t += c.pop_to("$a0")
        t += f"\njalr $ra, $a0\n"
        
        for i in range(0, len(expr_node.arguments)):
            t += c.pop_to("$a3")
        if isinstance(expr_node.name, Dot_Operator): #Pop hidden 'self' parameter
            t += c.pop_to("$a3")

        t += c.pop_to("$ra")
        t += c.pop_to("$fp")

        if is_result_used:
            t += c.push_from("$v0")
    
    elif isinstance(expr_node, New):
        t += c.push_from("$fp")
        t += c.push_from("$ra")
        
        for i in range(0, len(expr_node.arguments)):
            t += __expression_to_MIPS(expr_node.arguments[i], g, True, c)
        
        t += f"""
            ori $a0, $0, {g.type_to_size[expr_node.type_name]}
            ori $v0, $0, 9
            syscall
            
            ori $a0, $0, {g.type_to_id[expr_node.type_name]}
            sw $a0, 0($v0)
        """
        t += c.push_from("$v0")

        t += f"\njal _func{g.type_to_initializer[expr_node.type_name]}\n"
        
        for i in range(0, len(expr_node.arguments)):
            t += c.pop_to("$a3")
        t += c.pop_to("$a3")

        t += c.pop_to("$ra")
        t += c.pop_to("$fp")

        if is_result_used:
            t += c.push_from("$v0")

    elif isinstance(expr_node, Base_Function_Call):
        t += c.push_from("$fp")
        t += c.push_from("$ra")
        
        for i in range(0, len(expr_node.arguments)):
            t += __expression_to_MIPS(expr_node.arguments[i], g, True, c)
        t += __expression_to_MIPS(Identifier("self"), g, True, c)

        t += f"\njal _func{g.type_and_function_to_id[(expr_node.ancestor_name, expr_node.func_name)]}\n"
        
        for i in range(0, len(expr_node.arguments)):
            t += c.pop_to("$a3")
        t += c.pop_to("$a3")

        t += c.pop_to("$ra")
        t += c.pop_to("$fp")

        if is_result_used:
            t += c.push_from("$v0")

    elif isinstance(expr_node, Variable_Declarations):
        t += "\n#pepe\n"
        for name, value in zip(expr_node.names, expr_node.values):
            t += __expression_to_MIPS(value, g, True, c)
            if name in c.local_variables:
                c.local_variables[name].append(c.sp_offset)
            else:
                c.local_variables[name] = [c.sp_offset]
        
        t += __expression_to_MIPS(expr_node.body, g, True, c)
        if is_result_used:
            t += c.pop_to("$v0")
        
        for name in expr_node.names:
            c.local_variables[name].pop()
            if c.local_variables[name] == []:
                del c.local_variables[name]
            t += c.pop_to("$a0")

        if is_result_used:
            t += c.push_from("$v0")
        t += "\n#cuco\n"

    elif isinstance(expr_node, Variable_Destructive_Assignment):
        t += __expression_to_MIPS(expr_node.expression, g, True, c)
        
        #Get the index (if its an array element assignment), convert it to int, and then to offset (that is: multiply it by 4)
        if expr_node.indexExpression != None:
            t += __expression_to_MIPS(expr_node.indexExpression, g, True, c)
            t += c.pop_to("$f0")
            t += "\ncvt.w.s $f0, $f0\nmfc1 $a3, $f0\n"
            t += "ori $a1, $0, 4\nmult $a3, $a1\nmflo $a3\n"

        t += c.pop_to("$v0")

        if expr_node.selfDotType != None:
            offset_from_fp = c.local_variables["self"][-1]
            offset_from_object_base = g.type_and_member_to_offset[(expr_node.selfDotType.name, expr_node.var_name)]
            t += f"\nlw $a1, {offset_from_fp}($fp)\n"
            t += f"addi $a1, $a1, {offset_from_object_base}\n"
        else:
            offset_from_fp = c.local_variables[expr_node.var_name][-1]
            t += f"\nmove $a1, $fp\naddi $a1, $a1, {offset_from_fp}\n"
        
        if expr_node.indexExpression != None:
            t += "\nlw $a1, 0($a1)\nadd $a1, $a1, $a3\n"

        t += f"\nsw $v0, 0($a1)\n"

        if is_result_used:
            t += c.push_from("$v0")

    elif isinstance(expr_node, While):
        while_num = g.next_while_id
        g.next_while_id += 1
        
        if is_result_used:
            if isinstance(expr_node.type, Basic_or_Composite_Type):
                if expr_node.type.name == FLOAT_TYPE_NAME:
                    t += "lw $a0, _fl0\n"
                elif expr_node.type.name == STRING_TYPE_NAME:
                    t += "la $a0, _str0\n"
                else:
                    t += "ori $a0, $0, 0\n"
            else:
                t += "ori $a0, $0, 0\n"
            t += c.push_from("$a0") #Push default value
        
        t += f"_w{while_num}:\n"
        t += __expression_to_MIPS(expr_node.condition, g, True, c)
        t += c.pop_to("$a0")
        t += f"beqz $a0, _w{while_num}e\n" #End while if condition is not met

        if is_result_used:
            t += c.pop_to("$a1")
        t += __expression_to_MIPS(expr_node.body, g, is_result_used, c)
        t += f"j _w{while_num}\n"
        t += f"_w{while_num}e:"

    elif isinstance(expr_node, Binary_Operator):
        
        #Evaluate left and right
        t += __expression_to_MIPS(expr_node.left, g, True, c)
        t += __expression_to_MIPS(expr_node.right, g, True, c)
        
        if expr_node.operator_type in ["+", "-", "*", "/", "%"]:
            t += c.pop_to("$f2")
            t += c.pop_to("$f1")
            
            #Operate
            if expr_node.operator_type == "+":
                t += "add.s $f3, $f1, $f2\n"
            elif expr_node.operator_type == "-":
                t += "sub.s $f3, $f1, $f2\n"
            elif expr_node.operator_type == "*":
                t += "mul.s $f3, $f1, $f2\n"
            elif expr_node.operator_type == "/":
                t += "div.s $f3, $f1, $f2\n"
            elif expr_node.operator_type == "%":
                t += """
                    cvt.w.s $f1, $f1
                    cvt.w.s $f2, $f2
                    
                    mfc1 $a1, $f1
                    mfc1 $a2, $f2

                    rem $a1, $a1, $a2

                    mtc1 $a1, $f1
                    cvt.s.w $f3, $f1
                """
            
            #Push result
            if is_result_used:
                t += c.push_from("$f3")
        
        elif expr_node.operator_type in ["&", "|"]:
            t += c.pop_to("$a1")
            t += c.pop_to("$a0")
            
            if expr_node.operator_type == "&":
                t += "and $a2, $a0, $a1\n"
            elif expr_node.operator_type == "|":
                t += "or $a2, $a0, $a1\n"

            if is_result_used:
                t += c.push_from("$a2")
        
        elif expr_node.operator_type == "@":
            t += c.pop_to("$a1")
            t += c.pop_to("$a0")
            t += c.push_from("$fp")
            t += c.push_from("$ra")
            t += c.push_from("$a1")
            t += c.push_from("$a0")

            t += "\njal concat_strings\n"
            t += c.pop_to("$a3")
            t += c.pop_to("$a3")

            t += c.pop_to("$ra")
            t += c.pop_to("$fp")

            if is_result_used:
                t += c.push_from("$v0")
        elif expr_node.operator_type in ["<", ">", "<=", ">="]:
            t += c.pop_to("$f2")
            t += c.pop_to("$f1")

            if expr_node.operator_type == "<":
                t += "\nc.lt.s $f1, $f2\n"
            if expr_node.operator_type == ">":
                t += "\nc.lt.s $f2, $f1\n"
            if expr_node.operator_type == "<=":
                t += "\nc.le.s $f1, $f2\n"
            if expr_node.operator_type == ">=":
                t += "\nc.le.s $f2, $f1\n"

            t += f"""
                bc1f _cmp{g.next_comparison_id}f
                
                ori $a0, $0, 1
                j _cmp{g.next_comparison_id}e

                _cmp{g.next_comparison_id}f:
                ori $a0, $0, 0

                _cmp{g.next_comparison_id}e:
            """
            
            if is_result_used:
                t += c.push_from("$a0")

            g.next_comparison_id += 1
        elif expr_node.operator_type in ["==", "!="]:
            t += c.pop_to("$a1")
            t += c.pop_to("$a0")
            
            if isinstance(expr_node.left.type, Basic_or_Composite_Type) and expr_node.left.type.name == STRING_TYPE_NAME:
                #Call the string_cmp func
                t += c.push_from("$fp")
                t += c.push_from("$ra")
                
                t += c.push_from("$a1")
                t += c.push_from("$a0")

                t += f"\njal string_cmp\n"
                
                t += c.pop_to("$a3")
                t += c.pop_to("$a3")

                t += c.pop_to("$ra")
                t += c.pop_to("$fp")

                if expr_node.operator_type == "==":
                    t += f"beqz $v0, _cmp{g.next_comparison_id}f\n"
                elif expr_node.operator_type == "!=":
                    t += f"bnez $v0, _cmp{g.next_comparison_id}f\n"
            else:
                if expr_node.operator_type == "==":
                    t += f"bne $a0, $a1, _cmp{g.next_comparison_id}f\n"
                elif expr_node.operator_type == "!=":
                    t += f"beq $a0, $a1, _cmp{g.next_comparison_id}f\n"

            t += f"""
                ori $a0, $0, 1
                j _cmp{g.next_comparison_id}e

                _cmp{g.next_comparison_id}f:
                ori $a0, $0, 0

                _cmp{g.next_comparison_id}e:
            """

            if is_result_used:
                t += c.push_from("$a0")

            g.next_comparison_id += 1
        else:
            print(f"No implementado el operador {expr_node.operator_type}")
            exit()

    elif isinstance(expr_node, Index_Operator):
        t += __expression_to_MIPS(expr_node.array_reference, g, True, c)
        t += __expression_to_MIPS(expr_node.index, g, True, c)
        
        if isinstance(expr_node.type, Basic_or_Composite_Type): #String is the only non_array indexable type
            
            #Reserve memory for the new (mono-character) string and end it with a zero
            t += "\nori $a0, $0, 2\n"
            t += "ori $v0, $0, 9\nsyscall\n"
            t += "move $a1, $v0\n"
            t += "sb $0, 1($a1)\n"
            
            #Get the index and the reference, convert the index to int, and get the indexed character
            t += c.pop_to("$f0")
            t += c.pop_to("$v0")
            t += "cvt.w.s $f0, $f0\nmfc1 $a0, $f0\n"
            t += "add $v0, $v0, $a0\n"

            #Copy the indexed character in the new (mono-character) string
            t += "move $a0, $0\n"
            t += "lb $a0, 0($v0)\n"
            t += "sb $a0, 0($a1)\n"
            t += "move $a0, $a1\n"
        else:
            t += c.pop_to("$f0")
            t += c.pop_to("$v0")
            t += "\ncvt.w.s $f0, $f0\nmfc1 $a0, $f0\n"
            t += "ori $a1, $0, 4\nmult $a0, $a1\nmflo $a0\n"
            t += "add $v0, $v0, $a0\n"
            t += "lw $a0, 0($v0)\n"
        
        if is_result_used:
            t += c.push_from("$a0")

    elif isinstance(expr_node, Unary_Operator):
        if expr_node.operator_type == "-":
            t += __expression_to_MIPS(expr_node.operand, g, True, c)
            t += c.pop_to("$f1")
            t += "neg.s $f3, $f1\n"
            if is_result_used:
                t += c.push_from("$f3")
        elif expr_node.operator_type == "!":
            t += __expression_to_MIPS(expr_node.operand, g, True, c)
            t += c.pop_to("$a0")
            t += "xori $a3, $a0, 1\n"
            if is_result_used:
                t += c.push_from("$a3")

    elif isinstance(expr_node, Identifier):
        if is_result_used:
            if expr_node.name in c.local_variables:
                offset = c.local_variables[expr_node.name][-1]
                t += f"\nlw $a0, {offset}($fp)\n"
                t += c.push_from("$a0")
            elif expr_node.name in g.func_to_id:
                t += f"la $a0, _func{g.func_to_id[expr_node.name]}"
                t += c.push_from("$a0")
            else:
                print(f"No existe el identificador {expr_node.name}")
                exit()

    elif isinstance(expr_node, Array_Literal):
        if is_result_used:
            t += f"\nori $a0, $0, {4*(len(expr_node.expressions)+2)}\n"
            t += "ori $v0, $0, 9\nsyscall\n"
            
            #Store Array Current
            t += f"l.s $f0, _fl1\nmfc1 $a0, $f0\n"
            t += "sw $a0, 0($v0)\n"
            t += "addi $v0, $v0, 4\n"

            #Store Array Length 
            t += f"ori $a0, $0, {len(expr_node.expressions)}\n"
            t += "mtc1 $a0, $f0\ncvt.s.w $f0, $f0\nmfc1 $a0, $f0\n"
            t += "sw $a0, 0($v0)\n"
            t += "addi $v0, $v0, 4\n"
            t += c.push_from("$v0")

            t += "move $a1, $v0\n"

        for i in range(0, len(expr_node.expressions)):
            t += c.push_from("$a1")
            t += __expression_to_MIPS(expr_node.expressions[i], g, True, c)
            t += c.pop_to("$a0")
            t += c.pop_to("$a1")
            if is_result_used:
                t += "sw $a0, 0($a1)\n"
                t += "addi $a1, $a1, 4\n"

    elif isinstance(expr_node, Literal):
        if is_result_used:
            if type(expr_node.value) is bool:
                if expr_node.value == True:
                    t += "ori $a0, $0, 1\n"
                    t += c.push_from("$a0")
                elif expr_node.value == False:
                    t += "ori $a0, $0, 0\n"
                    t += c.push_from("$a0")
            elif type(expr_node.value) is str:
                g.data_segment += f"_str{g.next_str_id}: .asciiz \"{str(expr_node.value)}\"\n" #Add string constant to data segment
                t += f"\nla $a0, _str{g.next_str_id}\n"
                t += c.push_from("$a0")
                g.next_str_id += 1
            else:
                g.data_segment += f"_fl{g.next_float_id}: .float {float(expr_node.value)}\n" #Add float constant to data segment
                t += f"\nl.s $f1, _fl{g.next_float_id}\n"
                t += c.push_from("$f1")
                g.next_float_id += 1
    
    return t