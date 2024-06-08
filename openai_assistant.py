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
        prompt = '''What should be skills for this person: 
        Designation: {designation}
        Team: {team}
        Industry: {industry},
        Work Experience: {work_experience},
        Day at Work: {day_at_work}
        Selected Skills: {selected_skills}
        Additional Tasks the person want to do for personal growth: {additional_work}
        Tasks the person wants to handover: {handover}
        Provide the categories and skills inside those categories
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
