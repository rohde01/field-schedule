import os

def merge_files(input_files, output_file):
    try:
        with open(output_file, 'w') as outfile:
            for file in input_files:
                if os.path.isfile(file):
                    with open(file, 'r') as infile:
                        outfile.write(infile.read())
                        outfile.write('\n')  # Add newline to separate contents of different files
                else:
                    print(f"Warning: {file} not found.")
        print(f"All files merged into {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Define the list of input files
    input_files = [
        'config.py',
        'club_data.py',
        'constraints.py',
        'dbu_requirements.py',
        'model.py',
        'utils.py',
        'main.py'
    ]

    # Define the output file
    output_file = 'merged_output.py'

    # Merge the files
    merge_files(input_files, output_file)
