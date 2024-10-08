from app.models.application import ApplicationContent
from app.models.inference.use import UseMessage


def generate_openai_selection_system_message() -> str:
    return f"""Your task is to interpret the user's natural language instruction and select the relevant (task, application, table name, HTTP method) groupings so that an ORM can use your output to perform specific actions on the databases of applications.

Follow these guidelines: 
    1. Filter conditions belongs to the same task. E.g. "Show me all the users with the name John or have an age higher than 12" is one single task. Do not split this up. 
    2. The user's instruction may not be self-contained and you may need to refer to previous instructions to infer what the current instruction is about. However, the task segment you output should be self-contained and should not refer to previous instructions. Rephrase if necessary.
    3. For each task, it might involve requests to multiple applications and you need to decide which subset of applications the task is related to.
    4. For each application, you need to determine the subset of tables which the task is related to.
    5. For each table, you need to determine the appropriate HTTP methods to use given the task.  
    6. The chat history is provided as additional context for you to interpret the user's current instruction, but you only have to generate the relevant groupings based on the user's current instruction. 
"""

    # Note: There's this problem of the LLM splitting filter conditions into separate tasks. This is a problem because the filter conditions are part of the same task.

    # 1. The user's instruction might compose of multiple tasks and you need to split up his instruction into multiple sub-tasks. Rephrase or summarise if necessary, but do not leave out any necessary information when describing the sub-task.
    # 2. Note that filter conditions belongs to the same task. E.g. "Show me all the users with the name John or have an age higher than 12" is one single task. Do not split this up.


def generate_openai_selection_user_message(
    applications: list[ApplicationContent], message: str, chat_history: list[UseMessage]
) -> str:
    return f"""### Here are the applications that might be relevant to the user's instruction:

{[application.model_dump() for application in applications]}

### Here is the chat history:

{[message.model_dump() for message in chat_history]}

### Here is the user's current instruction:

{message}
"""
