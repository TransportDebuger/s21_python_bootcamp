def isPalindrome(val):
    if val < 0:
        return False
    originalNum = val
    reversedNum = 0
    while val > 0:
        digit = val % 10
        reversedNum  = reversedNum  * 10 + digit
        val = val // 10 
    return originalNum == reversedNum

def main():
    number = int(input())
    print(isPalindrome(number))

if __name__ == "__main__":
    main()