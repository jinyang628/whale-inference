from app.models.application import ApplicationContent, Table
from app.models.inference import HttpMethod
from app.models.message import Message


def generate_openai_http_request_system_message(http_method: HttpMethod) -> str:    
    match http_method:
        case HttpMethod.GET:
            return _generate_openai_get_request_system_message()
        case HttpMethod.POST:
            return _generate_openai_post_request_system_message()
        case HttpMethod.PUT:
            return _generate_openai_put_request_system_message()
        case HttpMethod.DELETE:
            return _generate_openai_delete_request_system_message()
        
def _generate_openai_get_request_system_message() -> str:
    return f"""Your task is to interpret a user's natural language instruction and supply the necessary parameters for an ORM to initiate a {HttpMethod.GET} request to the specified table in the application. 

Follow these guidelines:
    1. You might have to provide some filter conditions for the {HttpMethod.GET} request based on the table's schema and the user's instruction.
    3. Ensure that the value you provide for the filter condition(s) follows the data type specified for the column.
"""

def _generate_openai_post_request_system_message() -> str:
    return f"""Your task is to interpret a user's natural language instruction and supply the necessary parameters for an ORM to initiate a {HttpMethod.POST} request to the specified table in the application. 

Follow these guidelines:
    1. You must provide the necessary parameters for the {HttpMethod.POST} request based on the table's schema.
    2. Ensure that the value you provide for each table column follows the data type specified.
    3. If a particular parameter is not stated in the user's instruction, output the default value for that parameter as specified in the table's schema.
"""

# TODO: Some of the put requests is not a simple replacement but an increment/decrease of the current value (Should we introduce a new field that triggers that in the schema? Or should this be a multi-step process that involves going back to backend?)
def _generate_openai_put_request_system_message() -> str:
    return f"""Your task is to interpret a user's natural language instruction and supply the necessary parameters for an ORM to initiate a {HttpMethod.PUT} request to the specified table in the application. 

Follow these guidelines:
    1. You might have to provide some filter conditions for the {HttpMethod.PUT} request based on the table's schema and the user's instruction.
    2. You must provide the necessary columnn values to update for the {HttpMethod.PUT} request based on the table's schema and the user's instruction.
    3. Ensure that the value you provide for each table column follows the data type specified.
"""

def _generate_openai_delete_request_system_message() -> str:
    return f"""Your task is to interpret a user's natural language instruction and supply the necessary parameters for an ORM to initiate a {HttpMethod.DELETE} request to the specified table in the application. 

Follow these guidelines:
    1. You might have to provide some filter conditions for the {HttpMethod.DELETE} request based on the table's schema and the user's instruction.
    2. Ensure that the value you provide for each table column follows the data type specified.
"""


def generate_openai_http_request_user_message(
    application_name: str,
    table: Table,
    http_method: HttpMethod,
    message: str,
    chat_history: list[Message]
) -> str:    
    return f"""### Name of application: {application_name}

### Target table to generate {http_method} request for: 

{table.model_dump()}

### Here is the chat history:

{[message.model_dump() for message in chat_history]}

### Here is the current user's instruction:

{message}
"""
