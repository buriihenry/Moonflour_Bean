from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chat_response, double_check_json_output
from openai import OpenAI
load_dotenv()

class ClassificationAgent():
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("RUNPOD_TOKEN"),
            base_url=os.getenv("RUNPOD_CHATBOT_URL"),
        )
        self.model_name = os.getenv("MODEL_NAME")
    
    def get_response(self, messages):
        try:
            messages = deepcopy(messages)

            system_prompt = """
            You are a helpful AI assistant for a coffee shop application.
            Your task is to determine what agent should handle the user input. You have 3 agents to choose from:
            1. details_agent: This agent is responsible for answering questions about the coffee shop, like location, delivery places, working hours, details about menue items. Or listing items in the menu items. Or by asking what we have.
            2. order_taking_agent: This agent is responsible for taking orders from the user. It's responsible to have a conversation with the user about the order untill it's complete.
            3. recommendation_agent: This agent is responsible for giving recommendations to the user about what to buy. If the user asks for a recommendation, this agent should be used.

            Your output should be in a structured json format like so. each key is a string and each value is a string. Make sure to follow the format exactly:
            {
            "chain of thought": "go over each of the agents above and write some your thoughts about what agent is this input relevant to",
            "decision": "details_agent" or "order_taking_agent" or "recommendation_agent",
            "message": ""
            }
            """
            
            input_messages = [
                {"role": "system", "content": system_prompt},
            ]

            input_messages += messages[-3:]

            chatbot_output = get_chat_response(self.client, self.model_name, input_messages)
            chatbot_output = double_check_json_output(self.client, self.model_name, chatbot_output)
            
            # Validate that we got a response
            if not chatbot_output:
                raise ValueError("Empty response received from chatbot")
                
            output = self.postprocess(chatbot_output)
            return output

        except json.JSONDecodeError as e:
            print(f"JSON Parsing Error: {str(e)}")
            # Return a default response that won't break the application
            return {
                "role": "assistant",
                "content": "I apologize, but I encountered an error processing your request.",
                "memory": {
                    "agent": "classification_agent",
                    "classification_decision": "error",
                    "error": str(e)
                }
            }
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            return {
                "role": "assistant",
                "content": "I apologize, but I encountered an unexpected error.",
                "memory": {
                    "agent": "classification_agent",
                    "classification_decision": "error",
                    "error": str(e)
                }
            }

    def postprocess(self, chatbot_output):
        try:
            # Validate the JSON structure before parsing
            output = json.loads(chatbot_output)
            
            # Validate required keys
            required_keys = ['decision', 'message', 'chain of thought']
            missing_keys = [key for key in required_keys if key not in output]
            if missing_keys:
                raise ValueError(f"Missing required keys in response: {missing_keys}")
            
            # Validate decision value
            valid_decisions = ['details_agent', 'order_taking_agent', 'recommendation_agent']
            if output['decision'] not in valid_decisions:
                raise ValueError(f"Invalid decision value: {output['decision']}")

            dict_output = {
                "role": "assistant",
                "content": output['message'],
                "memory": {
                    "agent": "classification_agent",
                    "classification_decision": output['decision']
                }
            }
            return dict_output
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {chatbot_output}")
            raise
        except Exception as e:
            print(f"Error in postprocess: {str(e)}")
            raise