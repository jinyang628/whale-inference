from app.models.inference.create import CreateMessage


def generate_openai_application_system_message() -> str:
    return f"""Your task is create an application based on the user's description. You need to generate the database tables necessary to support the CRUD operations, and provide a description of the general tasks which the application supports. The user might follow up with additional requirements that you will need to incorporate into your design. 

Follow the routine below:
1. Clarify the user's requirements.
2. Propose a version of the database tables and describe the general tasks which the application supports.
3. Iterate with the user to refine the design based on their feedback. Ask clarification questions to get a better understanding of the application requirements if necessary.
4. End the conversation with a concluding message when the user is satisfied with the design.

Do not include the following columns in your response:
1. Primary key column. For this special column, you just need to indicate the primary key type.
2. Created_at or updated_at columns. For these special columns, you just need to indicate whether they are required or not.
"""

def generate_openai_application_user_message(
    message: str, 
    chat_history: list[CreateMessage]
) -> str:
    return f"""### Here is the chat history:

{[message.model_dump() for message in chat_history]}

### Here is the user's current message:

{message}

Please conclude the conversation if user is satisfied with the design.
"""