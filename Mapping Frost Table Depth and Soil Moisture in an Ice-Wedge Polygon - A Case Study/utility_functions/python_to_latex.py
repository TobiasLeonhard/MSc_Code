#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
python_to_latex.py

Utility functions to export pandas Data Frames to a custom LaTeX table format

Author: Tobias Leander Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2025
Last Modified: 2026-08-06
"""
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ============================================================ #
import sys
from pathlib import Path
parent_folder = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_folder))
from config.environment import *
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def export_to_latex(data: pd.DataFrame, caption: Tuple[str, str], precision_dict: dict, label: str, float_placement_identifier: str, output_path: Path, column_based: bool = False):
    """
    Custom function to write a pandas Data Frame as a LaTeX table.
    The first column is treated like a Index Column, the rest like value columns
    Args:
        data - pd.DataFrame: Data to write
        caption - (str, str): Short and Long Caption
        precision_dict - dict: Dictionary where precisions for different values can be defined
        label - str: Label for table
        float_placement_identifier - str:  Float Placement Specifier (or positioning parameter)
        output_path - Path: Path for output file
    """
    tab = "    "
    if float_placement_identifier == "":
        table_str = rf"\begin{{table}}" + "\n" + tab + r"\centering" + "\n"
    else:
        table_str = rf"\begin{{table}}[{float_placement_identifier}]" + "\n" + tab + r"\centering" + "\n"
    caption_body = caption[1].replace("\n", "\n" + 2 * tab)
    table_str += tab + rf"\caption[{caption[0]}]" + "{" + caption_body + "\n" + 2 * tab + "}"
    table_str += rf"\label{{{label}}}" +"\n"
    columns = data.columns
    col_format = "l" + "c"*(len(columns) - 1)
    table_str += tab + rf"\begin{{tabular}}{{{col_format}}}" + "\n"
    table_str += 2*tab + "\\toprule"+ "\n"

    table_str += 2*tab
    for col in columns:
        table_str += r"\makecell{" + str(col) + "}" + " & "
    table_str = table_str[:-3] + " \\\\" + "\n"
    table_str += 2*tab + "\\midrule"+ "\n"
    if column_based == False:
        metric_col = columns[0]

    for _, row in data.iterrows():
        table_str += 2*tab
        for col in columns:
            if column_based == False:
                if row[metric_col] in precision_dict.keys() and col != metric_col and isinstance(row[col], (int, float)):
                    value = round(row[col], precision_dict[row[metric_col]])
                    value = f"{value:.{precision_dict[row[metric_col]]}f}"
                else:
                    value = row[col]
            else:
                if col in precision_dict.keys() and isinstance(row[col], (int, float)):
                    value = round(row[col], precision_dict[col])
                    value = f"{value:.{precision_dict[col]}f}"
                else:
                    value = row[col]
            table_str += str(value) + " & "
        table_str = table_str[:-3] + " \\\\" + "\n"
    table_str += 2*tab + "\\bottomrule"+ "\n"
    table_str +=  tab + r"\end{tabular}" + "\n" + r"\end{table}"
    with open(output_path.with_suffix(".tex"), "w") as f:
        f.write(table_str)
    print(table_str)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
