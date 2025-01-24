from openai import OpenAI
import os
import json
from copy import deepcopy 
from .utils import get_chat_response, double_check_json_output
import dotenv
dotenv.load_dotenv()

class GuardAgent():
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("RUNPOD_TOKEN"),
            base_url=os.getenv("RUNPOD_CHATBOT_URL")
        )
        self.model_name=os.getenv("MODEL_NAME")

    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt ="""
            You are a helpful AI assistant for a coffee shop application which serves drinks and pastries.
            Your task is to determine whether the user is asking something relevant to the coffee shop or not.
            The user is allowed to:
            1. Ask questions about the coffee shop, like location, working hours,menu items and coffee shop related questions.
            2. Ask questions about the menu items. The can ask about the ingredients in an item and more details about the item.
            3. Make an order
            4. Ask for recommendations of what to buy.

            The user is not allowed to:
            1. Ask questions about anything else other than the coffee shop
            2. Ask questions about the staff or how to make a certain menu item

            Your output should be in a scturctured json format like so. each key is a string and each value is a string. Make sure to follow the format exactly:
            {
                "chain of thought": "go over each of the points above and see if the message lies under this point or not. Then you write some thoughts about what point is this input."
                "decision":"allowed" or "not allowed". Pick one of those and only write the word.
                "message": leave the message empty "" if it is allowed otherwise write "sorry I can't help with that. Can I help you with your order?" 
            }

        """    
        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        chatbot_output = get_chat_response(self.client, self.model_name, input_messages)
        chatbot_output = double_check_json_output(self.client, self.model_name,chatbot_output)
        
        try:
            output = self.postprocess(chatbot_output)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw output: {chatbot_output}")
            # Fallback response in case of error
            return {
                "role": "assistant",
                "content": "Sorry, there was an error processing your request. Could you please try again?",
                "memory": {
                    "agent": "guard_agent",
                    "guard_decision": "error"
                }
            }
        
        return output
    
    def postprocess(self, output):
        output = json.loads(output)

        dict_output = {
            "role": "assistant",
            "content": output["message"],
            "memory": {
                "agent": "guard_agent",
                "guard_decision": output["decision"]
            }
        }
        return dict_output