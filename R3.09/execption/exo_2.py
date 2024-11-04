
def open_file(file_name):
    try:
        with open('fichier.txt', 'r') as f:
            for l in f:
                l = l.rstrip("\n\r")
                print(l)

    except FileNotFoundError:
        print('File not found')
    except PermissionError:
        print('Permission denied')
    except Exception as e:
        print('An error occurred:', e)


def main():
    open_file('fichier.txt')

main()


