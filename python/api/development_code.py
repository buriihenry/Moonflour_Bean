from agents import (GuardAgent,
                    ClassificationAgent
                    )
import os

def main():
    pass

if __name__ == "__main__":
    guard_agent = GuardAgent()
    classification_agent = ClassificationAgent()

    messages = []
    while True:
        #os.system('cls' if os.name =='nt' else 'clear')

        print("\n\n Print Messages.........")
        for message in messages:
            print(f"{message['role']}:{message['content']}")

        # Get user input
        prompt = input("User: ")
        messages.append({"role":"user","content":prompt})  

        #get guard Agent's response
        guard_agent_response = guard_agent.get_response(messages)  
        
        if guard_agent_response["memory"]["guard_decision"] =="not allowed":
            messages.append(guard_agent_response)
            continue

        #Create classification agent which will assign the requests to order agents,details agent or recommendation agent
        classification_agent_response = classification_agent.get_response(messages) 
        chosen_agent = classification_agent_response["memory"]["classification_decision"]
        print("Chosen Agent: ",chosen_agent ) 
        
      

   