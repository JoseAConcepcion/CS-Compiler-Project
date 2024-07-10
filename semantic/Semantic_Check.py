def SemanticCheck(ast):
    errors = []
    type_collector = Type_Collector(errors)
    type_collector.visit(ast)
    context = type_collector.context
    errors = type_collector.errors
    builder = Type_Builder(context, errors)
    builder.visit(ast)
    variable_collector = Variable_Collector(context, errors)
    scope = variable_collector.visit(ast)
    checker, annotated_ast = Semantic_Check(errors)
    checker.visit(ast)
    return annotated_ast, errors