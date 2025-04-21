from collections import deque

def readMatrix(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            matrix = [list(map(int, line.split())) for line in file]
    except (FileNotFoundError) as err:
        raise ValueError(f"{err}")
    return matrix


def is_square(rows, cols, start_row, start_col, size, matrix):
    for i in range(start_row, start_row + size):
        for j in range(start_col, start_col + size):
            if matrix[i][j] != 1:
                return False
    return True


def is_circle(rows, cols, start_row, start_col, size, matrix):
    center_row = start_row + ((size-1) / 2)
    center_col = start_col + ((size-1) / 2)
    if size % 2:
        radius = (size - 1) / 2
    else: 
        radius = size / 2
    for i in range(start_row, start_row + size):
        for j in range(start_col, start_col + size):
            distance_sq = (i - center_row) ** 2 + (j - center_col) ** 2
            if matrix[i][j] == 1 and distance_sq > radius ** 2:
                return False
            if matrix[i][j] == 0 and distance_sq <= radius ** 2:
                return False
    return True


def findShapes(matrix):
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    squares = 0
    circles = 0
    
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] == 1 and not visited[i][j]:
                min_row, max_row = i, i
                min_col, max_col = j, j
                queue = deque([(i, j)])
                visited[i][j] = True

                while queue:
                    row, col = queue.popleft()
                    for deltar, deltac in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        r, c = row + deltar, col + deltac
                        if 0 <= r < rows and 0 <= c < cols and matrix[r][c] == 1 and not visited[r][c]:
                            visited[r][c] = True
                            queue.append((r, c))
                            min_row = min(min_row, r)
                            max_row = max(max_row, r)
                            min_col = min(min_col, c)
                            max_col = max(max_col, c)
                height = max_row - min_row + 1
                width = max_col - min_col + 1
                if height == width:
                    if is_square(rows, cols, min_row, min_col, height, matrix):
                        squares += 1
                    elif is_circle(rows, cols, min_row, min_col, height, matrix):
                        circles += 1

    return squares, circles


def main():
    try:
        matrix = readMatrix('input.txt')
        squares, circles = findShapes(matrix)
        print(squares, circles)
    except ValueError as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    main()