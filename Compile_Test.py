from AST_Nodes import *
import subprocess
from Code_Generation import *
from Default_Functions_and_Types import default_funcs, default_types
funcs = default_funcs
types = default_types

tpy0_f1 = Function_Definition("print_name", [], Function_Call(Identifier("print_str"), [Binary_Operator("@", Literal("miau jau muu "), Dot_Operator(Identifier("self", Basic_or_Composite_Type("Animal", None)), Identifier("name")))]))
tpy0_f2 = Function_Definition("set_fuerza", ["F"], Variable_Destructive_Assignment("fuerza_de_patica_principal", Identifier("F"), True, None, Basic_or_Composite_Type("Animal", None)))
tpy0_f3 = Function_Definition("print_fuerza", [], Function_Call(Identifier("print_flt"), [Dot_Operator(Identifier("self", Basic_or_Composite_Type("Animal", None)), Identifier("fuerza_de_patica_principal"), False)]))
tpy0 = Type_Definition("Animal", ["name", "patas", "fuerza_de_patica_principal"], ["name", "patas_minus_two"],
       [Identifier("name"), Binary_Operator("+", Identifier("patas_minus_two"), Literal(2)), Literal(8)], 
       [tpy0_f1, tpy0_f2, tpy0_f3], None)

types.append(tpy0)

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

types.append(tpy1)

fnc1 = Function_Definition("print_pepe", ["job", "age"], Expression_Block([
    Variable_Declarations(["x"], [New("Persona", [Literal(10), Literal("pescado")])], Expression_Block([
        Function_Call(Identifier("print_flt"), [Identifier("age")]),
        Function_Call(Identifier("print_str"), [Literal("\n")]),
        Function_Call(Identifier("print_str"), [Identifier("job")]),
        Function_Call(Identifier("print_str"), [Literal("\n")]),
    ])),
    Literal(2),
]))
funcs.append(fnc1)

epr = Variable_Declarations(["x"], [New("Persona", [Literal(10), Literal("pescado")])], Expression_Block([
    Function_Call(Identifier("print_pepe"), [Literal("non"), Literal(3)]),
    Function_Call(Identifier("print"), [Literal(False, Basic_or_Composite_Type(BOOL_TYPE_NAME, None))]),
    Function_Call(Dot_Operator(Identifier("x", Basic_or_Composite_Type("Persona", tpy1)), Identifier("print_name"), True), []),
    Function_Call(Dot_Operator(Identifier("x", Basic_or_Composite_Type("Persona", tpy1)), Identifier("set_fuerza"), True), [Literal(7)]),
]))


file = open("./compiled.asm", mode = "w")
file.write(program_to_MIPS(epr, funcs, types))
file.close()
subprocess.run("qtspim -f compiled.asm")
