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

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for declaration in node.declarations:
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