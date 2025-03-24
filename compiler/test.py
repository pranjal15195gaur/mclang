from top import e
from parser import parse, ParseError
import unittest

class TestRunTests(unittest.TestCase):
    def test_successful_tests(self):
        tests_ok = [
            ("5 + 3", 8),                                  # simple arithmetic
            ("if 1 == 1 { 10 } else { 20 }", 10),           # if-else expression (true branch)
            ("(10 - 3) * 2", 14),                           # using parentheses
            ("if 2 < 3 { 2 + 2 } else { 9 / 3 }", 4),      # if expression (true branch)
            ("if 2 < 3 { if 1 == 1 { 100 } else { 0 } } else { 42 }", 100),  # nested if
            ("5 + if 2 < 3 { 4 } else { 20 }", 9),         # if expression inside binary op
            ("5 + 3; 2 * 3", 6),                           # multi-statement; result from last statement (6)
            ("var x = 10; x + 5", 15),                      # variable declaration & usage (15)
            ("var a = 2; var b = a; a = 6;a + b", 8),            # using multiple variables (4)
            ("var a = 2; var b = 3; var c = a * b; c + 1", 7),  # chained variable declarations (7)
            ("var x = 0; while ( x < 3 ) { x = x + 1 }; x", 3),  # while loop test
            ("var sum = 0; for ( var i = 0; i < 3; i = i + 1 ) { sum = sum + i; i = i + 1; }; sum", 2),  # for loop summation
        ]
        for code, expected in tests_ok:
            with self.subTest(code=code):
                try:
                    ast = parse(code)
                    result = e(ast)
                    self.assertEqual(result, expected)
                except Exception as ex:
                    self.fail(f"Test failed for code: {code}\nError: {ex}")

    def test_failing_tests(self):
        tests_error = [
            "if 1 == 1 { 5",                          # missing closing brace
            "if 2 < 3 { 4 } else if { 5 }",           # missing condition after 'else if'
            "var x = 10 x + 5",                       # missing semicolon between statements
            "x + 5"                                   # using undefined variable
        ]
        for code in tests_error:
            with self.subTest(code=code):
                if code == "x + 5":
                    with self.assertRaises(ValueError):
                        ast = parse(code)
                        e(ast)
                else:
                    with self.assertRaises(ParseError):
                        ast = parse(code)
                        e(ast)

    def test_print(self):
        import io
        from contextlib import redirect_stdout
        tests_print = [
            ("print(5+5)", "10\n", 10),
            ("var x = 42; print(x)", "42\n", 42),
        ]
        for code, expected_output, expected_value in tests_print:
            with self.subTest(code=code):
                f = io.StringIO()
                with redirect_stdout(f):
                    ast = parse(code)
                    result = e(ast)
                output = f.getvalue()
                self.assertEqual(output, expected_output)
                self.assertEqual(result, expected_value)

    def test_project_euler(self):
        # Project Euler problem 1
        code = """  var ans = 0; 
                    for (var i = 0; i < 1000; i = i + 1) {
                        if (i % 3 == 0 or i % 5 == 0) { 
                            ans = ans + i; 
                        } 
                    }; 
                    ans
               """
        
        with self.subTest(code=code):
            ast = parse(code)
            result = e(ast)
            self.assertEqual(result, 233168)

        
        # Project Euler problem 2

        code =  """
                var ans = 0;
                var a = 0;
                var b = 1;
                while(b<4000000){
                    var temp = a + b;
                    if (temp%2==0){
                        ans = ans + temp;
                    }
                    a = b;
                    b = temp;
                };

                ans
                """

        with self.subTest(code=code):
            ast = parse(code)
            result = e(ast)
            self.assertEqual(result, 4613732)

        # Project Euler problem 3


def run_tests():
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests()