from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime
import gspread
import json, math, random
import os

load_dotenv()

app = Flask(__name__)
# app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')

db = SQLAlchemy(app)

# Initialize Google Sheets API
gc = gspread.service_account(filename=os.getenv("SERVICE_ACCOUNT_FILE"))
sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1ACRkJCkIy8Ovr2gVJZykc0p145GFbhf_sK1KG0wHr2w/edit#gid=0').sheet1

class MentorChecklist(db.Model):
    __tablename__ = 'mentor_checklist'

    id = db.Column(db.BigInteger, primary_key=True)
    cme_completion_date = db.Column(db.Date, nullable=True)
    cme_topic = db.Column(db.Text)
    cme_unique_id = db.Column(db.BigInteger, nullable=True)
    county = db.Column(db.Text)
    date_submitted = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    drill_topic = db.Column(db.Text)
    drill_unique_id = db.Column(db.Text)
    essential_cme_topic = db.Column(db.Boolean, default=False)
    essential_drill_topic = db.Column(db.Boolean, default=False)
    facility_code = db.Column(db.Text)
    facility_name = db.Column(db.Text)
    id_number_cme = db.Column(db.Text)
    id_number_drill = db.Column(db.Text)
    mentor_name = db.Column(db.Text)
    submission_id = db.Column(db.BigInteger)
    success_story = db.Column(db.Text)

    def json(self):
        return {
            'id' : self.id,
            'cme_completion_date' : self.cme_completion_date,
            'cme_topic' : self.cme_topic,
            'cme_unique_id' : self.cme_unique_id,
            'county' : self.county,
            'date_submitted' : self.date_submitted,
            'drill_topic' : self.drill_topic,
            'drill_unique_id' : self.drill_unique_id,
            'essential_cme_topic' : self.essential_cme_topic,
            'essential_drill_topic' : self.essential_drill_topic,
            'facility_code' : self.facility_code,
            'facility_name' : self.facility_name,
            'id_number_cme' : self.id_number_cme,
            'id_number_drill' : self.id_number_drill,
            'mentor_name' : self.mentor_name,
            'submission_id' : self.submission_id,
            'success_story' : self.success_story
        }

with app.app_context():   
    db.create_all()

# Create a test route
@app.route('/test')
def test_route():
    return make_response(jsonify({'message' : 'Testing routes'}), 200)

@app.route('/get_participation')
def get_participation():
    participation = MentorChecklist.query.all()
    return make_response(jsonify({'Participations' : [record.json() for record in participation]}), 200)

@app.route('/delete_participation')
def delete_participation():
    participation = MentorChecklist.query.all()
    for participant in participation:
        db.session.delete(participant)
        db.session.commit()
    return make_response(jsonify({'message' : 'All records deleted!'}), 200)
    

def both_cme_and_drill_done(assessment):
    assessments_done = assessment.split()
    if len(assessments_done) > 1:
        return True
    return False

def get_facility_code(county, record):
    name = f"mentor_checklist/mentor/q_facility_{county.lower()}"

    facility_name_list = record[name].split("_")
    facility_code = facility_name_list.pop(0)
    facility_name = ' '.join(facility_name_list)
    return facility_code, facility_name

def convert_topic_names(topic_name):
    topic_arr = topic_name.split("/")
    correct_name = topic_arr[0].replace('_', ' ')
    return correct_name
    

def check_cme_unique_code(cme_topic):
    digits = 8
    try:
        cme_unique_code = MentorChecklist.query.filter_by(cme_topic=cme_topic).first()
        cme_unique_code = cme_unique_code.cme_unique_id
    except:
        min = 10**(digits-1)
        max = 10**digits - 1
        cme_unique_code = random.randint(min, max)
    return cme_unique_code

def check_drill_unique_code(drill_topic):
    digits = 8
    try:
        drill_unique_code = MentorChecklist.query.filter_by(drill_topic=drill_topic).first()
        drill_unique_code = drill_unique_code.drill_unique_id
    except:
        min = 10**(digits-1)
        max = 10**digits - 1
        drill_unique_code = random.randint(min, max)
    return drill_unique_code

def get_cme_providers(record):
    column_name = "mentor_checklist/cme_grp/standard_phone_numbers_cme/"
    all_cme_providers = []
    for i in record:
        if column_name in i and record[i]:
            all_cme_providers.append(record[i])
    return all_cme_providers

def check_essential_cme_topic(topic, essential_topics):
    if topic in essential_topics:
        return True
    return False

def check_essential_drill_topic(topic, essential_topics):
    if topic in essential_topics:
        return True
    return False

def get_drill_providers(record):
    column_name = "mentor_checklist/drills_grp/id_numbers_drill/"
    all_drill_providers = []
    for i in record:
        if column_name in i and record[i]:
            all_drill_providers.append(record[i])
    return all_drill_providers


    
