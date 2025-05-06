## 🧠 About the App

**Finpro SQL AI** is an intelligent application designed to convert natural language questions into optimized SQL queries. It leverages advanced language models to interpret user intent and generate accurate SQL statements based on a predefined database schema.

The assistant is particularly useful for teams working with structured data, enabling users to query databases using plain English. By combining natural language processing with contextual understanding of the database, the app ensures both ease of use and precision.


<img src="images/UI-Bot.png" alt="Finpro SQL AI Interface" width="500"/>

---

### 🛠 Tech Stack

- **Frontend**: Built using **Streamlit**, a Python framework for creating interactive web applications quickly and intuitively.
- **Backend**: Developed in **Python**, leveraging language model APIs, natural language processing, and custom logic for query generation.
- **Database Context**: Defined in `db_context.py`, containing schema definitions (tables, columns, constraints), sample data, and domain-specific business logic.
- **Language Model**: Currently Integrated with **Google's Gemini LLM ("gemini-2.0-flash")** . It interprets the user's natural language query within the context of the database and returns well-structured SQL queries.

---

### 🔁 Application Flow

1. **User Input**:  
   The user enters a question or request in natural language.

2. **Query Processing**:  
   The input is captured and added to the ongoing chat history for context retention.

3. **Contextual Understanding**:  
   The app sends the input along with the structured context from `db_context.py` to the LLM.

4. **SQL Generation**:  
   If the input is relevant to the schema, the LLM generates an optimized SQL query that adheres to best practices.

5. **Response Display**:  
   The generated query is displayed alongside an explanation and, where applicable, alternative versions.

6. **User Interaction**:  
   The user may continue asking questions or request clarifications. The assistant maintains conversation history to support context-aware responses.

---

### ✨ Key Features

- **Natural Language Processing**:  
  Allows users to interact using everyday language instead of SQL syntax.

- **Contextual Awareness**:  
  Database schema and logic are embedded in the prompt, ensuring accurate and relevant queries.

- **Reusable Code Architecture**:  
  Teams can easily adapt the SQL AI to different databases by modifying `db_context.py`—no changes to the core logic are needed.

---

## ⚙️ Setup Instructions

To run SQL Assistant locally, follow these steps:

1. **Clone the Repository**

2. Setup virtual env using below commands and activate

    python3 -m venv venv
    
    source venv/bin/activate

3. **Install Dependencies**

    Make sure Python is installed, then run:


    pip3 install -r requirements.txt


4. **Configure Environment Variables**

    Update `.env` file in the project root and add your Gemini API key:


    GEMINI_API_KEY=your_api_key_here

    Note : Generate GEMINI_API_KEY from https://aistudio.google.com/apikey
    
    Copy the path of json_sheet_credentials.json in repo and update variable : "GOOGLE_CREDENTIALS_FILE"
    
    To connect to google sheet : Inside json_sheet_credentials.json the "private_key" value is tampered.Get the correct private key value from bijil and replace .


5. **Run the Application**


    streamlit run main.py

---

## 🔮 Future Scope planned

The SQL AI is designed for continuous improvement . Below are several areas for future development:

- **Integration with Multiple Language Models**  
  Support for various LLMs (e.g., OpenAI, Claude, or open-source models) to improve adaptability and performance.

- **Agentic Flow for Clarifications**  
  Enable the assistant to proactively ask users for clarification when queries are vague or ambiguous and re-iterate.

- **Query and Response Saving**  
  Allow users to save generated SQL queries and associated explanations for later reuse or documentation.

- **Chat History Management**  
  Add features to view, delete, and export chat history, improving usability and workflow continuity.

- **Prompt Optimization**  
  Continuously refine the prompt generation logic to ensure alignment with updated schema and business logic.

- **Large DB Context Handling**  
  Implement strategies to manage larger db schema contexts efficiently, ensuring responsiveness and performance at scale.

---

