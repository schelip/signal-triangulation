import sys, json

global receivers_data,  n_receivers, potency_values

def main(argv):
    global receivers_data

    if len(argv) <= 1:
        print_help()
        return

    if (not read_receivers_data(argv[1])):
        return
    
    match argv[2]:
        case "-h" | "--help":
            print_help()
        case "-v" | "--values":
            get_values_arguments(argv[3:])
        case "-i" | "--interactive":
            get_values_input()
        case _:
            print_help()


def read_receivers_data(file_name):
    global receivers_data
    global n_receivers
    try:
        with open(file_name, 'r') as f:
            if len(f.readlines()) <= 0:
                print("Bad file format: empty file")
                return

            f.seek(0)
            receivers_data = json.load(f)
            n_receivers = len(receivers_data)

            if n_receivers <= 3:
                print("Bad file format: at least 3 receivers are needed")
                return

            for i in range(n_receivers):
                if len(receivers_data[i]) < 4:
                    x, y = receivers_data[i][0], receivers_data[i][1]
                    print(f"Bad file format: receiver {i} (possibly at coords ({x}, {y})) does not have enough information")
                    return
                
            return True    
    except FileNotFoundError:
        print("Invalid arguments: file with receivers data not found")
    except json.JSONDecodeError:
        print("Bad file format: invalid JSON")


def print_help():
    print("""
Usage: path command [values]
Where path identifies the file with the receivers data and command is one of:
-v|--values       : parses the next n arguments and starts the program with n receivers and the
                    values of the arguments as the potency received by the receivers
-i|--interactive  : starts the program in interactive mode, asking for the number of receivers and the potency received values one by one
-h|--help         : shows this help menu
    """)


def get_values_arguments(values):
    if len(values) < 3:
        print("Invalid arguments: at least 3 potency received values needs to be passed as an argument")
        return
    try:
        values = [float(value) for value in values]
    except ValueError:
        print("Invalid arguments: at least one of the values is not a real number")
        return
    
    triangulate(values)


def get_values_input():
    global n_receivers
    values = []

    for i in range(n_receivers):
        while True:
            print(f"Input the potency received value for the receiver {i + 1}: ")
            try:
                values.append(float(input()))
                break
            except ValueError:
                print("Invalid input: not a real number")
                continue

    triangulate(values)


def triangulate(values):
    global receivers_data
    print(receivers_data)

if __name__ == "__main__":
    main(sys.argv)