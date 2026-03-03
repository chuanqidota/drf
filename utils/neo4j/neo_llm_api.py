# pip install langchain-openai langchain_community

# deepseek的api-key
# https://platform.deepseek.com/usage

# 采集器
# https://llm-graph-builder.neo4jlabs.com/



from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain

uri = "neo4j+s://0143b13f.databases.neo4j.io"
user = "neo4j"
password = "PiZUB3SIcbPB5s3ok5AU9mMn6QWHfVzOlkD2d-pyu4Q"

graph = Neo4jGraph(
    url=uri,
    username=user,
    password=password
)

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key="sk-476a55958ad94412bd3d602782e7ef24",
    base_url="https://api.deepseek.com/v1",
    temperature=0
)

chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True  # 必须确认
)

response = chain.invoke({
    "query": "找出node最多的label"
})

print(response)

"""
"model": "deepseek-chat"
"open_ai_api_key": "sk-476a55958ad94412bd3d602782e7ef24"
"open_ai_api_base": "https://api.deepseek.com/v1"

"feishu_bot_name": "影魔"
"feishu_app_id": "cli_a90efe7b66399cd5"
"feishu_app_secret": "csHP40BHHLCyVXBkysAD7cTvwSVdgJC3"
"""
