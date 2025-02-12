
# **Moonflour_Bean – AI Chatbot for Coffee Shop Apps**

Welcome to the **Moonflour_Bean Chat Agent** repository! This project contains the full-stack implementation of an AI-powered **Multi-agent** app designed to enhance customer experiences in a coffee shop application by simulating real-world interactions.

The chatbot utilizes **Large Language Models (LLMs)**, **Natural Language Processing (NLP)**, **RunPod’s infrastructure**, and **Firebase** to assist customers with:

✅ Taking orders  
✅ Answering detailed menu-related queries  
✅ Providing personalized product recommendations  

This chatbot is integrated within a **React Native mobile app** (currently under development).  

---

## **🎯 Project Goals**

The goal of this project is to develop an **intelligent, agent-based chatbot** capable of:

1. **Handling real-time customer interactions** – Allowing customers to place orders seamlessly.  
2. **Answering menu-related questions** – Providing details on ingredients, allergens, and other menu information using a **Retrieval-Augmented Generation (RAG) system**.  
3. **Offering personalized recommendations** – Utilizing a **market basket analysis recommendation engine** to suggest complementary items.  
4. **Ensuring structured order placement** – Guiding customers through an efficient ordering process for accuracy.  
5. **Filtering inappropriate queries** – Using a **Guard Agent** to block irrelevant or harmful inputs.  

---

## **🛠️ Core Agents in the Chatbot System**

### **1. Guard Agent** (Content Filtering)
- Serves as the **first line of defense** by monitoring all incoming queries.  
- Blocks **inappropriate, harmful, or irrelevant** messages before they reach other agents.  
- Ensures **safe and meaningful** interactions with the chatbot.  

### **2. Order Taking Agent** (Order Assistance)
- Guides users through the **entire order placement process** using **chain-of-thought** reasoning.  
- Captures all **customer preferences and order details** in a structured, logical manner.  
- Ensures orders are **complete and accurate** before processing.  

### **3. Details Agent (RAG System)** (Menu Information)
- Uses **Retrieval-Augmented Generation (RAG)** to provide detailed answers on menu items, including:  
  - **Ingredients**  
  - **Allergens**  
  - **Nutritional information**  
- Retrieves relevant data from a **vector database** and generates accurate responses.  

### **4. Recommendation Agent** (Personalized Suggestions)
- Works alongside the **Order Taking Agent** to suggest **complementary products** based on the user’s order history.  
- Uses a **market basket analysis model** to enhance **upselling opportunities** and help users discover new products.  

### **5. Classification Agent** (Query Routing)
- **Analyzes user intent** and directs queries to the appropriate agent.  
- Ensures queries are handled efficiently, whether they relate to:  
  - **Order placement**  
  - **Menu details**  
  - **Product recommendations**  

---

## **⚙️ How the Agents Work Together**

1. **User Query Processing:**  
   - A customer sends a message to the chatbot.  
   - The **Guard Agent** filters out any **harmful or irrelevant content**.  

2. **Intent Classification:**  
   - The **Classification Agent** determines the purpose of the query (e.g., ordering, menu details, recommendations).  

3. **Task Delegation:**  
   - The query is sent to the most relevant agent:  
     - **Order Taking Agent** for order-related queries.  
     - **Details Agent** for menu-related questions.  
     - **Recommendation Agent** for product suggestions.  

4. **Upselling Process:**  
   - Before finalizing an order, the **Order Taking Agent** may request recommendations from the **Recommendation Agent** to enhance the customer’s experience.  

---

## **📂 Folder Structure**

```
coffee_shop_customer_service_chatbot/
│   ├── Frontend/                # React Native app code (Coming soon)  
│   ├── python/ (Backend)  
│       ├── API/                # Backend API for the agent-based chatbot system  
│       ├── dataset/            # Dataset for training the recommendation engine  
│       ├── products/           # Product details (names, prices, descriptions, images)  
│       ├── vector_database.ipynb  # Builds the vector database for the RAG model  
│       ├── firebase_uploader.ipynb  # Uploads product data to Firebase  
│       ├── recommendation_engine.ipynb  # Trains the recommendation system  
```

---

## **🚀 Getting Started**

### **Prerequisites**
Ensure you have the following installed on your system:
- **Python 3.8+**
- **Node.js & npm**
- **React Native**
- **Firebase CLI** (for data management)
- **RunPod API Key** (for cloud-based inference)

### **Installation**
#### **Backend Setup**
```bash
# Clone the repository
git https://github.com/buriihenry/Moonflour_Bean.git

# Install dependencies
pip install -r requirements.txt
```

#### **Frontend Setup**
```bash
# Navigate to the frontend directory
cd ../Frontend

# Install dependencies
npm install
```

### **Running the Project**
#### **Start the Backend**
```bash
cd python
python main.py
```

#### **Start the Frontend**
```bash
cd ../Frontend
npm start
```

---

## **📌 Contributing**
Contributions are welcome! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add feature'`).
4. Push to your branch (`git push origin feature-name`).
5. Open a pull request.

---

## **📜 License**
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## **📞 Contact**
For any inquiries or support, feel free to reach out:
📌 GitHub: [buriihenry](https://github.com/buriihenry)  

Happy coding! ☕🤖




