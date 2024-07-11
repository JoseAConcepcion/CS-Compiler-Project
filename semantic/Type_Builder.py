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
        for types in node.type_list:
            self.visit(types)
        for functions in node.function_list:
            self.visit(functions)
        for protocols in node.protocol_list:
            self.visit(protocols)

    @visitor.when(Type_Definition)
    def visit(self, node: Type_Definition):
        try:
            self.current_type = self.context.get_type(node.name)
        except SemanticError as error:
            self.errors.append(SemanticError(error, node))
            self.current_type = ErrorType()

        self.current_type.param_names, self.current_type.param_types = (
            self.param_names_and_types_Type_Definition(node)
        )
        
        #parent can not be number, string or boolean
        if node.parent_name in ["Number", "String", "Boolean"]:
            self.errors.append(SemanticError(f"Type {node.parent_name} can not be a inherited", node))

        elif node.parent_name is not None:
            try:
                parent:Type = self.context.get_type(node.parent_name)
                current = parent
                while current is not None:
                    if current.name == self.current_type.name:
                        self.errors.append(SemanticError(f"Type {node.name} can not be a inherited from itself", node))
                        parent = ErrorType()
                        break
                    current = current.parent

            except SemanticError as error:
                self.errors.append(SemanticError(error, node))
                parent = ErrorType()

            # set parent
            try:
                self.current_type.set_parent(parent)
            except SemanticError as error:
                self.errors.append(SemanticError(error, node))
                self.current_type.set_parent(ErrorType())

            # visit variables and functions
            for function in node.functions:
                self.visit(function)
            for variables in node.variable_names:
                self.visit(variables)

    @visitor.when(Function_Definition) # add function call instead of function definition??
    def visit(self, node: Function_Definition):
        self.param_names, self.param_types = self.param_names_and_types_Function_Definition(node)


        try:
            self.context.create_function(node.name, node.argument_names, node.argument_type_annotations, node.return_type_annotation, node)
        except SemanticError as error:
            self.errors.append(SemanticError(error, node))

    @visitor.when(Protocol_Definition)
    def visit(self, node: Protocol_Definition):
        try:
            self.context.create_protocol(node.name, node.func_names, node.func_parameter_type_names, node.func_return_type_names, node.parent_name)
        except SemanticError as error:
            self.errors.append(SemanticError(error, node))

    
    def param_names_and_types_Type_Definition(self, node: Type_Definition):
        names = []
        types = []

        for name in node.variable_names:
            type = node.variable_type_name_annotations[node.variable_names.index(name)]
            if name in names:
                self.errors.append(SemanticError(f"Variable {name} already defined", node))
                types[names.index(name)] = ErrorType()
            else:
                if type is None:
                    type = UndefinedType()

            names.append(name)
            types.append(self.context.get_type(type))
        return names, types
    
    def param_names_and_types_Function_Definition(self, node: Function_Definition):
        names = []
        types = []

        for name in node.argument_names:
            type = node.argument_type_annotations[node.argument_names.index(name)]
            if name in names:
                self.errors.append(SemanticError(f"Variable {name} already defined", node))
                types[names.index(name)] = ErrorType()
            else:
                if type is None:
                    type = UndefinedType()

            names.append(name)
            types.append(self.context.get_type(type))
        return names, types

    def param_names_and_types_Protocol_Definition(self, node: Protocol_Definition):
        names = []
        types = []

        for name in node.func_names:
            type = node.func_parameter_type_names[node.func_names.index(name)]
            if name in names:
                self.errors.append(SemanticError(f"Variable {name} already defined", node))
                types[names.index(name)] = ErrorType()
            else:
                if type is None:
                    type = UndefinedType()

            names.append(name)
            types.append(self.context.get_type(type))
        return names, types