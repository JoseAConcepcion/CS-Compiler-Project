from cmp.semantic import *
from cmp.visitor import visitor
from AST_Nodes import *
from hulk_errors import *


class TypeBuilder:
    def __init__(self, context, errors=None):
        self.context: Context = context
        self.errors: list = [] if errors is None else errors
        self.current_type = None

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(Program_Root)
    def visit(self, node: Program_Root):
        for declaration in node.main_expression:
            self.visit(declaration)

    @visitor.when(Type_Definition)
    def visit(self, node: Type_Definition):
        try:
            self.current_type = self.context.get_type(node.name)
        except SemanticError as error:
            self.errors.append(SemanticError(error, node))
            self.current_type = ErrorType()

        self.current_type.param_names, self.current_type.param_types = (
            self.param_names_and_types(node)
        )
    
    def param_names_and_types(self, node):
        param_names = []
        param_types = []
        for name, type_name in zip(node.initializer_parameters, node.initializers_type_name_annotations):
            param_names.append(name)
            param_types.append(self.context.get_type(type_name))
        return param_names, param_types