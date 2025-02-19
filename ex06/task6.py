import json
import sys

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Incorrect format of data. Key-value lists needed.")
            
            lists = []
            for key, value in data.items():
                if not isinstance(value, list):
                    raise ValueError(f"Incorrect data format: '{key}' must be a list.")
                lists.append(value)
            
            return lists
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Error loading data {e}")

def merge_sorted_lists(lists, key="year"):
    pointers = [0] * len(lists)
    merged = []

    while True:
        min_value = None
        min_index = -1

        for i in range(len(lists)):
            if pointers[i] < len(lists[i]):
                current_value = lists[i][pointers[i]][key]
                if min_value is None or current_value < min_value:
                    min_value = current_value
                    min_index = i

        if min_index == -1:
            break

        merged.append(lists[min_index][pointers[min_index]])
        pointers[min_index] += 1

    return merged

def main():
    try:
        lists = load_data("input.txt")

        for lst in lists:
            for movie in lst:
                if not isinstance(movie, dict) or "year" not in movie:
                    raise ValueError("Incorrect fil format. Data field 'year' not present.")

        merged_list = merge_sorted_lists(lists)

        print(json.dumps(merged_list, ensure_ascii=False, indent=2))
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)

if __name__ == "__main__":
    main()