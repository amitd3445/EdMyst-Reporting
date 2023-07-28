from .graphing import *
from .edy import *
from typing import Dict, Union, List
import pathlib
import json
import os
import shutil
import datetime as dt
import weasyprint
from jinja2 import Environment, FileSystemLoader


def leadership_report(payload: Dict) -> None:
    """
    Generate the interviewer assessment report by parsing the payload

    The report will analyze and provide relevant questions based on the strengths and weaknesses of the candidate

    Args:
        param1(Dict): The candidate's profile and assessment results

    Returns:
        None

    Raises:
        TypeError: Must receieve nested dictionaries as an argument

    Notes:
        The PDF report generated is stored in the results directory
    """

    _validate_payload(payload)
    dict_payload = _parse_payload(payload)
    dict_payload["skills"] = _modify_scores(dict_payload["skills"])
    _generate_all_graphics(dict_payload)
    _save_background_pic()
    report = _generate_final_report(dict_payload)
    print(dict_payload["candidate_profile"])
    return report
    # _delete_temp_files()


def _validate_payload(payload: Dict) -> None:
    """
    Data validation step to make sure that the input is of the right type

    Args:
        param (Dict): A JSON blob representing the data to be processed.

    Returns:
        None

    Raises:
        TypeError: Must receieve dictionary which specific keys
    """
    # json blob
    if not isinstance(payload, dict):
        raise TypeError("Input must be a dictionary")

    # name
    if "Candidate" not in payload or any(
        [x not in payload["Candidate"] for x in ["name", "company"]]
    ):
        raise TypeError("candidate profile keys are missing")

    # pace
    if "speech_rate" not in payload or any(
        [
            x not in payload["speech_rate"]
            for x in [
                "assessment",
                "timestamp_graph_data",
                "measured",
                "inference",
                "recommended",
            ]
        ]
    ):
        raise TypeError("pace keys are missing")

    # pause
    if "praat_output" not in payload or any(
        [
            x not in payload["praat_output"]
            for x in [
                "average_pause_length",
                "pauses_count_sentence",
                "assessment",
                "articulation_rate",
                "pauses_count_strategic",
                "pauses_count_sensory",
                "phonation_time",
                "speech_rate_syllables",
                "pauses_count_per_min",
                "pauses_count_long",
                "inference",
                "pauses_count_transition",
            ]
        ]
    ):
        raise TypeError("pause keys are missing")

    # fillers
    if "filler_words" not in payload or any(
        [
            x not in payload["filler_words"]
            for x in [
                "assessment",
                "analysis",
                "result",
                "total_words",
                "recommendation",
                "data",
            ]
        ]
    ):
        raise TypeError("filler word keys are missing")

    # repeated words
    if "repeated_words" not in payload or any(
        [
            x not in payload["repeated_words"]
            for x in ["assessment", "result", "total_words", "analysis", "data"]
        ]
    ):
        raise TypeError("repeated word keys are missing")

    # eye contact
    if "looking_at_camera" not in payload or any(
        [
            x not in payload["looking_at_camera"]
            for x in [
                "assessment",
                "average_percentage",
                "result",
                "inference",
                "recommendation",
                "data",
            ]
        ]
    ):
        raise TypeError("eye contact keys are missing")

    # smile
    if "smiling" not in payload or any(
        [
            x not in payload["smiling"]
            for x in [
                "assessment",
                "average_percentage",
                "result",
                "inference",
                "recommendation",
                "data",
            ]
        ]
    ):
        raise TypeError("smiling keys are missing")

    # sentiment
    if "sentiment" not in payload or any(
        [
            x not in payload["sentiment"]
            for x in ["assessment", "measured", "inference", "recommended"]
        ]
    ):
        raise TypeError("sentiment keys are missing")

    # volume
    if "power_db" not in payload or any(
        [x not in payload["power_db"] for x in ["assessment", "inference", "data"]]
    ):
        raise TypeError("volume keys are missing")

    # skills
    if "recruiter_skills" not in payload:
        raise TypeError()
    else:
        # path_focus_area = (
        #     pathlib.Path(__file__).parent.parent / "resources" / "focus_area.json"
        # )
        # with open(path_focus_area) as file:
        #     dict_focus_area = json.load(file)

        list_skills = [
            skill
            for list_of_skills in dict_focus_area.values()
            for skill in list_of_skills
        ]
        for skill in payload["recruiter_skills"].keys():
            if skill not in list_skills:
                raise TypeError(f"missing {skill} from recruiter skill list")


