try:
    from sympy import *
    from sympy.solvers.solveset import linsolve
    import os
    import pickle
except Exception as e:
    print(e)
    print("Chybí potřebné moduly. Prosím nainstalujte sympy.")
    print("Spusťte: python3 -m pip install sympy")
    exit()
session_file = 'circuit_session.pkl'
init_printing()

def parse_equation(eq_input):
    """Převede zadanou rovnici z uživatelského vstupu na objekt Eq ze SymPy."""
    eq_input = eq_input.replace('=', '==')
    try:
        if '==' in eq_input:
            left, right = eq_input.split('==', 1)
            return Eq(sympify(left.strip()), sympify(right.strip()))
        else:
            return Eq(sympify(eq_input.strip()), 0)
    except SympifyError as e:
        raise ValueError(f"Neplatná rovnice: {eq_input}") from e

def collect_equations():
    """Interaktivně sbírá rovnice z uživatelského vstupu."""
    equations = []
    print("Zadejte rovnice (nebo prázdný vstup pro dokončení):")
    while True:
        eq_input = input(f"Rovnice {len(equations)+1}: ").strip()
        if not eq_input:
            break
        try:
            eq = parse_equation(eq_input)
            equations.append(eq)
            print(f"Přidáno: {eq}")
        except Exception as e:
            print(f"Chyba: {e}\nZkuste to znovu.")
    return equations

def get_solve_vars(available_symbols, num_equations):
    """Vyžádá si od uživatele proměnné, pro které se má řešit, s validací."""
    while True:
        input_vars = input(f"\nZadejte {num_equations} proměnné k řešení (oddělené čárkou): ").strip()
        if not input_vars:
            print("Musíte zadat alespoň jednu proměnnou.")
            continue
        
        try:
            solve_vars = [Symbol(v.strip()) for v in input_vars.split(',')]
        except Exception:
            print("Neplatný formát proměnných. Použijte např. 'x, y, z'.")
            continue

        missing = [v for v in solve_vars if v not in available_symbols]
        if missing:
            print(f"Proměnné {missing} nejsou v rovnicích. Dostupné proměnné: {available_symbols}")
            continue
        
        return solve_vars

def substitute_parameters(equations, solve_vars):
    """Interaktivně nahrazuje parametry podle pokynů uživatele."""
    symbols = sorted(set().union(*[eq.free_symbols for eq in equations]) - set(solve_vars),
                    key=lambda s: s.name)
    
    if not symbols:
        print("Žádné parametry k nahrazení.")
        return equations, {}
    
    print("\nDostupné parametry:", ', '.join(map(str, symbols)))
    substitutions = {}
    while True:
        choice = input("Zadejte parametr k nahrazení (nebo 'konec'): ").strip()
        if choice.lower() == 'konec':
            break
        
        try:
            symbol = Symbol(choice)
            if symbol not in symbols:
                print(f"Parametr {symbol} není v seznamu.")
                continue
        except Exception:
            print("Neplatný symbol.")
            continue
        
        while True:
            try:
                value = sympify(input(f"Hodnota pro {symbol}: "))
                break
            except SympifyError:
                print("Neplatný výraz. Zkuste např. 5, 1/2, nebo sqrt(2).")
        
        substitutions[symbol] = value
        equations = [eq.subs(symbol, value) for eq in equations]
        print("\nAktualizované rovnice:")
        for i, eq in enumerate(equations, 1):
            print(f"{i}: {eq}")
        
        # Aktualizace dostupných symbolů po substituci
        symbols = sorted(set().union(*[eq.free_symbols for eq in equations]) - set(solve_vars),
                        key=lambda s: s.name)
        if not symbols:
            print("Všechny parametry byly nahrazeny.")
            break
        print("\nZbývající parametry:", ', '.join(map(str, symbols)))
    
    return equations, substitutions

