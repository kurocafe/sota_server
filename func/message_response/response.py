import os
import ollama
import fitz
import traceback
from ctypes import *
from langchain.embeddings import OllamaEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import retrieval_qa
# from langchain.llms import ollama
from llama_index.llms.ollama.base import ChatMessage
from llama_index.llms.ollama import Ollama
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, PropertyGraphIndex
from llama_index.core.node_parser import SentenceSplitter
import pymupdf4llm
from pymupdf4llm import LlamaMarkdownReader
from func.db.add_db import add_msg, pull_msg

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

model = "llama3-test"

def test():
    llm = Ollama(model='llama3-soft', request_timeout=30.0)
    embed_model = OllamaEmbeddings(model="mxbai-embed-large")
    llama_reader = pymupdf4llm.LlamaMarkdownReader()
    llama_docs = llama_reader.load_data("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/takanabe.pdf")
    # print(f"LlamaIndexドキュメントの数: {len(llama_docs)}")
    # print(f"最初のドキュメントの内容: {llama_docs[0].text[:500]}")
    # reader = SimpleDirectoryReader(input_files=["/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/MuSE.pdf"])
    # data = reader.load_data()
    index = VectorStoreIndex.from_documents(llama_docs, embed_model=embed_model, transformations=[SentenceSplitter(chunk_size=1024)])
    # index = PropertyGraphIndex.from_documents(llama_docs, embed_model=embed_model, transformations=[SentenceSplitter(chunk_size=256)])
    # index = VectorStoreIndex.from_documents(llama_docs, embed_model=embed_model)
    query_engine = index.as_query_engine(llm=llm, streaming=False, similarity_top_k=5, score_threshold=0.75)
    response = query_engine.query("この論文を書いている大学はどこですか？")
    print(response)
    
def talk():
    llm = Ollama(model='llama:summary', request_timeout=120.0)
    # print(f"dir LLM: {dir(llm)}")
    
    # TestMessages = [
    #     ChatMessage(role="user", content="要約はできそうですか？") 
    # ]
    # test_response = llm.chat(TestMessages)
    # print(f"LLM test response: {test_response}")
    
    embed_model = OllamaEmbeddings(model="mxbai-embed-large")
    # test_embedding = embed_model.embed_text("こんにちは")
    # print(f"Test embedding: {test_embedding}")
    
    llama_reader = pymupdf4llm.LlamaMarkdownReader()
    llama_docs = llama_reader.load_data("/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/thesis.pdf")
    print(f"Loaded documents: {llama_docs}")
    
    index = VectorStoreIndex.from_documents(llama_docs, embed_model=embed_model, transformations=[SentenceSplitter(chunk_size=512)])
    print(f"Documents in index: {len(index.docstore.docs)}")
    
    query_engine = index.as_query_engine(llm=llm, streaming=False, similarity_top_k=12, verbose=True, score_threshold=0.8)

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
    
def ask_directly_with_llm():
    # LLM の初期化
    llm = Ollama(model='llama:summary', request_timeout=120.0)
    
    # PDF ファイルを読み込む
    pdf_path = "/mnt/data1/home/nakaura/VSCode/llama/sota_server/func/message_response/pdf/thesis.pdf"
    reader = LlamaMarkdownReader()
    documents = reader.load_data(pdf_path)
    
    # PDF 内容を LLM に渡す
    pdf_content = "\n".join([doc.get_content() for doc in documents])
    system_prompt = (
        "あなたは学術論文の要約の専門家です。以下の内容をもとに、質問に答えてください。\n\n"
        f"{pdf_content}\n"
    )
    
    # 初期プロンプトを設定
    llm_system_message = ChatMessage(role="system", content=system_prompt)
    
    print("質問を入力してください。終了するには 'quit' と入力してください。")
    while True:
        user_input = input("質問: ")
        if user_input.lower() == 'quit':
            break
        
        # ユーザーの質問を LLM に送信
        user_message = ChatMessage(role="user", content=user_input)
        response = llm.chat([llm_system_message, user_message])
        
        print("回答:")
        print(response)

    

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
    
def create_text(messages: list, text2, user_id) -> str:
    usr_message = {'role': 'user', 'content': text2}
    
    add_msg(user_id, usr_message)
    response = ollama.chat(model=model, messages=pull_msg(user_id))
    text = response['message']['content']
    new_message = {'role': 'assistant', 'content': text}
    
    add_msg(user_id, new_message)
    return text

def init_chat(user_id)-> str:
    init_text = "'SNS'、'情報検索'、'マルチモーダル'、'ロボット'、'テキストチャット'から、ユーザがどんなことに興味のあるかを聞いてください。"
    sys_message = {'role': 'system', 'content': init_text}
    add_msg(user_id, sys_message)
    response = ollama.chat(model=model, messages=pull_msg(user_id), options={"num_ctx": 128})
    text = response['message']['content']
    llm_message = {'role': 'assistant', 'content': text}
    add_msg(user_id, llm_message)
    
    return text

def gen_keyword(user_id) -> str:
    try:
        sys_text = "ユーザーの発言から、論文検索に使うキーワードを一つ決めてください。「」などは必要ないです。"
        sys_message = {'role': 'system', 'content': sys_text}
        add_msg(user_id, sys_message)
        response = ollama.chat(model=model, messages=pull_msg(user_id, 8))
        text = response['message']['content']
        llm_message = {'role': 'assistant', 'content': text}
        add_msg(user_id, llm_message)
        
        return text
    except Exception as e:
        print(f"gen_keyword ERROR: {e}")
        raise

if __name__ == "__main__":
    # load_model(model_file)
    # print(create_text([], text2="こんにちは！")
    # join()
    # test()
    # talk()
    # ask_directly_with_llm()
    print(f"keyword: {gen_keyword(821611534961606706)}")