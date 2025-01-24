import json
import pandas as pd
import os
from .utils import get_chat_response
from openai import OpenAI
from copy import deepcopy
from dotenv import load_dotenv
load_dotenv()


class RecommendationAgent():
    def __init__(self,apriori_recommendation_path,popular_recommendation_path):
        self.client = OpenAI(
            api_key=os.getenv("RUNPOD_TOKEN"),
            base_url=os.getenv("RUNPOD_CHATBOT_URL"),
        )
        self.model_name = os.getenv("MODEL_NAME")

        with open(apriori_recommendation_path, 'r') as file:
            self.apriori_recommendations = json.load(file)

        self.popular_recommendations = pd.read_csv(popular_recommendation_path)
        self.products = self.popular_recommendations['product'].tolist()
        self.product_categories = self.popular_recommendations['product_category'].tolist()
    
    def get_apriori_recommendation(self,products,top_k=5):
        recommendation_list = []
        for product in products:
            if product in self.apriori_recommendations:
                recommendation_list += self.apriori_recommendations[product]
        
        # Sort recommendation list by "confidence"
        recommendation_list = sorted(recommendation_list,key=lambda x: x['confidence'],reverse=True)

        recommendations = []
        recommendations_per_category = {}
        for recommendation in recommendation_list:
            # If Duplicated recommendations then skip
            if recommendation in recommendations:
                continue 

            # Limit 2 recommendations per category
            product_catory = recommendation['product_category']
            if product_catory not in recommendations_per_category:
                recommendations_per_category[product_catory] = 0
            
            if recommendations_per_category[product_catory] >= 2:
                continue

            recommendations_per_category[product_catory]+=1

            # Add recommendation
            recommendations.append(recommendation['product'])

            if len(recommendations) >= top_k:
                break

        return recommendations 

    def get_popular_recommendation(self,product_categories=None,top_k=5):
        recommendations_df = self.popular_recommendations
        
        if type(product_categories) == str:
            product_categories = [product_categories]

        if product_categories is not None:
            recommendations_df = self.popular_recommendations[self.popular_recommendations['product_category'].isin(product_categories)]
        recommendations_df = recommendations_df.sort_values(by='number_of_transactions',ascending=False)
        
        if recommendations_df.shape[0] == 0:
            return []

        recommendations = recommendations_df['product'].tolist()[:top_k]
        return recommendations

    def recommendation_classification(self,messages):
        system_prompt = """ You are a helpful AI assistant for a coffee shop application. Your task is to intelligently classify user recommendation requests into three precise categories:

            1. Apriori Recommendations: Triggered when the user references specific past orders or wants personalized suggestions based on previous purchases.
            2. Popular Recommendations: Activated when the user wants general suggestions or asks broadly about what to order.
            3. Popular Recommendations by Category: Triggered when the user asks about recommendations within a specific product category (e.g., "What coffee do you recommend?", "Any good pastries today?").

            Items in our coffee shop:
            """+ ",".join(self.products) + """

            Product Categories:
            """ + ",".join(self.product_categories) + """

            Guidelines for Classification:
            - If user mentions past orders or specific items, use Apriori Recommendations
            - If user asks generally "What should I order?", use Popular Recommendations
            - If user specifies a category, use Popular Recommendations by Category

            Output a structured JSON:
            {
            "chain of thought": "Analyze request, identify key signals for recommendation type",
            "recommendation_type": "apriori" or "popular" or "popular by category",
            "parameters": "List of specific items or categories, or empty list"
            }
            """

        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        chatbot_output =get_chat_response(self.client,self.model_name,input_messages)
        output = self.postprocess_classfication(chatbot_output)
        return output

    def get_response(self, messages):
        messages = deepcopy(messages)

        # Try to detect if the query is about pricing or details
        query = messages[-1]['content'].lower()
        if any(word in query for word in ['price', 'cost', 'how much', 'pricing']):
            # Delegate to DetailsAgent or create a custom pricing response
            return {
                "role": "assistant", 
                "content": "I can help you with pricing details. Would you like to know the price of a specific item?", 
                "message": "I can help you with pricing details. Would you like to know the price of a specific item?",
                "memory": {"agent": "recommendation_agent"}
            }

        # Existing recommendation logic
        recommendation_classification = self.recommendation_classification(messages)
        recommendation_type = recommendation_classification['recommendation_type']
        recommendations = []

        if recommendation_type == "apriori":
            recommendations = self.get_apriori_recommendation(recommendation_classification['parameters'])
        elif recommendation_type == "popular":
            recommendations = self.get_popular_recommendation()
        elif recommendation_type == "popular by category":
            recommendations = self.get_popular_recommendation(recommendation_classification['parameters'])
        else:
            recommendations = self.get_popular_recommendation()  # Fallback to popular recommendations
        
        if not recommendations:
            return {
                "role": "assistant", 
                "content": "We have a variety of delicious coffee and pastries! Would you like to hear some of our popular items?", 
                "message": "We have a variety of delicious coffee and pastries! Would you like to hear some of our popular items?",
                "memory": {"agent": "recommendation_agent"}
            }
    
    # Rest of the existing method...
    # Rest of the method remains the same...
        # Respond to User
        recommendations_str = ", ".join(recommendations)
        
        system_prompt = f"""
        You are a helpful AI assistant for a coffee shop application which serves drinks and pastries.
        your task is to recommend items to the user based on their input message. And respond in a friendly but concise way. And put it an unordered list with a very small description.

        I will provide what items you should recommend to the user based on their order in the user message. 
        """

        prompt = f"""
        {messages[-1]['content']}

        Please recommend me those items exactly: {recommendations_str}
        """

        messages[-1]['content'] = prompt
        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        chatbot_output =get_chat_response(self.client,self.model_name,input_messages)
        output = self.postprocess(chatbot_output)

        return output



    def postprocess_classfication(self, output):
        print(f"Raw chatbot output: {output}")  # Debugging to log the output

        # Check if output is empty or invalid before proceeding
        if not output:
            print("Error: Chatbot output is empty.")
            return {"recommendation_type": "", "parameters": []}

        try:
            # Attempt to load the JSON response
            output = json.loads(output)
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")
            print(f"Output received: {output}")  # Log the problematic output
            return {"recommendation_type": "", "parameters": []}

        return {
            "recommendation_type": output.get('recommendation_type', ""),
            "parameters": output.get('parameters', []),
        }


    def get_recommendations_from_order(self,messages,order):
        products = []
        for product in order:
            products.append(product['item'])

        recommendations = self.get_apriori_recommendation(products)
        recommendations_str = ", ".join(recommendations)

        system_prompt = f"""
        You are a helpful AI assistant for a coffee shop application which serves drinks and pastries.
        your task is to recommend items to the user based on their order.

        I will provide what items you should recommend to the user based on their order in the user message. 
        """

        prompt = f"""
        {messages[-1]['content']}

        Please recommend me those items exactly: {recommendations_str}
        """

        messages[-1]['content'] = prompt
        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        chatbot_output =get_chat_response(self.client,self.model_name,input_messages)
        output = self.postprocess(chatbot_output)

        return output
    
    def postprocess(self, output):
        return {
            "role": "assistant",
            "content": output,
            "message": output,  # Ensure 'message' is always present
            "memory": {"agent": "recommendation_agent"}
        }
        return output

