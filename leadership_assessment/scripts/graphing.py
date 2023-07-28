from typing import Dict, Union, List
from textwrap import wrap
import pathlib
from statistics import mean
import pandas as pd
import numpy as np
import matplotlib
import json

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors
from PIL import Image
from sklearn.preprocessing import MinMaxScaler
from .edy import *

dict_focus_area, dict_skills_text, skills_csv_df = get_skills_resources()

def generate_skill_score_bar_charts(
    dict_scores: Dict[str, Dict[str, Union[float, int]]]
) -> None:
    """
    Creates bar graphs for all focus areas based on the individual's self-assessment and save the
    static image to the tmp folder

    Args:
        param1(Dict[str, Dict[str, int | str]]): The candidate's profile and assessment results

    Returns:
        None
    """
    for focus_area, dict_skills in dict_scores.items():
        print(focus_area, dict_skills)
        filename_ending = focus_area + ".jpg"
        path_focus_area = pathlib.Path(f"/tmp/{filename_ending}")#.parent.parent / "tmp" / filename_ending

        categories = ["\n".join(category.split(" ")) for category in dict_skills.keys()]
        values = [np.round(1.0 * x, 1) for x in dict_skills.values()]

        fig, ax = plt.subplots(figsize=(20, 10))
        ax_bar = ax.bar(categories, values, alpha=0.2)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_position(("outward", 5))
        ax.bar_label(ax_bar, fontsize=16, padding=5, fmt="%.1f")
        ax.set_ylim(1, 10)

        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = "Helvetica"
        plt.rcParams["axes.edgecolor"] = "#333F4B"
        plt.rcParams["axes.linewidth"] = 0.8
        plt.rcParams["xtick.color"] = "#333F4B"

        plt.title(focus_area, fontsize=35)
        plt.xticks(fontsize=17)
        plt.yticks([])
        plt.tight_layout()
        plt.savefig(path_focus_area, format="jpg")
        plt.clf()

    matplotlib.pyplot.close()


def generate_focus_area_spider_plot(
    dict_scores: Dict[str, Dict[str, Union[float, int]]]
) -> None:
    """
    Creates spidersplot graph that displays the self-assessment scores

    Args:
        param(Dict[str, Dict[str, Union[float, int]]]): a nested dictionary that corresponds to
        the score receieved for each focus area/skill

    Returns:
        None
    """
    categories = ["\n".join(wrap(category, 15)) for category in dict_scores.keys()]

    list_scores = [mean(skills.values()) for skills in dict_scores.values()]
    list_scores = list_scores + list_scores[:1]

    N = len(categories)
    PI = 3.14592

    # define color scheme for up to 10 comparisons
    color = "#429bf4"  # (Blue)

    angles = [n / float(N) * 2 * PI for n in range(N)]
    angles += angles[:1]

    plt.rc("figure", figsize=(10, 10))

    ax = plt.subplot(1, 1, 1, polar=True)

    ax.set_theta_offset(PI / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 10)

    plt.xticks(angles[:-1], categories, color="black", size=16)
    ax.tick_params(axis="x", pad=24)

    ax.set_rlabel_position(0)
    plt.yticks([1, 10], ["1", "10"], color="black", size=10)
    plt.ylim(0, 10)

    ax.plot(angles, list_scores, color=color, linewidth=1, linestyle="solid")
    ax.fill(angles, list_scores, color=color, alpha=0.3)

    for i, (angle, radius) in enumerate(zip(angles[:-1], list_scores[:-1])):
        x = angle
        y = radius

        if x >= 0 and x <= 1.5:
            xytext = (0, 8)
        elif x <= 3:
            xytext = (8, 0)
        elif x < 4.5:
            xytext = (0, -8)
        else:
            xytext = (-8, 0)

        ax.annotate(
            np.round(list_scores[i], 1),
            xy=(x, y),
            xytext=xytext,
            textcoords="offset points",
            ha="center",
            va="center",
        )

    path_spiderplot_graph = (
        pathlib.Path(f"/tmp/focus_area_spider_plot.jpg")#.parent.parent / "tmp" / "focus_area_spider_plot.jpg"
    )
    plt.savefig(path_spiderplot_graph, format="jpg")

    # crop the left and right sides of the image
    image = Image.open(path_spiderplot_graph)
    width, height = image.size
    crop_width = int(width * 0.25)
    left = crop_width
    top = 0
    right = width - crop_width
    bottom = height
    cropped_image = image.crop((left, top, right, bottom))
    cropped_image.save(path_spiderplot_graph)

    matplotlib.pyplot.close()


