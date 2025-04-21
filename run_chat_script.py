import json

from openai import OpenAI

from utils import func_to_json

SYSTEM_PROMPT = """You are an helpful assistant who helps with solving math problems. Do not use your prior knowledge to answer, use available tools to yield results, or inform the user that you cannot help with the query."""
OPENAI_MODEL = 'gpt-4o'


def add(a: float, b: float):
   """Add two numbers"""
   return a + b


def subtract(a: float, b: float):
   """Subtract two numbers"""
   return a - b


def multiply(a: float, b: float):
   """Multiply two numbers"""
   return a * b


def divide(a: float, b: float):
   """Divide two numbers"""
   if b == 0:
      return "ValueError: denominator cannot be zero."
   return a / b


if __name__ == '__main__':
    oai_client = OpenAI()

    available_tools = [
       {'type': 'function', 'function': func_to_json(add)}, 
       {'type': 'function', 'function': func_to_json(subtract)}, 
       {'type': 'function', 'function': func_to_json(multiply)}, 
       {'type': 'function', 'function': func_to_json(divide)}
    ]

    # chat history stores all the current and previous chat messages (developer/user/assistant/tool messages)
    chat_history = [{'role': 'developer', 'content': SYSTEM_PROMPT}]
    while True:
       user_query = input('You: ')
       if user_query == 'q':
          break

       chat_history.append({'role': 'user', 'content': user_query})
       while True:
            response = oai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=chat_history,
                tools=available_tools,
                tool_choice="auto"
            )
            chat_history.append(response.choices[0].message.model_dump())

            # If there are tool call(s), run each tool call, append the result to chat history, and query LLM again
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:       
                    tool_call_id = tool_call.id
                    func_name, func_args = tool_call.function.name, json.loads(tool_call.function.arguments)
                    func_result = locals()[func_name](**func_args)
                    chat_history.append({'role': 'tool', 'tool_call_id': tool_call_id, 'content': str(func_result)})
            else:
                # No tool call or end of task -- print the final response and wait for user query again
                print('>>>> ', chat_history[-1]['content'])
                break

    print('The entire chat history (with tool call messages):', chat_history)
