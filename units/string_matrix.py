def to_string(matrix):
    if type(matrix) is str:
        return matrix
    result = ""
    for row in matrix:
        result += "".join(str(x) for x in row)
    return result


def to_matrix(string):
    if type(string) is list:
        return string
    result = [[string[i * 6 + j] for j in range(6)] for i in range(6)]
    return result