def _parse_payload(payload: Dict) -> Dict:
    """
    Parses the json blob representing the data to be processed in order to return a dictionary containing the relevant data

    Args:
        param (Dict): A JSON blob representing the data to be processed.

    Returns:
        Dict: a dictionary containing the relevant data used to generate the report
    """
    dict_parsed_data = {}

    # candidate profile
    dict_parsed_data["candidate_profile"] = payload["Candidate"]
    dict_parsed_data["candidate_profile"]["name"] = payload["Candidate"]["name"]
    dict_parsed_data["candidate_profile"]["company_name"] = payload["Candidate"][
        "company"
    ]

    # pace
    list_pace_keys = [
        "assessment",
        "timestamp_graph_data",
        "measured",
        "inference",
        "recommended",
    ]
    dict_parsed_data["pace"] = {
        key: payload["speech_rate"][key] for key in list_pace_keys
    }

    # pause
    list_pause_keys = [
        "average_pause_length",
        "pauses_count_sentence",
        "assessment",
        "articulation_rate",
        "pauses_count_strategic",
        "pauses_count_sensory",
        "phonation_time",
        "speech_rate_syllables",
        "pauses_count_per_min",
        "pauses_count_long",
        "inference",
        "pauses_count_transition",
    ]
    dict_parsed_data["pause"] = {
        key: payload["praat_output"][key] for key in list_pause_keys
    }

    # fillers
    list_filler_keys = [
        "assessment",
        "analysis",
        "result",
        "total_words",
        "recommendation",
        "data",
    ]
    dict_parsed_data["fillers"] = {
        key: payload["filler_words"][key] for key in list_filler_keys
    }

    # repeated words
    list_repeated_word_keys = [
        "assessment",
        "result",
        "total_words",
        "analysis",
        "data",
    ]
    dict_parsed_data["repeated_words"] = {
        key: payload["repeated_words"][key] for key in list_repeated_word_keys
    }

    # eye contact
    list_eye_contact_keys = [
        "assessment",
        "average_percentage",
        "result",
        "inference",
        "recommendation",
        "data",
    ]
    dict_parsed_data["eye_contact"] = {
        key: payload["looking_at_camera"][key] for key in list_eye_contact_keys
    }

    # smile
    list_smile_keys = [
        "assessment",
        "average_percentage",
        "result",
        "inference",
        "recommendation",
        "data",
    ]
    dict_parsed_data["smile"] = {
        key: payload["smiling"][key] for key in list_smile_keys
    }

    # sentiment
    list_sentiment_keys = ["assessment", "measured", "inference", "recommended"]
    dict_parsed_data["sentiment"] = {
        key: payload["sentiment"][key] for key in list_sentiment_keys
    }

    # volume
    list_volume_keys = ["assessment", "inference", "data"]
    dict_parsed_data["volume"] = {
        key: payload["power_db"][key] for key in list_volume_keys
    }

    # skills
    # path_focus_area = (
    #     pathlib.Path(__file__).parent.parent / "resources" / "focus_area.json"
    # )
    # with open(path_focus_area) as file:
    #     dict_focus_area = json.load(file)

    list_skills = list(
        set(
            skill
            for list_of_skills in dict_focus_area.values()
            for skill in list_of_skills
        )
    )
    dict_parsed_data["skills"] = {}
    for skill in list_skills:
        if skill in payload["recruiter_skills"].keys():
            dict_parsed_data["skills"][skill] = payload["recruiter_skills"][skill]
    return dict_parsed_data


def _modify_scores(
    dict_scores: Dict[str, Union[float, int]]
) -> Dict[str, Dict[str, Union[float, int]]]:
    """
    Modify the scores dictionary to make the data more manageable

    Args:
        param1(Dict[str, Dict[str, int | str]]): The candidate's assessment results

    Returns:
        Dict[str, Dict[str, Union[float, int]]]:
    """
    # path_focus_area = (
    #     pathlib.Path(__file__).parent.parent / "resources" / "focus_area.json"
    # )
    # with open(path_focus_area) as file:
    #     dict_focus_area = json.load(file)

    dict_modified_scores = {key: {} for key in dict_focus_area.keys()}

    for skill, score in dict_scores.items():
        for focus_area, list_skills in dict_focus_area.items():
            if skill in list_skills:
                
                dict_modified_scores[focus_area][skill] = score
    print(dict_modified_scores)
    return dict_modified_scores


