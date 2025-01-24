import os
import json
from .utils import get_chat_response,double_check_json_output
from openai import OpenAI
from copy import deepcopy
from dotenv import load_dotenv
load_dotenv()


class OrderTakingAgent():
    def __init__(self, recommendation_agent):
        self.client = OpenAI(
            api_key=os.getenv("RUNPOD_TOKEN"),
            base_url=os.getenv("RUNPOD_CHATBOT_URL"),
        )
        self.model_name = os.getenv("MODEL_NAME")

        self.recommendation_agent = recommendation_agent
    
    def get_response(self,messages):
        messages = deepcopy(messages)
        system_prompt = """
            You are a customer support Bot for a coffee shop called Moonflour Bean. You are tasked with taking the user's order.

            here is the menu for this coffee shop.

            Cappuccino - Ksh 495.00
            Jumbo Savory Scone - Ksh 357.50
            Latte - Ksh 522.50
            Chocolate Chip Biscotti - Ksh 275.00
            Espresso shot - Ksh 220.00
            Hazelnut Biscotti - Ksh 302.50
            Chocolate Croissant - Ksh 412.50
            Dark chocolate (Drinking Chocolate) - Ksh 550.00
            Cranberry Scone - Ksh 385.00
            Croissant - Ksh 357.50
            Almond Croissant - Ksh 440.00
            Ginger Biscotti - Ksh 275.00
            Oatmeal Scone - Ksh 357.50
            Ginger Scone - Ksh 385.00
            Chocolate syrup - Ksh 165.00
            Hazelnut syrup - Ksh 165.00
            Caramel syrup - Ksh 165.00
            Sugar Free Vanilla syrup - Ksh 165.00
            Dark chocolate (Packaged Chocolate) - Ksh 330.00

            Things to NOT DO:
            * DON't ask how to pay by cash or Card.
            * Don't tell the user to go to the counter
            * Don't tell the user to go to place to get the order


            You're task is as follows:
            1. Take the User's Order
            2. Validate that all their items are in the menu
            3. if an item is not in the menu let the user and repeat back the remaining valid order
            4. Ask them if they need anything else.
            5. If they do then repeat starting from step 3
            6. If they don't want anything else. Using the "order" object that is in the output. Make sure to hit all three points
                1. list down all the items and their prices
                2. calculate the total. 
                3. Thank the user for the order and close the conversation with no more questions

            The user message will contain a section called memory. This section will contain the following:
            "order"
            "step number"
            please utilize this information to determine the next step in the process.
            
            produce the following output without any additions, not a single letter outside of the structure bellow.
            Your output should be in a structured json format like so. each key is a string and each value is a string. Make sure to follow the format exactly:
            {
            "chain of thought": Write down your critical thinking about what is the maximum task number the user is on write now. Then write down your critical thinking about the user input and it's relation to the coffee shop process. Then write down your thinking about how you should respond in the response parameter taking into consideration the Things to NOT DO section. and Focus on the things that you should not do. 
            "step number": Determine which task you are on based on the conversation.
            "order": this is going to be a list of jsons like so. [{"item":put the item name, "quanitity": put the number that the user wants from this item, "price":put the total price of the item }]
            "response": write the a response to the user
            }
        """

        last_order_taking_status = ""
        asked_recommendation_before = False
        for message_index in range(len(messages)-1,0,-1):
            message = messages[message_index]
            
            agent_name = message.get("memory",{}).get("agent","")
            if message["role"] == "assistant" and agent_name == "order_taking_agent":
                step_number = message["memory"]["step number"]
                order = message["memory"]["order"]
                asked_recommendation_before = message["memory"]["asked_recommendation_before"]
                last_order_taking_status = f"""
                step number: {step_number}
                order: {order}
                """
                break

        messages[-1]['content'] = last_order_taking_status + " \n "+ messages[-1]['content']

        input_messages = [{"role": "system", "content": system_prompt}] + messages        

        chatbot_output = get_chat_response(self.client,self.model_name,input_messages)

        # double check json 
        chatbot_output = double_check_json_output(self.client,self.model_name,chatbot_output)

        output = self.postprocess(chatbot_output,messages,asked_recommendation_before)

        return output

    def postprocess(self, output, messages, asked_recommendation_before):
        try:
            output = json.loads(output)
            
            # Handle case where order is a string representation of JSON
            if isinstance(output["order"], str):
                try:
                    output["order"] = json.loads(output["order"])
                except json.JSONDecodeError:
                    output["order"] = []  # Fallback to empty order if parsing fails
            
            response = output['response']
            if not asked_recommendation_before and output["order"]:
                recommendation_output = self.recommendation_agent.get_recommendations_from_order(
                    messages, 
                    output['order']
                )
                response = recommendation_output['content']
                asked_recommendation_before = True

            dict_output = {
                "role": "assistant",
                "content": response,
                "memory": {
                    "agent": "order_taking_agent",
                    "step number": output.get("step number"),
                    "order": output["order"],
                    "asked_recommendation_before": asked_recommendation_before,
                }
            }
            
            return dict_output
            
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw output: {output}")
            # Fallback response
            return {
                "role": "assistant",
                "content": "I apologize, there was an error processing your order. Could you please repeat your order?",
                "memory": {
                    "agent": "order_taking_agent",
                    "step number": "1",
                    "order": [],
                    "asked_recommendation_before": False
                }
            }
        except KeyError as e:
            print(f"Missing key in output: {e}")
            # Fallback response for missing keys
            return {
                "role": "assistant",
                "content": "I apologize, there was an error with your order. Could you please try again?",
                "memory": {
                    "agent": "order_taking_agent",
                    "step number": "1",
                    "order": [],
                    "asked_recommendation_before": False
                }
            }