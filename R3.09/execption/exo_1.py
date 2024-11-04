
def divEntier(x: int, y: int) -> int:
    try:
        if x < y:
            return 0
        else:
            x = x - y
            return divEntier(x, y) + 1
    except x < 0 or y < 0:
        print("Erreur: Division par 0")
    except y == 0:
        print("Erreur: Division par 0")



def main():
    try:
        x = int(input("Entrez un entier x: "))
        y = int(input("Entrez un entier y: "))
        print(divEntier(x, y))
    except ValueError:
        print("Erreur: Veuillez entrer un entier")
    except ZeroDivisionError:
        print("Erreur: Division par 0")


main()