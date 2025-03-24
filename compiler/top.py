from dataclasses import dataclass

class AST:
    pass

# New Environment class for static scoping
class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}
    def lookup(self, name):
        if name in self.values:
            return self.values[name]
        elif self.parent is not None:
            return self.parent.lookup(name)
        else:
            raise ValueError(f"Variable {name} not defined")
    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
        elif self.parent is not None:
            self.parent.assign(name, value)
        else:
            raise ValueError(f"Variable {name} not defined")
    def declare(self, name, value):
        self.values[name] = value

@dataclass
class BinOp(AST):
    op: str
    left: AST
    right: AST

@dataclass
class UnOp(AST):
    op: str
    num: AST

@dataclass
class Float(AST):
    val: str

@dataclass
class Int(AST):
    val: str

@dataclass
class Parentheses(AST):
    val: AST

@dataclass
class If(AST):
    cond: AST
    then: AST
    elseif_branches: list[tuple[AST, AST]]
    elsee: AST

@dataclass
class VarDecl(AST):
    name: str
    value: AST

@dataclass
class VarReference(AST):
    name: str

@dataclass
class Assignment(AST):
    name: str
    value: AST

@dataclass
class Program(AST):
    statements: list[AST]

@dataclass
class For(AST):
    init: AST
    condition: AST
    increment: AST
    body: AST

@dataclass
class While(AST):
    condition: AST
    body: AST

@dataclass
class Print(AST):
    expr: AST

@dataclass
class FunctionCall(AST):
    name: str
    args: list[AST]

# New AST nodes for arrays
@dataclass
class ArrayLiteral(AST):
    elements: list[AST]

@dataclass
class ArrayIndex(AST):
    array: AST
    index: AST

@dataclass
class FunctionDef(AST):
    name: str
    params: list[str]
    body: AST

# A helper to represent a user‐defined function (its parameter names, body, and the closure in which it was defined)
@dataclass
class UserFunction:
    params: list[str]
    body: AST
    closure: Environment

@dataclass
class Return(AST):
    value: AST

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


def e(tree: AST, env=None) -> int:
    if env is None:
        env = Environment()

    match tree:

        case FunctionDef(name, params, body):
            uf = UserFunction(params, body, env)
            env.declare(name, uf)
            return uf
        

        case Program(stmts):
            result = None
            for stmt in stmts:
                result = e(stmt, env)
            return result

        case VarDecl(name, value):
            result = e(value, env)
            env.declare(name, result)
            return result

        case Assignment(name, value):
            result = e(value, env)
            env.assign(name, result)
            return result

        case VarReference(name): 
            return env.lookup(name)
        case Int(v): 
            return int(v)
        case Float(v): 
            return float(v)
        case UnOp("-", expp): 
            return -1 * e(expp, env)

        case BinOp(op, l, r):
            left_val = e(l, env)
            right_val = e(r, env)
            match op:
                case "**": return left_val ** right_val
                case "*": return left_val * right_val
                case "/":
                    if isinstance(left_val, int) and left_val % right_val == 0:
                        return left_val // right_val
                    return left_val / right_val
                case "%": return left_val % right_val
                case "+": return left_val + right_val
                case "-": return left_val - right_val
                case "<": return left_val < right_val
                case "<=": return left_val <= right_val
                case ">": return left_val > right_val
                case ">=": return left_val >= right_val
                case "==": return left_val == right_val
                case "!=": return left_val != right_val
                case "and": return (left_val and right_val)
                case "or": return (left_val or right_val)
                case _: raise ValueError(f"Unsupported binary operator: {op}")

        case Parentheses(expp): 
            return e(expp, env)

        case If(cond, then, elseif_branches, elsee):
            if cond is None:
                raise ValueError("Condition missing in 'if' statement")
            for elseif_cond, _ in elseif_branches:
                if elseif_cond is None:
                    raise ValueError("Condition missing in 'elseif' statement")
            if e(cond, env):
                return e(then, Environment(env))
            for elseif_cond, elseif_then in elseif_branches:
                if e(elseif_cond, env):
                    return e(elseif_then, Environment(env))
            if elsee is not None:
                return e(elsee, Environment(env))
            return None

        case For(init, condition, increment, body):
            e(init, env)
            result = None
            while e(condition, env):
                result = e(body, Environment(env))
                e(increment, env)
            return result

        case While(condition, body):
            result = None
            while e(condition, env):
                result = e(body, env)
            return result

        case Print(expr):
            value = e(expr, env)
            print(value)
            return value

        case FunctionCall(name, args):
            evaluated_args = [e(a, env) for a in args]
            try:
                func = env.lookup(name)
            except ValueError:
                func = None
            if func is not None and isinstance(func, UserFunction):
                if len(evaluated_args) != len(func.params):
                    raise ValueError(f"Function {name} expects {len(func.params)} arguments, got {len(evaluated_args)}")
                new_env = Environment(func.closure)
                for param, arg in zip(func.params, evaluated_args):
                    new_env.declare(param, arg)
                try:
                    return e(func.body, new_env)
                except ReturnException as re:
                    return re.value
            elif name == "max":
                return max(*evaluated_args)
            elif name == "min":
                return min(*evaluated_args)
            else:
                raise ValueError(f"Unknown function {name}")

        case Return(expr):
            # When a return is encountered, evaluate the expression and raise an exception to exit the function.
            raise ReturnException(e(expr, env))

        # New evaluation rules for arrays
        case ArrayLiteral(elements):
            return [e(el, env) for el in elements]
        case ArrayIndex(array, index):
            arr = e(array, env)
            idx = e(index, env)
            if not isinstance(idx, int):
                raise ValueError("Array index must be an integer")
            # One-based indexing: adjust for Python's zero-based lists.
            return arr[idx - 1]

        
                
        case _:
            raise ValueError("Unsupported node type")
