import sys, json, numpy as np

def main(argv: list[any]) -> None:
    """Main procedure, calls the functions to receive the data, prepare the data and then calculate the result

    Args:
        argv (list): command line arguments
    """
    pivot = 0
    
    if len(argv) <= 1:
        print_help()
        return

    receivers_data = read_receivers_data(argv[1])
    if not receivers_data:
        return
    
    A = get_coeficients_matrix(receivers_data, pivot)
    if not type(A) is np.ndarray:
        return
    
    potency_values = None

    match argv[2]:
        case "-v" | "--values":
            potency_values = get_potency_values_arguments(argv[3:])
        case "-i" | "--interactive":
            potency_values = get_potency_values_input(len(receivers_data))
        case _: # including -h | --help
            print_help()
            return
        
    if potency_values == None:
        print("Error reading potency values")
        return
    if len(potency_values) != len(receivers_data):
        print(f"Invalid arguments: inadequate number of potency values for receivers (expected {len(receivers_data)})")

    B = get_results_matrix(receivers_data, potency_values, pivot)

    if not type(B) is np.ndarray:
        return
    
    triangulate(A, B)

def print_help() -> None:
    """Prints usage info for the program"""
    print("""
Usage: path command [values]
Where path identifies the file with the receivers data and command is one of:
-v|--values       : parses the next n arguments and starts the program with n receivers and the
                    values of the arguments as the potency received by the receivers
-i|--interactive  : starts the program in interactive mode, asking for the number of receivers
                    and the potency received values one by one
-h|--help         : shows this help menu
    """)


def read_receivers_data(file_name: str) -> list[dict[float, float, float, float]]:
    """Tries to read the contents of a json file and returns the dict with the data of the receivers

    Args:
        file_name (str): name of the file to be read

    Returns:
        False: if the reading operation failed;
        list[dict[float, float, float, float]]: the dicts containing the receivers data, following the structure:
        [
            {
                x: float - the x coordinate of the receiver
                y: float - the y coordinate of the receiver
                p0: float - reference potency value, measured 1 meter from the receiver
                L: float - attenuation factor for the receiver
            }
        ], if the contents were succesfuly read.
    """
    try:
        with open(file_name, 'r') as f:
            if len(f.readlines()) <= 0:
                print("Bad file format: empty file")
                return False
            
            f.seek(0)
            receivers_data = json.load(f)
            n_receivers = len(receivers_data)

            if n_receivers <= 3:
                print("Bad file format: at least 3 receivers are needed")
                return False

            for i in range(n_receivers):
                if len(receivers_data[i]) < 4:
                    x, y = receivers_data[i][0], receivers_data[i][1]
                    print(f"Bad file format: receiver {i} (possibly at coords ({x}, {y})) does not have enough information")
                    return False

            return receivers_data    
    except FileNotFoundError:
        print("Invalid arguments: file with receivers data not found")
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
        return [float(value) for value in arguments]
    except ValueError:
        print("Invalid arguments: at least one of the values is not a real number")
    return False


def get_potency_values_input(n_receivers: int) -> list[float]:
    """Starts interactive mode, which will ask for as much potency values as expected, and returns those values

    Args:
        n_receivers (int): how many receivers there are, therefore how many values to ask for

    Returns:
        list[float]: the potency values informed
    """
    potency_values = []
    for i in range(n_receivers):
        while True:
            print(f"Input the potency received value for the receiver {i + 1}: ")
            try:
                potency_values.append(float(input()))
                break
            except ValueError:
                print("Invalid input: not a real number")
                continue
    return potency_values


def get_coeficients_matrix(receivers_data: list[dict[float, float, float, float]],
                           pivot: float) -> np.ndarray:
    """Generates a matrix (A) from the receivers data, based on their coordinates. This matrix comes
    from the position equations for each receiver, contructed by the Pithagorean Theorem, of the form
        fk(x, y, z) = (x - xk)^2 + (y - yk)^2 = dk^2
    which are then expanded to
        fk(x, y, z) = x^2 - 2*x*xk + xk^2 + y^2 - 2*y*yk + yk^2 = dk^2
    and grouped as
        fk(x, y, z) = x^2 + xk^2 + y^2 + yk^2 - 2*(x*xk + y*yk) = ck
    finally, they are linearized using an arbitrary pivot number (e.g 1)
        f1 - f2 = 2*x*(x2 - x1) + 2*y*(y2 - y1) = c2 - c1
        f1 - f3 = 2*x*(x3 - x1) + 2*y*(y3 - y1) = c3 - c1
        ...
        f1 - fm = 2x(xm - x1) + 2y(ym - y1) = c2 - c1
    and represented in matrix notation
        | 2*(x2 - x1)    2*(y2 - y1)|             |c2 - c1|
        | 2*(x3 - x1)    2*(y3 - y1)|       |x|   |c3 - c1|
        |...                        |   x   |y| = |...    | <> A x X = B
        | 2*(xm - x1)    2*(ym - y1)|       |z|   |cm - c1|

    Args:
        receivers_data (list[dict[float, float, float, float]]): the receivers data, including their coordinates
        pivot (float): the arbitrary pivot number to linearize the system

    Returns:
        np.ndarray: The Mx2 coeficients matrix
    """
    A = np.array([
        [2 * (receivers_data[i]["x"] - receivers_data[pivot]["x"]), 2 * (receivers_data[i]["y"] - receivers_data[pivot]["y"])]
        for i in range(len(receivers_data)) if i != pivot])
    
    if A.shape[0] == A.shape[1] and np.linalg.det(A) == 0:
        print("Bad receivers data: coeficient matrix based on the positions has null determinant")
        return False
    
    return A


def get_estimated_distance(receiver_data: dict[float, float, float, float], value: float):
    """Calculates the estimated distance between a receiver and the emissor using the formula
    
    d = 10^((p0 - p) / (10 * L))

    Where p0 is the expected potency value, p is the received potency value and L is the attenuation factor

    Args:
        receiver_data (dict[float, float, float, float]): the receiver data dictionary, inclding the keys p0 and L
        value (float): the received potency value

    Returns:
        float: the estimated distance
    """
    return 10**((receiver_data["p0"] - value) / (10 * receiver_data["L"]))


def get_results_matrix(receivers_data: list[dict[float, float, float, float]],
                       potency_values: list[float],
                       pivot: int) -> np.ndarray:
    """Generates a matrix (B) with the results of the linearized equations, as seen on the summary for get_coeficients_matrix.

    Args:
        receivers_data (list): a list of the receivers data
        potency_values (list): the received potency values for each receiver
        pivot (int): the arbitrary pivot number to linearize the system

    Returns:
        np.ndarray: The Mx1 results matrix
    """
    d_pivot = get_estimated_distance(receivers_data[pivot], potency_values[pivot])
    return np.array([get_estimated_distance(receivers_data[i], potency_values[i]) - d_pivot
                  for i in range(len(receivers_data)) if i != pivot])


def triangulate(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    print(A)
    print(B)


if __name__ == "__main__":
    main(sys.argv)