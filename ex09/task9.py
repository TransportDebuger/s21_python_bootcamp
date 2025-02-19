def main():
    import sys

    N, x = map(float, sys.stdin.readline().split())
    N = int(N)
    coefficients = []
    for _ in range(N):
        coefficient = float(sys.stdin.readline())
        coefficients.append(coefficient)
    derivative_value = 0
    for i in range(N):
        power = N - i
        derivative_value += power * coefficients[i] * (x ** (power - 1))
    print(f"{derivative_value:.3f}")

if __name__ == "__main__":
    main()