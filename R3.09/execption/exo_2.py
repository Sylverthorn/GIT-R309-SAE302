
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
    except FileExistsError:
        print('File already exists')
    except IOError:
        print('An error occurred while reading the file')


def main():
    open_file('fichier.txt')

main()


