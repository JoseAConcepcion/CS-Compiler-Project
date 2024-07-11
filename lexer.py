import ply.lex as lex
import tokrules
def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1
# Construir el lexer
lexer = lex.lex(module=tokrules)

# Prueba de entrada
data = '''\
print("The message is \"Hello World\"");
print("The meaning of life is " @ 42);
print(sin(2 * PI) ^ 2 + cos(3 * PI / log(4, 64)));
{
    print(42);
    print(sin(PI/2));
    print("Hello World");
}
function tan(x) => sin(x) / cos(x);
function cot(x) => 1 / tan(x);
function tan(x) => sin(x) / cos(x);

print(tan(PI) ** 2 + cot(PI) ** 2);
function operate(x, y) {
    print(x + y);
    print(x - y);
    print(x * y);
    print(x / y);
}
let msg = "Hello World." in print(msg);
let number = 42, text = "The meaning of life is" in
    print(text @ number);
let number = 42 in
    let text = "The meaning of life is" in
        print(text @ number);
let number = 42 in (
    let text = "The meaning of life is" in (
            print(text @ number)
        )
    );
let a = 6, b = a * 7 in print(b);
let a = 6 in
    let b = a * 7 in
        print(b);
let a = 5, b = 10, c = 20 in {
    print(a+b);
    print(b*c);
    print(c/a);
}
let a = 0 in {
    print(a);
    a := 1;
    print(a);
}
let a = 0 in
    let b = a := 1 in {
        print(a);
        print(b);
    };
let a = 42 in if (a % 2 == 0) print("Even") else print("odd");
let a = 10 in while (a >= 0) {
    print(a);
    a := a - 1;
}
for (x in range(0, 10)) print(x);
let iterable = range(0, 10) in
    while (iterable.next())
        let x = iterable.current() in
            print(x);
type Point {
    x = 0;
    y = 0;

    getX() => self.x;
    getY() => self.y;

    setX(x) => self.x := x;
    setY(y) => self.y := y;
}
type PolarPoint inherits Point {
    rho() => sqrt(self.getX() ^ 2 + self.getY() ^ 2);
    // ...
}
type Person(firstname, lastname) {
    firstname = firstname;
    lastname = lastname;

    name() => self.firstname @@ self.lastname;
}
type Knight inherits Person {
    name() => "Sir" @@ base();
}

let p = new Knight("Phil", "Collins") in
    print(p.name());
    
let x: Number = 42 in print(x);

type A {
    // ...
}

type B inherits A {
    // ...
}

type C inherits A {
    // ...
}

let x : A = if (rand() < 0.5) new B() else new C() in
    if (x is B)
        let y : B = x as B in {
            // you can use y with static type B
        }
    else {
        print(5); // x cannot be downcasted to B
    }

protocol Equatable extends Hashable {
    equals(other: Object): Boolean;
}

for (x in range(0,10)) {
    print(x); // code that uses `x`
}

let squares = [x^2 || x in range(1,10)] in print(x);
// prints 2, 4, 6, 8, 10, ...

'''

lexer.input('print("The message is \"Hello World\"");')

# Procesar tokens
while True:         
    tok = lexer.token()
    if not tok: break      # No more input  
    print(tok.value, tok.type)