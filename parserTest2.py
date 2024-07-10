import ply.lex as lex
import tokrules
from tokrules import tokens
from ply import yacc
from AST_Nodes import *
lexer = lex.lex(module=tokrules)

sErrorList = []

precedence = (
    # ("right", "PRINT","SQRT","SIN","COS","EXP","LOG","RAND"),
    ("right", "LET", "IN"),
    ("right", "IF", "ELIF", "ELSE"),
    ("right", "WHILE", "FOR"),
    ("nonassoc", "ASIGN"),
    ("right", "DESTRUCTASIGN"),
    ("left", "AS"),
    ("left", "IS"),
    ("left", "CONCAT", "DOUBLECONCAT"),
    ("left", "OR"),
    ("left", "AND"),
    ("left", "EQUAL", "DIFFERENT"),
    ("nonassoc", "MINOREQUAL", "MAJOREQUAL", "MINOR", "MAJOR"),
    ("right", "NOT"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MODULE"),
    ("right", "POWER"),
    ("right", "UMINUS"),
    ("right", "LPAREN", "RPAREN"),
    ("nonassoc", "ID"),
    ("left", "DOT"),
)


def p_empty(p):
    "empty :"
    pass


def p_type_of(p):
    "type_of : DOUBLEDOTS args"
    p[0] = p[2]


def p_type_of_empty(p):
    "type_of : empty"
    p[0] = ""


def p_id(p):
    "id : ID type_of"
    p[0] = Identifier(p[1], p[2])


def p_program(p):
    "program : functions_types_protocols global_high_level_expression"
    functions = []
    types = []
    protocols = []
    for item in p[1]:
        if isinstance(item, Function_Definition):
            functions.append(item)
        elif isinstance(item, Type_Definition):
            types.append(item)
        elif isinstance(item, Protocol_Definition):
            protocols.append(item)
    p[0] = Program_Root(functions, types, protocols, p[2])


def p_global_high_level_expression(p):
    "global_high_level_expression : high_level_expression"
    p[0] = p[1]


def p_global_high_level_expression_e(p):
    "global_high_level_expression : empty"
    p[0] = None


def p_functions_types_protocols_list_items(p):
    """functions_types_protocols : function_definition functions_types_protocols
    | type_def functions_types_protocols
    | protocol_definition functions_types_protocols
    """
    p[0] = [p[1]] + p[2]


def p_function_type_list_items_empty(p):
    "functions_types_protocols : empty"
    p[0] = []


def p_protocol(p):
    "protocol_definition : PROTOCOL ID opt_extends LBRACE protocol_methods RBRACE optional_semicolon"
    methodsNames = []
    methodsTypes = []
    for item in p[5]:
        methodsNames.append(item.name)
        methodsTypes.append(item.type_name_annotations)
    p[0] = Protocol_Definition(p[2],methodsNames, methodsTypes, p[3].name, p[3].type)


def p_protocol_extends(p):
    "opt_extends : EXTENDS ID"
    p[0] = Identifier(p[2])


def p_protocol_extends_e(p):
    "opt_extends : empty"
    p[0] = None


def p_protocol_methods(p):
    "protocol_methods : protocol_method protocol_methods"
    p[0] = [p[1]] + p[2]


def p_protocol_methods_e(p):
    "protocol_methods : protocol_method empty"
    p[0] = [p[1]]


def p_protocol_method(p):
    "protocol_method : ID LPAREN protocol_methods_arguments RPAREN DOUBLEDOTS args SEMICOLON"
    names = []
    types = []
    for element in p[3]:        
        names.append(element.name)
        types.append(element.type)
    # id = ID(p[1], p[6])
    # params = Params(p[3])
    # for i in p[3]:
    #     i.parent = params
    p[0] = Function_Definition(p[1],names,None,types,p[6])
    # id.parent = p[0]
    # params.parent = p[0]

def p_args(p):
    """
    args : ID
    | OBJECT
    | NUMBERTYPE
    | STRINGTYPE
    | BOOLEANTYPE    
    """
    p[0] = Identifier(p[1])
def p_protocol_methods_arguments(p):
    "protocol_methods_arguments : ID DOUBLEDOTS args protocol_methods_arguments_rem"
    p[0] = [Identifier(p[1], p[3])] + p[4]


def p_protocol_methods_arguments_e(p):
    "protocol_methods_arguments : empty"
    p[0] = []


def p_protocol_methods_arguments_rem(p):
    "protocol_methods_arguments_rem : COMMA ID DOUBLEDOTS args protocol_methods_arguments_rem"
    p[0] = [Identifier(p[2], p[4])] + p[5]


def p_protocol_methods_arguments_rem_e(p):
    "protocol_methods_arguments_rem : empty"
    p[0] = []


def p_exp_func_call(p):
    "expression : func_call_next"
    p[0] = p[1]


def p_func_call(p):
    "func_call_next : ID LPAREN func_call_args RPAREN"
    if p[1] == 'base':
        p[0] = Base_Function_Call(p[3])
    else: p[0] = Function_Call(Identifier(p[1]), p[3])


def p_exp_type_call(p):
    "expression : type_call"
    p[0] = p[1]


def p_type_call(p):
    "type_call : NEW ID LPAREN func_call_args RPAREN"
    p[0] = New(p[2], p[4])


def p_func_call_args(p):
    "func_call_args : func_call_args_list"
    p[0] = p[1]


def p_func_call_args_list(p):
    "func_call_args_list : expression func_call_args_list_rem"
    p[0] = [p[1]] + p[2]


def p_func_call_args_list_e(p):
    "func_call_args_list : empty"
    p[0] = []


def p_func_call_args_list_rem(p):
    "func_call_args_list_rem : COMMA expression func_call_args_list_rem"
    p[0] = [p[2]] + p[3]


def p_func_call_args_list_rem_e(p):
    "func_call_args_list_rem : empty"
    p[0] = []


def p_function_definition(p):
    "function_definition : FUNCTION ID LPAREN func_params RPAREN type_of ARROW high_level_expression"
    # id = ID(p[2], p[6])
    names = []
    types = []
    for item in p[4]:
        names.append(item.name)
        types.append(item.type)
    p[0] = Function_Definition(p[2], names, p[8],types, p[6])


def p_function_definition_fullform(p):
    "function_definition : FUNCTION ID LPAREN func_params RPAREN type_of expression_block optional_semicolon"
    names = []
    types = []
    for item in p[4]:
        names.append(item.name)
        types.append(item.type)
    p[0] = Function_Definition(p[2], names, p[7],types, p[6])


def p_func_params(p):
    "func_params : func_params_list"
    p[0] = p[1]
    # for i in p[1]:
    #     i.parent = p[0]


def p_func_params_list(p):
    "func_params_list : id func_params_list_rem"
    p[0] = [p[1]] + p[2]


def p_func_params_list_e(p):
    "func_params_list : empty"
    p[0] = []


def p_func_params_list_rem(p):
    "func_params_list_rem : COMMA id func_params_list_rem"
    p[0] = [p[2]] + p[3]


def p_func_params_list_rem_e(p):
    "func_params_list_rem : empty"
    p[0] = []


def p_type_def(p):
    "type_def : TYPE ID optional_type_params optional_inheritance LBRACE type_members RBRACE optional_semicolon"
    variable_names = []
    variable_types_anotations = []
    functions = []
    init_expressions = []
    params_names = []
    params_types = []
    for item in p[3]:
        params_names.append(item.name)
        params_types.append(item.type)
    for item in p[6]:
        if isinstance(item, Variable_Declarations):
            variable_names += item.names[0]
            variable_types_anotations += item.type_name_annotations[0]
            init_expressions += item.body
        elif isinstance(item, Function_Definition):
            functions.append(item)
    p[0] = Type_Definition(p[2],variable_names, params_names,init_expressions, functions, p[4][0], p[4][1], variable_types_anotations, params_types)


def p_optional_inheritance(p):
    "optional_inheritance : INHERITS ID optional_inheritance_params"
    p[0] = (p[2], p[3])


def p_optional_inheritance_e(p):
    "optional_inheritance : empty"
    p[0] = None


def p_optional_inheritance_params(p):
    "optional_inheritance_params : LPAREN func_call_args RPAREN"
    p[0] = p[2]


def p_optional_inheritance_params_e(p):
    "optional_inheritance_params : empty"
    p[0] = []


def p_optional_type_params(p):
    "optional_type_params : LPAREN typedef_params RPAREN"
    p[0] = p[2]


def p_optional_type_params_e(p):
    "optional_type_params : empty"
    p[0] = []


def p_typedef_params(p):
    "typedef_params : id typedef_params_rem"
    p[0] = [p[1]] + p[2]


def p_typedef_params_e(p):
    "typedef_params : empty"
    p[0] = []


def p_typedef_params_rem(p):
    "typedef_params_rem : COMMA id typedef_params_rem"
    p[0] = [p[2]] + p[3]


def p_typedef_params_rem_e(p):
    "typedef_params_rem : empty"
    p[0] = []


def p_type_members(p):
    "type_members : type_member type_members"
    p[0] = [p[1]] + p[2]


def p_type_members_e(p):
    "type_members : empty"
    p[0] = []


def p_member_func(p):
    "type_member : member_func"
    p[0] = p[1]


def p_member_function_definition(p):
    "member_func : ID LPAREN func_params RPAREN type_of ARROW high_level_expression"
    names = []
    types = []
    for item in p[3]:
        names.append(item.name)
        types.append(item.type)
    p[0] = Function_Definition(p[1], names, p[7],types, p[5])


def p_member_function_definition_fullform(p):
    "member_func : ID LPAREN func_params RPAREN type_of expression_block optional_semicolon"
    names = []
    types = []
    for item in p[3]:
        names.append(item.name)
        types.append(item.type)
    p[0] = Function_Definition(p[1], names, p[6],types, p[5])


def p_member_var(p):
    "type_member : member_var"
    p[0] = p[1]


def p_member_var_dec(p):
    "member_var : id ASIGN high_level_expression"
    p[0] = Variable_Declarations([p[1]], p[3])
    # p[1].parent = p[0]
    # p[3].parent = p[0]


def p_expression_tbl(p):
    """expression : expression_block"""
    p[0] = p[1]


def p_high_level_expression(p):
    """high_level_expression : expression SEMICOLON
    | expression_block
    """
    p[0] = p[1]


def p_expression_block(p):
    "expression_block : LBRACE expression_block_list RBRACE"
    p[0] = Expression_Block(p[2])
    # for i in p[2]:
    #     i.parent = p[0]


def p_expression_block_list(p):
    "expression_block_list : high_level_expression expression_block_list"
    p[0] = [p[1]] + p[2]


def p_expression_block_list_e(p):
    "expression_block_list : empty"
    p[0] = []


def p_hl_let(p):
    """high_level_expression : LET assign_values IN high_level_expression"""
    p[0] = Variable_Declarations(p[2][0], p[2][1],p[4])
    # for i in p[2]:
    #     i.parent = p[0]
    # p[4].parent = p[0]


def p_let(p):
    """expression : LET assign_values IN expression"""
    p[0] = Variable_Declarations(p[2][0], p[2][1],p[4])
    # for i in p[2]:
    #     i.parent = p[0]
    # p[4].parent = p[0]


def p_assign_values(p):
    """assign_values : id ASIGN expression rem_assignments"""
    # assign = Assign(p[1], p[3])
    # p[1].parent = assign
    # p[3].parent = assign
    p[0] = [p[1]+ p[5][0], [p[3]] + p[5][1]]


def p_rem_assignments(p):
    "rem_assignments : COMMA id ASIGN expression rem_assignments"

    # assign = Assign(p[2], p[4])
    # p[2].parent = assign
    # p[4].parent = assign
    p[0] = [[p[2]]+ p[5][0], [p[4]] + p[5][1]]


def p_rem_assignments_empty(p):
    "rem_assignments : empty"
    p[0] = [[],[]]


def p_if_hl(p):
    "high_level_expression : IF expression_parenthized expression opt_elifs ELSE high_level_expression"
    # first = Case(p[2], p[3], "if")
    # p[2].parent = first
    # p[3].parent = first

    # else_cond = TrueLiteral()
    # last = Case(else_cond, p[6], "else")
    # else_cond.parent = last
    # p[6].parent = last
    opt_elif = p[4]
    while opt_elif.next != []:
        opt_elif = opt_elif.next
    opt_elif.next = p[6]
    p[0] = If(p[2],p[3], p[4])

    # for i in p[0].case_list:
    #     i.parent = p[0]


def p_if_exp(p):
    "expression : IF expression_parenthized expression opt_elifs ELSE expression"
    # first = Case(p[2], p[3], "if")
    # p[2].parent = first
    # p[3].parent = first

    # else_cond = TrueLiteral()
    # last = Case(else_cond, p[6], "else")
    # else_cond.parent = last
    # p[6].parent = last
    opt_elif = p[4]
    while opt_elif.next != []:
        opt_elif = opt_elif.next
    opt_elif.next = p[6]
    p[0] = If(p[2],p[3], p[4])

    # for i in p[0].case_list:
    #     i.parent = p[0]


def p_opt_elifs(p):
    "opt_elifs : ELIF expression_parenthized expression opt_elifs"
    # elif_cond = Case(p[2], p[3], "elif")
    # p[2].parent = elif_cond
    # p[3].parent = elif_cond
    p[0] = If(p[2], p[3], p[4])


def p_opt_elifs_e(p):
    "opt_elifs : empty"
    p[0] = []


def p_optional_semicolon(p):
    """optional_semicolon : SEMICOLON
    | empty"""


def p_for_hl(p):
    "high_level_expression : FOR LPAREN destroyable IN expression RPAREN high_level_expression"
    p[0] = For(p[5],p[3],p[7])


def p_for(p):
    "expression : FOR LPAREN destroyable IN expression RPAREN expression"
    p[0] = For(p[5],p[3],p[7])


def p_while_hl(p):
    "high_level_expression : WHILE expression_parenthized high_level_expression"
    p[0] = While(p[2], p[3])
    # p[2].parent = p[0]
    # p[3].parent = p[0]


def p_while(p):
    "expression : WHILE expression_parenthized expression"
    p[0] = While(p[2], p[3])
    # p[2].parent = p[0]
    # p[3].parent = p[0]


def p_expression_group(p):
    "expression : expression_parenthized"
    p[0] = p[1]


def p_expression_parenthized(p):
    "expression_parenthized : LPAREN expression RPAREN"
    p[0] = p[2]

def p_indexed_destructive_asign(p):
    """indexed_destructive_asign : id LBRAC expression RBRAC 
    | id DOT id LBRAC expression RBRAC"""
    if(p[2]!= "."):
        p[0] = (p[1], p[3], False)
    else:
        p[0] = (p[3], p[5], True)
def p_expression_binop(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression
    | expression POWER expression
    | expression MODULE expression
    | expression CONCAT expression
    | expression DOUBLECONCAT expression
    | expression AND expression
    | expression OR expression
    | expression EQUAL expression
    | expression DIFFERENT expression
    | expression MINOREQUAL expression
    | expression MAJOREQUAL expression
    | expression MINOR expression
    | expression MAJOR expression
    | destroyable DESTRUCTASIGN expression
    | member_resolute DESTRUCTASIGN expression
    | indexed_destructive_asign DESTRUCTASIGN expression
    | expression IS type_test
    | expression AS type_test
    """
    if p[2] == "@@":
        p[0] = Binary_Operator(binary_operators['@'], p[1], Binary_Operator(binary_operators['@'], p[3], " "))
    elif(p[2] == "^"):
        p[0] = Exponentiation_Operator(p[1], p[3])
    elif p[2] == "is":
        p[0] = Is_Operator(p[1],p[3])
    elif p[2] == ":=":
        if isinstance(p[1], Identifier):     
            p[0]=Variable_Destructive_Assignment(p[1],p[3],False, None)
        elif(isinstance(p[1],Dot_Operator)):
            p[0] = Variable_Destructive_Assignment(p[1].right.name, p[3], True, None)     
        else: p[0] = Variable_Destructive_Assignment(p[1][0], p[3], p[1][2], p[1][1])     
    else:
        Binary_Operator(p[2],p[1],p[3])
    
    # if p[2] == ":=":
    #     p[0] = BinOp(left=p[1], op="AD", right=p[3])
    # else:
    #     p[0] = BinOp(left=p[1], op=p[2], right=p[3])

    # p[1].parent = p[0]
    # p[3].parent = p[0]


def p_expression_binop_hl(p):
    """high_level_expression : expression PLUS high_level_expression
    | expression MINUS high_level_expression
    | expression TIMES high_level_expression
    | expression DIVIDE high_level_expression
    | expression POWER high_level_expression
    | expression MODULE high_level_expression
    | expression CONCAT high_level_expression
    | expression DOUBLECONCAT high_level_expression
    | expression AND high_level_expression
    | expression OR high_level_expression
    | expression EQUAL high_level_expression
    | expression DIFFERENT high_level_expression
    | expression MINOREQUAL high_level_expression
    | expression MAJOREQUAL high_level_expression
    | expression MINOR high_level_expression
    | expression MAJOR high_level_expression
    | destroyable DESTRUCTASIGN high_level_expression
    | member_resolute DESTRUCTASIGN high_level_expression
    | indexed_destructive_asign DESTRUCTASIGN expression
    """
    if p[2] == "@@":
        p[0] = Binary_Operator(binary_operators['@'], p[1], Binary_Operator(binary_operators['@'], p[3], " "))
    elif(p[2] == "^"):
        p[0] = Exponentiation_Operator(p[1], p[3])
    elif p[2] == "is":
        p[0] = Is_Operator(p[1],p[3])
    elif p[2] == ":=":
        if isinstance(p[1], Identifier):     
            p[0]=Variable_Destructive_Assignment(p[1],p[3],False, None)
        elif(isinstance(p[1],Dot_Operator)):
            p[0] = Variable_Destructive_Assignment(p[1].right.name, p[3], True, None)     
        else: p[0] = Variable_Destructive_Assignment(p[1][0], p[3], p[1][2], p[1][1])        
    else:
        Binary_Operator(p[2],p[1],p[3])
    # if p[2] == ":=":
    #     p[0] = BinOp(left=p[1], op="AD", right=p[3])
    # else:
    #     p[0] = BinOp(left=p[1], op=p[2], right=p[3])

    # p[0] = BinOp(left=p[1], op=p[2], right=p[3])
    # p[1].parent = p[0]
    # p[3].parent = p[0]


def p_destroyable(p):
    "destroyable : ID"
    p[0] = Identifier(p[1])


def p_type_test(p):
    "type_test : args"
    p[0] = Identifier(p[1])


def p_exp_member_resolute(p):
    "expression : member_resolute"
    p[0] = p[1]


def p_member_resolute(p):
    "member_resolute : id DOT member_resolut"
    if(p[1].name== "self"):
        p[0] = Dot_Operator(p[1], p[3])
    else:
        raise Exception("It is no possible to apply a destructive asignment on a private member")



def p_member_resolut_att(p):
    "member_resolut : ID"
    p[0] = Identifier(p[1])


def p_expression_unary(p):
    """expression : NOT expression
    | MINUS expression %prec UMINUS"""
    p[0] = Unary_Operator(p[1], p[2])
    # p[2].parent = p[0]


def p_expression_unary_hl(p):
    """high_level_expression : NOT high_level_expression
    | MINUS high_level_expression %prec UMINUS"""
    p[0] = Unary_Operator(p[1], p[2])
    # p[2].parent = p[0]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = Literal(p[1])


def p_expression_string(p):
    "expression : STRING"
    p[0] = Literal(p[1])


def p_expression_variable(p):
    "expression : ID"
    p[0] = Identifier(p[1])


def p_expression_vector(p):
    "expression : vector"
    p[0] = p[1]


def p_vector_ext(p):
    "vector : LBRAC func_call_args RBRAC"
    p[0] = Array_Literal(p[2])
    # p[2].parent = p[0]


def p_vector_int(p):
    "vector : LBRAC expression GENERATOR destroyable IN expression RBRAC"
    p[0] = Array_Implicit_Declaration(p[3], p[5], p[7])


def p_expression_vector_ind_pare(p):
    "expression :  expression LBRAC expression RBRAC"
    p[0] = Index_Operator(p[1], Index_Expression_With_ABC(p[3],p[1]))
    # p[1].parent = p[0]
    # p[3].parent = p[0]


def p_expression_pi(p):
    "expression : PI"
    p[0] = Literal(builtin_numerical_constants['PI'])


def p_expression_e(p):
    "expression : E"
    p[0] = Literal(builtin_numerical_constants['E'])


def p_expression_true(p):
    "expression : TRUE"
    p[0] = Literal(True)


def p_expression_false(p):
    "expression : FALSE"
    p[0] = Literal(False)


def p_expression_print(p):
    "expression : PRINT LPAREN expression RPAREN"
    p[0] = Function_Call(Identifier("print"), [p[3]])
    # p[3].parent = p[0]

def p_expression_range(p):
    """
    expression : RANGE LPAREN expression RPAREN
    | RANGE LPAREN expression COMMA expression RPAREN    
    """
    p[0] = Function_Call(Identifier("range"), p[3])


def p_expression_sqrt(p):
    "expression : SQRT LPAREN expression RPAREN"
    p[0] = Function_Call(Identifier("sqrt"), [p[3]])
    # p[3].parent = p[0]


def p_expression_sin(p):
    "expression : SIN LPAREN expression RPAREN"
    p[0] = Function_Call(Identifier("sin"), [p[3]])
    # p[3].parent = p[0]


def p_expression_cos(p):
    "expression : COS LPAREN expression RPAREN"
    p[0] = Function_Call(Identifier("cos"), [p[3]])
    # p[3].parent = p[0]


def p_expression_exp(p):
    "expression : EXP LPAREN expression RPAREN"
    p[0] = Function_Call(Identifier("exp"), [p[3]])
    # p[3].parent = p[0]


def p_expression_log(p):
    "expression : LOG LPAREN expression COMMA expression RPAREN"
    p[0] = Function_Call(Identifier("log"), [p[3], p[5]])
    # p[3].parent = p[0]
    # p[5].parent = p[0]


def p_expression_rand(p):
    "expression : RAND LPAREN RPAREN"
    p[0] = Function_Call(Identifier("rand"), [])


def p_error(p):
    sErrorList.append(p)
    print("Error!")
    print(p)
    # print(sErrorList[-1])


parser = yacc.yacc(start="program", method="LALR")
while True:
    code = input("calc > ")
    if not code:
        break
    print(parser.parse(code, lexer=lexer))
    