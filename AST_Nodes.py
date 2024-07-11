from typing import List

###--- Types --###
class Type:
    pass

STRING_TYPE_NAME = "string"
FLOAT_TYPE_NAME = "float"
BOOL_TYPE_NAME = "bool"
OBJECT_TYPE_NAME = "object"
basic_types = [FLOAT_TYPE_NAME, STRING_TYPE_NAME, BOOL_TYPE_NAME, OBJECT_TYPE_NAME]
class Basic_or_Composite_Type(Type):
    def __init__(self, name: str, definition): #definition: Type_Definition or Protocol_Definition (para float, string, bool y object esta definicion es = None)
        self.name = name
        self.definition = definition

class Array_Type(Type):
    def __init__(self, undelying_type: Basic_or_Composite_Type):
        self.undelying_type = undelying_type

###--- Expressions ---###
class Expression:
    type: Type = None #SIEMPRE se llena en el semmantic checker, para todo 

class ASSEMBLY_INSERT(Expression):
    def __init__(self, ass):
        self.ass = ass

builtin_numerical_constants = {"PI": 3.14, "E": 2.71}
class Literal(Expression):
    def __init__(self, value, type = None):
        self.value = value
        self.type = type

class Array_Literal(Expression):
    def __init__(self, expressions: List[Expression], type = Array_Type(None)):
        self.expressions = expressions
        self.type = type

class Identifier(Expression):
    def __init__(self, name: str, type = None):
        self.name = name
        self.type = type

builtin_func_names = ["print", "sqrt", "sin", "cos", "exp", "log", "rand"]
class Function_Call(Expression):
    def __init__(self, name: Expression, arguments: List[Expression]):
        self.name = name
        self.arguments = arguments

class Base_Function_Call(Expression):
    def __init__(self, arguments: List[Expression], ancestor_name: str = None, func_name: str = None): #ancestor_name es el nombre del tipo ancestro que tiene la funcion a la que se esta llamando con base
        self.arguments = arguments

        self.ancestor_name = ancestor_name
        self.func_name = func_name

binary_operators = [
    "+", "-", "*", "/", "@"
    "<", ">", "<=", ">=", "==", "!=",
    "&", "|"]
class Binary_Operator(Expression):
    def __init__(self, operator_type, left: Expression, right: Expression, type = None):
        self.left = left
        self.right = right
        self.operator_type = operator_type
        self.type = type

def Exponentiation_Operator(left: Expression, right: Expression):
    return Function_Call(Identifier("exp"), [Binary_Operator("*", right, Function_Call(Identifier("log_e"), [left]))])

class Dot_Operator(Expression):
    def __init__(self, left: Expression, right: Identifier, right_is_function_name: bool = False, type: Type = None): #right_is_function_name se llena en el semmantic checker realmente
        self.left = left
        self.right = right
        self.right_is_function_name = right_is_function_name
        self.type = type

class Index_Operator(Expression):
    def __init__(self, array_reference: Expression, index: Expression, type = None):
        self.array_reference = array_reference
        self.index = index
        self.type = type

def Print_Error_and_Exit(message: str):
    return Expression_Block([
        Function_Call(Identifier("print_str"), [Literal(message)]), 
        ASSEMBLY_INSERT("ori $2, $0, 10\nsyscall\n") #EXIT
    ])

def Index_Expression_With_ABC(index: Expression, array_reference: Expression) -> Expression: #Wrapper, para checkear que el indice sea valido, en tiempo de ejecucion.
    return Variable_Declarations([".index"], [index], Expression_Block([
        If(  Binary_Operator("|",   Binary_Operator(">=", Identifier(".index"), Dot_Operator(array_reference, Identifier("length"))),   Binary_Operator("<", Identifier(".index"), Literal(0))), 
            Expression_Block([Print_Error_and_Exit("Array Bounds Check Failed!!!! Exiting program..."), Literal(True)]), If(
                Literal(True), Literal(False), None
            )
        ),
        Identifier(".index")
    ]))

class Is_Operator(Expression):
    def __init__(self, left: Expression, right: Identifier):
        self.left = left
        self.right = right
        self.type = Basic_or_Composite_Type(BOOL_TYPE_NAME, None)

class As_Keyword(Expression):
    def __init__(self, left: Expression, right: Identifier, type_of_right: Type = None):
        self.left = left
        self.right = right
        self.type = type_of_right

