# Interaktivní řešení rovni

Tento projekt umožňuje interaktivní zadávání a řešení systému rovnic za využití knihovny **SymPy**. Uživatel může zadávat rovnice, vybírat proměnné, nahrazovat parametry hodnotami a následně řešit systém symbolicky i numericky. Projekt také podporuje ukládání a načítání relací, takže můžete pokračovat tam, kde jste skončili.

## Obsah
- [Instalace](#instalace)
- [Spuštění projektu](#spuštění-projektu)
- [Používání projektu](#používání-projektu)
  - [Interaktivní režim](#interaktivní-režim)
  - [Seznam dostupných příkazů](#seznam-dostupných-příkazů)
- [Ukládání a načítání relací](#ukládání-a-načítání-relací)
- [Poznámky](#poznámky)

## Instalace

Před spuštěním projektu se ujistěte, že máte nainstalovanou knihovnu **SymPy**. Pokud knihovna chybí, program vás upozorní a vypíše následující příkaz pro instalaci:

python3 -m pip install sympy


## Spuštění projektu

Projekt spusťte příkazem:

python3 main.py

## Používání projektu

### Průběh programu

1. **Kontrola závislostí:**  
   - Při spuštění se ověřuje, zda jsou nainstalovány všechny potřebné moduly. Pokud některý modul chybí, program se zastaví a upozorní vás.

2. **Načtení relace:**  
   - Pokud existuje soubor `circuit_session.pkl`, program načte předchozí relaci (rovnice, substituce a řešení) a pokračuje v interaktivním režimu.

3. **Zadávání rovnic:**  
   - Pokud není relace načtena, budete vyzváni k zadání rovnic. Každá zadaná rovnice je převedena na objekt pomocí knihovny SymPy.

4. **Výběr proměnných:**  
   - Po zadání rovnic vyberete proměnné, pro které se má systém rovnic řešit.

5. **Nahrazování parametrů:**  
   - Následuje možnost nahradit ostatní parametry (symboly, které nejsou určeny k řešení) jejich hodnotami, což pomáhá při přesnějším řešení systému.

6. **Řešení systému:**  
   - Program nejprve vyzkouší lineární řešení pomocí `linsolve`. Pokud to není možné, použije obecný solver `solve`.
   - Výsledky jsou následně zpracovány a zobrazeny jak ve formě symbolických, tak numerických hodnot.

### Interaktivní režim

Po vyřešení rovnic vstoupíte do interaktivního režimu, ve kterém můžete:
- Zadávat další matematické výrazy.
- Přiřazovat nové hodnoty proměnným (např. `x = 5`).
- Aktualizovat substituce a znovu řešit systém.
- Procházet nápovědu a ovládat další funkce.

### Seznam dostupných příkazů

- **`help`**  
  Zobrazí nápovědu se seznamem všech dostupných příkazů a jejich stručným popisem.

- **`equations`**  
  Vypíše aktuální systém rovnic se započítanými substitucemi. Každá rovnice je očíslovaná pro snadnější orientaci.

- **`substitutions`**  
  Zobrazí aktuální substituce, tj. seznam symbolů a hodnot, které již byly nahrazeny.

- **`solve`**  
  Spustí opětovné řešení systému rovnic s aktuálními hodnotami. Tento příkaz je užitečný, pokud provedete nějaké změny v substitucích.

- **`vars`**  
  Vypíše proměnné, pro které se řeší systém rovnic, což vám připomene, na které neznámé se soustředíte.

- **`delete`**  
  Vymaže aktuální uloženou relaci. Tento příkaz vyžaduje potvrzení specifickým textem ("Matous je nejlepsi"), aby nedošlo k náhodnému smazání dat.

- **`save`**  
  Uloží aktuální stav (rovnice, substituce, řešení a proměnné) do souboru `circuit_session.pkl`.

- **`exit` / `quit`**  
  Uloží aktuální relaci a ukončí interaktivní režim.

- **Matematické výrazy a přiřazení:**  
  Kromě výše uvedených příkazů můžete zadávat libovolné matematické výrazy, které program vyhodnotí. Pokud výraz obsahuje přiřazení (např. `x = 5`), aktualizuje se substituční seznam, což znamená, že od té chvíle bude symbol `x` nahrazen hodnotou `5`.

## Ukládání a načítání relací

Relace se ukládá do souboru `circuit_session.pkl` pomocí funkce `save_session`. Při opětovném spuštění projektu program zkontroluje, zda tento soubor existuje:
- Pokud ano, načte se předchozí relace a pokračuje se v interaktivním režimu.
- Pokud ne, budete vyzváni k zadání nových rovnic a dalších údajů.

## Poznámky

- **Formátování výstupu:**  
  Zadáním výrazu obsahujícího klíčové slovo `latex` se výstup přepne do LaTeX formátu, což může být užitečné při tvorbě přehlednějších matematických zápisů.

- **Bezpečnostní opatření:**  
  Příkaz `delete` vyžaduje specifické potvrzení, aby se předešlo náhodnému vymazání dat.

- **Flexibilita interaktivního režimu:**  
  Interaktivní režim funguje jako dynamický kalkulátor, který umožňuje nejen zadávat a upravovat rovnice, ale také průběžně sledovat změny v substitucích a řešení.