@app.route('/process_and_store', methods=['POST'])
def process_and_store():
    try:
        essential_cme_topics = ['Postpartum haemorrhage (PPH)', 'Infection prevention']
        essential_drill_topics = ['Eclampsia']
        # Process data (replace this with your processing logic)
        data_to_process = []
        for record in sheet.get_all_records():
            if record['__version__']:
                data_to_process.append(record)

        
        for record in data_to_process:
            cme_completion_date = record['mentor_checklist/cme_grp/cme_completion_date'] if record['mentor_checklist/cme_grp/cme_completion_date'] != '' else None
            county = record['mentor_checklist/mentor/q_county'] 
            date_submitted = record['_submission_time']
            facility_code = get_facility_code(county, record)[0]
            facility_name = get_facility_code(county, record)[1]
            mentor_name = record['mentor_checklist/mentor/name']
            submission_id = int(record['_id'])
            success_story = record['mentor_checklist/success_grp/story_success'] if record['mentor_checklist/success_grp/story_success'] != "" else ""
            # Total sessions
            total_cmes = int(record['mentor_checklist/cme_grp/cme_total']) if record['mentor_checklist/cme_grp/cme_total'] != '' else 0
            total_drills = int(record['mentor_checklist/drills_grp/drills_total']) if record['mentor_checklist/drills_grp/drills_total'] != '' else 0
            # get attendees
            cme_providers = get_cme_providers(record)
            drill_providers = get_drill_providers(record)

            # Session topics
            cme_topic_1 = convert_topic_names(record['mentor_checklist/cme_grp/cme_topics']) if record['mentor_checklist/cme_grp/cme_topics'] != '' else ""
            cme_topic_2 = convert_topic_names(record['mentor_checklist/cme_grp/cme_topics_2']) if record['mentor_checklist/cme_grp/cme_topics_2'] != '' else ""

            drill_topic_1 = convert_topic_names(record['mentor_checklist/drills_grp/drill_topics']) if record['mentor_checklist/drills_grp/drill_topics'] != '' else ""
            drill_topic_2 = convert_topic_names(record['mentor_checklist/drills_grp/drill_topics_2']) if record['mentor_checklist/drills_grp/drill_topics_2'] != '' else ""

            # Ensure there are no blank cme topics as well as drill topics
            cme_topics = []
            if cme_topic_1 != "":
                cme_topics.append(cme_topic_1)
            if cme_topic_2 != "":
                cme_topics.append(cme_topic_2)

            drill_topics = []
            if drill_topic_1 != "":
                drill_topics.append(drill_topic_1)
            if drill_topic_2 != "":
                drill_topics.append(drill_topic_2)

            if total_cmes > 0 and len(cme_topics) > 0:
                topics = len(cme_topics)
                while topics > 0:
                    for cme_topic in cme_topics:
                        for cme_provider in cme_providers:
                            data = {
                                'cme_completion_date' : cme_completion_date,
                                'cme_topic' : cme_topic,
                                'cme_unique_id' : check_cme_unique_code(cme_topic),
                                'county' : county,
                                'date_submitted' : date_submitted,
                                'drill_topic' : "",
                                'drill_unique_id' : "",
                                'essential_cme_topic' : check_essential_cme_topic(cme_topic, essential_cme_topics),
                                'essential_drill_topic' : False,
                                'facility_code' : facility_code,
                                'facility_name' : facility_name,
                                'id_number_cme' : cme_provider,
                                'id_number_drill' : "",
                                'mentor_name' : mentor_name,
                                'submission_id' : submission_id,
                                'success_story' : success_story
                            }
                            cme_checklist_instance = MentorChecklist(
                                cme_completion_date=data['cme_completion_date'],
                                cme_topic=data['cme_topic'],
                                cme_unique_id=data['cme_unique_id'],
                                county=data['county'],
                                date_submitted=data['date_submitted'],
                                drill_topic=data['drill_topic'],
                                drill_unique_id=data['drill_unique_id'],
                                essential_cme_topic=data['essential_cme_topic'],
                                essential_drill_topic=data['essential_drill_topic'],
                                facility_code=data['facility_code'],
                                facility_name=data['facility_name'],
                                id_number_cme=data['id_number_cme'],
                                id_number_drill=data['id_number_drill'],
                                mentor_name=data['mentor_name'],
                                submission_id=data['submission_id'],
                                success_story=data['success_story']
                            )
                            db.session.add(cme_checklist_instance)
                            db.session.commit()
                    
                    topics -= 1
                total_cmes -= 1

            if total_drills > 0 and len(drill_topics) > 0:
                drill_topics_count = len(drill_topics)
                while drill_topics_count > 0:
                    for drill_topic in drill_topics:
                        for drill_provider in drill_providers:
                            data = {
                                'cme_completion_date' : cme_completion_date,
                                'cme_topic' : "",
                                'cme_unique_id' : None,
                                'county' : county,
                                'date_submitted' : date_submitted,
                                'drill_topic' : drill_topic,
                                'drill_unique_id' : check_drill_unique_code(drill_topic),
                                'essential_cme_topic' : False,
                                'essential_drill_topic' : check_essential_drill_topic(drill_topic, essential_drill_topics),
                                'facility_code' : facility_code,
                                'facility_name' : facility_name,
                                'id_number_cme' : "",
                                'id_number_drill' : drill_provider,
                                'mentor_name' : mentor_name,
                                'submission_id' : submission_id,
                                'success_story' : success_story
                            }
                            drill_checklist_instance = MentorChecklist(
                                cme_completion_date=data['cme_completion_date'],
                                cme_topic=data['cme_topic'],
                                cme_unique_id=data['cme_unique_id'],
                                county=data['county'],
                                date_submitted=data['date_submitted'],
                                drill_topic=data['drill_topic'],
                                drill_unique_id=data['drill_unique_id'],
                                essential_cme_topic=data['essential_cme_topic'],
                                essential_drill_topic=data['essential_drill_topic'],
                                facility_code=data['facility_code'],
                                facility_name=data['facility_name'],
                                id_number_cme=data['id_number_cme' ],
                                id_number_drill=data['id_number_drill'],
                                mentor_name=data['mentor_name'],
                                submission_id=data['submission_id'],
                                success_story=data['success_story']
                            )
                            db.session.add(drill_checklist_instance)
                            db.session.commit()
                        
                    drill_topics_count -= 1
                total_drills -= 1

        return jsonify({"message": "Process successful"})
    except Exception as e:
        return jsonify({"error": str(e)})


