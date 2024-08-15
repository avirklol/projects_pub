from openai import OpenAI
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    organization=os.getenv('OPENAI_ORG'),
    project=os.getenv('OPENAI_PROJECT'),
)

instructions = """You are an expert in integrations software and can identify when a user would benefit from using Unito.
You will provide a boolean value for each post, indicating whether the post is a good candidate for Unito integration.
A candidate would be a post where a user is discussing a need to sync data between two tools. Or, a user is asking for a way to automate a process between two tools.
Or, a user is looking to increase productivity by connecting two tools.
Use the provided function to evaluate the posts.
"""

evaluate_unito_candidates_function = {
    "type": "function",
    "function": {
        "name": "evaluate_unito_candidates",
        "description": "Evaluates a thread of messages to determine which are good candidates for Unito integration based on specific criteria.",
        "parameters": {
            "type": "object",
            "properties": {
                "messages": {
                    "type": "array",
                    "description": "A list of messages in the thread to be evaluated.",
                    "items": {
                        "type": "string",
                        "description": "A single message from the thread."
                    }
                }
            },
            "required": ["messages"]
        },
        "returns": {
            "type": "array",
            "description": "A list of boolean values, each indicating whether a message is a good candidate for Unito integration.",
            "items": {
                "type": "boolean"
            }
        }
    }
}

assistant = client.beta.assistants.create(
  name="Unito Expert",
  instructions=instructions,
  tools=[evaluate_unito_candidates_function],
  model="gpt-4o-mini",
)

def filter_posts_bulk(posts: list) -> list:

    global assistant, client

    df = pd.DataFrame(posts)
    thread = client.beta.threads.create()

    for i, row in df.iterrows():
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content= row['body']
        )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        print('Run completed.')
    else:
        print(run.status)


        # prompt += f"Post {i+1} Body: {row['body']}\nDoes this post match the context? Answer 'yes' or 'no'.\n"

    answers = []

    for tool in run.required_action.submit_tool_outputs.tool_calls:
            answers.append(output)

    # Filter the matching posts
    if True in answers:

        matching_df = df[answers]
        matching_posts = matching_df.to_dict('records')

        return matching_posts

    else:

        return ['No matching posts found.']

client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)


# Batch processing to improve speed
    batch_size = 10  # Adjust batch size as needed
    matching_posts_df = pd.DataFrame()

    for i in range(0, len(posts), batch_size):
        batch_df = df_posts.iloc[i:i+batch_size]
        matching_posts_df = pd.concat([matching_posts_df, filter_posts_bulk(context, batch_df)], ignore_index=True)

    # Convert the result back to a list of dictionaries if needed
    matching_posts = matching_posts_df.to_dict('records')

    # Output the results
    for match in matching_posts:
        print(match)
