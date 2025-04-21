def generatePascalTriangle(n):
    if n < 1:
        raise ValueError("Number of strings can't be less than 1.")

    triangle = []
    for row_num in range(n):
        row = [1]
        if triangle:
            prev_row = triangle[-1]
            row += [prev_row[i] + prev_row[i + 1] for i in range(len(prev_row) - 1)]
            row += [1]
        triangle.append(row)
    return triangle

def printPascalTringle(triangle):
    for row in triangle:
        print(*row)

def main():
    try:
        numOfRows = int(input())
        triangle = generatePascalTriangle(numOfRows)
        printPascalTringle(triangle)
    except ValueError as err:
        print(f"Error: {err}")
    

if __name__ == "__main__":
    main()