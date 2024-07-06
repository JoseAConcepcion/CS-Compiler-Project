from typing import List

###--- Types --###
class Type:
    pass

basic_types = ["float", "string", "bool", "object"]
class Basic_or_Composite_Type(Type):
    def __init__(self, name: str, definition): #definition: Type_Definition (para float, string, bool y object esta definicion es = None)
        self.name = name
        self.definition = definition

class Array_Type(Type):
    def __init__(self, undelying_type: Basic_or_Composite_Type):
        self.undelying_type = undelying_type

###--- Expressions ---###
class Expression:
    type: Type = None #@Semantic

class ASSEMBLY_INSERT(Expression):
    def __init__(self, ass):
        self.ass = ass

builtin_numerical_constants = {"PI": 3.14, "E": 2.71}
class Literal(Expression):
    def __init__(self, value):
        self.value = value

class Identifier(Expression):
    def __init__(self, name: str, type = None): #TODO: quitar el = None?
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
    "&", "|", "[]"]
class Binary_Operator(Expression):
    def __init__(self, operator_type, left: Expression, right: Expression):
        self.left = left
        self.right = right
        self.operator_type = operator_type

class Dot_Operator(Expression):
    def __init__(self, left: Expression, right: Identifier, right_is_function_name: bool):
        self.left = left
        self.right = right
        self.right_is_function_name = right_is_function_name

unary_operators = ["-", "!", ]
class Unary_Operator(Expression):
    def __init__(self, operator_type: str, operand: Expression):
        self.operand = operand
        self.operator_type = operator_type

class Expression_Block(Expression):
    def __init__(self, expressions: List[Expression]):
        self.expressions = expressions

class Function_Definition(Expression):
    def __init__(self, name: str, argument_names: List[str], body: Expression): #TODO: add "argument_types" argument or something like that
        self.name = name
        self.argument_names = argument_names
        self.body = body

class Variable_Declarations(Expression):
    def __init__(self, names: List[str], values: List[Expression], body: Expression):
        self.names = names
        self.values = values
        self.body = body

class Variable_Destructive_Assignment(Expression):
    def __init__(self, var_name: str, expression: Expression, selfDotType: Type): #si selfDotType = None, entonces la asignacion es a una variable local.
        self.var_name = var_name
        self.expression = expression
        self.selfDotType = selfDotType

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
    def __init__(self, name: str, variable_names: List[str], initializer_parameters: List[str], initializer_expressions: List[Expression], functions: List[Function_Definition], parent): 
        #TODO: initializer parameter types + parent_initializer_paramenters?
        self.name = name
        self.variable_names = variable_names
        self.initializer_parameters = initializer_parameters
        self.initializer_expressions = initializer_expressions
        self.functions = functions
        self.parent = parent

class New(Expression):
    def __init__(self, type_name: str, arguments: List[Expression]):
        self.type_name = type_name
        self.arguments = arguments

class Protocol(Expression): #TODO
    def __init__(self, name: str):
        pass

#class VectorImplicitDeclaration... tampoco existe, transpila a for o algo deso...???
