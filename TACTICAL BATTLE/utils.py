def limpiar_terminal():
    print(chr(27) + "[2J")


def validar_celda(celda, max_col, max_row):
    if len(celda) != 2:
        return False
    if celda[0] < 'A' or celda[0] > max_col:
        return False

    if celda[1] < '1' or celda[1] > max_row:
        return False
    return True


def comprobar_celda_disponible(celda, equipo):
    for p in equipo:
        if p.posicion == celda:
            return False
    return True


def validar_celda_contigua(celda1, celda2):
    if ord(celda1[0]) - 1 == ord(celda2[0]) or ord(celda1[0]) + 1 == ord(celda2[0]): # La letra es contigua
        return ord(celda1[1]) == ord(celda2[1]) # El numero es igual

    if ord(celda1[1]) - 1 == ord(celda2[1]) or ord(celda1[1]) + 1 == ord(celda2[1]): # El numero es contiguo
        return ord(celda1[0]) == ord(celda2[0]) # La letra es igual

    return False


def main():
    print(validar_celda_contigua('C1', 'C3'))  # False
    print(validar_celda_contigua('B2', 'C3'))  # False
    print(validar_celda_contigua('C1', 'C0'))  # True
    print(validar_celda_contigua('C1', 'C2'))  # True
    print(validar_celda_contigua('C1', 'B1'))  # True
    print(validar_celda_contigua('C1', 'D1'))  # True


if __name__ == '__main__':
    main()
