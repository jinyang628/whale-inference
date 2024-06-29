from app.models.application import ApplicationContent
from app.models.message import Message


def generate_openai_system_message() -> str:    
    return f"""Your task is to classify user's natural language instruction into specific categories so that an ORM can use your output to perform specific actions on the databases of applications.

Follow these guidelines:
    1. The user's instruction might be related to multiple applications and you need to decide which subset of applications the user's instruction is related to.
    2. For each application, you need to determine the subset of tables which the user's instruction is related to.
    3. For each table, you need to determine the appropriate HTTP methods to use given the user's instructions
    4. For each HTTP method, you may need to provide additional filter conditions so that the HTTP request is issued correctly as per the user's instruction. Your filter conditions should be a valid python dictionary where the key is the column name and value is the target to filter for.
"""

def generate_openai_user_message(
    applications: list[ApplicationContent],
    message: str,
    chat_history: list[Message]
) -> str:
    return f"""



"""