def generate_skill_score_colorbar_plots(
    dict_scores: Dict[str, Dict[str, Union[float, int]]]
) -> None:
    """
    Creates horizontal gauge charts based on the individual's scores.

    Args:
        param(Dict[str, Dict[str, Union[float, int]]]): a nested dictionary that corresponds
        to the score receieved for each focus area/skill

    Returns:
        None
    """
    # path_skill_range = (
    #     pathlib.Path(__file__).parent.parent / "resources" / "skill_range.csv"
    # )
    df_skill_range = skills_csv_df

    fig = plt.figure(figsize=(8, 2))
    ax = fig.add_axes([0.1, 0.2, 0.8, 0.4])
    ax2 = fig.add_axes([0.1, 0.1, 0.8, 0.1])
    ax3 = fig.add_axes([0.1, 0.6, 0.8, 0.1])

    left_color = "#FCBEC1"
    right_color = "#D9FBC8"
    center_color = "#F4F4F4"

    # Create a colormap for the left half (green to white)
    cmap_left = mcolors.LinearSegmentedColormap.from_list(
        "LeftCmap", [left_color, center_color]
    )

    # Create a colormap for the right half (white to red)
    cmap_right = mcolors.LinearSegmentedColormap.from_list(
        "RightCmap", [center_color, right_color]
    )

    # white cmap
    cmap_white = mcolors.LinearSegmentedColormap.from_list(
        "WhiteCmap", ["white", "white"]
    )

    # Combine the left and right colormaps
    colors = np.vstack(
        (cmap_left(np.linspace(0, 1, 256)), cmap_right(np.linspace(0, 1, 256)))
    )
    cmap_custom = mcolors.ListedColormap(colors)
    for skill_dict in dict_scores.values():
        for skill, score in skill_dict.items():
            min_gauge_value = df_skill_range.loc[
                df_skill_range["Skills (Competencies)"] == skill, "Min"
            ].values[0]
            max_gauge_value = df_skill_range.loc[
                df_skill_range["Skills (Competencies)"] == skill, "Max"
            ].values[0]
            r1_gauge_value = df_skill_range.loc[
                df_skill_range["Skills (Competencies)"] == skill, "R1"
            ].values[0]
            r2_gauge_value = df_skill_range.loc[
                df_skill_range["Skills (Competencies)"] == skill, "R2"
            ].values[0]

            guage_range = np.linspace(min_gauge_value, max_gauge_value, 512)

            norm = matplotlib.colors.Normalize(
                vmin=guage_range[0], vmax=guage_range[-1]
            )

            cbar = matplotlib.colorbar.ColorbarBase(
                ax,
                cmap=cmap_custom,
                norm=norm,
                orientation="horizontal",
                boundaries=guage_range,
            )

            cbar2 = matplotlib.colorbar.ColorbarBase(
                ax2,
                cmap=cmap_white,
                norm=norm,
                orientation="horizontal",
                boundaries=guage_range,
            )

            cbar3 = matplotlib.colorbar.ColorbarBase(
                ax3,
                cmap=cmap_white,
                norm=norm,
                orientation="horizontal",
                boundaries=guage_range,
            )

            cbar.outline.set_visible(False)
            cbar2.outline.set_visible(False)
            cbar3.outline.set_visible(False)

            ax.axvspan(score - 0.1, score + 0.1, 0, 1, facecolor="#000000")
            ax2.axvspan(score - 0.1, score + 0.1, 0, 1, facecolor="#000000")
            ax3.axvspan(score - 0.1, score + 0.1, 0, 1, facecolor="#000000")

            file_name = skill + ".jpg"
            path_skill_gauge_chart = pathlib.Path(f"/tmp/{file_name}")#.parent.parent / "tmp" / file_name

            ax.set_xticks([])
            ax2.set_xticks([])
            ax3.set_xticks([])

            annotation = plt.annotate(
                "1", xy=(0.1, 0.1), xycoords="figure fraction", ha="center", fontsize=14
            )
            annotation2 = plt.annotate(
                "10",
                xy=(0.9, 0.1),
                xycoords="figure fraction",
                ha="center",
                fontsize=14,
            )
            annotation3 = plt.annotate(
                str(np.round(score, 1)),
                xy=(score / 11, 0.75),
                xycoords="figure fraction",
                ha="center",
                fontsize=14,
            )

            plt.savefig(path_skill_gauge_chart, format="jpg")

            annotation.remove()
            annotation2.remove()
            annotation3.remove()


