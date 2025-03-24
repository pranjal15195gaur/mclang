from top import (BinOp, UnOp, Float, Int, If, Parentheses, Program, VarDecl,
                 VarReference, Assignment, AST, For, While, Print, 
                 ArrayLiteral, ArrayIndex, FunctionCall, FunctionDef, Return)


from lexer import IntToken, FloatToken, OperatorToken, KeywordToken, ParenToken, Token, lex

class ParseError(Exception):
    pass

def parse(s: str) -> AST:
    from more_itertools import peekable
    t = peekable(lex(s))

    def expect(what: Token):
        if t.peek(None) == what:
            next(t)
            return
        raise ParseError

    # Rename existing parse_cmp to parse_comparison (handles arithmetic comparisons)
    def parse_comparison():
        l = parse_add_sub()
        match t.peek(None):
            case OperatorToken('<') | OperatorToken('<=') | OperatorToken('>') | OperatorToken('>=') | OperatorToken('==') | OperatorToken('!='):
                op = t.peek(None).o
                next(t)
                r = parse_add_sub()
                return BinOp(op, l, r)
            case _:
                return l

    # New helper: logical and has higher precedence than logical or.
    def parse_logic_and():
        expr = parse_comparison()
        while t.peek(None) == KeywordToken("and"):
            next(t)
            right = parse_comparison()
            expr = BinOp("and", expr, right)
        return expr

    # New helper: logical or, lowest precedence among logical operators.
    def parse_logic_or():
        expr = parse_logic_and()
        while t.peek(None) == KeywordToken("or"):
            next(t)
            right = parse_logic_and()
            expr = BinOp("or", expr, right)
        return expr

    def parse_add_sub():
        ast = parse_mul_div()
        while True:
            match t.peek(None):
                case OperatorToken('+'):
                    next(t)
                    ast = BinOp('+', ast, parse_mul_div())
                case OperatorToken('-'):
                    next(t)
                    ast = BinOp('-', ast, parse_mul_div())
                case _:
                    break
        return ast

    def parse_mul_div():
        ast = parse_exp()
        while True:
            match t.peek(None):
                case OperatorToken('*') | OperatorToken('/') | OperatorToken('%'):
                    op = t.peek(None).o
                    next(t)
                    ast = BinOp(op, ast, parse_exp())
                case _:
                    break
        return ast

    def parse_exp():
        l = parse_if()
        match t.peek(None):
            case OperatorToken('**'):
                next(t)
                r = parse_if()
                return BinOp("**", l, r)
            case _:
                return l

    def parse_if():
        if t.peek(None) != KeywordToken("agr_teri_maa_chudi_aur"):
            return parse_atom()
        next(t)  # consume "if"
        cond = parse_logic_or()           # use logical expression for condition
        then_expr = parse_block()         # parse then block
        elseif_branches = []
        while t.peek(None) == KeywordToken("varna"):
            next(t)  # consume "else"
            if t.peek(None) == KeywordToken("agr_teri_maa_chudi_aur"):
                next(t)  # consume "if"
                elseif_cond = parse_logic_or()
                elseif_then = parse_block()
                elseif_branches.append((elseif_cond, elseif_then))
            else:
                else_expr = parse_block()
                return If(cond, then_expr, elseif_branches, else_expr)
        return If(cond, then_expr, elseif_branches, None)

    def parse_atom():
        match t.peek(None):
            case IntToken(v):
                next(t)
                node = Int(v)
            case FloatToken(v):
                next(t)
                node = Float(v)
            case ParenToken('('):
                next(t)
                node = parse_logic_or()      # full expression in parentheses
                expect(ParenToken(')'))
            case OperatorToken('-'):
                next(t)
                node = UnOp('-', parse_atom())
            case OperatorToken('['):
                # Array literal
                next(t)  # consume '['
                elements = []
                if t.peek(None) != OperatorToken(']'):
                    elements.append(parse_logic_or())
                    while t.peek(None) == OperatorToken(','):
                        next(t)
                        elements.append(parse_logic_or())
                expect(OperatorToken(']'))
                node = ArrayLiteral(elements)
            case KeywordToken(x) if x not in ["agr_teri_maa_chudi_aur", "varna", " madarchod_ye_hai", "and", "or", "bol_behen_ke_lund", "for", "jab_tak_teri_maa_chude_aur"]:
                func_name = x
                next(t)
                if t.peek(None) == ParenToken('('):
                    next(t)  # consume '('
                    call_args = []
                    if t.peek(None) != ParenToken(')'):
                        call_args.append(parse_logic_or())
                        while t.peek(None) == OperatorToken(','):
                            next(t)
                            call_args.append(parse_logic_or())
                    try:
                        expect(ParenToken(')'))
                    except ParseError:
                        raise ParseError("Unclosed parenthesis in function call")
                    node = FunctionCall(func_name, call_args)
                else:
                    node = VarReference(func_name)
            case _:
                raise ParseError("Unexpected token in atom")
        
        # Handle postfix array indexing: e.g. x[1] or [1,2,3][2]
        while t.peek(None) == OperatorToken('['):
            next(t)  # consume '['
            index_expr = parse_logic_or()
            expect(OperatorToken(']'))
            node = ArrayIndex(node, index_expr)
        return node

    
    # New helper to parse a block of statements enclosed in '{' and '}'
    def parse_block():
        try:
            expect(OperatorToken('{'))
        except ParseError:
            raise ParseError("Expected '{' at beginning of block")
        statements = []
        while t.peek(None) is not None and t.peek(None) != OperatorToken('}'):
            statements.append(parse_statement())
            if t.peek(None) == OperatorToken(';'):
                next(t)
        try:
            expect(OperatorToken('}'))
        except ParseError:
            raise ParseError("Missing closing '}' after block")
        return Program(statements) if len(statements) > 1 else statements[0]
    
    def parse_statement():
        match t.peek(None):
            # --- New case for function definitions ---
            case KeywordToken("iski_maa_ki_choot_def"):
                next(t)  # consume "def"
                token = t.peek(None)
                if not (isinstance(token, KeywordToken) and token.w not in ["agr_teri_maa_chudi_aur", "varna", " madarchod_ye_hai", "and", "or", "bol_behen_ke_lund", "for", "jab_tak_teri_maa_chude_aur"]):
                    raise ParseError("Expected function name after 'def'")
                func_name = token.w
                next(t)
                try:
                    expect(ParenToken('('))
                except ParseError:
                    raise ParseError("Expected '(' after function name")
                params = []
                if t.peek(None) != ParenToken(')'):
                    # At least one parameter
                    token = t.peek(None)
                    if not isinstance(token, KeywordToken):
                        raise ParseError("Expected parameter name")
                    params.append(token.w)
                    next(t)
                    while t.peek(None) == OperatorToken(','):
                        next(t)
                        token = t.peek(None)
                        if not isinstance(token, KeywordToken):
                            raise ParseError("Expected parameter name")
                        params.append(token.w)
                        next(t)
                try:
                    expect(ParenToken(')'))
                except ParseError:
                    raise ParseError("Expected ')' after parameter list")
                body = parse_block()  # Reuse block parsing for the function body.
                return FunctionDef(func_name, params, body)
            
            case KeywordToken("chod_de"):
                next(t)  # consume "return"
                expr = parse_logic_or()  # parse the expression following 'return'
                return Return(expr)

            case KeywordToken("bol_behen_ke_lund"):
                next(t)  # consume "print"
                try:
                    expect(ParenToken('('))
                except ParseError:
                    raise ParseError("Expected '(' after 'print'")
                expr = parse_logic_or()
                try:
                    expect(ParenToken(')'))
                except ParseError:
                    raise ParseError("Expected ')' after print argument")
                return Print(expr)
            case KeywordToken("for"):
                next(t)  # consume "for"
                try:
                    expect(ParenToken('('))
                except ParseError:
                    raise ParseError("Expected '(' after 'for'")
                init = parse_statement()  # allow var-decl/assignment in initialization
                try:
                    expect(OperatorToken(';'))
                except ParseError:
                    raise ParseError("Expected ';' after for-loop initializer")
                condition = parse_logic_or()
                try:
                    expect(OperatorToken(';'))
                except ParseError:
                    raise ParseError("Expected ';' after for-loop condition")
                increment = parse_statement()  # allow assignment in increment
                try:
                    expect(ParenToken(')'))
                except ParseError:
                    raise ParseError("Expected ')' after for-loop increment")
                body = parse_block()  # use block parser for loop body
                return For(init, condition, increment, body)
            case KeywordToken("jab_tak_teri_maa_chude_aur"):
                next(t)  # consume "while"
                try:
                    expect(ParenToken('('))
                except ParseError:
                    raise ParseError("Expected '(' after 'while'")
                condition = parse_logic_or()
                try:
                    expect(ParenToken(')'))
                except ParseError:
                    raise ParseError("Expected ')' after while-loop condition")
                body = parse_block()  # use block parser for loop body
                return While(condition, body)
            case KeywordToken("madarchod_ye_hai"):
                next(t)  # consume "var"
                token = t.peek(None)
                if not (isinstance(token, KeywordToken) and token.w not in ["if", "else", "var", "for", "while", "and", "or", "print"]):
                    raise ParseError("Expected variable name after 'var'")
                var_name = token.w
                next(t)
                try:
                    expect(OperatorToken('='))
                except ParseError:
                    raise ParseError("Expected '=' after variable name in declaration")
                expr = parse_logic_or()
                return VarDecl(var_name, expr)
            case _:
                expr = parse_logic_or()
                if isinstance(expr, VarReference) and t.peek(None) == OperatorToken('='):
                    next(t)  # consume '='
                    rhs = parse_logic_or()
                    return Assignment(expr.name, rhs)
                return expr

    def parse_program():
        statements = []
        while t.peek(None) is not None:
            statements.append(parse_statement())
            # Optionally consume a semicolon if present.
            if t.peek(None) == OperatorToken(';'):
                next(t)
        return statements[0] if len(statements) == 1 else Program(statements)



    result = parse_program()

    
    return result
