from Variable_Collector import *
from Semantic_Check import *
from Type_Collector import *
from Type_Builder import *
from Type_Check import *

#Todo 1ra pasada Fase 1 Recoleccion de tipos
#Todo 2da pasada Fase 2 Construccion de tipos
#Todo 3ra pasada Fase 3 Inferencias de tipos

# TypeCollector
# TypeBuilder
# SemanticCheck
# TypeCheck?

def semantic_check(ast):
    errors = []

    type_collector = TypeCollector(errors)
    type_collector.visit(ast)
    context = type_collector.context
    errors = type_collector.errors
    
    builder = TypeBuilder(context, errors)
    builder.visit(ast)

    variable_collector = VariableCollector(context, errors)
    scope = variable_collector.visit(ast)

    
    checker, annotated_ast = SemanticCheck(errors)
    checker.visit(ast)

    return annotated_ast, errors