def generate_color_bar_plot(
    metric_name: str,
    metric_unit_measurement: str,
    metric_average: Union[int, float],
    metric_middle_max: Union[int, float],
    metric_middle_min: Union[int, float],
    bar_max: Union[int, float],
    bar_min: Union[int, float],
    bar_annotations: Dict[str, str],
    colorbar_range: List[int],
    colorbar_colors: List[str],
) -> None:
    """
    Generate a colorbar based on custom specific arguments provided

    Args:
        metric_name(str): name of the metric
        metric_unit_measurement(str): the unit of measurement of the metric
        metric_average(Union[int, float]): the average value measured
        metric_middle_max(Union[int, float]): the maximum value for the middle range
        metric_middle_min(Union[int, float]): the minimum value for the middle range
        bar_max(Union[int, float]): the maximum value for the metric
        bar_min(Union[int, float]): the minimum value for the metric
        bar_annotations(Dict[str, str]): the labels used to define the intervals
        color_range(List[int]): the position where the colors change along the interval
        colorbar_colors(List[str]): hexademical colors for each point given

    Returns:
        None
    """
    fig = plt.figure(figsize=(8, 2))
    ax = fig.add_axes([0.1, 0.2, 0.8, 0.4])
    ax2 = fig.add_axes([0.1, 0.6, 0.8, 0.1])
    ax3 = fig.add_axes([0.1, 0.1, 0.8, 0.1])

    scale_colorbar_range = MinMaxScaler()
    scale_colorbar_range = scale_colorbar_range.fit_transform(
        np.array(colorbar_range).reshape(-1, 1)
    )

    cmap_custom = mcolors.LinearSegmentedColormap.from_list(
        "custom_cmap", list(zip(scale_colorbar_range, colorbar_colors)), N=256
    )

    cmap_white = mcolors.LinearSegmentedColormap.from_list(
        "WhiteCmap", ["white", "white"]
    )

    guage_range = np.linspace(bar_min, bar_max, 512)

    norm = matplotlib.colors.Normalize(vmin=guage_range[0], vmax=guage_range[-1])

    cbar = matplotlib.colorbar.ColorbarBase(
        ax,
        cmap=cmap_custom,
        norm=norm,
        orientation="horizontal",
        boundaries=guage_range,
    )

    cbar2 = matplotlib.colorbar.ColorbarBase(
        ax2,
        cmap=cmap_white,
        norm=norm,
        orientation="horizontal",
        boundaries=guage_range,
    )

    cbar3 = matplotlib.colorbar.ColorbarBase(
        ax3,
        cmap=cmap_white,
        norm=norm,
        orientation="horizontal",
        boundaries=guage_range,
    )

    cbar.outline.set_visible(False)
    cbar2.outline.set_visible(False)
    cbar3.outline.set_visible(False)

    # middle range
    ax.axvspan(
        metric_middle_min - 0.15, metric_middle_min + 0.15, 0, 1, facecolor="#000000"
    )
    ax.axvspan(
        metric_middle_max - 0.15, metric_middle_max + 0.15, 0, 1, facecolor="#000000"
    )

    ax.set_xticks([])
    ax2.set_xticks([])
    ax3.set_xticks([])

    # user metric conversion to location fraction
    if metric_average < bar_min:
        metric_value_annotation_location = 0.1
    elif metric_average > bar_max:
        metric_value_annotation_location = 0.9
    else:
        metric_value_annotation_location = (
            0.1 + (metric_average - bar_min) / (bar_max - bar_min) * 0.8
        )

    low_annotation_location = 0.1 + 0.8 * (metric_middle_min - bar_min) / 2 / (
        bar_max - bar_min
    )
    middle_annotation_location = 0.1 + 0.8 * (
        (metric_middle_max + metric_middle_min) / 2 - bar_min
    ) / (bar_max - bar_min)
    high_annotation_location = 0.1 + 0.8 * (
        (bar_max + metric_middle_max) / 2 - bar_min
    ) / (bar_max - bar_min)
    middle_low_annotation_location = 0.1 + 0.8 * (metric_middle_min - bar_min) / (
        bar_max - bar_min
    )
    middle_high_annotation_location = 0.1 + 0.8 * (metric_middle_max - bar_min) / (
        bar_max - bar_min
    )

    plt.annotate(
        bar_annotations["low"],
        xy=(low_annotation_location, 0.375),
        xycoords="figure fraction",
        ha="center",
        fontsize=10,
    )

    plt.annotate(
        bar_annotations["middle"],
        xy=(middle_annotation_location, 0.375),
        xycoords="figure fraction",
        ha="center",
        fontsize=10,
    )

    plt.annotate(
        bar_annotations["high"],
        xy=(high_annotation_location, 0.375),
        xycoords="figure fraction",
        ha="center",
        fontsize=10,
    )

    plt.annotate(
        str(int(np.round(metric_average, 0))) + metric_unit_measurement,
        xy=(metric_value_annotation_location, 0.525),
        xytext=(metric_value_annotation_location, 0.8),
        xycoords="figure fraction",
        ha="center",
        fontsize=10,
        arrowprops={"arrowstyle": "->", "linewidth": 1.5, "edgecolor": "black"},
        va="center",
    )

    plt.annotate(
        str(metric_middle_min),
        xy=(middle_low_annotation_location, 0.075),
        xycoords="figure fraction",
        ha="center",
        fontsize=10,
    )

    plt.annotate(
        str(metric_middle_max),
        xy=(middle_high_annotation_location, 0.075),
        xycoords="figure fraction",
        ha="center",
        fontsize=10,
    )

    file_name = metric_name + "_colorbar.jpg"
    path_color_bar = pathlib.Path(f"/tmp/{file_name}")#.parent.parent / "tmp" / file_name

    plt.savefig(path_color_bar, format="jpg")

    # crop the top and bottom sides of the image
    image = Image.open(path_color_bar)
    width, height = image.size
    crop_height = int(height * 0.1)
    left = 0
    top = crop_height
    right = width
    bottom = height - crop_height * 0.5
    cropped_image = image.crop((left, top, right, bottom))
    cropped_image.save(path_color_bar)


