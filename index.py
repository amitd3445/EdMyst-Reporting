import sys
import os
import json
from talentinsights_assessment.scripts.talentinsights_pdf_report import *
from leadership_assessment.scripts.leadership_pdf_report import *

pdf = {
    "leadership_assessment": leadership_report,
    "talentinsights_assessment": talentinsights_report,
}


def _upload_to_s3(payload):
    local_file, bucket_name, blob_name = (
        payload["local_file"],
        payload["bucket_name"],
        payload["blob_name"],
    )
    AwsConfig.s3_client.upload_file(local_file, bucket_name, blob_name)


def _send_email_to_candidate(payload):
    email = payload.get("email")
    if email:
        email_data = email_template(payload)
        sns_data = {"emails": [email_data]}
        res = AwsConfig.sns_client.publish(
            TopicArn=send_email_topic, Message=json.dumps(sns_data)
        )
        print(res)


steps_after_pdf = {
    "upload to s3": {
        "assessment_types": ["leadership_assessment", "talentinsights_assessment"],
        "function": _upload_to_s3,
    },
    "send email to candidate": {
        "assessment_types": [
            "leadership_assessment",
        ],
        "function": _send_email_to_candidate,
    },
}


def after_pdf_generated(payload):
    assessment_type = payload.get("assessment_type")
    for task, data in steps_after_pdf.items():
        if assessment_type in data["assessment_types"]:
            print(task, data["function"](payload))


def handler(event, context):
    print("starting generate_pdf")
    Message = event["Records"][0]["Sns"]["Message"]
    data = Message if type(Message) == type({}) else json.loads(Message)
    user_id = data.get("user_id")
    if not user_id:
        return "no user id given"
    video_id = data.get("video_id")
    video_data = data.get("video_data")
    reference_no = data.get("reference_no")
    name = video_data.get("name", "undefined")
    company_name = video_data.get("company_name", "")
    candidate_profile = {
        "name": name,
        "company": company_name,
        "user_id": user_id,
        "video_id": video_id,
        "reference_no": reference_no,
    }
    job_fitment = video_data.get("job_fitment", {"R1": 40, "R2": 60, "S": 0})
    payload = {
        "skill_scores": video_data.get("recruiter_skills", {}),
        "Candidate": candidate_profile,
        **video_data,
        "Job Fitment": job_fitment,
    }
    assessment_type = payload.get("assessment_type")
    generate_pdf = pdf[assessment_type](payload.copy())

    payload["local_file"] = generate_pdf
    payload["bucket_name"] = leadership_assessment_pdf_bucket
    payload["blob_name"] = f"{user_id}/{video_id}.pdf"

    after_pdf_generated(payload)

    return f"pdf generated for user_id - {user_id} video_id - {video_id}   " + str(
        generate_pdf
    )


path_data = pathlib.Path(__file__).parent / "data" / "sample_video_data.json"
with open(path_data, encoding="utf8") as file:
    dict_data = json.load(file)
print(handler(dict_data, ""))