def _generate_all_graphics(paylaod):
    """
    Create all graphics for the report and save them to the /tmp folder for future use. Graphing
    functions are imported from the graphing.py module

    Args:
        param1(Dict):

    Returns:
        None
    """

    # generate bar chart for focus area/skills
    generate_skill_score_bar_charts(paylaod["skills"])

    # generate spider plot for focus area
    generate_focus_area_spider_plot(paylaod["skills"])

    # generate color bar for all skills
    generate_skill_score_colorbar_plots(paylaod["skills"])

    # generate color bar for pace
    generate_color_bar_plot(
        metric_name="pace",
        metric_unit_measurement=" words/min",
        metric_average=paylaod["pace"]["measured"]["average"],
        metric_middle_max=150,
        metric_middle_min=120,
        bar_max=210,
        bar_min=60,
        bar_annotations={"high": "Too Fast", "middle": "Optimal", "low": "Too Slow"},
        colorbar_range=[60, 100, 120, 150, 170, 210],
        colorbar_colors=[
            "#FAC2B6",
            "#FADDB6",
            "#BBFAB6",
            "#BBFAB6",
            "#FADDB6",
            "#FAC2B6",
        ],
    )

    # generate line chart for pace
    generate_line_chart(
        metric_name="pace",
        metric_unit_measurement="words/min",
        metric_average=paylaod["pace"]["measured"]["average"],
        metric_middle_max=150,
        metric_middle_min=120,
        colorbar_min=60,
        colorbar_max=210,
        metric_time_series_x_y=paylaod["pace"]["timestamp_graph_data"],
        colorbar_range=[60, 100, 120, 150, 170, 210],
        colorbar_colors=[
            "#FAC2B6",
            "#FADDB6",
            "#BBFAB6",
            "#BBFAB6",
            "#FADDB6",
            "#FAC2B6",
        ],
    )

    # generate colorbar for eye contact
    generate_color_bar_plot(
        metric_name="eye_contact",
        metric_unit_measurement="%",
        metric_average=paylaod["eye_contact"]["average_percentage"],
        metric_middle_max=70,
        metric_middle_min=50,
        bar_max=100,
        bar_min=0,
        bar_annotations={"high": "High", "middle": "Optimal", "low": "Low"},
        colorbar_range=[0, 30, 50, 70, 100],
        colorbar_colors=["#FAC2B6", "#FADDB6", "#BBFAB6", "#BBFAB6", "#FADDB6"],
    )

    # generate colorbar for sentiment
    generate_color_bar_plot(
        metric_name="sentiment",
        metric_unit_measurement="%",
        metric_average=100 * paylaod["sentiment"]["measured"]["average"]
        if paylaod["sentiment"]["measured"]["average"] < 1
        else paylaod["sentiment"]["measured"]["average"],
        metric_middle_max=65,
        metric_middle_min=35,
        bar_max=100,
        bar_min=0,
        bar_annotations={"high": "Positive", "middle": "Neutral", "low": "Negative"},
        colorbar_range=[0, 30, 50, 85, 100],
        colorbar_colors=["#FAC2B6", "#FADDB6", "#FADDB6", "#BBFAB6", "#BBFAB6"],
    )

    # generate colorbar for smile
    generate_color_bar_plot(
        metric_name="smile",
        metric_unit_measurement="%",
        metric_average=100 * paylaod["smile"]["average_percentage"]
        if paylaod["smile"]["average_percentage"] < 1
        else paylaod["smile"]["average_percentage"],
        metric_middle_max=65,
        metric_middle_min=35,
        bar_max=100,
        bar_min=0,
        bar_annotations={"high": "Positive", "middle": "Neutral", "low": "Negative"},
        colorbar_range=[0, 30, 50, 85, 100],
        colorbar_colors=["#FAC2B6", "#FADDB6", "#FADDB6", "#BBFAB6", "#BBFAB6"],
    )

    # generate colorbar for volume
    generate_color_bar_plot(
        metric_name="volume",
        metric_unit_measurement=" dB",
        metric_average=paylaod["volume"]["inference"]["result"]["average_power"],
        metric_middle_max=80,
        metric_middle_min=60,
        bar_max=150,
        bar_min=0,
        bar_annotations={"high": "High", "middle": "Optimal", "low": "Low"},
        colorbar_range=[0, 30, 50, 60, 80, 90, 100, 150],
        colorbar_colors=[
            "#FB9993",
            "#FAC2B6",
            "#FADDB6",
            "#BBFAB6",
            "#BBFAB6",
            "#FADDB6",
            "#FAC2B6",
            "#FB9993",
        ],
    )

    # generate line chart for volume
    generate_line_chart(
        metric_name="volume",
        metric_unit_measurement="Decibels",
        metric_average=paylaod["volume"]["inference"]["result"]["average_power"],
        metric_middle_max=80,
        metric_middle_min=60,
        colorbar_min=0,
        colorbar_max=150,
        metric_time_series_x_y=paylaod["volume"]["data"],
        colorbar_range=[0, 30, 50, 60, 80, 90, 100, 150],
        colorbar_colors=[
            "#FB9993",
            "#FAC2B6",
            "#FADDB6",
            "#BBFAB6",
            "#BBFAB6",
            "#FADDB6",
            "#FAC2B6",
            "#FB9993",
        ],
    )

    # generate bar chart for pauses
    generate_stacked_bar_chart_pauses(paylaod["pause"])


