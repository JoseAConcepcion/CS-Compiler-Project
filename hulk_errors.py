class HulkError: #base class for errors handling
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        error_str = f'HULK Error: {self.message}'
        if self.line is not None and self.column is not None:
            error_str += f' [Line: {self.line}, Column: {self.column}]'
        return error_str

class LexicError(HulkError): 
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno

    RED = '\033[91m'
    RESET = '\033[0m'  

    def __str__(self):
        return "Error lexico: token invalido " + self.RED + '%s' %(self.value) + self.RESET + " en la linea %d" %  (self.lineno)


class SemanticError(HulkError):
    WRONG_SIGNATURE = 'Method \'%s\' already defined in an ancestor with a different signature.'
    SELF_IS_READONLY = 'Variable "self" is read-only.'
    INCOMPATIBLE_TYPES = 'Cannot convert \'%s\' into \'%s\'.'
    VARIABLE_NOT_DEFINED = 'Variable \'%s\' is not defined.'
    INVALID_OPERATION = 'Operation \'%s\' is not defined between \'%s\' and \'%s\'.'
    INVALID_UNARY_OPERATION = 'Operation \'%s\' is not defined for \'%s\'.'
    INCONSISTENT_USE = 'Inconsistent use of \'%s\'.'
    EXPECTED_ARGUMENTS = 'Expected %s arguments, but got %s in \'%s\'.'
    CANNOT_INFER_PARAM_TYPE = 'Cannot infer type of parameter \'%s\' in \'%s\'. Please specify it.'
    CANNOT_INFER_ATTR_TYPE = 'Cannot infer type of attribute \'%s\'. Please specify it.'
    CANNOT_INFER_RETURN_TYPE = 'Cannot infer return type of \'%s\'. Please specify it.'
    CANNOT_INFER_VAR_TYPE = 'Cannot infer type of variable \'%s\'. Please specify it.'
    BASE_OUTSIDE_METHOD = 'Cannot use "base" outside of a method.'
    METHOD_NOT_DEFINED = 'Method \'%s\' is not defined in any ancestor.'