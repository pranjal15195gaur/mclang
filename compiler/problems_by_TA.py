from top import e
from parser import parse, ParseError

def problem_by_TA():
    # Problem statement: Write the multiplication table of 17 till 15 terms
    code = """
            iski_maa_ki_choot_def fib(num){
                agr_teri_maa_chudi_aur num == 0 or num == 1{
                    chod_de num;
                };
                chod_de fib(num-1) + fib(num-2);
            };
            
            madarchod_ye_hai number = 1;
            jab_tak_teri_maa_chude_aur ( number < 15 ) {
                bol_behen_ke_lund(fib(number));
                number = number + 1;
            }
            
           """
    try:
        ast = parse(code)
        e(ast)
    except ParseError as pe:
        print("Parse Error:", pe)
    except Exception as ex:
        print("Error:", ex)

if __name__ == "__main__":
    problem_by_TA()