def _save_background_pic(old_path_background_pic=None) -> None:
    """
    Save the background picture to the /tmp folder in order to be referenced by the html file

    Args:
        optional_arg (pathlib.Path): path to background picture

    Returns:
        None
    """
    # provide a path to the background pic or I'll just assume it's in the resources folder
    if old_path_background_pic is None:
        old_path_background_pic = (
            pathlib.Path(__file__).parent.parent / "resources" / "background.jpg"
        )

    new_path_background_pic = pathlib.Path(
        "/tmp/background.jpg"
    )  # .parent.parent / "tmp" / "background.jpg"
    shutil.copy(old_path_background_pic, new_path_background_pic)


def _generate_final_report(dict_payload) -> None:
    """
    Generate final report by first generating the html code and then the corresponding pdf report

    Args:
        param1(Dict[str, str]): a dictionary representing the candidate's scores
        param2(Dict[str, Dict[str, Union[float, int]]]): a nested dictionary that corresponds to
        the score receieved for each focus area/skill

    Returns:
        None
    """
    _generate_html(dict_payload)
    return _generate_pdf(dict_payload)


def _generate_html(dict_payload: Dict) -> None:
    """
    Render the html file by using jinja2 and the pilot.html file to customize the html file
    based on the specific candidate's scores

    Args:
        param1(Dict[str, str]): a dictionary representing the candidate's scores

    Returns:
        None
    """
    path_templates = pathlib.Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(path_templates))
    template = env.get_template("pilot.html")

    dict_bottom_top_skills = _get_bottom_and_top_skills(dict_payload["skills"])

    payload = {
        "dict_payload": dict_payload,
        "dict_bottom_top_skills": dict_bottom_top_skills,
        "dict_bottom_top_skills_text": _get_text_for_top_and_bottom_skills(
            dict_bottom_top_skills
        ),
        "dict_all_skills_description": _get_all_skills_description(dict_payload["skills"]),
        "date": dt.date.today().strftime("%Y-%b-%d"),
    }
    rendered_template = template.render(payload)

    path_rendered_template = pathlib.Path(
        "/tmp/rendered_template.html"
    )  # .parent.parent / "tmp" / "rendered_template.html"

    with open(path_rendered_template, "w") as file:
        file.write(rendered_template)


def _get_bottom_and_top_skills(
    dict_scores: Dict[str, Dict[str, Union[float, int]]]
) -> Dict[str, List[str]]:
    """
    Helper function to determine the bottom 3 and top 3 skills

    Args:
        param1(Dict[str, Dict[str, Union[float, int]]]): a nested dictionary that corresponds
        to the score receieved for each focus area/skill

    Returns:
        Dict[str, List[str]]: Dictionary consisting of the bottom 3 skills and top 3 skills
    """
    list_skill_scores = []
    for skill_dict in dict_scores.values():
        for skill, score in skill_dict.items():
            list_skill_scores.append((skill, score))

    sorted_list_skill_scores = sorted(list_skill_scores, key=lambda x: x[1])
    list_bottom_skills = [x[0] for x in sorted_list_skill_scores[:3] if x[1] < 7]
    list_top_skills = [x[0] for x in sorted_list_skill_scores[-3:] if x[1] > 5]
    return {"bottom_skills": list_bottom_skills, "top_skills": list_top_skills}


