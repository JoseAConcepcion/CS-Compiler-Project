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

    @visitor.when(nodes.Program_Root)
    def visit(self, node: nodes.Program_Root):
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
        range_type = self.context.create_type('Range')
        range_type.set_parent(object_type)

        # todo Iterables

        for types in node.type_list:
            self.visit(types)
        for functions in node.func_list:
            self.visit(functions)
        for protocols in node.protocol_list:
            self.visit(protocols)

        return self.context, self.errors

    @visitor.when(nodes.Type_Definition)
    def visit(self, node: nodes.Type_Definition):
        try:
            self.context.create_type(node.name, node)
        except SemanticError as e:
            self.errors.append(e)
            if node.type in self.context.types:
                self.context.types[node.name] = ErrorType()
            else:
                self.errors.append(SemanticError(f"Type {node.name} already exists")) #, node.line, node.column handle later
            
           
    @visitor.when(nodes.Function_Definition)
    def visit(self, node: nodes.Function_Definition):
        try:
            self.context.create_function(node.name, node)
        except SemanticError as e:
            self.errors.append(e)
            if node.name in self.context.functions:
                self.context.functions[node.name] = ErrorType()
            else:    
                self.errors.append(SemanticError(f"Function {node.name} already exists"))

    @visitor.when(nodes.Protocol_Definition)
    def visit(self, node: nodes.Protocol_Definition):
        try:
            self.context.create_protocol(node.name, node)
        except SemanticError as e:
            self.errors.append(e)
            if node.name in self.context.protocols:
                self.context.protocols[node.name] = ErrorType()
            else:    
                self.errors.append(SemanticError(f"Protocol {node.name} already exists"))
            
