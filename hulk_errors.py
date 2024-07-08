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


class HulkTypeCheckError(HulkError):
    BASIC_TYPE_CHECK = 'Basic type check failed.'
    INFERENCE_ERROR = 'Inference error occurred.'
    FUNCTION_ARGUMENTS = 'Function arguments type and quantity check failed.'
    SELF_OVERWRITE = 'Self overwrite in method is not allowed.'
    ATTRIBUTE_TYPE_CHECK = 'Attribute type check failed.'
    NO_DECLARATION_IN_WRONG_PLACE = 'No declaration allowed in inappropriate places.'
    KEYWORD_OVERLOAD = 'Keyword overloading is prohibited.'
    ARRAY_TYPE_CONSISTENCY = 'Array type consistency check failed.'
    AS_IS_CHECK = 'AS/IS check failed.'
    IF_RETURN_TYPE_INFERENCE = 'Return type inference for if statement failed.'
    SELF_TYPE_ANNOTATION = 'Self type annotation required.'
    METHOD_SIGNATURE_CHECK = 'Method signature check failed.'
    SELF_OVERLOAD_PROHIBITED = 'Self overload is prohibited.'
    STRING_MUTATION_PROHIBITED = 'String mutation is prohibited.'
    INVALID_VARIABLE_DECLARATION = 'Invalid variable declaration.'
    PARAMETER_NAMING_CHECK = 'Parameter naming check failed.'