def _get_text_for_top_and_bottom_skills(
    dict_bottom_top_skills: Dict[str, List[str]]
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Helper function to retrieve the text from report_dynamic_txt.json file based on the top 3 and bottom 3 skills

    Args:
        param1(Dict[str, List[str]]): Dictionary consisting of the bottom 3 skills and top 3 skills

    Returns:
        Dict[str, Dict[str, Dict[str, str]]]: a dictionary that maps top and bottom skills to the respective text
    """
    # path_skills_json = (
    #     pathlib.Path(__file__).parent.parent / "resources" / "skills.json"
    # )
    # with open(path_skills_json) as file:
    #     dict_skills_text = json.load(file)

    dict_bottom_top_skills_text = {}
    for skill_position, list_skill in dict_bottom_top_skills.items():
        dict_bottom_top_skills_text[skill_position] = {}
        for skill in list_skill:
            dict_bottom_top_skills_text[skill_position][skill] = {}
            for field, value in dict_skills_text[skill].items():
                dict_bottom_top_skills_text[skill_position][skill][field] = value
    return dict_bottom_top_skills_text


def _get_all_skills_description(payload_skills: Dict[str, List[str]]) -> Dict[str, Dict[str, str]]:
    print(payload_skills)
    """
    Helper function to get the descriptions of all skills

    Args:
        None

    Returns:
        Dict[str, Dict[str, str]]: dictionary representing all focus areas and their corresponding
        skills and their corresponding descriptions
    """
    # path_skills_json = (
    #     pathlib.Path(__file__).parent.parent / "resources" / "skills.json"
    # )
    # with open(path_skills_json) as file:
    #     dict_skills_text = json.load(file)

    # path_focus_area_json = (
    #     pathlib.Path(__file__).parent.parent / "resources" / "focus_area.json"
    # )
    # with open(path_focus_area_json) as file:
    #     dict_focus_area = json.load(file)

    dict_skills_text_cleaned = {key: {} for key in dict_focus_area.keys()}

    for focus_area, skills in payload_skills.items():
        for skill in skills.keys():
            dict_skills_text_cleaned[focus_area][skill] = dict_skills_text[skill][
                "Description"
            ]

    return dict_skills_text_cleaned


def _generate_pdf(dict_payload: Dict) -> None:
    """
    Creates the final PDF file and saves to the results folder

    Args:
        param1(Dict[str, int | str]]): The candidate's profile

    Returns:
        None
    """
    user_id, video_id = (
        dict_payload["candidate_profile"]["user_id"],
        dict_payload["candidate_profile"]["video_id"],
    )
    name, company = dict_payload["candidate_profile"]["name"].replace(
        " ", "_"
    ), dict_payload["candidate_profile"]["company_name"].replace(" ", "_")
    date_today_string = dt.date.today().strftime("%Y-%m-%d")
    report_filename = f"{video_id}"  # "_".join([name, company, date_today_string])
    report_filename += ".pdf"

    path_html_file = pathlib.Path(
        "/tmp/rendered_template.html"
    )  # .parent.parent / "tmp" / "rendered_template.html"
    path_pdf_report = pathlib.Path(
        f"/tmp/{report_filename}"
    )  # .parent.parent / "results" / report_filename

    weasyprint.HTML(path_html_file).write_pdf(path_pdf_report)
    return path_pdf_report


def _delete_temp_files() -> None:
    """
    Deletes all files that were created except for the PDF file (images/graphs and html/css)

    Args:
        None

    Returns:
        None
    """
    directory = pathlib.Path("/tmp")  # .parent.parent / "tmp"

    # Get a list of all files in the directory
    file_list = os.listdir(directory)

    # Iterate over the file list and delete each file
    for filename in file_list:
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)


# if __name__ == "__main__":
#     path_data = pathlib.Path(__file__).parent.parent / "data" / "sample_video_data.json"
#     with open(path_data) as file:
#         dict_data = json.load(file)

#     generate_interview_report(dict_data)
