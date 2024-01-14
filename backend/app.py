import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import spacy
import parsedatetime
from datetime import time, date, datetime, timedelta
import pytz
from icalendar import Calendar, Event
from dotenv import load_dotenv
import os
import uuid
import boto3

app = Flask(__name__)

CORS(app)


@app.route("/")
def home():
    return "ok"


@app.route('/api/get-events', methods=['POST'])
def get_events():
    data = request.get_json()
    ics_url = data.get('url', None)
    ical = Calendar.from_ical(requests.get(ics_url).text)
    res = []
    for event in ical.walk("VEVENT"):
        res.append({
            "summary": str(event.get("SUMMARY")),
            "start": str(event.get("dtstart").dt.strftime("%a, %b %-d, %Y, %-I:%M %p")),
            "end": str(event.get("dtend").dt.strftime("%a, %b %-d, %Y, %-I:%M %p"))
        })
    res = sorted(res, key=lambda x: datetime.strptime(
        x["start"], "%a, %b %d, %Y, %I:%M %p"), reverse=True)
    return jsonify(events=res)


@app.route('/api/process_prompt', methods=['POST'])
def process_prompt():
    data = request.get_json()
    res = ner(data.get('prompt', None), data.get('user', None))
    message = "Event created successfully!" if res[
        "success"] else "A valid event could not be determined from your input."
    return jsonify(result=res, message=message)


def ner(prompt: str, user: dict):  # Named entity recognition (NER)
    nlp_ner = spacy.load("./ner/model")
    doc = nlp_ner(prompt)
    date = []
    time = []
    description = []
    relative = []

    # Determine all entites
    for ent in doc.ents:
        if ent.label_ == "RELATIVE":
            relative.append(ent.text)
        elif ent.label_ == "TIME":
            time.append(ent.text)
        elif ent.label_ == "DESCRIPTION":
            description.append(ent.text)
        elif ent.label_ == "DATE":
            date.append(ent.text)

    # If no fixed dates and relative dates, or description, detected, then unsuccessful
    if (len(date) == 0 and len(relative) == 0) or (len(description) == 0):
        return {"success": False}
    else:
        return parsing(date, time, relative, description, user)


def parsing(raw_dates, raw_times, raw_relative, raw_description, user):
    parsed_dates = []
    parsed_times = []

    # convert all dates in 'raw_dates' array to datetime.date objects and append them to 'parsed_dates' array
    for i in range(len(raw_dates)):
        time_struct, parse_status = parsedatetime.Calendar().parse(
            raw_dates[i])
        if parse_status != 0:
            parsed_dates.append(date(*time_struct[:3]))

    # convert all relative dates in 'raw_relative' array to datetime.date objects and append them to 'parsed_dates' array
    for i in range(len(raw_relative)):
        time_struct, parse_status = parsedatetime.Calendar().parse(
            raw_relative[i])
        if parse_status != 0:
            parsed_dates.append(date(*time_struct[:3]))

    # convert all times in 'raw_times' array to datetime.time objects and append them to 'parsed_times' array
    for i in range(len(raw_times)):
        time_struct, parse_status = parsedatetime.Calendar().parse(
            raw_times[i])
        if parse_status != 0:
            parsed_times.append(
                time(*time_struct[3:5], tzinfo=pytz.timezone(user["timezone"])))
            
    # for v1.0, only support start and end dates, so only have a maximum of two dates
    parsed_dates = parsed_dates[:2]
    parsed_times = parsed_times[:2]  # same applies to times

    # if no dates can be parsed, immediately return False
    if len(parsed_dates) == 0:
        return {"success": False}
    else:
        return ics(parsed_dates, parsed_times, str.title(' '.join(raw_description)), user)


def ics(parsed_dates, parsed_times, description, user):
    start, end = None, None

    # Case 1: 1 date, 1 time [i.e. end time not specified]
    if (len(parsed_dates) == len(parsed_times) == 1):
        start = datetime.combine(parsed_dates[0], parsed_times[0])

        # If end time is not specified, the default duration will be set to 30 minutes
        end = start + timedelta(minutes=30)

    # Case 2: 1 date, 2 times [i.e. start and end time both specified]
    elif (len(parsed_dates) == 1 and len(parsed_times) == 2):
        start = datetime.combine(parsed_dates[0], parsed_times[0])
        end = datetime.combine(parsed_dates[0], parsed_times[1])

    # Case 3: 2 dates, 2 times [i.e. start date & time with end date & time]
    elif (len(parsed_dates) == len(parsed_times) == 2):
        start = datetime.combine(parsed_dates[0], parsed_times[0])
        end = datetime.combine(parsed_dates[1], parsed_times[1])
        
    # Case 4: 1 date, no times [i.e. all-day event]
    elif (len(parsed_dates) == 1 and len(parsed_times) == 0):
        # For all-day events, we input just the date (without any time) in ICS file
        start = parsed_dates[0]
        end = start  # For all-day events, start date and end date are equal in ICS file

    # Case 5: 2 dates, no times [i.e. all-day event everyday from starting to ending date]
    elif (len(parsed_dates) == 2 and len(parsed_times) == 0):
        start = parsed_dates[0]
        end = parsed_dates[1]

    # If no case is fulfilled, return unsuccessful status
    else:
        return {"success": False}

    # Add dates to ICS event
    event = Event()
    event.add('dtstart', start)
    event.add('dtend', end)
    event.add('summary', description)
    event.add('dtstamp', datetime.now())

    # This is a uuid for the ical event itself; it is not related to the user's uuid
    event.add('uid', str(uuid.uuid4()))

    # Initalize S3 client
    load_dotenv()
    s3 = boto3.client('s3',
                      aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.environ.get(
                          'AWS_SECRET_ACCESS_KEY'),
                      region_name=os.environ.get('AWS_REGION')
                      )
    
    # Change url depending on if the user is existing or new
    ics_url = os.environ.get('S3_ICS_URL_PREFIX') + user['uuid'] + '.ics'
    if (user["new_user"]):
        ics_url = os.environ.get('S3_SKELETON_ICS_URL')

    # Get content of corresponding ICS file from S3
    ical = Calendar.from_ical(requests.get(ics_url).text)
    ical.add_component(event)

    # Write the calendar with new event to ICS file
    file_name = user["uuid"] + '.ics'
    with open(file_name, 'wb') as file:
        file.write(ical.to_ical())
    file.close()

    # Upload the ICS file to S3
    s3.upload_file(file_name, os.environ.get(
        'S3_BUCKET_NAME'), 'ics/' + file_name)
    
    # Remove local ICS file
    os.remove(file_name)
    return {
        "start": start,
        "end": end,
        "description": description,
        "success": True,
        "uuid": user["uuid"],
        "new_user": user["new_user"],
        "timezone": user["timezone"],
        "link": os.environ.get('S3_ICS_URL_PREFIX') + file_name
    }

if __name__ == "__main__":
    app.run(port=8080)
