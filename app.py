from flask import Flask, render_template, request, jsonify
from openai import AzureOpenAI
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
import os
import json
import PyPDF2
import docx

# === ENVIRONMENT SETUP ===
load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
MODEL = os.getenv("AZURE_OPENAI_MODEL")
UPLOAD_FOLDER = 'python_uploads_test'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

# === AZURE OPENAI SETUP ===
client = AzureOpenAI(
    api_version="2024-07-01-preview",
    azure_endpoint=endpoint,
    api_key=api_key
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Global conversations dictionary
conversations = {}

# ==== FUNCTION SPECIFICATION ====
functions_spec = [
    {
        "name": "get_leave_policy",
        "description": "Find information about leave policies, such as vacation, sick leave, unpaid leave",
        "parameters": {
            "type": "object",
            "properties": {
            "question": {
                "type": "string",
                "description": "User's question about leave policy"
            }
            },
            "required": ["question"]
        }   
    },
    {
        "name": "get_overtime_policy",
        "description": "Find information about overtime policies, such as work on weekends, holidays, overtime pay",
        "parameters": {
            "type": "object",
            "properties": {
            "question": {
                "type": "string",
                "description": "User's question about overtime"
            }
            },
            "required": ["question"]
        }
    },
    {
        "name": "get_workplace_rules",
        "description": "Find information about general workplace rules such as working hours, dress code, behavior",
        "parameters": {
            "type": "object",
            "properties": {
            "question": {
                "type": "string",
                "description": "User's question about workplace rules"
            }
            },
            "required": ["question"]
        }
    }
]


def load_system_message(path="prompt/system_prompt.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Failed to load system prompt: {e}")
        return []

default_system_message = load_system_message()

def load_func_system_message(path="prompt/function_sys_prompt.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Failed to load function_sys_prompt.txt: {e}")
        return []

function_system_message = load_func_system_message()

# Load few-shot examples từ file JSON
def load_few_shot_examples(path="prompt/few_shot_examples.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load few-shot examples: {e}")
        return []

few_shot_examples = load_few_shot_examples()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(file_path):
    print(f"Reading file {file_path}")
    try:
        ext = file_path.rsplit('.', 1)[1].lower()
        if ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == 'pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        elif ext == 'docx':
            doc = docx.Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        return ""
    except Exception as e:
        print(f"⚠️ Failed to read file {file_path}: {e}")


def query_policy(question, document_name):
    doc_path = os.path.join("doc", document_name)
    doc_content = extract_text(doc_path)
    print(f"Content file: {doc_content[:3000]}")
    messages = [
        {"role": "system", "content": function_system_message},
        {"role": "user", "content": f"User question: {question}\n\nPolicy Document:\n{doc_content}"}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        result = response.choices[0].message.content.strip()
        return result

    except Exception as e:
        print(f"⚠️ Failed to query policy: {e}")

# ==== FUNCTION IMPLEMENTATION ====
def get_leave_policy(question: str) -> str:
    return query_policy(question, "Leave Benefits for Employees.docx")

def get_overtime_policy(question: str) -> str:
    return query_policy(question, "Regulation Working Overtime.docx")

def get_workplace_rules(question: str) -> str:
    return query_policy(question, "Regulation Internal Labor.docx")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new_chat", methods=["POST"])
def new_chat():
    chat_id = str(uuid.uuid4())
    conversations[chat_id] = [{"role": "system", "content": default_system_message}]
    conversations[chat_id] = conversations[chat_id] + few_shot_examples
    return jsonify({"chat_id": chat_id})

@app.route("/chat/<chat_id>", methods=["POST"])
def chat(chat_id):
    user_message = request.json.get("message")

    if chat_id not in conversations:
        return jsonify({"error": "Chat ID not found. Please create new Chat!"}), 404
    
    # Add user message
    conversations[chat_id].append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversations[chat_id],
            functions=functions_spec,
            function_call="auto"
        )

        message = response.choices[0].message
        
        if not message.function_call:
            
            reply = message.content.strip()
            # Add assistant reply to message list
            conversations[chat_id].append({"role": "assistant", "content": reply})
            return jsonify({"reply": reply})
        else :
            func_name = message.function_call.name
            arguments = json.loads(message.function_call.arguments)
            question = arguments.get('question')
            print(f"Function calling: {message.function_call}")

            # Add assistant function call to message list
            conversations[chat_id].append({"role": "assistant", "function_call": message.function_call})

            # Call the correct backend function
            if func_name == "get_leave_policy":
                result = get_leave_policy(question)
            elif func_name == "get_overtime_policy":
                result = get_overtime_policy(question)
            elif func_name == "get_workplace_rules":
                result = get_workplace_rules(question)
            else:
                result = "⚠️ Unknown function called."

            print(f"Result of Function calling: {result}")

            # Add function call to message list
            conversations[chat_id].append({"role": "function", "name": func_name, "content": result})

            # Send the result back to model for final response
            follow_up = client.chat.completions.create(
                model=MODEL,
                messages=conversations[chat_id]
            )

            final_answer = follow_up.choices[0].message.content.strip()
            # Add assistant reply to message list
            conversations[chat_id].append({"role": "assistant", "content": final_answer})
            return jsonify({"reply": final_answer})

    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return jsonify({"reply": f"Error: {str(e)}"}), 500
    
@app.route("/load_chat/<chat_id>")
def load_chat(chat_id):
    if chat_id not in conversations:
        return jsonify({"error": "Chat ID not found"}), 404
    return jsonify({"messages": conversations[chat_id]})

@app.route("/upload", methods=["POST"])
def upload():
    # global document_text
    # if 'file' not in request.files:
    #     return jsonify({"error": "No file part"}), 400
    # file = request.files['file']
    # if file.filename == '':
    #     return jsonify({"error": "No selected file"}), 400
    # if file and allowed_file(file.filename):
    #     filename = secure_filename(file.filename)
    #     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #     file.save(filepath)
    #     document_text = extract_text(filepath)
    #     return jsonify({"message": "File uploaded and processed."})
    return jsonify({"error": "Invalid file type"}), 400

if __name__ == "__main__":
    app.run(debug=True)
