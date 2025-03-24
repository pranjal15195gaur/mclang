# lexer.py
from collections.abc import Iterator
from dataclasses import dataclass

class Token:
    pass

@dataclass
class IntToken(Token):
    v: str

@dataclass
class FloatToken(Token):
    v: str

@dataclass
class OperatorToken(Token):
    o: str

@dataclass
class KeywordToken(Token):
    w: str

@dataclass
class ParenToken(Token):
    w: str

def lex(s: str) -> Iterator[Token]:
    i = 0
    while True:
        while i < len(s) and s[i].isspace():
            i += 1

        if i == len(s):
            return

        if s[i].isdigit():
            t = s[i]
            i += 1
            isFloat = False
            isValid = True
            while i < len(s) and (s[i].isdigit() or s[i] == '.'):
                if s[i] == '.':
                    if isFloat: isValid = False
                    isFloat = True
                t += s[i]
                i += 1

            if not isValid: 
                raise ValueError('Invalid number token found :- {}'.format(t))

            if isFloat: 
                yield FloatToken(t)
            else: 
                yield IntToken(t)

        elif s[i].isalpha() or s[i] == '_':
            t = s[i]
            i += 1
            while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                t += s[i]
                i += 1
            # Then proceed with token matching as before:
            match t:
                case 'agr_teri_maa_chudi_aur' | 'varna':
                    # You can add special handling if needed.
                    yield KeywordToken(t)
                case _:
                    yield KeywordToken(t)

        elif s[i] == '(':
            i += 1
            yield ParenToken('(')

        elif s[i] == ')':
            i += 1
            yield ParenToken(')')

        elif s[i] == '{':
            i += 1
            yield OperatorToken('{')

        elif s[i] == '}':
            i += 1
            yield OperatorToken('}')

        elif s[i] in '+-*/<>=!':
            if s[i:i+2] in ['<=', '>=', '==', '!=', '**']:
                yield OperatorToken(s[i:i+2])
                i += 2
            else:
                yield OperatorToken(s[i])
                i += 1

        elif s[i] == ';':
            i += 1
            yield OperatorToken(';')

        elif s[i] == '%':  # modulo operator
            i += 1
            yield OperatorToken('%')

        elif s[i] == ',':
            i += 1
            yield OperatorToken(',')

        elif s[i] == '[':
            i += 1
            yield OperatorToken('[')

        elif s[i] == ']':
            i += 1
            yield OperatorToken(']')

        else:
            raise ValueError('Unexpected character found :- {}'.format(s[i]))
