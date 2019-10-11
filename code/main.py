import image_utils
import corner_finding
import grid_reading as grid_r
import grid_info as grid_i
import data_exporting
import tkinter as tk
import file_handling
import typing

answers_results = data_exporting.OutputSheet([x for x in grid_i.Field])
keys_results = data_exporting.OutputSheet([grid_i.Field.TEST_FORM_CODE])

app = tk.Tk()
input_directory = file_handling.prompt_folder(
    "Select a folder to import scans from")
image_paths = file_handling.filter_images(
    file_handling.list_file_paths(input_directory))
output_directory = file_handling.prompt_folder(
    "Select a folder to save results in")
app.destroy()

for image_path in image_paths:
    image = image_utils.get_image(image_path)
    prepared_image = image_utils.prepare_scan_for_processing(image)

    # Find the corners, skipping the image on failure
    try:
        corners = corner_finding.find_corner_marks(prepared_image)
    except corner_finding.CornerFindingError:
        print(f"{image_path.name}: Can't find corners.")
        continue

    # Establish a grid
    grid = grid_r.Grid(corners, grid_i.GRID_HORIZONTAL_CELLS,
                       grid_i.GRID_VERTICAL_CELLS, prepared_image)

    # Get the answers for questions
    answers = [
        grid_r.read_answer_as_string(i, grid)
        for i in range(grid_i.NUM_QUESTIONS)
    ]

    field_data: typing.Dict[grid_i.Field, str] = {}

    # Read the last name. If it indicates this exam is a key, treat it as such
    last_name = grid_r.read_field_as_string(grid_i.Field.LAST_NAME, grid)
    if last_name == grid_i.KEY_LAST_NAME:
        form_code_field = grid_i.Field.TEST_FORM_CODE
        field_data[form_code_field] = grid_r.read_field_as_string(
            form_code_field, grid)
        keys_results.add(field_data, answers)
        print(f"Processed '{image_path.name}' successfully as the key for form code {field_data[form_code_field]}.")
    else:
        field_data[grid_i.Field.LAST_NAME] = last_name
        for field in grid_i.Field:
            # Avoids re-reading the last name value to save some time
            if field is not grid_i.Field.LAST_NAME:
                field_data[field] = grid_r.read_field_as_string(field, grid)
        answers_results.add(field_data, answers)
        print(f"Processed '{image_path.name}' successfully.")


answers_results.save(output_directory / "results.csv")
if (keys_results.row_count != 0):
    keys_results.save(output_directory / "keys.csv")
print(f"Results saved to {str(output_directory)}")