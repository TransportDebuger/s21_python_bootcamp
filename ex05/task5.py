def isValidFloat(str):
    if not str:
        return False
    allowedChars = set("0123456789-.")
    if not all(char in allowedChars for char in str):
        return False
    if str.count("-") > 1 or (str.count("-") == 1 and str[0] != "-"):
        return False
    if str.count(".") > 1:
        return False
    return True

def strToFloat(str):
    
    if not isValidFloat(str):
        raise ValueError("Incorrect input")

    if "." in str:
        integerPart, fractalPart = str.split(".")
    else:
        integerPart, fractalPart = str, "0"

    intval = 0
    sign = 1
    if integerPart and integerPart[0] == "-":
        sign = -1
        integerPart = integerPart[1:]
    for char in integerPart:
        intval = intval * 10 + int(char)

    fractval = 0
    for i, char in enumerate(fractalPart):
        fractval += int(char) * (10 ** -(i + 1))
    return sign * (intval + fractval)

def main():
    try:
        str = input()
        number = strToFloat(str)

        result = number * 2
        print(f"{result:.3f}")
        # print("{:.3f}".format(result))
        # print("%.3f" % result)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()