def split_file(input_file, output_file1, output_file2):
    with open(input_file, 'r', encoding='latin-1') as file:
        lines = file.readlines()

    total_lines = len(lines)
    half_lines = total_lines // 2

    with open(output_file1, 'w', encoding='latin-1') as file1:
        file1.writelines(lines[:half_lines])

    with open(output_file2, 'w', encoding='latin-1') as file2:
        file2.writelines(lines[half_lines:])

if __name__ == "__main__":
    input_file = "rockyou.txt"
    output_file1 = "rockyou_half1.txt"
    output_file2 = "rockyou_half2.txt"

    split_file(input_file, output_file1, output_file2)

    print("Splitting complete. Check the files", output_file1, "and", output_file2)
