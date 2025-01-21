from openai import OpenAI
import os
import pandas as pd
import json
from copy import deepcopy 
from .utils import get_chat_response
import dotenv
dotenv.load_dotenv()

class RecommendationAgent():
    def __init__(self,apriori_recommendation_path,popular_recommendations_path):
        self.client = OpenAI(
            api_key=os.getenv("RUNPOD_TOKEN"),
            base_url=os.getenv("RUNPOD_CHATBOT_URL")
        )
        self.model_name=os.getenv("MODEL_NAME")
        
        with open(apriori_recommendation_path,'r') as file:
            self.apriori_recommendations = json.load(file)

        self.popular_recommendations = pd.read_csv(popular_recommendations_path)
        self.products = self.popular_recommendations["product"].tolist()
        self.product_categories = self.popular_recommendations["product_category"].tolist()

    def get_apriori_recommendations(self,products, top_k=5):
        recommendation_list = []
        
        for product in products:
            if product in self.apriori_recommendations:
                recommendation_list += self.apriori_recommendations[product]

        # sort the recommendations by the number of times they appear in the list   
        recommendation_list = sorted(recommendation_list,key= lambda x:x['confidence'],reverse=True)

        recommendations = []
        recommendation_per_category = {}

        for recommendation in recommendation_list:
            if recommendation in recommendations:
                continue
            product_category = recommendation["product_category"]

            if product_category not in recommendation_per_category:
                recommendation_per_category[product_category] = 0

            if recommendation_per_category[product_category] >= 2:
                continue  
            recommendation_per_category[product_category] += 1

            recommendations.append(recommendation['product'])

            if len(recommendations) >= top_k:
                break
        return recommendations    

                


    def get_popular_recommendations(self,product_categories=None, top_k=5):
        recommendation_df = self.popular_recommendations

        if type(product_categories)== str:
            product_categories = [product_categories]

        if product_categories is not None:
            recommendation_df = self.popular_recommendations[self.popular_recommendations["product_category"].isin(product_categories)] 
        recommendation_df = recommendation_df.sort_values(by="number_of_transactions",ascending=False)

        if recommendation_df.shape[0]==0:
            return []
        
        recommendations = recommendation_df["product"].tolist()[:top_k]
        return recommendations
    
