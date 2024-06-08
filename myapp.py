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
    data = request.json
    # Get the value of the 'additional_words' parameter from the POST request
    name = data.get('name')
    gender = data.get('gender')
    designation = data.get('designation')
    team = data.get('team')
    industry = data.get('industry')
    work_experience = data.get('work_experience')
    day_at_work = data.get('day_at_work')
    debug = data.get('debug')

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
    data = request.json
    mongo_object_id = data.get('id')
    name = data.get('name')
    gender = data.get('gender')
    designation = data.get('designation')
    team = data.get('team')
    industry = data.get('industry')
    work_experience = data.get('work_experience')
    day_at_work = data.get('day_at_work')
    selected_skills = data.get('selected_skills')
    additional_work = data.get('additional_work')
    handover = data.get('handover')
    debug = data.get('debug')

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

