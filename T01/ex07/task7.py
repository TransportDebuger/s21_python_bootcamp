def main():
    import sys
    
    N, M = map(int, sys.stdin.readline().split())
    grid = [list(map(int, sys.stdin.readline().split())) for _ in range(N)]
    dp = [[0] * M for _ in range(N)]
    dp[0][0] = grid[0][0]
    for j in range(1, M):
        dp[0][j] = dp[0][j-1] + grid[0][j]
    for i in range(1, N):
        dp[i][0] = dp[i-1][0] + grid[i][0]
    for i in range(1, N):
        for j in range(1, M):
            dp[i][j] = grid[i][j] + max(dp[i-1][j], dp[i][j-1])
    print(dp[N-1][M-1])

# Запуск программы
if __name__ == "__main__":
    main()