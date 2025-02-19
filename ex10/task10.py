def main():
    import sys

    try:
        N, required_time = map(int, sys.stdin.readline().split())
        if N < 2:
            raise ValueError("Number of devices must be equal or greater 2.")

        devices = []
        for _ in range(N):
            year, cost, time = map(int, sys.stdin.readline().split())
            devices.append((year, cost, time))

        year_to_devices = {}
        for device in devices:
            year, cost, time = device
            if year not in year_to_devices:
                year_to_devices[year] = []
            year_to_devices[year].append((cost, time))

        min_total_cost = float('inf')

        for year, devices_in_year in year_to_devices.items():
            if len(devices_in_year) < 2:
                continue

            for i in range(len(devices_in_year)):
                for j in range(i + 1, len(devices_in_year)):
                    cost1, time1 = devices_in_year[i]
                    cost2, time2 = devices_in_year[j]
                    if time1 + time2 == required_time:
                        total_cost = cost1 + cost2
                        if total_cost < min_total_cost:
                            min_total_cost = total_cost

        if min_total_cost == float('inf'):
            raise ValueError("The pair of suitable devices not found.")

        # Вывод результата
        print(min_total_cost)

    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)

# Запуск программы
if __name__ == "__main__":
    main()