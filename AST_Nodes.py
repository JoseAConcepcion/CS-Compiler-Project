from typing import List

###--- Types --###
class Type:
    pass

basic_types = ["float", "string", "bool", "object"]
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

class Array_Literal(Expression):#TODO
    def __init__(self, expressions: List[Expression], type = None):
        self.expressions = expressions

class Identifier(Expression):
    def __init__(self, name: str, type = None):
        self.name = name
        self.type = type

builtin_func_names = ["print", "sqrt", "sin", "cos", "exp", "log", "rand"]
class Function_Call(Expression):
    def __init__(self, name: Expression, arguments: List[Expression]):
        self.name = name
        self.arguments = arguments

binary_operators = [
    "+", "-", "*", "/", "^", "@"
    "<", ">", "<=", ">=", "==", "!=",
    "&", "|"]
class Binary_Operator(Expression):
    def __init__(self, operator_type, left: Expression, right: Expression, type = None):
        self.left = left
        self.right = right
        self.operator_type = operator_type
        self.type = type

class Dot_Operator(Expression):
    def __init__(self, left: Expression, right: Identifier, right_is_function_name: bool = False): #right_is_function_name se llena en el semmantic checker realmente
        self.left = left
        self.right = right
        self.right_is_function_name = right_is_function_name

class Index_Operator(Expression):
    def __init__(self, array_reference: Expression, index: Expression, type = None):
        self.array_reference = array_reference
        self.index = index
        self.type = type

def Print_Error_and_Exit(message: str):
    return Expression_Block([
        Function_Call(Identifier("print_str"), [Literal(message)]), 
        ASSEMBLY_INSERT("ori $2, $0, 10\nsyscall") #EXIT
    ])

def Index_Expression_With_ABC(index: Expression, array_reference: Expression) -> Expression: #Wrapper, para checkear que el indice sea valido, en tiempo de ejecucion.
    return Expression_Block([
        If(  Binary_Operator("|",   Binary_Operator(">=", index, Dot_Operator(array_reference, Identifier("length"))),   Binary_Operator("<", index, Literal(0))), 
            Expression_Block([Print_Error_and_Exit("Array Bounds Check Failed!!!! Exiting program..."), Literal(True)]), If(
                Literal(True), Literal(False), None
            )
        ),
        index
    ])

class Is_Operator(Expression):
    def __init__(self, left: Expression, right: Identifier):
        self.left = left
        self.right = right

        self.right_definition = None

unary_operators = ["-", "!", ]
class Unary_Operator(Expression):
    def __init__(self, operator_type: str, operand: Expression):
        self.operand = operand
        self.operator_type = operator_type

class Expression_Block(Expression):
    def __init__(self, expressions: List[Expression]):
        self.expressions = expressions

class Function_Definition(Expression):
    def __init__(self, name: str, argument_names: List[str], body: Expression, type_name_annotations: List[str] = []): #type_name_annotations[x] = None si no se anotó ese argumento
        self.name = name
        self.argument_names = argument_names
        self.body = body

        self.argument_type_annotations = type_name_annotations

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
    def __init__(self, condition: Expression, body: Expression, next):
        self.condition = condition
        self.body = body
        self.next = next

# class Else... no hay, es un if(True) con next = None

class While(Expression):
    def __init__(self, condition: Expression, body: Expression):
        self.condition = condition
        self.body = body

#class For... no hay, transpila a una combinacion de Variable_Declarations y While

class Type_Definition(Expression):
    def __init__(self, name: str, variable_names: List[str], initializer_parameters: List[str], 
                 initializer_expressions: List[Expression], functions: List[Function_Definition], parent_name: str, 
                 parent_initializer_expressions: List[Expression] = None): 
        self.name = name
        self.variable_names = variable_names
        self.initializer_parameters = initializer_parameters
        self.initializer_expressions = initializer_expressions
        self.functions = functions
        self.parent_name = parent_name
        self.parent_initializer_expressions = parent_initializer_expressions

        self.initializer_parameter_types = []
        self.parent = None

class New(Expression):
    def __init__(self, type_name: str, arguments: List[Expression]):
        self.type_name = type_name
        self.arguments = arguments

class Protocol_Definition(Expression):
    def __init__(self, name: str, func_names: List[str], func_parameter_type_names: List[List[str]]):
        self.name = name
        self.func_names = func_names
        self.func_parameter_type_names = func_parameter_type_names

        self.func_parameter_types = []

def Array_Implicit_Declaration(expr: Expression, var: Identifier, iterable: Expression) -> Expression:
    pass #TODO

class Program_Root:
    def __init__(self, func_list: List[Function_Definition], type_list: List[Type_Definition], protocol_list: List[Protocol_Definition], 
                 main_expression: Expression):
        self.func_list = func_list
        self.type_list = type_list
        self.protocol_list = protocol_list
        self.main_expression = main_expression
