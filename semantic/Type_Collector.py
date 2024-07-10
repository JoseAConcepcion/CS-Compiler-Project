from cmp.semantic import *
import cmp.visitor as visitor
import AST_Nodes as nodes
from hulk_errors import SemanticError


#Type colecction
class TypeCollector(object):
    def __init__(self):
        self.errors = []
        self.context = None
        
    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(nodes.ProgramNode)
    def visit(self, node: nodes.ProgramNode):
        self.context = Context()

        ### Add the built-in types ###

        # Create the Object type
        object_type = self.context.create_type('Object')

        # Create the Number type
        number_type = self.context.create_type('Number')
        number_type.set_parent(object_type)

        # Create the Boolean type
        bool_type = self.context.create_type('Boolean')
        bool_type.set_parent(object_type)

        # Create the String type
        string_type = self.context.create_type('String')
        string_type.set_parent(object_type)


        ### Add the built-in functions ###
        self.context.create_function('print', ['value'], [object_type], string_type)
        self.context.create_function('sqrt', ['value'], [number_type], number_type)
        self.context.create_function('sin', ['angle'], [number_type], number_type)
        self.context.create_function('cos', ['angle'], [number_type], number_type)
        self.context.create_function('exp', ['value'], [number_type], number_type)
        self.context.create_function('log', ['value'], [number_type], number_type)
        self.context.create_function('rand', [], [], number_type)
        self.context.create_function('parse', ['value'], [string_type], number_type)


        # Create protocols
        self.context.create_protocol('Protocol')

        
        # Create range
        range_type = self.context.create_range('Range')
        range_type.set_parent(object_type)

        for declaration in node.declarations:
            self.visit(declaration)

        return self.context, self.errors

    @visitor.when(nodes.Type_Definition)
    def visit(self, node: nodes.Type_Definition):
        try:
            self.context.create_type(node.name, node)
        except SemanticError as e:
           self.errors.append(e)

    @visitor.when(nodes.Protocol_Definition)
    def visit(self, node: nodes.Protocol_Definition):
        try:
            self.context.create_protocol(node.name, node)
        except SemanticError as e:
            self.errors.append(e)
