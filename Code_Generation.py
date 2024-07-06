from AST_Nodes import *
from Assembly_Codes import *

class Globals:
    def __init__(self):
        self.data_segment = ".data\n_fl0: .float 13.0\n" #TODO: change back to 0.0
        self.next_float_id = 1
        self.next_str_id = 1
        self.next_while_id = 1
        self.next_comparison_id = 1
        self.next_if_id = 1
        self.next_func_id = 1

        self.func_to_id = {} #(key, value) = (function_name_in_code, corresponding_label_number_in_assembly)
        self.type_to_constructor = {} #(key, value) = (type_name_in_code, corresponding_label_number_in_assembly)
        self.type_and_function_to_id = {} #(key, value) = ((type_name_in_code, function_name_in_code), corresponding_label_number_in_assembly)
        self.type_and_member_to_offset = {} #(key, value) = ((type_name_in_code, member_name_in_code), offset_from_start_of_object)

class Context:
    def __init__(self):
        self.sp_offset = 0 #Offset of $sp from $fp
        self.local_variables = {} #Offsets of the variable, for each variable name
    
    def push_from(self, register):
        self.sp_offset -= 4
        if register[1] == "f" and register[2] != "p":
            return f"\naddi $sp, $sp, -4\nswc1 {register}, 0($sp)\n"
        else:
            return f"\naddi $sp, $sp, -4\nsw {register}, 0($sp)\n"
        
    def pop_to(self, register):
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
        #t += "move $sp, $fp\n"
        t += "j $ra\n"
        return t

def program_to_MIPS(main_expr: Expression, global_funcs: List[Function_Definition], global_types: List[Type_Definition]):
    
    #Preamble
    t = ASSEMBLY_TEXT_PREAMBLE
    g = Globals()
    
    #So you like functions and assembly? Name every function in assembly
    for func in global_funcs:
        g.func_to_id[func.name] = g.next_func_id
        g.next_func_id += 1
    
    #For each type, assign and id to the constructor, every function, and assign offset to each member (function or data)
    for type in global_types: #TODO: herencia
        g.type_to_constructor[type.name] = g.next_func_id
        g.next_func_id += 1

        for func in type.functions:
            g.type_and_function_to_id[(type.name, func.name)] = g.next_func_id
            g.next_func_id += 1
        
        offset = 0
        for member_name in type.variable_names:
            g.type_and_member_to_offset[(type.name, member_name)] = offset
            offset += 4
        for func in type.functions:
            g.type_and_member_to_offset[(type.name, func.name)] = offset
            offset += 4

    #Translate the functions to assembly
    for func in global_funcs:
        t += function_to_mips(func, g, g.func_to_id[func.name])

    #Translate types to assembly
    for type in global_types:
        #Constructor (TODO: initializer)
        t += f"\n_func{g.type_to_constructor[type.name]}:\n"
        t += "move $fp, $sp\n"

        t += f"\nori $a0, $0, {4*(len(type.functions)+len(type.variable_names))}\n"
        t +="ori $v0, $0, 9\nsyscall\n"

        for func in type.functions:
            t += f"\nla $a0, _func{g.type_and_function_to_id[(type.name,func.name)]}\n"
            t += f"sw $a0, {g.type_and_member_to_offset[(type.name,func.name)]}($v0)\n"

        t += "lw $a0, _fl0\n"#HACK
        t += f"sw $a0, {g.type_and_member_to_offset[(type.name,'age')]}($v0)\n"#HACK (initializer will be here LOL)
        
        t += "j $ra\n"

        #Methods
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

