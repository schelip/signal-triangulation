import sys, json, random as rd, numpy as np

def main(argv: list[any]) -> None:
    """Main procedure, calls the functions to receive the data, prepare the data and then calculate the result

    Args:
        argv (list): command line arguments
    """
    
    if len(argv) <= 1:
        print_help()
        return

    receptors_data = read_receptors_data(argv[1])
    if not receptors_data:
        return
    
    potency_values, pivot = None, None
    n_receptors = len(receptors_data)

    if argv[2] == "-v" or argv[2] == "--values":
        potency_values = get_potency_values_arguments(argv[3:])
        pivot = get_pivot_arguments(n_receptors, argv[-2:])
    elif argv[2] == "-i" or argv[2] == "--interactive":
        potency_values = get_values_input(n_receptors)
        pivot = get_pivot_input(n_receptors)
    else:
        print_help()
        return
        
    if potency_values == None or potency_values == False:
        print("Error reading potency values")
        return
    if len(potency_values) != len(receptors_data):
        print(f"Invalid arguments: inadequate number of potency values for receptors (expected {len(receptors_data)})")
        return
    if pivot != 0 and (pivot == None or not pivot):
        print("Error getting pivot")
        return

    A = get_coeficients_matrix(receptors_data, pivot)
    if not type(A) is np.ndarray:
        return
    print(f"Receptor position coeficients matrix: \n{A}\n")

    print(f"Estimated distances:\n{np.array([get_estimated_distance(receptors_data[i], potency_values[i]) for i in range(len(receptors_data))])}\n")

    B = get_results_matrix(receptors_data, potency_values, pivot)

    if not type(B) is np.ndarray:
        return
    print(f"System results matrix: \n{B}\n")
    
    X = triangulate(A, B)

    if type(X) is np.ndarray:
        print(f"Estimated position: ({X.item(0)}, {X.item(1)})")
    

def print_help() -> None:
    """Prints usage info for the program"""
    print("""
Usage: path <command> [<values>...]
Where path identifies the file with the receptors data and command is one of:
-v|--values       : parses the next n arguments and starts the program with n receptors and the
                    values of the arguments as the potency received by the receptors
-p|--pivot        : parses the next argument as the equation to be used as a pivot to linearize the
                    system. can only be used AFTER a --values usage
-i|--interactive  : starts the program in interactive mode, asking for the number of receptors
                    and the potency received values one by one
-h|--help         : shows this help menu
    """)


def read_receptors_data(file_name: str) -> list[dict[float, float, float, float]]:
    """Tries to read the contents of a json file and returns the dict with the data of the receptors

    Args:
        file_name (str): name of the file to be read

    Returns:
        False: if the reading operation failed;
        list[dict[float, float, float, float]]: the dicts containing the receptors data, following the structure:
        [
            {
                x: float - the x coordinate of the receptor
                y: float - the y coordinate of the receptor
                p0: float - reference potency value, measured 1 meter from the receptor
                L: float - attenuation factor for the receptor
            }
        ], if the contents were succesfuly read.
    """
    try:
        with open(file_name, 'r') as f:
            if len(f.readlines()) <= 0:
                print("Bad file format: empty file")
                return False
            
            f.seek(0)
            receptors_data = json.load(f)
            n_receptors = len(receptors_data)

            if n_receptors < 3:
                print("Bad file format: at least 3 receptors are needed")
                return False

            for i in range(n_receptors):
                if len(receptors_data[i]) < 4:
                    x, y = receptors_data[i][0], receptors_data[i][1]
                    print(f"Bad file format: receptor {i} (possibly at coords ({x}, {y})) does not have enough information")
                    return False

            return receptors_data    
    except FileNotFoundError:
        print("Invalid arguments: file with receptors data not found")
    except json.JSONDecodeError:
        print("Bad file format: invalid JSON")
    return False


def get_potency_values_arguments(arguments: list[any]) -> list[float]:
    """Validates and returns the potency values passed as command line arguments on the -v mode

    Args:
        arguments (list): the values passed as command line arguments

    Returns:
        False: if the arguments passed were invalid
        list[float]: the potency values informed
    """
    if len(arguments) < 3:
        print("Invalid arguments: at least 3 potency received values needs to be passed as an argument")
        return False
    try:
        if arguments[-2] == "-p":
            arguments = arguments[:-2]
        return [float(value) for value in arguments]
    except ValueError:
        print("Invalid arguments: at least one of the values is not a real number")
    return False


def get_pivot_arguments(n_receptors: int, argv: list[any]) -> int:
    """Parses the arguments to get the pivot equation index or generates a random value

    Args:
        n_receptors (int): The number of receptors, for validation  
        argv (list[any]): The arguments passed to the command line

    Returns:
        False: If an error ocurred
        int: The read/generated pivot index
    """
    if argv[-2] == "-p":
        try:
            pivot = int(argv[-1])
            if pivot < 0 or pivot >= n_receptors:
                print(f"Invalid arguments: pivot value must be non-negative and adequate to the number of receptors {n_receptors} - 1 = {n_receptors - 1}")
                return False
            return pivot
        except ValueError:
            print("Invalid arguments: expected integer value for pivot")
            return False
    else:
        pivot = rd.randint(0, n_receptors - 1)



