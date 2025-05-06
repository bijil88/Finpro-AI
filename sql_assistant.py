import google.generativeai as genai
import os
from db_context import load_mysql_context, load_response_context
import re

def get_sql_suggestions(user_query, chat_history, similar_queries=None, sheets_handler=None):
    """Generate SQL suggestions based on user query, chat history, and similar queries."""
    # Configure Gemini with the API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        },
    )
    
    # Check if user is asking to search the Excel sheet
    if any(phrase in user_query.lower() for phrase in ["check excel", "search excel", "look in excel", "check sheet", "search sheet"]):
        if similar_queries:
            # Format the similar queries for the response
            similar_queries_text = "\n\nSimilar queries found in database:\n"
            for query in similar_queries:
                similar_queries_text += f"\nQuestion: {query['question']}\nSQL: {query['sql']}\n"
            
            return f"""
                    ANALYSIS:
                    I found similar queries in the database that might help answer your question.

                    {similar_queries_text}

                    If none of these match your needs, please provide more details about your query requirements.
                    """
        else:
            return """
                ANALYSIS:
                I searched the database but couldn't find any similar queries.

                Please provide more details about your query requirements, such as:
                - Which table(s) are involved?
                - What columns do you need?
                - What filtering conditions are needed?
                - Any specific aggregation or sorting requirements?
                """
    
    # Load the MySQL context prompt
    mysql_context = load_mysql_context()
    response_context = load_response_context()
    
    # Prepare similar queries context if available
    similar_queries_context = ""
    if similar_queries:
        similar_queries_context = """
        
        ===== TRUSTED VERIFIED QUERIES FROM GOOGLE SHEETS DATABASE =====
        The following queries are HIGHLY RELEVANT to the user's question and have been PREVIOUSLY VERIFIED.
        They should be considered as TRUSTED REFERENCE EXAMPLES when crafting your response.
        If the user explicitly asks for queries from the database or if their question is almost identical to one below,
        you should primarily base your response on these queries.
        
        """
        for query in similar_queries:
            similar_queries_context += f"Question: {query['question']}\n"
            similar_queries_context += f"SQL: {query['sql']}\n"
            similar_queries_context += f"Similarity Score: {query['score']:.2f}\n\n"
    
    # Get all queries from the database for examples
    example_queries = ""
    if sheets_handler:
        all_queries = sheets_handler.get_all_queries()
        if all_queries:
            example_queries = """
            
            ===== VERIFIED EXAMPLE QUERIES FROM GOOGLE SHEETS DATABASE =====
            The following are sample queries from our verified database. 
            These examples show the typical patterns and structures used in our SQL queries.
            Use these as reference for style, table relationships, and query construction patterns
            even if they don't directly relate to the current question.
            
            """
            for query in all_queries:  # Include all queries as examples
                example_queries += f"Question: {query['question']}\n"
                example_queries += f"SQL: {query['sql']}\n\n"
    
    # Structure the prompt with system message
    system_prompt = f"""
    {mysql_context}

    {response_context}
    
    {example_queries}
    
    {similar_queries_context}

    USER QUERY: {user_query}

    IMPORTANT INSTRUCTIONS FOR HANDLING QUERIES FROM GOOGLE SHEETS:
    1. If the user asks to "check Google Sheets", "use saved queries", "reference the database", or similar:
       - Prioritize the TRUSTED VERIFIED QUERIES listed above
       - If a query has high similarity (above 80%), consider adapting it directly
       - Clearly indicate which query you're using and why it's relevant

    2. When working with similar questions:
       - If a very similar question exists in the TRUSTED VERIFIED QUERIES, adapt that SQL directly
       - Mention that you're using a verified query from the database
       - If modifications are needed, explain what you changed and why

    Based on the above context, example queries, and similar queries from the database, please:
    1. Analyze the user's query
    2. Consider the example queries and similar queries found in the database
    3. Generate an appropriate SQL query that matches the user's requirements
    4. Provide a clear explanation of the query
    5. If there are alternative approaches, mention them as well
    6. If you're using a query from the database, clearly mention it in the analysis

    Format your response as:
    ANALYSIS:
    [Your analysis of the query and approach]
    [If using a query from the database, mention: "This query was found in our database with a similarity score of X%"]

    BEST QUERY:
    ```sql
    [Your SQL query]
    ```

    EXPLANATION:
    [A clear explanation of what the query does]

    ALTERNATIVE APPROACH:
    ```sql
    [Alternative SQL query if applicable]
    ```

    ALTERNATIVE EXPLANATION:
    [Explanation of the alternative approach if applicable]
    """
    
    try:
        # Create the full conversation history
        history = [
            {
                "role": "user",
                "parts": [system_prompt],
            },
            {
                "role": "model",
                "parts": ["I understand. I'll analyze the user's query in the context of the example queries and similar queries from the database, then generate an appropriate SQL query with explanations. I'll clearly indicate if I'm using a query from the database."],
            }
        ]
        
        # Add the conversation history
        for message in chat_history:
            history.append({
                "role": message["role"],
                "parts": [message["content"]]
            })
        
        # Start chat session with the history
        chat_session = model.start_chat(history=history)
        
        # Send the current user query
        response = chat_session.send_message(user_query)
        
        # Clean up the response if it's from the database
        if similar_queries and any(query['sql'] in response.text for query in similar_queries):
            # Extract the SQL query and explanation
            sql_match = re.search(r"```sql\n(.*?)\n```", response.text, re.DOTALL)
            explanation_match = re.search(r"EXPLANATION:\n(.*?)(?=ALTERNATIVE|$)", response.text, re.DOTALL)
            
            if sql_match and explanation_match:
                sql = sql_match.group(1).strip()
                explanation = explanation_match.group(1).strip()
                
                # Format a clean response
                return f"""
                        ANALYSIS:
                        This query was found in our database.

                        BEST QUERY:
                        ```sql
                        {sql}
                        ```

                        EXPLANATION:
                        {explanation}
                        """
        
        return response.text
    except Exception as e:
        return f"""
                ANALYSIS:
                Unable to process query due to an error: {str(e)}

                BEST QUERY:
                ```sql
                -- Error occurred while generating query
                -- Please check your API key and try again
                ```

                Please ensure you have a valid Gemini API key configured in your .env file.
                """