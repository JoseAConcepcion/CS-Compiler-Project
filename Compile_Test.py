from AST_Nodes import *
import subprocess
from Code_Generation import *
from Default_Functions_and_Types import default_funcs, default_types
funcs = default_funcs
types = default_types
protocols = []

tpy2_f1 = Function_Definition("print_tipo", [], Function_Call(Identifier("print_str"), [Dot_Operator(Identifier("self", Basic_or_Composite_Type("Cosa", None)), Identifier("tipo"))]))
tpy2 = Type_Definition("Cosa", ["tipo"], ["tipo"],
       [Identifier("tipo")], 
       [tpy2_f1], None)

#types.append(tpy2)

tpy0_f1 = Function_Definition("print_name", [], Function_Call(Identifier("print_str"), [Binary_Operator("@", Literal("miau jau muu "), Dot_Operator(Identifier("self", Basic_or_Composite_Type("Animal", None)), Identifier("name")))]))
tpy0_f2 = Function_Definition("set_fuerza", ["F"], Variable_Destructive_Assignment("fuerza_de_patica_principal", Identifier("F"), True, None, Basic_or_Composite_Type("Animal", None)))
tpy0_f3 = Function_Definition("print_fuerza", [], Function_Call(Identifier("print_flt"), [Dot_Operator(Identifier("self", Basic_or_Composite_Type("Animal", None)), Identifier("fuerza_de_patica_principal"), False)]))
tpy0 = Type_Definition("Animal", ["name", "patas", "fuerza_de_patica_principal"], ["name", "patas_minus_two"],
       [Identifier("name"), Binary_Operator("+", Identifier("patas_minus_two"), Literal(2)), Literal(8)], 
       [tpy0_f1, tpy0_f2, tpy0_f3], "Cosa", [Literal("pelo")])
tpy0.parent = tpy2

#types.append(tpy0)

tpy1_f1 = Function_Definition("print_age", [], Function_Call(Identifier("print_flt"), [Dot_Operator(Identifier("self", Basic_or_Composite_Type("Persona", None)), Identifier("age"), False)]))
tpy1_f2 = Function_Definition("set_age", ["age"], Variable_Destructive_Assignment("age", Identifier("age"), True, None, Basic_or_Composite_Type("Persona", None)))
tpy1_f3 = Function_Definition("print_job", [], Function_Call(Identifier("print_str"), [Dot_Operator(Identifier("self", Basic_or_Composite_Type("Persona", None)), Identifier("job"), False)]))
tpy1_f4 = Function_Definition("print_balance1", [], Function_Call(Identifier("print_flt"), [Index_Operator(Dot_Operator(Identifier("self", Basic_or_Composite_Type("Persona", None)), Identifier("bank_balances"), False), Literal(1))]))
tpy1_f5 = Function_Definition("set_balance1", ["b1"], Variable_Destructive_Assignment("bank_balances", Identifier("b1"), True, Literal(1), Basic_or_Composite_Type("Persona", None)))
tpy1_f6 = Function_Definition("print_name", [], Expression_Block([
    Base_Function_Call([], "Animal", "print_name"),
    Function_Call(Identifier("print_str"), [Literal("\n")]),
    Function_Call(Identifier("print_str"), [Binary_Operator("@", Literal("Me llamo "), Dot_Operator(Identifier("self", Basic_or_Composite_Type("Persona", None)), Identifier("job")))])
]))
    
tpy1 = Type_Definition("Persona", ["age", "job", "bank_balances", "name"], ["age", "job"], 
       [Binary_Operator("+", Literal(1), Identifier("age")), Identifier("job"), Array_Literal([Literal(7), Literal(13)]), Literal("Juan")], 
       [tpy1_f1, tpy1_f2, tpy1_f3, tpy1_f4, tpy1_f5, tpy1_f6], "Animal", [Binary_Operator("@", Identifier("job"), Literal("s")), Literal(0)])
tpy1.parent = tpy0

#types.append(tpy1)

fnc1 = Function_Definition("print_pepe", ["job", "age"], Expression_Block([
    Variable_Declarations(["x"], [New("Persona", [Literal(10), Literal("pescado")])], Expression_Block([
        Function_Call(Identifier("print_flt"), [Identifier("age")]),
        Function_Call(Identifier("print_str"), [Literal("\n")]),
        Function_Call(Identifier("print_str"), [Identifier("job")]),
        Function_Call(Identifier("print_str"), [Literal("\n")]),
    ])),
    Literal(2),
]))
#funcs.append(fnc1)

tpy3 = Type_Definition("Nada", [], [],
       [], 
       [], None)
#types.append(tpy3)

prtcl1 = Protocol_Definition("Proto", ["print_name"], [[]], ["String"], None)
#protocols.append(prtcl1)

tpy_range_next = Function_Definition("next", [], Binary_Operator("<", 
    Variable_Destructive_Assignment("currentv", Binary_Operator("+", Dot_Operator(Identifier("self", Basic_or_Composite_Type("Range", None)), Identifier("currentv"), False), Literal(1)), True, None, Basic_or_Composite_Type("Range", None)),
    Dot_Operator(Identifier("self", Basic_or_Composite_Type("Range", None)), Identifier("max"), False)))
tpy_range_current = Function_Definition("current", [], Dot_Operator(Identifier("self", Basic_or_Composite_Type("Range", None)), Identifier("currentv")))
tpy_range = Type_Definition("Range", ["min", "max", "currentv"], ["min", "max"], 
       [Identifier("min"), Identifier("max"), Binary_Operator("-", Identifier("min"), Literal(1))], 
       [tpy_range_next, tpy_range_current], None)
#types.append(tpy_range)

fnc_range = Function_Definition("range", ["min", "max"], New("Range", [Identifier("min") ,Identifier("max")]))
#funcs.append(fnc_range)

epr = Variable_Declarations(["x"], [Array_Literal([Literal(28), Literal(59), Literal(62)])], Expression_Block([
    For(Identifier("x", Array_Type(None)), "i", Expression_Block([
        Function_Call(Identifier("print_flt"), [Identifier("i")]),
        Function_Call(Identifier("print_str"), [Literal("\n")]),
    ]))
]))

file = open("./compiled.asm", mode = "w")
file.write(program_to_MIPS(epr, funcs, types, protocols))
file.close()
subprocess.run("qtspim -f compiled.asm")
