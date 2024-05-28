import json
import os
from dotenv import load_dotenv
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain_community.llms import openllm
from astrapy import DataAPIClient

load_dotenv()

# Initialize the client
client = DataAPIClient(os.getenv('ASTRA_DB_APPLICATION_TOKEN'))
db = client.get_database_by_api_endpoint(os.getenv('ASTRA_DB_API_ENDPOINT'))

print(f"Connected to Astra DB: {db.list_collection_names()}")

cloud_config = {
    'secure_connect_bundle': 'text_adventure/secure-connect-text-adventure-database.zip'
}
auth_provider = PlainTextAuthProvider(username='user', password='pass')

cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

message_history = CassandraChatMessageHistory(
    session_id="anything",
    session=session,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600
)

message_history.clear()

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)

template = """

"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

llm = OpenAI(openai_api_key=os.getenv('OPENAI_API_KEY'))
llm_chain = openllm(
    llm=llm,
    prompt=prompt,
    memory=cass_buff_memory
)

choice = "start"

while True:
    response = llm_chain.predict(human_input=choice)
    print(response.strip())

    if "The End." in response:
        break

    choice = input("Your reply: ")
