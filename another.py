try:
    from sympy import *
    from sympy.solvers.solveset import linsolve
    import os
    import pickle
except Exception as e:
    print(e)
    print("Required modules not installed. Please install sympy.")
    print("Run: python3 -m pip install sympy")
    exit()
session_file = 'circuit_session.pkl'
init_printing()

def parse_equation(eq_input):
    """Parse a single equation from user input into a SymPy Eq object."""
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
    """Collect multiple equations from user input."""
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
    """Prompt user for variables to solve for, with validation."""
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
    """Interactive parameter substitution with user guidance."""
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
        
        # Update available symbols after substitution
        symbols = sorted(set().union(*[eq.free_symbols for eq in equations]) - set(solve_vars),
                        key=lambda s: s.name)
        if not symbols:
            print("Všechny parametry byly nahrazeny.")
            break
        print("\nZbývající parametry:", ', '.join(map(str, symbols)))
    
    return equations, substitutions

def solve_system(equations, solve_vars):
    """Solve the system with proper numerical evaluation"""
    try:
        # First try linear solver
        lin_solution = linsolve(equations, solve_vars)
        if lin_solution != EmptySet:
            solutions = [dict(zip(solve_vars, sol)) for sol in lin_solution]
    except (ValueError, TypeError):
        solutions = None

    # Fallback to non-linear solver if needed
    if not solutions:
        solutions = solve(equations, solve_vars, dict=True)

    if not solutions:
        print("No solutions found")
        return None

    # Process solutions for numerical evaluation
    processed = []
    for sol in solutions:
        numerical_sol = {}
        for var, expr in sol.items():
            # Attempt to numerically evaluate if possible
            try:
                numerical_sol[var] = expr.evalf() if expr.free_symbols else expr
            except:
                numerical_sol[var] = expr
        processed.append(numerical_sol)

    print("\nSolutions found:")
    for i, sol in enumerate(processed, 1):
        print(f"Solution {i}:")
        for var, val in sol.items():
            if val.free_symbols:
                print(f"  {var} = {val} (symbolic)")
            else:
                print(f"  {var} = {val.evalf(4)} (numerical)")
    
    return processed

def show_help():
    print("\nHelp:")
    print("Interactive mode ")
    print("Available commands:")
    print("- 'help' - show this help message")
    print("- 'equations' - show current equation system")
    print("- 'substitutions' - show current parameter values")
    print("- 'solve' - re-solve system with current values")
    print("- 'vars' - show variables being solved for")
    print("- 'delete' - deletes the current session and exits")
    print("- 'save' - saves the current sessions")
    print("- 'exit' | 'quit' - save and quit")
    print("- Any math expression to evaluate")

def save_session(solutions, substitutions, equations, solve_vars):
    # save_data
    session_data = {
        'equations': equations,
        'substitutions': substitutions,
        'solve_vars': solve_vars,
        'solutions': solutions,
    }
    with open(session_file, 'wb') as f:
        pickle.dump(session_data, f)
    print("\nSession saved successfully.")

def parse(f):
    '''parses the equation'''
    if use_latex:
        return latex(f)
    else:
        return f

use_latex = False
def interactive_session(solutions, substitutions, equations, solve_vars):
    """Enhanced interactive session with persistent substitutions"""
    global use_latex
    # Create combined substitution map with string keys
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
        
        # Handle commands
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
                print("\nCurrent equation system:")
                for i, eq in enumerate(current_eqs, 1):
                    print(f"Equation {pares(i)}: {parse(eq)}")
                continue
            case 'substitutions':
                print("\nCurrent substitutions:")
                for k, v in substitutions.items():
                    print(f"  {parse(k)} = {parse(v)}")
                continue
            case 'vars':
                print("\nVariables being solved for:")
                print(", ".join(map(str, solve_vars)))
                continue
            case 'solve':
                current_eqs = [eq.subs(substitutions) for eq in equations]
                new_solutions = solve_system(current_eqs, solve_vars)
                if new_solutions:
                    solutions = new_solutions
                    # Update both substitution systems
                    sub_map.update({str(k): v for sol in solutions for k, v in sol.items()})
                    print("System re-solved with current substitutions")
                continue
            case 'help':
                show_help()
                continue
            case _:
                # Handle variable assignments
                try:
                    if '=' in expr:
                        lhs_str, rhs_str = map(str.strip, expr.split('=', 1))
                        
                        # Validate left-hand side
                        try:
                            lhs_sym = Symbol(lhs_str)
                        except:
                            print(f"Invalid symbol name: {parse(lhs_str)}")
                            continue
                        
                        # Prevent overriding solution variables
                        # if lhs_sym in solve_vars:
                        #    print(f"Cannot assign to solution variable {lhs_sym}")
                        #    continue
                        
                        # Parse right-hand side
                        try:
                            rhs_expr = sympify(rhs_str, locals=sub_map)
                        except Exception as e:
                            print(f"Invalid expression: {parse(e)}")
                            continue
                        
                        # Update persistent substitutions
                        substitutions[lhs_sym] = rhs_expr
                        # Update local evaluation map
                        sub_map[lhs_str] = rhs_expr
                        print(f"Added substitution: {parse(lhs_sym)} = {parse(rhs_expr)}")
                        continue

                    # Evaluate expressions
                    expr = sympify(expr, locals=sub_map)
                    substituted = expr.subs(substitutions)
                    
                    try:
                        numerical = substituted.evalf()
                        if numerical != substituted:
                            print(f"Symbolic: {parse(substituted)} = ", end = "")
                            print(f"{parse(numerical.evalf(4))}")
                        else:
                            print(f"Result: {parse(numerical.evalf(4))}")
                    except:
                        print(f"Symbolic result: {parse(substituted)}")
                except Exception as e:
                    print(f"Error: {str(e)}")


def main():
    session_loaded = False
    solutions = None
    substitutions = {}
    equations = []
    solve_vars = []

    # Attempt to load existing session (only difference is pickle loading)
    if os.path.exists(session_file):
        try:
            with open(session_file, 'rb') as f:
                session_data = pickle.load(f)
            equations = session_data['equations']
            substitutions = session_data['substitutions']
            solve_vars = session_data['solve_vars']
            solutions = session_data.get('solutions', None)
            session_loaded = True
            print("\nLoaded existing session.")
            
            # Print equations if loaded
            if equations:
                print("\nCurrent equations:")
                for i, eq in enumerate(equations, 1):
                    print(f"Equation {i}: {eq}")
                if substitutions:
                    print("\nCurrent substitutions:")
                    for k, v in substitutions.items():
                        print(f"{k} = {v}")
        except Exception as e:
            print(f"\nError loading session: {e}")
            session_loaded = False

    try:
        if session_loaded:
            # Directly use loaded data
            if solutions is None or not solutions:
                solutions = solve_system(equations, solve_vars)
            if solutions:
                interactive_session(solutions, substitutions, equations, solve_vars)
        else:
            # Normal operation flow
            equations = collect_equations()
            if not equations:
                print("No equations to solve.")
                return

            all_symbols = set().union(*[eq.free_symbols for eq in equations])
            print("\nAvailable symbols:", ', '.join(map(str, all_symbols)))
            
            solve_vars = get_solve_vars(all_symbols, len(equations))
            print("\nSolving for:", ', '.join(map(str, solve_vars)))
            
            equations, substitutions = substitute_parameters(equations, solve_vars)
            
            solutions = solve_system(equations, solve_vars)

            interactive_session(solutions, substitutions, equations, solve_vars)


    
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nProgram exited.")

if __name__ == "__main__":
    main()