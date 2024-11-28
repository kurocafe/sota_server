import ollama
import traceback
from ctypes import *
from langchain_community.embeddings import OllamaEmbeddings
from llama_index.llms.ollama import Ollama
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
import pymupdf4llm

model_file='''
FROM elyza:jp8b
SYSTEM あなたは大学の教授です。学生の研究のアドバイスをします
TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>"""
PARAMETER stop "<|start_header_id|>"
PARAMETER stop "<|end_header_id|>"
PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|reserved_special_token"
'''

def test():
    llm = Ollama(model='llama3_rag', request_timeout=30.0)
    embed_model = OllamaEmbeddings(model="mxbai-embed-large")
    llama_reader = pymupdf4llm.LlamaMarkdownReader()
    llama_docs = llama_reader.load_data("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/MuSE.pdf")
    # print(f"LlamaIndexドキュメントの数: {len(llama_docs)}")
    # print(f"最初のドキュメントの内容: {llama_docs[0].text[:500]}")
    # reader = SimpleDirectoryReader(input_files=["/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/MuSE.pdf"])
    # data = reader.load_data()
    index = VectorStoreIndex.from_documents(llama_docs, embed_model=embed_model, transformations=[SentenceSplitter(chunk_size=256)])
    # index = VectorStoreIndex.from_documents(llama_docs, embed_model=embed_model)
    query_engine = index.as_query_engine(llm=llm, streaming=False, similarity_top_k=5)
    response = query_engine.query("私は感情分析の研究をしたいと考えています。使用すべきデータセットを教えてください。")
    print(response)
    
    
import fitz

def join():
    doc1 = fitz.open("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/MuSE.pdf")
    
    doc2 = fitz.open("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/IEMOCAP.pdf")
    
    doc1.insert_pdf(doc2)
    
    doc1.save("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/joined.pdf")


def load_model(model_file):
    print('OLLAMA')
    # createしたらどっかに保存されるので2回目以降は作らなくてもいい
    try: 
        ollama.create(model='llama3_rag', modelfile=model_file)
    except Exception as e:
        print(f"エラーです。{str(e)}")
        traceback.print_exc()
    
def create_text(messages: list, text2) -> str:
    print(ollama.show(model="llama3_soft"))
    usr_message = {'role': 'user', 'content': text2}
    messages.append(usr_message)
    if 40 < len(messages):
        messages.pop(1)
    print(messages)
    response = ollama.chat(model='llama3_soft', messages=messages)
    text = response['message']['content']
    new_message = {'role': 'assistant', 'content': text}
    if 10 < len(messages):
        messages.pop(1)
    messages.append(new_message)
    
    return text

if __name__ == "__main__":
    # load_model(model_file=model_file)
    # print(create_text([], text2="こんにちは！")
    # join()
    test()