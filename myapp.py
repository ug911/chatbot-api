from flask import Flask, request, send_file
from flask_cors import CORS
from openai_assistant import ChatbotAssistant

app = Flask(__name__)
CORS(app)

chatbot_assistant = ChatbotAssistant()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/get_skills_options', methods=['POST'])
def get_skills_options():
    # Get the value of the 'additional_words' parameter from the POST request
    name = request.form.get('name')
    gender = request.form.get('gender')
    designation = request.form.get('designation')
    team = request.form.get('team')
    industry = request.form.get('industry')
    work_experience = request.form.get('work_experience')
    day_at_work = request.form.get('day_at_work')
    debug = request.form.get('debug')

    prompt_variables = {
        'designation': designation,
        'team': team,
        'industry': industry,
        'work_experience': work_experience,
        'day_at_work': day_at_work
    }

    msg = '\n'.join(['{}:{}'.format(k, v) for k, v in prompt_variables.items()])
    print('{}/{}'.format(name, gender))
    print(msg)
    if not debug:
        result = chatbot_assistant.generate_skills_options(prompt_variables=prompt_variables)
    else:
        result = {
            'message': msg
        }
    return result


@app.route('/get_skills_map', methods=['POST'])
def get_skills_map():
    # Get the value of the 'additional_words' parameter from the POST request
    mongo_object_id = request.form.get('id')
    name = request.form.get('name')
    gender = request.form.get('gender')
    designation = request.form.get('designation')
    team = request.form.get('team')
    industry = request.form.get('industry')
    work_experience = request.form.get('work_experience')
    day_at_work = request.form.get('day_at_work')
    selected_skills = request.form.get('selected_skills')
    additional_work = request.form.get('additional_work')
    handover = request.form.get('handover')
    debug = request.form.get('debug')

    prompt_variables = {
        'designation': designation,
        'team': team,
        'industry': industry,
        'work_experience': work_experience,
        'day_at_work': day_at_work,
        'selected_skills': selected_skills,
        'additional_work': additional_work,
        'handover': handover
    }

    msg = '\n'.join(['{}:{}'.format(k, v) for k, v in prompt_variables.items()])
    print('{}/{}'.format(name, gender))
    print(msg)
    if not debug:
        result = chatbot_assistant.generate_skills_map(prompt_variables=prompt_variables, object_id=mongo_object_id)
    else:
        result = {
            'message': msg
        }
    return result