def __expression_to_MIPS(expr_node, g: Globals, is_result_used, c: Context):
    t = ""
    
    if isinstance(expr_node, ASSEMBLY_INSERT):
        t += expr_node.ass
    
    elif isinstance(expr_node, Expression_Block):
        for i in range(len(expr_node.expressions)):
            t += __expression_to_MIPS(expr_node.expressions[i], g, ((i==len(expr_node.expressions)-1) and is_result_used), c)
    
    elif isinstance(expr_node, Dot_Operator):
        t += __expression_to_MIPS(expr_node.left, g, True, c)
        t += c.pop_to("$a0")
        
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
    
    elif isinstance(expr_node, New): #TODO: refactorize somehow???
        t += c.push_from("$fp")
        t += c.push_from("$ra")
        
        for i in range(0, len(expr_node.arguments)):
            t += __expression_to_MIPS(expr_node.arguments[i], g, True, c)

        t += f"\njal _func{g.type_to_constructor[expr_node.type_name]}\n"
        
        for i in range(0, len(expr_node.arguments)):
            t += c.pop_to("$a3")

        t += c.pop_to("$ra")
        t += c.pop_to("$fp")

        if is_result_used:
            t += c.push_from("$v0")

    elif isinstance(expr_node, Variable_Declarations):
        for name, value in zip(expr_node.names, expr_node.values):
            t += __expression_to_MIPS(value, g, True, c)
            if name in c.local_variables:
                c.local_variables[name].append(c.sp_offset)
            else:
                c.local_variables[name] = [c.sp_offset]
        
        t += __expression_to_MIPS(expr_node.body, g, is_result_used, c)
        if is_result_used:
            t += c.pop_to("$v0")
        
        for name in expr_node.names:
            c.local_variables[name].pop()
            if c.local_variables[name] == []:
                del c.local_variables[name]
            c.pop_to("$a0")

        if is_result_used:
            t += c.push_from("$v0")

    elif isinstance(expr_node, Variable_Destructive_Assignment): #TODO: array
        t += __expression_to_MIPS(expr_node.expression, g, True, c)
        t += c.pop_to("$v0")
        
        if expr_node.selfDotType != None:
            offset_from_fp = c.local_variables["self"][-1]
            offset_from_object_base = g.type_and_member_to_offset[(expr_node.selfDotType.name, expr_node.var_name)]
            t += f"\nlw $a0, {offset_from_fp}($fp)\n"
            t += f"sw $v0, {offset_from_object_base}($a0)\n"
        else:
            offset_from_fp = c.local_variables[expr_node.var_name][-1]
            t += f"\nsw $v0, {offset_from_fp}($fp)\n"

        if is_result_used:
            t += c.push_from("$v0")

    elif isinstance(expr_node, While):
        while_num = g.next_while_id
        g.next_while_id += 1
        
        if is_result_used:
            t += "la $a0, _fl0\n" #BUG?????????? (maybe lw?)
            t += c.push_from("$a0") #Push default value @@@TODO: handle non_float returns... (wait for semmantic checker)
        
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
        
        #Evaluate left and right and pop its values
        t += __expression_to_MIPS(expr_node.left, g, True, c)
        t += __expression_to_MIPS(expr_node.right, g, True, c)
        
        if expr_node.operator_type in ["+", "-", "*", "/", "^"]: #@@TODO: this is a hack. Wait for Semmantic Checker...
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
            
            #Push result
            if is_result_used:
                t += c.push_from("$f3")
        
        elif expr_node.operator_type in ["&", "|"]: #@@TODO: this is a hack. Wait for Semmantic Checker...
            t += c.pop_to("$a1")
            t += c.pop_to("$a0")
            
            if expr_node.operator_type == "&":
                t += "and $a2, $a0, $a1\n"
            elif expr_node.operator_type == "|":
                t += "or $a2, $a0, $a1\n"

            if is_result_used:
                t += c.push_from("$a2")
        
        elif expr_node.operator_type == "@": #TODO: llevar de numero a string implicitamente
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
            if expr_node.type == "string":
                pass #TODO: string compare
            else:
                t += c.pop_to("$a1")
                t += c.pop_to("$a0")

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

    elif isinstance(expr_node, Literal):
        if is_result_used:
            if expr_node.value == True: #@@TODO: this is a hack? Wait for Semmantic Checker...
                t += "ori $a0, $0, 1\n"
                t += c.push_from("$a0")
            elif expr_node.value == False:
                t += "ori $a0, $0, 0\n"
                t += c.push_from("$a0")
            elif type(expr_node.value) is str:
                g.data_segment += f"_str{g.next_str_id}: .asciiz \"{str(expr_node.value)}\"\n" #Add float constant to data segment
                t += f"\nla $a0, _str{g.next_str_id}\n"
                t += c.push_from("$a0")
                g.next_str_id += 1
            else:
                g.data_segment += f"_fl{g.next_float_id}: .float {float(expr_node.value)}\n" #Add float constant to data segment
                t += f"\nl.s $f1, _fl{g.next_float_id}\n"
                t += c.push_from("$f1")
                g.next_float_id += 1
    
    return t