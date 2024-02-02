import os

import pytest

from wikitextparser.parser import WikiTextParser

parser = WikiTextParser()


def file_paths():
    data_dir = "tests/data"
    for f in os.listdir(data_dir):
        if f.endswith(".txt"):
            yield os.path.join(data_dir, f)



@pytest.mark.parametrize("file_path", file_paths())
def test_parse_file(file_path):
    """
    Test that uses the fixture to iterate through the file paths
    and call the parse method for each file
    """

    with open(file_path, "r") as f:
        file_contents = f.read()
    try:
        ast = parser.parse(file_contents)
        os.makedirs("tests/images", exist_ok=True)
        parser.print_as_image(ast, f"tests/images/{os.path.basename(file_path)}.svg")
        reconstructed_text = parser.reconstruct(ast)
        # Assert the expected results based on your parsing logic
        assert reconstructed_text == file_contents

    except Exception as e:
        print(f"Error parsing file: {file_path}")
        raise e  # Re-raise the exception to fail the test
