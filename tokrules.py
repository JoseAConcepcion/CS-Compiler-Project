#Lista de palabras reservadas
reserved = {    
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'for' : 'FOR',
    'range': 'RANGE',
    'print' : 'PRINT',
    'in': 'IN',
    'let': 'LET',
    'as': 'AS',
    'true': 'TRUE',
    'false': 'FALSE',
    'type': 'TYPE',
    'self': 'SELF',
    'new': 'NEW',
    'inherits': 'INHERITS',
    'base': 'BASE',
    'Object': 'OBJECT',
    'Number': 'NUMBERTYPE',
    'String': 'STRINGTYPE',
    'Boolean': 'BOOLEANTYPE',
    'is': 'IS',
    'sqrt': 'SQRT',
    'sin': 'SIN',
    'cos': 'COS',    
    'exp': 'EXP',
    'log': 'LOG',
    'rand': 'RAND',
    'PI': 'PI',
    'E': 'E',
    'function': 'FUNCTION',
    'protocol': 'PROTOCOL',
    'extends': 'EXTENDS',
    
}
# Lista de nombres de tokens
tokens = [
   'NUMBER',
   'STRING',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'POWER',
   'MODULE',
   'ASIGN',
   'DESTRUCTASIGN',
   'LPAREN',
   'RPAREN',
   'LBRACE',
   'RBRACE',
   'LBRAC',
   'RBRAC',
   'COMMA',
   'SEMICOLON',
   'ARROW',
   'CONCAT',
   'DOUBLECONCAT',
   'MINOR',
   'MAJOR',
   'EQUAL',
   'DIFFERENT',
   'MINOREQUAL',
   'MAJOREQUAL',
   'AND',
   'OR',
   'NOT',
   'DOT',
   'CONFORMS',
   'DOUBLEDOTS',
   'GENERATOR',
   'ID',
   'COMMENTS',
] + list(reserved.values())

def t_COMMENTS(t):
    r'//.*'
    t.lexer.lineno += t.value.count('\n')
#Expresion regular para el id
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

# Expresiones a ignorar
t_ignore = ' \t'
# Expresiones regulares para tokens simples
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_POWER   = r'\^'
t_MODULE = r'%'
t_ASIGN   = r'='
t_DESTRUCTASIGN = r':='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_LBRAC = r'\['
t_RBRAC = r'\]'
t_COMMA   = r','
t_SEMICOLON = r';'
t_ARROW = r'=>'
t_CONCAT = r'@'
t_DOUBLECONCAT = r'@@'
t_MINOR = r'<'
t_MAJOR = r'>'
t_EQUAL = r'=='
t_DIFFERENT = r'!='
t_MINOREQUAL = r'<='
t_MAJOREQUAL = r'>='
t_AND = r'&&'
t_OR = r'\|'
t_NOT = r'!'
t_DOT = r'\.'
t_CONFORMS = r'<='
t_DOUBLEDOTS = r':'
t_GENERATOR = r'\|\|'


# Expresión regular para NUMBER
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

#Expresion regular para STRING
def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t
# Regla para manejar errores
def t_error(t):
    raise("Error lexico: %s en la linea %d" % (t.value[0], t.lineno))
    t.lexer.skip(1)

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
