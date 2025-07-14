import os
import glob


def get_text_files(directory):
    """Get all text files in the specified directory"""
    files_path = os.path.join(directory, "*.txt")
    return sorted(glob.glob(files_path))


def merge_text_files(input_dir, output_file):
    """Merge all text files from input directory into a single output file"""
    # Get all text files from the input directory
    text_files = get_text_files(input_dir)
    print(f"Found {len(text_files)} text files to merge")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Merge contents
    merged_content = []
    for file_path in text_files:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Add file header and content to the merged content
            merged_content.append(f"--- {filename} ---\n\n{content}\n\n")
            print(f"Added content from {filename}")
        except Exception as e:
            print(f"Error processing file {filename}: {e}")

    # Write merged content to output file
    if merged_content:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(merged_content))
        print(f"All content successfully merged into {output_file}")
    else:
        print("No content was merged, output file not created")


def main():
    input_dir = "./temp/translated"
    output_file = "./temp/combined_translation.txt"

    merge_text_files(input_dir, output_file)
    print("Merge process completed")


if __name__ == "__main__":
    main()
