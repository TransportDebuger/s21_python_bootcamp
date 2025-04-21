def main():
    vector1 = [float(x) for x in input().split()]
    vector2 = [float(x) for x in input().split()]
    dot_product = sum(v1 * v2 for v1, v2 in zip(vector1, vector2))
    print(dot_product)

if __name__ == "__main__":
    main()