def get_values_input(n_receptors: int) -> list[float]:
    """Starts interactive mode, which will ask for as much potency values as expected, and returns those values

    Args:
        n_receptors (int): how many receptors there are, therefore how many values to ask for

    Returns:
        list[float]: the potency values informed
    """
    potency_values = []
    for i in range(n_receptors):
        while True:
            print(f"Input the potency received value for the receptor {i + 1}: ")
            try:
                potency_values.append(float(input()))
                break
            except ValueError:
                print("Invalid input: not a real number")
                continue
    return potency_values


def get_pivot_input(n_receptors: int) -> int:
    """Queries the user for the pivot equation index, or generates a random value

    Args:
        n_receptors (int): how many receptors there are, for validation

    Returns:
        int: the read/generated pivot index
    """
    while True:
        print(f"Input the pivot for the linearization (max {n_receptors - 1}) or <enter> for random: ")
        try:
            inp = input()
            if inp == "":
                return rd.randint(0, n_receptors - 1)
            else:
                pivot = int(inp)
                if pivot < 0 or pivot >= n_receptors:
                    print(f"Invalid arguments: pivot value must be non-negative and not higher than number of receptors {n_receptors}")
                    continue
                return pivot
        except ValueError:
            print("Invalid input: not an integer")
            continue


def get_coeficients_matrix(receptors_data: list[dict[float, float, float, float]],
                           pivot: float) -> np.ndarray:
    """Generates a matrix (A) from the receptors data, based on their coordinates. This matrix comes
    from the position equations for each receptor, contructed by the Pithagorean Theorem, of the form
        fk(x, y, z) = (x - xk)^2 + (y - yk)^2 = dk^2
    which are then expanded to
        fk(x, y, z) = x^2 - 2*x*xk + xk^2 + y^2 - 2*y*yk + yk^2 = dk^2
    and grouped as
        fk(x, y, z) = x^2 + xk^2 + y^2 + yk^2 - 2*(x*xk + y*yk) = ck
    finally, they are linearized using an arbitrary pivot number (e.g 1)
        f2 - f1 = 2*x*(x1 - x2) + 2*y*(y1 - y2) = c2 - c1
        f3 - f1 = 2*x*(x1 - x3) + 2*y*(y1 - y3) = c3 - c1
        ...
        fm - f1 = 2x(x1 - xm) + 2y(y1 - ym) = cm - c1
    and represented in matrix notation
        | 2*(x1 - x2)    2*(y1 - y2)|             |c2 - c1|
        | 2*(x1 - x3)    2*(y1 - y3)|       |x|   |c3 - c1|
        |...                        |   x   |y| = |...    | <> A x X = B
        | 2*(x1 - xm)    2*(y1 - ym)|       |z|   |cm - c1|

    Args:
        receptors_data (list[dict[float, float, float, float]]): the receptors data, including their coordinates
        pivot (float): the arbitrary pivot number to linearize the system

    Returns:
        False: if an error ocurred
        np.ndarray: The Mx2 coeficients matrix
    """
    A = np.array([
        [2 * (receptors_data[pivot]["x"] - receptors_data[i]["x"]), 2 * (receptors_data[pivot]["y"] - receptors_data[i]["y"])]
        for i in range(len(receptors_data)) if i != pivot])
    
    if A.shape[0] == A.shape[1] and np.linalg.det(A) == 0:
        print("Bad receptors data: coeficient matrix based on the positions has null determinant")
        return False
    
    return A


def get_estimated_distance(receptor_data: dict[float, float, float, float], value: float):
    """Calculates the estimated distance between a receptor and the emissor using the formula
    
    d = 10^((p0 - p) / (10 * L))

    Where p0 is the expected potency value, p is the received potency value and L is the attenuation factor

    Args:
        receptor_data (dict[float, float, float, float]): the receptor data dictionary, inclding the keys p0 and L
        value (float): the received potency value

    Returns:
        float: the estimated distance
    """
    return 10 ** ((receptor_data["p0"] - value) / (10 * receptor_data["L"]))


def get_results_matrix(receptors_data: list[dict[float, float, float, float]],
                       potency_values: list[float],
                       pivot: int) -> np.ndarray:
    """Generates a matrix (B) with the results of the linearized equations, as seen on the summary for get_coeficients_matrix.

    Args:
        receptors_data (list): a list of the receptors data
        potency_values (list): the received potency values for each receptor
        pivot (int): the arbitrary pivot number to linearize the system

    Returns:
        np.ndarray: The Mx1 results matrix
    """
    d_pivot = get_estimated_distance(
        receptors_data[pivot],
        potency_values[pivot]
    ) ** 2 - receptors_data[pivot]["x"] ** 2 - receptors_data[pivot]["y"] ** 2

    return np.array([
        (get_estimated_distance(receptors_data[i], potency_values[i]) ** 2 -
         receptors_data[i]["x"] ** 2 -
         receptors_data[i]["y"] ** 2) -
         d_pivot
        for i in range(len(receptors_data))
        if i != pivot])


def triangulate(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Triangulates the position of the emissor using the linearized system in matrix form

    Args:
        A (np.ndarray): Receptor position coeficients matrix
        B (np.ndarray): System results matrix

    Returns:
        np.ndarray: 1D array with the estimated X and Y coordinates
    """
    return np.linalg.inv(A.T @ A) @ A.T @ B


if __name__ == "__main__":
    main(sys.argv)