def As_Operator(left: Expression, right: Identifier, type_of_right: Type = None):
    return If(Is_Operator(left, right), As_Keyword(left, right, type_of_right), If(Literal(True), 
    Expression_Block([
        Print_Error_and_Exit("You tried to convert between incompatible types!!!! Exiting program...")
    ]), None, type_of_right), type_of_right)

unary_operators = ["-", "!", ]
class Unary_Operator(Expression):
    def __init__(self, operator_type: str, operand: Expression):
        self.operand = operand
        self.operator_type = operator_type

class Expression_Block(Expression):
    def __init__(self, expressions: List[Expression]):
        self.expressions = expressions

class Function_Definition(Expression):
    def __init__(self, name: str, argument_names: List[str], body: Expression, type_name_annotations: List[str] = [], return_type_annotation: str = ""): #type_name_annotations[x] = None si no se anotó ese argumento
        self.name = name
        self.argument_names = argument_names
        self.body = body

        self.argument_type_annotations = type_name_annotations
        self.return_type_annotation = return_type_annotation

class Variable_Declarations(Expression):
    def __init__(self, names: List[str], values: List[Expression], body: Expression, type_name_annotations: List[str] = []): #type_name_annotations[x] = None si no se anotó esa variable
        self.names = names
        self.values = values
        self.body = body

        self.type_name_annotations = type_name_annotations

class Variable_Destructive_Assignment(Expression):
    def __init__(self, var_name: str, expression: Expression, is_self_dot: bool, indexExpression: Expression, selfDotType: Type = None): #Si selfDotType = None, entonces la asignacion es a una variable local. Analogamente, si indexExpression = None, no es una asignacion a un elemento de un array
        self.var_name = var_name
        self.expression = expression
        self.selfDotType = selfDotType
        self.is_self_dot = is_self_dot
        self.indexExpression = indexExpression

class If(Expression): 
    def __init__(self, condition: Expression, body: Expression, next, type = None):
        self.condition = condition
        self.body = body
        self.next = next
        self.type = type

# class Else... no hay, es un if(True) con next = None

class While(Expression):
    def __init__(self, condition: Expression, body: Expression):
        self.condition = condition
        self.body = body

def For(iterable: Expression, variable_name: str, body: Expression):
    return Variable_Declarations([".it"], [iterable], While(Function_Call(Dot_Operator(Identifier(".it"), Identifier("next"), True), []), 
        Variable_Declarations([variable_name], [Function_Call(Dot_Operator(Identifier(".it"), Identifier("current"), True), [])], body)
    ), ["Iterable"])

class Type_Definition(Expression):
    def __init__(self, name: str, variable_names: List[str], initializer_parameters: List[str], 
                 initializer_expressions: List[Expression], functions: List[Function_Definition], parent_name: str, 
                 parent_initializer_expressions: List[Expression] = None, 
                 variable_type_name_annotations: List[str] = [], initializers_type_name_annotations: List[str] = []): 
        self.name = name
        self.variable_names = variable_names
        self.initializer_parameters = initializer_parameters
        self.initializer_expressions = initializer_expressions
        self.functions = functions
        self.parent_name = parent_name
        self.parent_initializer_expressions = parent_initializer_expressions
        self.variable_type_name_annotations = variable_type_name_annotations
        self.initializers_type_name_annotations = initializers_type_name_annotations

        self.initializer_parameter_types = []
        self.variable_parameter_types = []
        self.parent: Type_Definition = None
        self.inhereted_functions = []

class New(Expression):
    def __init__(self, type_name: str, arguments: List[Expression]):
        self.type_name = type_name
        self.arguments = arguments

class Protocol_Definition(Expression):
    def __init__(self, name: str, func_names: List[str], func_parameter_type_names: List[List[str]], func_return_type_names: List[str], parent_name: str):
        self.name = name
        self.func_names = func_names
        self.func_parameter_type_names = func_parameter_type_names
        self.func_return_type_names = func_return_type_names
        self.parent_name = parent_name

        self.func_parameter_types = []

def Array_Implicit_Declaration(expr: Expression, var: Identifier, iterable: Expression) -> Expression:
    return Array_Literal([Literal(42), Literal(73), Literal(13), Literal(5)]) #TODO

class Program_Root:
    def __init__(self, func_list: List[Function_Definition], type_list: List[Type_Definition], protocol_list: List[Protocol_Definition], 
                 main_expression: Expression):
        self.func_list = func_list
        self.type_list = type_list
        self.protocol_list = protocol_list
        self.main_expression = main_expression