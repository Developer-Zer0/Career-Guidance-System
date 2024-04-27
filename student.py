import random
import json
import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = api_key=os.getenv("OPENAI_API_KEY")

class Student():

  def __init__(self, orig_schema, llm='gpt'):
    self.schema = orig_schema
    self.llm = llm
    self.history = []
    self.last_detected_fields = []
    self.threshold = 0.6

  def llm_request(self, prompt, mode='text'):
    if self.llm == 'gpt':
      if mode == 'json':
        r = self.gpt4_request(prompt, 'json_object')
        # print(r)
        response = json.loads(r.content)
      else:
        r = self.gpt4_request(prompt)
        response = r.content
      return response

    elif self.llm == 'llama':
      pass

  def gpt4_request(self, prompt, mode='text', temperature=1, max_tokens=2048):
    message=[{"role": "system", "content": prompt}]
    frequency_penalty=0.0

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = message,
        response_format={ "type":mode },
        temperature=temperature,
        max_tokens=max_tokens,
        frequency_penalty=frequency_penalty
    )
    return response.choices[0].message

  def fill_init_schema(self, description):
    sys_prompt = """
      You are given an empty schema of a person in JSON format. You are also given a short description of the person.
      You need to extract information from the description and add it to the relevant fields in the schema.
      For example, if the description contains the person's name then you must add it under Demographics.Name in the schema.
      You must output the final JSON after adding all the information.
      """
    nl = "\n"
    final_prompt = f'{sys_prompt}{nl}{str(self.schema.get_schema())}{nl}{description}{nl}'
    # print(final_prompt)
    response = self.llm_request(final_prompt, 'json')
    # print(response)

    ##TODO Check if returned schema has the same keys as the original schema
    # self.schema = response
    self.schema.curr_schema = response

  def update_schema(self, user_dialogue, sys_values, sys_response, relevant_fields):
    # Option 1: Manually fill in values
    # assert len(sys_values) == len(relevant_fields)
    # for ind, field in enumerate(relevant_fields):
    #   if field[1] == 'new':
    #     pass
    #   elif field[1] == 'previous':
    #     pass
    #   elif field == 'continue_dialogue':
    #     pass
    #   elif field == 'suggest_career':
    #     pass

    # Option 2: Use ChatGPT to fill in schema
    sys_prompt = """
      You are given a partially filled schema of a person in JSON format. You are also given a question asked to the person and a response by the person.
      You need to extract information from the response and add it to the relevant fields in the schema.
      For example, if the response contains the person's middle school's name then you must add it under Education.Middle-School.Name in the schema.
      You must output the final JSON after adding all the information.
      """
    nl = "\n"
    final_prompt = f'{sys_prompt}{nl}{str(self.schema.get_schema())}{nl}{user_dialogue}{nl}{sys_response}{nl}'
    # print(final_prompt)
    response = self.llm_request(final_prompt, 'json')
    # print(response)

    ##TODO Check if returned schema has the same keys as the original schema
    # self.schema = response
    self.schema.curr_schema = response

  def respond(self, user_dialogue):
    relevant_fields = self.select_schema_fields(user_dialogue)

    empty_flag = False
    # print(fields)
    # for field in relevant_fields:
    # f = field.split('_')
    if relevant_fields[0] == 'continue_dialogue':
      sys_prompt = """
        You are given a schema of a student in JSON format. This schema represents the information and personality of the student. You are in a dialogue with a career counsellor.
        You are also given the current counsellor utterance and the previous dialogue history between the counsellor and you.
        Make sure that you respond properly to the counsellor's utterance by referring to the previous dialogue history. Answer as if you were the student given in the schema.
        """
      q = f'{user_dialogue}'
      nl = "\n"
      final_prompt = f'{str(self.schema.get_schema())}{nl}<Dialogue History>: {self.history}{nl}{sys_prompt}{nl}<Counsellor Utterance>: {q}{nl}'
      print(final_prompt)
      r = self.llm_request(final_prompt)
      print(r)

      self.update_schema(user_dialogue, None, r, relevant_fields)

      self.history.append(f'Counsellor: {user_dialogue}{nl}')
      self.history.append(f'System: {r}{nl}')

      return r

    elif relevant_fields[0] == 'suggest_career':

      
      if self.schema.progress_percent() <= self.threshold*100:
        empty_field = self.schema.choose_random_empty()
        sys_prompt = """
          You are given a schema of a student in JSON format. This schema represents the information and personality of the student. You are in a dialogue with a career counsellor.
          You are also given the current counsellor utterance and the previous dialogue history between the counsellor and you.
          The counsellor has suggested you a career choice. You need to reject this suggestion as it too early in the dialogue.
          You will be given Field following the suggestions which is currently empty in the JSON schema. You need to generate values and a story for that field which will also help you to explain why you are rejecting the counsellor's suggestion.
          You are given two examples. Answer as if you were the person given in the schema.
          ## Example 1. <Counsellor Suggestion>: I think you should become a Doctor. <Field>: Relationships.Mother <Answer>: My mother is actually a Surgeon. She works at Apollo Hospital in Luton Town. But since my childhood, she has always been busy. She never has time for her family and I have very few memories of her. I feel like I want a career where I can have a proper work-life balance. So, I don't think being a Doctor is for me.
          ## Example 2. <Counsellor Suggestion>: Have you considered Engineering as your career? <Field>: Education.High-School <Answer>: In the third year of my high school, I took a lot of Math courses. I quickly realized performing huge number of calculations is not for me. I don't think Engineering would be a good idea.
          """
        q = f'<Counsellor Suggestion>: {user_dialogue} <Field>: {empty_field} <Answer>: '
        nl = "\n"
        final_prompt = f'{str(self.schema.get_schema())}{nl}<Dialogue History>: {self.history}{nl}{sys_prompt}{nl}{q}{nl}'
        print(final_prompt)
        r = self.llm_request(final_prompt)
        print(r)

        self.update_schema(user_dialogue, None, r, empty_field)
        
        self.history.append(f'Counsellor: {user_dialogue}{nl}')
        self.history.append(f'System: {r}{nl}')

        return r
      
      else:
        sys_prompt = """
          You are given a schema of a student in JSON format. This schema represents the information and personality of the student. You are in a dialogue with a career counsellor.
          You are also given the current counsellor utterance and the previous dialogue history between the counsellor and you.
          The counsellor has suggested you a career choice. You need to cross-check the suggestion with your schema.
          Accept the suggestion if it makes sense with respect to the dialogue you have had till now and the career seems in line with the personality in the schema. Reject if the suggestion contradicts the dialogue and schema.
          Answer as if you were the person given in the schema.
          """
        q = f'{user_dialogue}'
        nl = "\n"
        final_prompt = f'{str(self.schema.get_schema())}{nl}<Dialogue History>: {self.history}{nl}{sys_prompt}{nl}<Counsellor Suggestion>: {q}{nl}'
        print(final_prompt)
        r = self.llm_request(final_prompt)
        print(r)

        self.history.append(f'Counsellor: {user_dialogue}{nl}')
        self.history.append(f'System: {r}{nl}')

        return r
    
    else:
      gen_f = ', '.join(relevant_fields)
      sys_prompt = """
        You are given a schema of a young student in JSON format. This schema represents the information and personality of the student. You are also given a question asked to the student.
        You are also given fields in the schema that do not contain any information. You can choose to generate values for that field while answering the given question as the student.
        You are also given the previous dialogue history between the counsellor and student. Make sure you use that before answering the question to keep the information consistent.
        The values that you generate must be included in your answer somewhere. Also, make sure that the values you create are consistent with the person's personality given by the schema
        Wherever possible come up with a specific story for your selected value. Try incorporating that story in your response.
        Make sure that the answer completely responds to the question. Do not repeat sentences that are already present in the dialogue history.
        Wherever applicable generate a small anecdote accompanying your response while also keeping it consistent with the schema.
        You are given two examples. Answer as if you were that student.
        ## Example 1. <Question> Where have you worked previously? <Field> Work-experience <Value> Town library <Answer> Um... I was a part-timer at the Town Library for a year during my high school. My father's friend works there and so his referral got me the job.
        ## Example 2. <Question> Tell me something about your family and upbringing? <Field> Relationships.Mother.Name <Value> Martha <Answer> Let me think. Yeah my mother, Martha is a really strict person. She rarely lets me play outside with my friends. It was always this exam and that exam that she had me studying for. I feel I am also bad at making decisions for myself because I rely on her.
        ## Example 3. <Question> Can you list me your education history? <Field> Education.Elementary-School, Education-College <Value> Nancy, Carlton's Community College <Answer> Sure! My elementary school was Nancy and then I went to St. Mary's Middle School. After that I attended the same school for my High School. Finally, I am right now in Carlton's Community College.
        You must output value and the Answer in the above format.
        """
      q = f'<Question> {user_dialogue} <Field> {gen_f}'
      nl = "\n"
      final_prompt = f'{str(self.schema.get_schema())}{nl}<Dialogue History>: {self.history}{nl}{sys_prompt}{nl}{q}{nl}'
      print(final_prompt)
      r = self.llm_request(final_prompt)
      print(r)
      _, _, response = r.partition('<Value>')
      sys_values, _, sys_response = response.partition('<Answer>')
      print('Sys_value: ', sys_values, 'sys_answer: ', sys_response)

      self.update_schema(user_dialogue, sys_values, sys_response, relevant_fields)

      self.history.append(f'Counsellor: {user_dialogue}{nl}')
      self.history.append(f'System: {sys_response}{nl}')

      return sys_response

  def select_schema_fields(self, dialogue):

    # Option 2
    sys_prompt = """
      You are given a schema of a person in JSON format and the dialogue history between the counsellor and you. This schema represents the information and personality of the person. You are also given a question asked to the person.
      From the question, you need to choose the dialog acts that represent the question.
      You need to refer to the person's schema and the dialogue history to determine if new information is asked or information about a previous field is asked.
      The list of dialog acts from which you can choose are ['suggest_career','request_new_Demographics_Name','retrieve_previous_Demographics_Name','request_new_Demographics_Age','retrieve_previous_Demographics_Age','request_new_Demographics_Gender','retrieve_previous_Demographics_Gender','request_new_Demographics_Race','retrieve_previous_Demographics_Race','request_new_Demographics_Current-Residence','retrieve_previous_Demographics_Current-Residence','request_new_Demographics_Previous-Residences','retrieve_previous_Demographics_Previous-Residences','request_new_Personality_Goals','retrieve_previous_Personality_Goals','request_new_Personality_Likes','retrieve_previous_Personality_Likes','request_new_Personality_Dislikes','retrieve_previous_Personality_Dislikes','request_new_Personality_Hobbies','retrieve_previous_Personality_Hobbies','request_new_Personality_Notes','retrieve_previous_Personality_Notes','request_new_Relationships_Father','retrieve_previous_Relationships_Father','request_new_Relationships_Mother','retrieve_previous_Relationships_Mother','request_new_Relationships_Siblings','retrieve_previous_Relationships_Siblings','request_new_Work-Experience','retrieve_previous_Work-Experience', 'request_new_Education_Elementary-School','retrieve_previous_Education_Elementary-School','request_new_Education_Middle-School','retrieve_previous_Education_Middle-School','request_new_Education_High-School','retrieve_previous_Education_High-School','request_new_Education_College','retrieve_previous_Education_College','continue_dialogue']
      If the question is referring to previous dialogue from the history or some information exists in the schema about that field, then the dialog act might be one of the 'retrieve_previous' ones.
      You are given six examples.
      ## Example 1. <Question>: Where have you worked previously? <Response>: request_new_Work-Experience
      ## Example 2. <Question>: Where was your middle school - St. Mary's school located? <Response>: retrieve_previous_Education_Middle-School
      ## Example 3. <Question>: How long were you in university? <Response>: retrieve_previous_Education_College
      ## Example 4. <Question>: Tell me something about your family and upbringing? <Response>: request_new_Relationships_Father, request_new_Relationships_Mother, request_new_Relationships_Siblings, request_new_Education
      ## Example 5. <Question>: What do you like to do in your free time? <Response>: request_new_Personality_Likes, request_new_Personality_Hobbies, request_new_Personality_Notes
      ## Example 6. <Question>: Go on. Tell me more. <Response>: continue_dialogue
      ## Example 7. <Question>: Have you considered going into Art school? <Response>: suggest_career
      You must output the dialog acts separated by commas.
      """
    nl = "\n"
    final_prompt = f'{str(self.schema.get_schema())}{nl}<Dialogue History>: {self.history}{nl}{sys_prompt}{nl}<Question>: {dialogue}{nl}'
    # print(final_prompt)
    r = self.llm_request(final_prompt)
    filtered_fields = []
    r = r.replace(' ', '').split(',')
    print('Schema Fields detected:', r)
    try:
      for field in r:
        f = field.split('_')
        if f[1] == 'new':
          # print(self.schema.is_empty('_'.join(f[2:])))
          if self.schema.is_empty('_'.join(f[2:])):
            filtered_fields.append('.'.join(f[2:]))
            self.schema.get_field_new_element('_'.join(f[2:]))
          else:
            filtered_fields.append('.'.join(['Reject']+f[2:]))
        elif f[1] == 'previous':
          l = self.schema.find_empty('_'.join(f[2:]))
          for fs in l:
            filtered_fields.append('.'.join(f[2:] + [fs]))
        elif field == 'suggest_career':
          filtered_fields = ['suggest_career']
          break
    except:
      pass

    if len(filtered_fields) == 0:
      filtered_fields.append('continue_dialogue')
    self.last_detected_fields = filtered_fields
    print('Schema Fields filtered:', filtered_fields)
    return filtered_fields
