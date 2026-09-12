import yaml
import openai
from datetime import datetime
from mongo_connect import MongoConnect


class ChatbotAssistant:
    def __init__(self):
        # Initialize any necessary attributes or resources here
        with open("configs/config.yaml", "r") as f:
            cx = yaml.safe_load(f)

        self.client = openai.OpenAI(
            # This is the default and can be omitted
            api_key=cx['openai']['api_key'],
        )
        self.mongo_client = MongoConnect()
        self.mongo_object = None
        self.object_id = None
        self.skills_options = None
        self.skills_map = None
        self.model = cx['openai'].get('model', 'gpt-3.5-turbo')
        pass


    def chat_completion(self, messages, key):
        """
        Generates skills for the employee based on input parameters.

        Args:
            messages: Array of user, assistant and system messages
            key: Specify the type of task that the chat completion is being used for

        Returns:
            str: Generated response
        """
        print(messages)
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
        )
        response = chat_completion.choices[0].message.to_dict()['content']
        self.mongo_client.update({
            "$addToSet": {
                "runs": {
                    "run_at": datetime.now(),
                    "key": key,
                    "messages": messages,
                    "model": self.model,
                    "response": chat_completion.to_dict()
                }
            }
        })
        return response


    def generate_skills_options(self, prompt_variables):
        """
        Generates skills options for the employee based on input parameters

        Args:
            prompt_variables: Variables to be used in prompts

        Returns:
            str: Generate Skills Options
        """
        self.object_id = self.mongo_client.create_new()
        prompt = '''I need a list of 30 skills for an employee based on their professional profile. 
        Provide the skills for the following role:
        1. Title: {designation}
        2. Work Experience total: {work_experience} years
        3. Industry: {industry}
        4. Team: {team}
        5. How does their work day look like: {day_at_work}
        
        Output format:
        {{
        "designation" : <>, "work_experience" : <>, "industry" : <>, "team": <>, "selected_skills" : []
        }}
        
        Give only json as output. 
        Do not put \'''json\''' in your output.
        '''.format(
            designation=prompt_variables['designation'],
            team=prompt_variables['team'],
            industry=prompt_variables['industry'],
            work_experience=prompt_variables['work_experience'],
            day_at_work=prompt_variables['day_at_work']
        )

        messages = [{
            "role": "user",
            "content": prompt
        }]

        # Use OpenAI chat completion to generate skills
        self.skills_options = self.chat_completion(messages, key='skills')
        return {
            'id': self.object_id,
            'skills_options': self.skills_options
        }


    def generate_skills_map(self, prompt_variables, object_id):
        """
        Generates skills options for the employee based on input parameters

        Args:
            prompt_variables: Variables to be used in prompts

        Returns:
            str: Generate Skills Options
        """
        self.object_id = object_id
        prompt = '''Based on the information provided below, provide 6 statements about the skills and tasks that they person is doing. 
        
        ## Information about the user:
        - Designation: {designation}
        - Team: {team}
        - Industry: {industry},
        - Work Experience: {work_experience},
        - Typical day at Work: {day_at_work}
        - Selected Skills: {selected_skills}
        - Additional tasks they want to do for personal growth: {additional_work}
        - Tasks they wants to handover: {handover}
        
        Output: 
        - Provide 6 statements about the skills and tasks the person in their current role is doing. 
        - Of these 6, 3 statements should be encouraging mentioning the skills they have selected
        - Of these 6, 3 should be about what they should focus more on and improve
        - Do not provide any additional statements
        '''.format(
            designation=prompt_variables['designation'],
            team=prompt_variables['team'],
            industry=prompt_variables['industry'],
            work_experience=prompt_variables['work_experience'],
            day_at_work=prompt_variables['day_at_work'],
            selected_skills=prompt_variables['selected_skills'],
            additional_work=prompt_variables['additional_work'],
            handover=prompt_variables['handover']
        )

        messages = [{
            "role": "user",
            "content": prompt
        }]

        # Use OpenAI chat completion to generate skills
        self.skills_options = self.chat_completion(messages, key='skills')
        return {
            'id': self.object_id,
            'skills_options': self.skills_options
        }


    def find_object_or_create(self, token):
        mongo_object = {'stage': 0}
        return mongo_object

    def generate_next_stage(self, token, last_user_input):
        self.mongo_object = self.mongo_client.find_object_or_create(token)
        last_stage_num = last_user_input.get('stage', 0)
        stage_num = last_stage_num + 1
        if stage_num != 1:
            self.mongo_client.update({"$addToSet": {"stage": last_user_input}})
        self.mongo_object = self.mongo_client.find_object_or_create(token)

        if stage_num == 1:
            response = {
                'stage': 1,
                'title': '',
                'subtitle': '',
                'questions': [
                    {'q': 'Enter your name', 't': 'SHORT_TEXT'},
                    {'q': 'Enter your gender', 't': 'OPTIONS', 'o': ['Male', 'Female', 'Other']},
                    {'q': 'What industry does your company work in?', 't': 'SHORT_TEXT'},
                    {'q': 'What is your designation?', 't': 'SHORT_TEXT'},
                    {'q': 'Which team do you work in?', 't': 'SHORT_TEXT'}
                ]
            }
        elif stage_num == 2:
            response = {
                'stage': 2,
                'title': '',
                'subtitle': '',
                'questions': [
                    {'q': 'What does your typical day at work look like?', 't': 'LONG_TEXT'},
                    {'q': 'How many years of work experience do you have?', 't': 'NUMERIC'}
                ]
            }
        elif stage_num == 3:
            skills = self.generate_skills_by_category()
            cs = [[k, v] for k, v in skills.items()]
            response = {
                'stage': 3,
                'title': '',
                'subtitle': '',
                'questions': [
                    {'q': 'Which of these {} skills are you good at?'.format(cs[0][0]), 't': 'OPTIONS', 'o': cs[0][1]},
                    {'q': 'Which of these {} skills do you feel most confident in?'.format(cs[1][0]), 't': 'OPTIONS', 'o': cs[1][1]},
                    {'q': 'Which of these {} skills do you consider your strengths?'.format(cs[2][0]), 't': 'OPTIONS', 'o': cs[2][1]}
                ]
            }
        elif stage_num == 4:
            response = {
                'stage': 4,
                'title': '',
                'subtitle': '',
                'questions': [
                    {'q': 'Mention a few things you would like to do additionally for your personal growth?', 't': 'LONG_TEXT'},
                    {'q': 'Mention a few things you would like handover to someone else?', 't': 'LONG_TEXT'}
                ]
            }
        elif stage_num == 5: #sneakpeek
            sneakpeek = self.generate_sneakpeek()
            response = {
                'stage': 5,
                'title': 'Here is your Skill Analysis!',
                'subtitle': sneakpeek
            }
        return response

    def generate_skills_by_category(self):
        stages = self.mongo_object.get('stage', [])
        if len(stages) < 2:
            raise Exception("Stages not correctly present")

        prompt = '''I need a list of 30 skills for an employee based on their professional profile. 
                Provide the skills for the following role:
                1. Title: {designation}
                2. Work Experience total: {work_experience} years
                3. Industry: {industry}
                4. Team: {team}
                5. How does their work day look like: {day_at_work}

                Output format:
                {{
                "designation" : <>, "work_experience" : <>, "industry" : <>, "team": <>, "selected_skills" : []
                }}

                Give only json as output. 
                Do not put \'''json\''' in your output.
                '''.format(
            industry=stages[0][2]['a'],
            designation=stages[0][3]['a'],
            team=stages[0][4]['a'],
            day_at_work=stages[1][0]['a'],
            work_experience=stages[1][1]['a']
        )

        messages = [{
            "role": "user",
            "content": prompt
        }]

        # Use OpenAI chat completion to generate skills
        skills_by_category = self.chat_completion(messages, key='skills')
        return skills_by_category

    def generate_sneakpeek(self):
        stages = self.mongo_object.get('stage', [])
        if len(stages) < 4:
            raise Exception("Stages not correctly present")

        prompt = '''Based on the information provided below, provide 6 statements about the skills and tasks that they person is doing. 

                ## Information about the user:
                - Designation: {designation}
                - Team: {team}
                - Industry: {industry},
                - Work Experience: {work_experience},
                - Typical day at Work: {day_at_work}
                - Selected Skills: {selected_skills}
                - Additional tasks they want to do for personal growth: {additional_work}
                - Tasks they wants to handover: {handover}

                Output: 
                - Provide 6 statements about the skills and tasks the person in their current role is doing. 
                - Of these 6, 3 statements should be encouraging mentioning the skills they have selected
                - Of these 6, 3 should be about what they should focus more on and improve
                - Do not provide any additional statements
                '''.format(
            industry=stages[0][2]['a'],
            designation=stages[0][3]['a'],
            team=stages[0][4]['a'],
            day_at_work=stages[1][0]['a'],
            work_experience=stages[1][1]['a'],
            selected_skills=','.join(stages[2][0]['a'] + stages[2][1]['a'] + stages[2][2]['a']),
            additional_work=stages[3][0]['a'],
            handover=stages[3][1]['a']
        )

        messages = [{
            "role": "user",
            "content": prompt
        }]

        # Use OpenAI chat completion to generate skills
        sneakpeek = self.chat_completion(messages, key='sneakpeek')
        return sneakpeek