def solve_system(equations, solve_vars):
    """Vyřeší systém rovnic s numerickým vyhodnocením."""
    try:
        # Nejprve se pokusí o lineární řešení
        lin_solution = linsolve(equations, solve_vars)
        if lin_solution != EmptySet:
            solutions = [dict(zip(solve_vars, sol)) for sol in lin_solution]
    except (ValueError, TypeError):
        solutions = None

    # Pokud lineární řešení selže, použije se nelineární solver
    if not solutions:
        solutions = solve(equations, solve_vars, dict=True)

    if not solutions:
        print("Nebyla nalezena žádná řešení")
        return None

    # Zpracování řešení pro numerické vyhodnocení
    processed = []
    for sol in solutions:
        numerical_sol = {}
        for var, expr in sol.items():
            # Pokusí se numericky vyhodnotit, pokud je to možné
            try:
                numerical_sol[var] = expr.evalf() if expr.free_symbols else expr
            except:
                numerical_sol[var] = expr
        processed.append(numerical_sol)

    print("\nNalezena řešení:")
    for i, sol in enumerate(processed, 1):
        print(f"Řešení {i}:")
        for var, val in sol.items():
            if val.free_symbols:
                print(f"  {var} = {val} (symbolické)")
            else:
                print(f"  {var} = {val.evalf(4)} (číselné)")
    
    return processed

def show_help():
    print("\nNápověda:")
    print("Interaktivní režim")
    print("Dostupné příkazy:")
    print("- 'help' - zobrazí tuto nápovědu")
    print("- 'equations' - zobrazí aktuální systém rovnic")
    print("- 'substitutions' - zobrazí aktuální hodnoty substitucí")
    print("- 'solve' - znovu vyřeší systém s aktuálními hodnotami")
    print("- 'vars' - zobrazí proměnné, pro které se řeší systém")
    print("- 'delete' - smaže aktuální relaci a ukončí program")
    print("- 'save' - uloží aktuální relaci")
    print("- 'exit' | 'quit' - uloží relaci a ukončí program")
    print("- Libovolný matematický výraz k vyhodnocení")

def save_session(solutions, substitutions, equations, solve_vars):
    # Uložení dat relace
    session_data = {
        'equations': equations,
        'substitutions': substitutions,
        'solve_vars': solve_vars,
        'solutions': solutions,
    }
    with open(session_file, 'wb') as f:
        pickle.dump(session_data, f)
    print("\nRelace byla úspěšně uložena.")

def parse(f):
    '''Parsuje rovnici'''
    if use_latex:
        return latex(f)
    else:
        return f