def generate_line_chart(
    metric_name: str,
    metric_unit_measurement: str,
    metric_average: Union[int, float],
    metric_middle_max: Union[int, float],
    metric_middle_min: Union[int, float],
    colorbar_min: Union[int, float],
    colorbar_max: Union[int, float],
    metric_time_series_x_y: Dict[str, Union[int, float]],
    colorbar_range: List[int],
    colorbar_colors: list[str],
) -> None:
    """
    Generate a line chart that graphs the pace over time and compares it to the middle range


    Args:
        metric_name(str): name of the metric
        metric_unit_measurement(str): the unit of measurement of the metric
        metric_average(Union[int, float]): the average value measured
        metric_middle_max(Union[int, float]): the maximum value for the middle range
        metric_middle_min(Union[int, float]): the minimum value for the middle range
        colorbar_max(Union[int, float]): the maximum value for the metric
        colorbar_min(Union[int, float]): the minimum value for the metric
        bar_annotations(Dict[str, str]): the labels used to define the intervals
        metric_timer_series_x_y(Dict[str, Union[int, float]]): time series data for the particular metric
        color_range(List[int]): the position where the colors change along the interval
        colorbar_colors(List[str]): hexademical colors for each point given

    Returns:
        None
    """
    # interpolate data in order to populate scatterplot
    pace_time_series_x = [
        np.round(x["millisec"] / 60000, 2) for x in metric_time_series_x_y
    ]
    pace_time_series_y = [np.round(x["value"], 0) for x in metric_time_series_x_y]

    segments =  0 if len(pace_time_series_x) == 0 else len(pace_time_series_x) - 1
    points_per_segment = 100
    pace_time_series_x_scatter = np.linspace(
        min(pace_time_series_x, default=0), max(pace_time_series_x, default=0), segments * points_per_segment
    )
    pace_time_series_y_scatter = np.array(
        [
            np.linspace(
                pace_time_series_y[x], pace_time_series_y[x + 1], points_per_segment
            )
            for x in range(segments)
        ]
    ).flatten()

    # create custom color map based on color range list
    scale_colorbar_range = MinMaxScaler()
    scale_colorbar_range = scale_colorbar_range.fit_transform(
        np.array(colorbar_range).reshape(-1, 1)
    )
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "custom_cmap", list(zip(scale_colorbar_range, colorbar_colors)), N=256
    )

    fig, ax = plt.subplots(1, 2, width_ratios=[20, 1])
    fig.set_figwidth(12)
    fig.set_figheight(6)

    ax[0].scatter(
        x=pace_time_series_x_scatter,
        y=pace_time_series_y_scatter,
        c=pace_time_series_y_scatter,
        cmap=cmap,
        vmin=colorbar_min,
        vmax=colorbar_max,
    )
    ax[0].set_ylim(colorbar_min, colorbar_max)
    ax[0].set_xlim(0, max(pace_time_series_x_scatter, default=0))

    ax[0].spines["right"].set_color("none")
    ax[0].spines["top"].set_color("none")

    ax[0].xaxis.set_ticks_position("bottom")
    ax[0].yaxis.set_ticks_position("left")

    # remove origin ticker
    func = lambda x, pos: "" if np.isclose(x, 0) else x
    ax[0].xaxis.set_major_formatter(ticker.FuncFormatter(func))
    ax[0].yaxis.set_major_formatter(ticker.FuncFormatter(func))

    # remove decimals from y axis ticker
    ax[0].yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f"))
    
    ax[0].xaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
    
    ax[0].tick_params(axis="both", which="major", labelsize=14)
    ax[0].set_xlim(min(pace_time_series_x_scatter, default=0), max(pace_time_series_x_scatter, default=0))

    # plot average pace value
    y_mean = [metric_average] * len(pace_time_series_x_scatter)
    ax[0].plot(
        pace_time_series_x_scatter,
        y_mean,
        linestyle="-",
        color="red"
        if metric_average > metric_middle_max or metric_average < metric_middle_min
        else "green",
    )

    ax[0].set_xlabel("Minutes", fontsize=14)
    ax[0].set_ylabel(metric_unit_measurement, fontsize=14)

    ax[0].set_facecolor("#EEEFEE")
    ax[0].grid(linestyle="--", linewidth=1)

    # create colorbar
    guage_range = np.linspace(colorbar_min, colorbar_max, 512)

    norm = matplotlib.colors.Normalize(vmin=guage_range[0], vmax=guage_range[-1])

    cbar = matplotlib.colorbar.ColorbarBase(
        ax[1],
        cmap=cmap,
        norm=norm,
        orientation="vertical",
        boundaries=guage_range,
    )

    cbar.outline.set_visible(False)

    ax[1].set_yticks([])

    plt.subplots_adjust(wspace=0.1, hspace=0)

    file_name = metric_name + "_line_chart.jpg"
    path_line_chart = pathlib.Path(f"/tmp/{file_name}")#.parent.parent / "tmp" / file_name

    plt.savefig(path_line_chart, format="jpg")

    # crop the top and bottom sides of the image
    image = Image.open(path_line_chart)
    width, height = image.size
    crop_height = int(height * 0.075)
    left = 0
    top = crop_height
    right = width
    bottom = height - crop_height * 0.3
    cropped_image = image.crop((left, top, right, bottom))
    cropped_image.save(path_line_chart)


