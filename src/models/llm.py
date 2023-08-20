from langchain import HuggingFacePipeline
from langchain.document_loaders import DirectoryLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from transformers import AutoTokenizer, pipeline
import torch

#if we have powerful system then we can use model of 40b parameters
model = "tiiuae/falcon-7b-instruct" #tiiuae/falcon-40b-instruct

tokenizer = AutoTokenizer.from_pretrained(model)

pipeline = pipeline(
    "text-generation", #task
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto",
    max_new_tokens=200,
    do_sample=True,
    top_k=10,
    num_return_sequences=1,
    eos_token_id=tokenizer.eos_token_id
)

llm = HuggingFacePipeline(pipeline = pipeline, model_kwargs = {'temperature':0.5})

directory = './data'

def load_docs(directory):
    loader = DirectoryLoader(directory)
    documents = loader.load()
    return documents

template = """
You are a Master Logs monitoring bot.

You are given set of logs identify non-compliant log activity and suggest corrective action based on the given ruleset. If the log is compliant don't generate anything
The answer should be strictly in the required format.

The answer should be in below format:
Answer:
Failure=
Action=

Example conversation:

<human>: [2023-08-20 09:15:30] User successfully created account username: "rob" password: "###"
<assistant>:
Failure=Violated rule no. 1: All user accounts must have a password that is at least 8 characters long and contains at least one uppercase letter, one lowercase letter, and one number
Action=Delete the created user and enforce constraint on creation of new accounts.
<human>: [2023-08-20 09:15:30] User successfully created account username: "rob" password: "Darshan123"
<assistant>: No rule violated!

###############################################################################################

The set of rules and regulations are:
{context}

Input Log: {question}

Answer:
"""

def get_non_complaint_logs(logs):
    documents = load_docs(directory)

    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    qa_chain = load_qa_chain(llm, chain_type="stuff",verbose=True, prompt=QA_CHAIN_PROMPT)
    result = qa_chain.run(input_documents=documents,question=logs)
    return result