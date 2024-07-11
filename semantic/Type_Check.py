from cmp.visitor import visitor
from cmp.semantic import *
from AST_Nodes import *
from hulk_errors import *

class TypeChecker():
    def __init__(self, context, errors=None):
        self.context : Context = context
        self.errors: list[SemanticError] = [] if errors is None else errors
        self.current_type : Type = None
        self.current_method : Method = None

    @visitor.when(Program_Root)
    def visit(self, node: Program_Root):
        for types in node.type_list:
            self.visit(types)
        for functions in node.func_list:
            self.visit(functions)
        for protocols in node.protocol_list:
            self.visit(protocols)

    @visitor.when(Type_Definition)
    def visit(self, node: Type_Definition):
        self.current_type : Type = self.context.get_type(node.identifier)
        if isinstance(self.current_type, ErrorType):
            return
        
        # visit the