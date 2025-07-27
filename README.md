# HR Assistant

A web-based AI chatbot built with **Flask** and powered by **Azure OpenAI (GPT-4o-mini)**. This assistant supports chatting, uploading policy documents, and answering questions based on specific files (leave, overtime, workplace rules).

---

## 📦 Features

- Chat with OpenAI GPT-4o-mini via Azure API
- Multi-conversation support (sidebar)
- Upload and parse `.txt`, `.pdf`, `.docx` documents
- Function calling to retrieve specific company policies
- Document-aware responses
- Professional ChatGPT-style UI (with conversation history)

---

## 📁 Project Structure

project-root/
│
├── app.py # Main Flask backend
├── templates/
│ └── index.html # Frontend chat UI
├── static/
│ ├── style.css # Chat UI styling
│ └── script.js # Frontend logic
├── prompt/
│ ├── system_prompt.txt
│ ├── function_sys_prompt.txt
│ └── few_shot_examples.json
├── doc/ # Static documents for querying (e.g. policies)
│ └── *.docx / *.pdf
├── python_uploads_test/ # Uploaded files by users
├── .env # Your Azure API keys
└── README.md


---

## 🚀 Getting Started

### 1. Clone Project

```bash

```

### 2. Create virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

> If `requirements.txt` does not exist, use:

```bash
pip install flask python-dotenv openai PyPDF2 python-docx
```

### 3. Setup `.env`

Create a `.env` file in the root folder:

```
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-api-key
```

### 4. Run the App

```bash
python app.py
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## 🧠 Function Calling Support

This app supports OpenAI function calling for:

| Function Name         | Purpose                          | Related File                        |
| --------------------- | -------------------------------- | ----------------------------------- |
| `get_leave_policy`    | Vacation, sick, and unpaid leave | `Leave Benefits for Employees.docx` |
| `get_overtime_policy` | Overtime rules and compensation  | `Regulation Working Overtime.docx`  |
| `get_workplace_rules` | General internal regulations     | `Regulation Internal Labor.docx`    |

These files are placed inside the `doc/` folder.

---

## 📄 Uploading Files (Not Implementation)

User-uploaded `.txt`, `.pdf`, and `.docx` files are processed (but currently not yet integrated with chat context). You can expand this by injecting uploaded content into conversation history or embedding retrieval pipeline.

---

## 🛡 Error Handling

* Frontend JavaScript displays error messages returned from backend APIs.
* Backend routes return appropriate JSON errors with `status_code 400/404/500` if needed.
* Errors from document reading and API calls are printed in console and relayed back.

---

## 🔧 Customization

* To modify system prompt: edit `prompt/system_prompt.txt`
* To add more few-shot examples: edit `prompt/few_shot_examples.json`
* To add new policies: drop new `.docx/.pdf` files into `doc/` and define a new function

---

## 📝 License

This project is intended for internal or demo use. You may adapt or extend it under your organization's policy.

---

## 🙋 Support

If you need help customizing this app or deploying it to cloud (Azure App Service, Vercel, etc.), feel free to ask!

```

---