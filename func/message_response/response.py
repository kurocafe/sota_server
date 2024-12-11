import os
import ollama
import traceback
from ctypes import *
from langchain_community.embeddings import OllamaEmbeddings
from llama_index.llms.ollama import Ollama
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, PropertyGraphIndex
from llama_index.core.node_parser import SentenceSplitter
import pymupdf4llm

model_file='''
FROM /mnt/data1/home/nakaura/VSCode/llama/sota_server/Llama-3-ELYZA-JP-8B-q4_k_m.gguf
SYSTEM あなたは大学の教授です。学生の研究のアドバイスをします
TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>"""
PARAMETER stop "<|start_header_id|>"
PARAMETER stop "<|end_header_id|>"
PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|reserved_special_token|>"
'''

def test():
    llm = Ollama(model='llama3-soft', request_timeout=30.0)
    embed_model = OllamaEmbeddings(model="mxbai-embed-large")
    llama_reader = pymupdf4llm.LlamaMarkdownReader()
    llama_docs = llama_reader.load_data("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/MuSE.pdf")
    # print(f"LlamaIndexドキュメントの数: {len(llama_docs)}")
    # print(f"最初のドキュメントの内容: {llama_docs[0].text[:500]}")
    # reader = SimpleDirectoryReader(input_files=["/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/MuSE.pdf"])
    # data = reader.load_data()
    index = VectorStoreIndex.from_documents(llama_docs, embed_model=embed_model, transformations=[SentenceSplitter(chunk_size=256)])
    # index = PropertyGraphIndex.from_documents(llama_docs, embed_model=embed_model, transformations=[SentenceSplitter(chunk_size=256)])
    # index = VectorStoreIndex.from_documents(llama_docs, embed_model=embed_model)
    query_engine = index.as_query_engine(llm=llm, streaming=False, similarity_top_k=5, score_threshold=0.75)
    response = query_engine.query("この論文を書いている大学はどこですか？")
    print(response)
    
def talk():
    llm = Ollama(model='elyza:8b-instruct', request_timeout=30.0)
    embed_model = OllamaEmbeddings(model="mxbai-embed-large")
    llama_reader = pymupdf4llm.LlamaMarkdownReader()
    llama_docs = llama_reader.load_data("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/MuSE.pdf")
    index = VectorStoreIndex.from_documents(llama_docs, embed_model=embed_model, transformations=[SentenceSplitter(chunk_size=256)])
    query_engine = index.as_query_engine(llm=llm, streaming=False, similarity_top_k=5, verbose=False)

    print("質問を入力してください。終了するには 'quit' と入力してください。")
    while True:
        user_input = input("質問: ")
        if user_input.lower() == 'quit':
            break
        response = query_engine.query(user_input)
        
        # responseオブジェクトから実際の回答テキストを抽出
        if hasattr(response, 'response'):
            print(response.response)
        elif isinstance(response, str):
            print(response)
        else:
            print("回答を取得できませんでした。")
    
def test2():
    # ドキュメントの読み込み
    documents = SimpleDirectoryReader("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf").load_data()

    # Ollamaを使用してLlamaモデルを初期化
    llm = Ollama(model="llama3_rag")

    # PropertyGraphIndexの作成
    index = PropertyGraphIndex.from_documents(documents)

    # クエリエンジンの作成
    query_engine = index.as_query_engine(llm=llm)

    # クエリの実行
    response = query_engine.query("あなたの質問をここに入力")
    print(response)
    
    
import fitz

def join():
    doc1 = fitz.open("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/MuSE.pdf")
    
    doc2 = fitz.open("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/IEMOCAP.pdf")
    
    doc1.insert_pdf(doc2)
    
    doc1.save("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/joined.pdf")


def load_model(model_file):
    print(model_file)
    # モデルファイルの存在確認
    if not os.path.isfile(model_file):
        print("ファイルがないよ！")
        return
    
    # createしたらどっかに保存されるので2回目以降は作らなくてもいい
    try: 
        ollama.create(model='llama3_rag', modelfile=model_file)
        print("モデルが正常にロードされました")
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
    # load_model(model_file)
    # print(create_text([], text2="こんにちは！")
    # join()
    # test()
    talk()