import csv
import re
import pathlib
import json
import unicodedata


def parse_data(
    path_report_text_input: pathlib.PosixPath,
    path_focus_area_json_output: pathlib.PosixPath,
    path_skills_json_output: pathlib.PosixPath,
) -> None:
    """
    Receieves paths to a csv file that contains all text associated with the leadership assessment
    report. Parses the data and creates two json files which are used for generating the report

    Args:
        param1(pathlib.PosixPath): path to the input csv file containing raw text
        param2(pathlib.PosixPath): path for where the focus area json file is stored
        param3(pathlib.PosixPath): path for where the skills json file is stored

    Returns:
        None
    """

    with open(path_report_text_input, "r") as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        header_split_rows = header[5:]

        focus_areas_dict = {}
        skills_dict = {}

        for row in reader:
            for i, cell in enumerate(row):
                # Replace \u2019 with a regular apostrophe
                replaced_cell = (
                    unicodedata.normalize("NFKD", cell)
                    .encode("ascii", "ignore")
                    .decode("utf-8")
                )
                row[i] = replaced_cell

            if row[0] not in focus_areas_dict.keys():
                focus_areas_dict[row[0]] = []
            focus_areas_dict[row[0]].append(row[1])

            skills_dict[row[1]] = {}

            skills_dict[row[1]]["description"] = row[2]
            skills_dict[row[1]]["Overview-Performance strength"] = row[3]
            skills_dict[row[1]]["Overview-Improvement Opportunities"] = row[4]

            remaining_rows = row[5:]

            for i, val in enumerate(remaining_rows):
                sentences = re.split(r"\d+[\.,]", val)
                sentences = [
                    sentence.strip() for sentence in sentences if sentence.strip()
                ]
                skills_dict[row[1]][header_split_rows[i]] = []
                for sentence in sentences:
                    skills_dict[row[1]][header_split_rows[i]].append(sentence)

    with open(path_focus_area_json_output, "w") as json_file:
        json.dump(focus_areas_dict, json_file)

    with open(path_skills_json_output, "w") as json_file:
        json.dump(skills_dict, json_file)


if __name__ == "__main__":
    input_file = pathlib.Path(__file__).parent.parent / "resources" / "report_text.csv"
    focus_file = pathlib.Path(__file__).parent.parent / "resources" / "focus_area.json"
    skill_file = pathlib.Path(__file__).parent.parent / "resources" / "skills.json"
    parse_data(input_file, focus_file, skill_file)
