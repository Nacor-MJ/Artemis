import unittest
from sympy import Symbol, Eq, sympify
from sympy import EmptySet


# Předpokládáme, že váš kód je uložen v modulu 'project.py'
import main as project


# Definice symbolů pro testy
x = Symbol('x')
y = Symbol('y')
a = Symbol('a')

class TestProjectFunctions(unittest.TestCase):

    def test_parse_equation_with_equal(self):
        # Test parsování rovnice se znakem "="
        eq = project.parse_equation("x+1=3")
        expected = Eq(sympify("x+1"), sympify("3"))
        self.assertEqual(eq, expected)

    def test_parse_equation_without_equal(self):
        # Test parsování rovnice bez explicitního "=" (předpokládá pravou stranu 0)
        eq = project.parse_equation("x+1")
        expected = Eq(sympify("x+1"), 0)
        self.assertEqual(eq, expected)

    def test_parse_equation_invalid(self):
        # Očekáváme, že neplatný výraz vyvolá ValueError.
        try:
            parse_equation("x++1=3")
        except Exception as e:
            print(f"Vyvolána výjimka: {type(e).__name__}, zpráva: {e}")


    def test_solve_system_linear(self):
        # Test řešení jednoduché lineární rovnice: x+1=3 => x=2
        eq = project.parse_equation("x+1=3")
        solution = project.solve_system([eq], [x])
        self.assertIsNotNone(solution)
        self.assertEqual(len(solution), 1)
        # Ověříme, že hodnota x se rovná 2
        self.assertAlmostEqual(solution[0][x], 2)

    def test_solve_system_nonlinear(self):
        # Test řešení nelinární rovnice: x^2 - 4 = 0 => x=2 a x=-2
        eq = project.parse_equation("x**2 - 4 = 0")
        solution = project.solve_system([eq], [x])
        self.assertIsNotNone(solution)
        # Seřadíme výsledky a ověříme, že jsou to -2 a 2
        sol_values = sorted([float(sol_dict[x]) for sol_dict in solution])
        self.assertEqual(sol_values, [-2.0, 2.0])

    def test_get_solve_vars(self):
        # Simulace interaktivního vstupu pro funkci get_solve_vars
        import builtins
        original_input = builtins.input
        try:
            # Simulujeme, že uživatel zadá "x, y"
            builtins.input = lambda prompt="": "x, y"
            solve_vars = project.get_solve_vars({x, y}, 2)
            self.assertEqual(solve_vars, [x, y])
        finally:
            builtins.input = original_input

    def test_substitute_parameters(self):
        # Simulace interaktivního vstupu pro funkci substitute_parameters.
        # Zadáme parametr "a" a jeho hodnotu "5", poté "konec".
        import builtins
        inputs = iter(["a", "5", "konec"])
        original_input = builtins.input
        try:
            builtins.input = lambda prompt="": next(inputs)
            eq = project.parse_equation("a + 1 = 3")
            eqs, subs = project.substitute_parameters([eq], [])
            # Ověříme, že substituce obsahuje symbol a s hodnotou 5
            self.assertIn(a, subs)
            self.assertEqual(subs[a], sympify("5"))
            # Ověříme, že v rovnici byl symbol a nahrazen
            self.assertEqual(eqs[0], Eq(sympify("5+1"), sympify("3")))
        finally:
            builtins.input = original_input

if __name__ == "__main__":
    unittest.main()
