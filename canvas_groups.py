# create groups in canvas from data/students2020.csv
################
# using the CLI:

##############################
# using as an imported module:
# from canvas_groups import create_groups
# create_groups("students2020.csv", 53659, group_set_name="lab1", group_prefix="Group ")
# see help(create_groups) for more info

import os
import pandas as pd
from canvasapi import Canvas
from typing import Union
from tqdm import tqdm
import argparse
import getpass


def create_groups(
    course_code: int,
    groups_csv_file: str = "data/students2020.csv",
    group_set_name: str = "New Group Set",
    group_prefix: str = "Group ",
    api_url: str = "https://canvas.ubc.ca/",
    token: Union[bool, str] = True,
):
    """Create groups on Canvas from a csv file.

    Parameters
    ----------
    groups_csv_path : str
        path to csv file that at least has the columns 'student_number' and 'group_num'.
    course_code : int
        Canvas course code.
    group_set_name : str, optional
        name of the new group set that will contain the groups, by default "new-group-set".
    group_prefix : str, optional
        prefix to append to each group in the new group set, by default an empty string "".
    api_url : str, optional
        base URL of the Canvas instance's API, by default "https://canvas.ubc.ca/"
    token : Union[bool, str], optional
        True if you have an environment variable "CANVAS_API". If you don't,
        set to False and enter token interactively. You can also pass your
        token directly as a string, by default True, by default True

    Examples
    --------
    >>> from canvas_groups import create_groups
    >>> create_groups("student_groups.csv", course_code=53659)
    """

    # load data
    group_col = "group_num"
    id_col = "student_number"
    df = pd.read_csv(groups_csv_file)
    # connect to canvas
    course = _token_verif(course_code, api_url, token)
    new_group_set = course.create_group_category(name=group_set_name)
    # unfortunately, I need student's canvas id's to do this (not the same as their UBC id)
    # for now I'll just map these with a dictionary
    ids = {_.sis_user_id: _.id for _ in course.get_users()}
    bad_ids = []
    for group_num in tqdm(df[group_col].unique()):
        g = new_group_set.create_group(name=f"{group_prefix}{group_num}")
        for student_id in df.query(f"{group_col} == @group_num")[id_col]:
            try:
                _ = g.create_membership(ids[str(student_id)])
            except KeyError:
                bad_ids.append(student_id)  # catch invalid students
    if len(bad_ids):
        print(
            "Some students were not found in Canvas or some other error occurred. Here are the ids of the trouble-makers!"
        )
        print(bad_ids)


def _token_verif(course_code: int, api_url: str, token: Union[bool, str]):
    """Verify a connection to Canvas with the given params.

    Parameters
    ----------
    course_code : int
        Course code, get from canvas course url, e.g., 53659.
    api_url : str
        The base URL of the Canvas instance's API, e.g., "https://canvas.ubc.ca/"
    token : Union[bool, str]
        True if you have an environment variable "CANVAS_API". If you don't,
        set to False and enter token interactively. You can also pass your
        token directly as a string

    Returns
    -------
    canvasapi.course.Course
        Canvas course object
    """

    if token == True:
        api_key = os.environ.get("CANVAS_API")
        if api_key is None:
            raise NameError(
                "Sorry, I could not find a token 'CANVAS_API' in your environment variables. Check your environment variables, or use 'submit(course_code, token_present=False)' to try enter your token interactively."
            )
        try:
            canvas = Canvas(api_url, api_key)
            course = canvas.get_course(course_code)
            return course
        except:
            print(
                "I found a token but could not access the given Canvas course. Perhaps you entered the wrong course code? Or your token is invalid? You can also try to use 'submit(course_code, token_present=False)' to enter your token interactively."
            )
            raise
    elif isinstance(token, str):
        try:
            canvas = Canvas(api_url, token)
            course = canvas.get_course(course_code)
            return course
        except:
            print(
                "I found a token but could not access the given Canvas course. Perhaps you entered the wrong course code? Or your token is invalid? You can also try to use 'submit(course_code, token_present=False)' to enter your token interactively."
            )
            raise

    else:
        print("Please paste your token here and then hit enter:")
        api_key = getpass.getpass()
        print("Token successfully entered - thanks!")
        print("")
        try:
            canvas = Canvas(api_url, api_key)
            course = canvas.get_course(course_code)
            return course
        except:
            print(
                "You entered a token but I still could not access the given Canvas course. Perhaps you entered the wrong course code? Or your token is invalid?"
            )
            raise


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--course", type=int, help="Canvas course code.", required=True)
    parser.add_argument(
        "--csv", default="data/students2020.csv", type=str, help="Path to student csv."
    )
    parser.add_argument(
        "--name", default="New Group Set", type=str, help="Name of the group set."
    )
    parser.add_argument(
        "--prefix", default="Group ", type=str, help="Prefix to add to groups."
    )
    parser.add_argument(
        "--url",
        default="https://canvas.ubc.ca/",
        type=str,
        help="Use testing data files?",
    )
    parser.add_argument(
        "--token",
        action="store_false",
        help="If CANVAS_PAT exists as an environment variable.",
    )
    args = parser.parse_args()

    create_groups(args.course, args.csv, args.name, args.prefix, args.url, args.token)