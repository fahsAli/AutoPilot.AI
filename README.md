# `AutoPilot.AI`

**`AutoPilot.AI`** is an advanced framework that dynamically generates intelligent agents to orchestrate and execute tasks autonomously. It leverages cutting-edge AI to decompose complex tasks, create specialized agents, and then execute those tasks with minimal human intervention. This project aims to automate the process of task management by creating, managing, and executing autonomous agents tailored for each job.

## Features

- **Dynamic Agent Creation**: Automatically generate agents based on a task description.
- **Task Decomposition**: Break down complex tasks into manageable subtasks.
- **Autonomous Execution**: Agents execute tasks and return results without manual intervention.
- **AI-Powered Orchestration**: Uses state-of-the-art AI models to handle task execution and agent orchestration.
- **Flexible Architecture**: Easily customizable agents and tasks that can integrate with other systems.

---

## How It Works

1. **User Input**: You provide a natural language task description (e.g., "Write a resignation letter").
2. **Task Analysis**: A TaskAnalyzer agent evaluates the task and determines what kind of specialized agent should be created.
3. **Prompt Engineering**: A PromptEngineer agent generates an optimized system prompt tailored to the agent type and task.
4. **Agent Creation**: A new specialized AssistantAgent is instantiated with the generated prompt and configuration.
5. **Execution**: The specialized agent performs the task and returns results to the Coordinator agent, which delivers them to the user.

---

## Example

Running the project out-of-the-box with the included task:
```python
"Write a formal resignation letter for someone leaving a company after 5 years"
```

Will result in:

* Automatic detection of the task type (e.g., WriterAgent)
* Custom system prompt generation
* Task execution by a tailored AI agent
* Returned, fully written letter

## Project Structure

```
AutoPilot.AI/
│
├── main.py                   # Entry point: runs coordinator and agent pipeline
├── .env                      # Your OpenAI API key (ignored from Git)
├── requirements.txt          # Dependencies (generated with `pip freeze`)
├── working_dir/              # Temp folder for agent execution (auto-created)
├── .gitignore                # Ignores venv, .env, __pycache__, etc.
└── README.md                 # This file
```


## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/fahsAli/AutoPilot.AI.git
cd AutoPilot.AI
```

### 2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key
Create a .env file:
```ini
OPENAI_API_KEY=your_openai_key_here
```

### 5. Run the app
```bash
python main.py
```

## Author
Developed with ❤️ by [Ali FAHS](https://github.com/fahsAli)