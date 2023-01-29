import sys

def main(argv):
    match argv[1]:
        case "-v" | "--values":
            get_values_arguments(argv[2:])
        case "-h" | "--help":
            print_help()
        case "-i" | "--interactive":
            get_values_input()
        case _:
            print_help()


def print_help():
    print("""
        Usage: command [arguments]
        Possible commands:
        -v|--values\t\t: parses the next n arguments and starts the program with n receivers and the values of the arguments as the potency received by the receivers
        -i|--interactive\t: starts the program in interactive mode, asking for the number of receivers and the potency received values one by one
        -h|--help\t\t: shows this help menu
    """)


def get_values_arguments(values):
    if len(values) <= 0:
        print("Invalid arguments: at least one potency received value needs to be passed as an argument")
        return
    try:
        values = [float(value) for value in values]
    except ValueError:
        print("Invalid arguments: at least one values is not a real number")
        return
    
    triangulate(values)


def get_values_input():
    n_receivers = -1
    values = []

    while True:
        print("Input the number of receptors: ")
        try:
            n_receivers = int(input())
        except ValueError:
            print("Invalid input: not a positive integer")
            continue
        if (n_receivers <= 0):
            print("Invalid input: at least one receiver is needed")
        else: break

    for i in range(n_receivers):
        while True:
            print("Input the potency received value for the receiver " + str(i + 1) + ": ")
            try:
                values.append(float(input()))
                break
            except ValueError:
                print("Invalid input: not a real number")
                continue

    triangulate(values)


def triangulate(values):
    print(values)

if __name__ == "__main__":
    main(sys.argv)