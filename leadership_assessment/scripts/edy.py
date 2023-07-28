leadership_assessment_pdf_bucket = "leadership-assessment-pdf"
edy_csvs_bucket = "edy-csv-bucket"

send_email_topic = "arn:aws:sns:us-east-1:380665605337:send_email"


import boto3
import datetime as dt
import pandas as pd

date_today_string = dt.date.today().strftime("%Y-%m-%d")

aws_session = boto3.Session()


class AwsConfigs:
    s3_client = aws_session.client(service_name="s3")
    transcribe_client = aws_session.client(service_name="transcribe")
    cognito_client = aws_session.client("cognito-idp")
    mediaconvert_client = aws_session.client(
        "mediaconvert",
        endpoint_url="https://q25wbt2lc.mediaconvert.us-east-1.amazonaws.com",
    )
    sns_client = aws_session.client("sns")
    ses_client = aws_session.client("ses")


AwsConfig = AwsConfigs()


def email_template(payload):
    assessment_type = payload.get("assessment_type", "leadership_assessment")
    email_types = {
        "leadership_assessment": {
            "email_type": "raw_send_email",
            "email_data": {
                "from": "support@edmyst.com",
                "to": [payload["email"]],
                "subject": " ".join(
                    [
                        "Here is your EdMyst Assessment report for",
                        payload["Candidate"]["name"],
                    ]
                ),
                "body": [
                    {
                        "content": " ".join(
                            [
                                "Hi",
                                payload["Candidate"]["name"],
                                ", \n\n Thank you for taking the Assessment. Please find attached the output report.\nFor any questions, we can be reached at assessment@edmyst.com\nWe wish you the best in your development journey.\n\nAssessment Team,\nEdMyst Inc.",
                            ]
                        ),
                        "type": "plain",
                    },
                    # {"content": f"<h1>Powered by EdMyst</h1>", "type": "html"},
                ],
                "attachments": [
                    {
                        "type": "s3",
                        "data": {
                            "bucket": leadership_assessment_pdf_bucket,
                            "object": "/".join(
                                [
                                    payload["Candidate"]["user_id"],
                                    payload["Candidate"]["video_id"],
                                ]
                            )
                            + ".pdf",
                            "file_name": "_".join(
                                [
                                    payload["Candidate"]["name"],
                                    payload["Candidate"]["company"],
                                    date_today_string,
                                ]
                            )
                            + ".pdf",
                        },
                    }
                ],
            },
        },
        "talentinsights_assessment": {
            "email_type": "raw_send_email",
            "email_data": {
                "from": "support@edmyst.com",
                "to": [payload["email"]],
                "subject": " ".join(
                    [
                        "Here is your EdMyst Assessment report for",
                        payload["Candidate"]["name"],
                    ]
                ),
                "body": [
                    {
                        "content": " ".join(
                            [
                                "Hi",
                                payload["Candidate"]["name"],
                                ", \n\n Thank you for taking the Assessment. Please find attached the output report.\nFor any questions, we can be reached at assessment@edmyst.com\nWe wish you the best in your development journey.\n\nAssessment Team,\nEdMyst Inc.",
                            ]
                        ),
                        "type": "plain",
                    },
                    # {"content": f"<h1>Powered by EdMyst</h1>", "type": "html"},
                ],
                "attachments": [
                    {
                        "type": "s3",
                        "data": {
                            "bucket": leadership_assessment_pdf_bucket,
                            "object": "/".join(
                                [
                                    payload["Candidate"]["user_id"],
                                    payload["Candidate"]["video_id"],
                                ]
                            )
                            + ".pdf",
                            "file_name": "_".join(
                                [
                                    payload["Candidate"]["name"],
                                    payload["Candidate"]["company"],
                                    date_today_string,
                                ]
                            )
                            + ".pdf",
                        },
                    }
                ],
            },
        }
    }

    return email_types[assessment_type]

def get_skills_resources():
    skills_csv = '/tmp/Leadership Assessment Report Content.csv'
    AwsConfig.s3_client.download_file(edy_csvs_bucket, 'Leadership Assessment Report Content.csv', skills_csv)
    skills_csv_df = pd. read_csv(skills_csv)
    focus_areas = skills_csv_df["Focus Area"].unique()
    dict_focus_area = {}
    for focus_area in list(focus_areas):
        dict_focus_area[focus_area] = list(skills_csv_df["Skills (Competencies)"].loc[skills_csv_df["Focus Area"] == focus_area])

    skills = list(skills_csv_df["Skills (Competencies)"].unique())
    skills_csv_headers = skills_csv_df.iloc
    dict_skills_text = {}
    skills_csv_headers = list(skills_csv_df.columns)
    print(skills_csv_headers[2:10])
    for skill in skills:
        skill_dict = {}
        for key in skills_csv_headers[2:10]:
            value = str(list(skills_csv_df[key].loc[skills_csv_df["Skills (Competencies)"] == skill])[0])
            if "{-}" in value: value = [t.strip() for t in list(filter(None, value.strip().split("{-}")))]
            skill_dict[key] = value
        dict_skills_text[skill] = skill_dict

    return dict_focus_area, dict_skills_text, skills_csv_df