use_latex = False
def interactive_session(solutions, substitutions, equations, solve_vars):
    """Rozšířený interaktivní režim s perzistentními substitucemi."""
    global use_latex
    # Vytvoří mapu substitucí s klíči jako řetězce
    sub_map = {str(k): v for k, v in substitutions.items()}
    for sol in solutions:
        sub_map.update({str(k): v for k, v in sol.items()})

    show_help()

    while True:
        expr = input("\n>>> ").strip()

        use_latex = False
        og_expr = expr
        expr = expr.replace("latex", "")

        if og_expr != expr:
            use_latex = True
        
        # Zpracování příkazů
        match expr.lower():
            case 'delete':
                confirm_message = "Matous je nejlepsi"
                if input(f"Pro potvrzení napište '{confirm_message}': "):
                    os.remove(session_file)
                return
            case "exit" | "quit":
                save_session(solutions, substitutions, equations, solve_vars)
                return
            case "save":
                save_session(solutions, substitutions, equations, solve_vars)
            case 'equations':
                current_eqs = [eq.subs(substitutions) for eq in equations]
                print("\nAktuální systém rovnic:")
                for i, eq in enumerate(current_eqs, 1):
                    print(f"Rovnice {i}: {parse(eq)}")
                continue
            case 'substitutions':
                print("\nAktuální substituce:")
                for k, v in substitutions.items():
                    print(f"  {parse(k)} = {parse(v)}")
                continue
            case 'vars':
                print("\nProměnné, pro které se řeší:")
                print(", ".join(map(str, solve_vars)))
                continue
            case 'solve':
                current_eqs = [eq.subs(substitutions) for eq in equations]
                new_solutions = solve_system(current_eqs, solve_vars)
                if new_solutions:
                    solutions = new_solutions
                    # Aktualizace substituční mapy
                    sub_map.update({str(k): v for sol in solutions for k, v in sol.items()})
                    print("Systém byl znovu vyřešen s aktuálními substitucemi")
                continue
            case 'help':
                show_help()
                continue
            case _:
                # Zpracování přiřazení proměnných
                try:
                    if '=' in expr:
                        lhs_str, rhs_str = map(str.strip, expr.split('=', 1))
                        
                        # Validace levé strany
                        try:
                            lhs_sym = Symbol(lhs_str)
                        except:
                            print(f"Neplatný název symbolu: {parse(lhs_str)}")
                            continue
                        
                        # Parsování pravé strany
                        try:
                            rhs_expr = sympify(rhs_str, locals=sub_map)
                        except Exception as e:
                            print(f"Neplatný výraz: {parse(e)}")
                            continue
                        
                        # Aktualizace perzistentních substitucí
                        substitutions[lhs_sym] = rhs_expr
                        sub_map[lhs_str] = rhs_expr
                        print(f"Přidána substituce: {parse(lhs_sym)} = {parse(rhs_expr)}")
                        continue

                    # Vyhodnocení výrazu
                    expr = sympify(expr, locals=sub_map)
                    substituted = expr.subs(substitutions)
                    
                    try:
                        numerical = substituted.evalf()
                        if numerical != substituted:
                            print(f"Symbolické: {parse(substituted)} = ", end = "")
                            print(f"{parse(numerical.evalf(4))}")
                        else:
                            print(f"Výsledek: {parse(numerical.evalf(4))}")
                    except:
                        print(f"Symbolický výsledek: {parse(substituted)}")
                except Exception as e:
                    print(f"Chyba: {str(e)}")

def main():
    session_loaded = False
    solutions = None
    substitutions = {}
    equations = []
    solve_vars = []

    # Pokus o načtení existující relace
    if os.path.exists(session_file):
        try:
            with open(session_file, 'rb') as f:
                session_data = pickle.load(f)
            equations = session_data['equations']
            substitutions = session_data['substitutions']
            solve_vars = session_data['solve_vars']
            solutions = session_data.get('solutions', None)
            session_loaded = True
            print("\nByla načtena existující relace.")
            
            # Výpis načtených rovnic
            if equations:
                print("\nAktuální rovnice:")
                for i, eq in enumerate(equations, 1):
                    print(f"Rovnice {i}: {eq}")
                if substitutions:
                    print("\nAktuální substituce:")
                    for k, v in substitutions.items():
                        print(f"{k} = {v}")
        except Exception as e:
            print(f"\nChyba při načítání relace: {e}")
            session_loaded = False

    try:
        if session_loaded:
            # Přímo použít načtená data
            if solutions is None or not solutions:
                solutions = solve_system(equations, solve_vars)
            if solutions:
                interactive_session(solutions, substitutions, equations, solve_vars)
        else:
            # Standardní průběh programu
            equations = collect_equations()
            if not equations:
                print("Nebyla zadána žádná rovnice.")
                return

            all_symbols = set().union(*[eq.free_symbols for eq in equations])
            print("\nDostupné symboly:", ', '.join(map(str, all_symbols)))
            
            solve_vars = get_solve_vars(all_symbols, len(equations))
            print("\nŘešení pro:", ', '.join(map(str, solve_vars)))
            
            equations, substitutions = substitute_parameters(equations, solve_vars)
            
            solutions = solve_system(equations, solve_vars)

            interactive_session(solutions, substitutions, equations, solve_vars)
    
    except Exception as e:
        print(f"\nChyba: {e}")
    finally:
        print("\nProgram ukončen.")

if __name__ == "__main__":
    main()