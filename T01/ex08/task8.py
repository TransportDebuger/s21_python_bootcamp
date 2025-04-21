def main():
    import sys

    N = int(sys.stdin.readline())
    unique_numbers = set()
    for _ in range(N):
        number = int(sys.stdin.readline())
        unique_numbers.add(number)
    print(len(unique_numbers))

if __name__ == "__main__":
    main()