def generate_stacked_bar_chart_pauses(dict_pauses: Dict) -> None:
    """
    Create the stacked bar chart based on actual pauses relative to the recommended min and max pauses

    Args:
        param1(Dict[]): The candidate's profile and assessment results

    Returns:
        None
    """

    fig = plt.figure(figsize=(10, 4))

    keys_categories = [
        "pauses_count_sensory",
        "pauses_count_sentence",
        "pauses_count_transition",
        "pauses_count_strategic",
        "pauses_count_long",
    ]

    categories = [
        (x.replace("pauses_count_", "") + " pause").title() for x in keys_categories
    ]
    values_min = [
        max(dict_pauses[key]["data"]["recommended"]["min"], 0)
        for key in keys_categories
    ]
    values_max = [
        dict_pauses[key]["data"]["recommended"]["max"] for key in keys_categories
    ]
    values_count = [
        dict_pauses[key]["data"]["inference"]["count"] for key in keys_categories
    ]
    
    values_max_greater_than_min = [max(0, x[1] - x[0]) for x in zip(values_min, values_max)]
    values_gap = [max(0, x[1] - x[0]) for x in zip(values_max, values_count)]
    
    bar1 = plt.barh(categories, values_min, color="#ACF387")
    bar2 = plt.barh(categories, values_max_greater_than_min, left=values_min, color="#F9F096")
    bar3 = plt.barh(categories, values_gap, left=values_max, color="#FC6157")
    scatter = plt.scatter(x=values_count, y=categories, marker="x", color="#000000")

    plt.legend(
        [bar1, bar2, bar3, scatter],
        ["Recommended Min", "Recommended Max", "Gap", "Actual"],
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=4,
    )
    plt.xlabel("Number Of Pauses")
    plt.tight_layout()

    path_stack_bar_chart = (
        pathlib.Path("/tmp/pauses_stacked_bar_chart.jpg")#.parent.parent / "tmp" / "pauses_stacked_bar_chart.jpg"
    )
    plt.savefig(path_stack_bar_chart)
