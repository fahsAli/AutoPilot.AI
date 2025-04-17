import openai
import autogen
import os
import json
from typing import List, Dict, Any, Callable
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class DynamicAgentFactory:
    """Custom tool to create specialized agents with dynamically generated roles based on task analysis"""
    def __init__(self, base_llm_config):
        self.base_llm_config = base_llm_config
        self.agents = {}
    
    def analyze_task(self, task):
        """Analyze the task and determine what type of agent is needed"""
        analyzer = autogen.AssistantAgent(
            name="TaskAnalyzer",
            llm_config=self.base_llm_config,
            system_message="""You analyze tasks and determine the best type of specialized agent to handle them.
            Respond with a valid JSON object containing:
            {
                "agent_type": "a short descriptive name for the type of agent needed",
                "description": "brief description of what this agent does"
            }
            """
        )
        
        user_proxy = autogen.UserProxyAgent(
            name="AnalyzerProxy",
            human_input_mode="NEVER"
        )
        
        user_proxy.initiate_chat(
            analyzer, 
            message=f"Analyze this task and tell me what type of specialized agent would be best suited to handle it: '{task}'. Respond with ONLY a JSON object containing agent_type and description."
        )
        
        messages = user_proxy.chat_messages[analyzer.name]
        analysis_text = messages[-1]['content']
        
        try:
            if "```json" in analysis_text:
                json_content = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                json_content = analysis_text.split("```")[1].split("```")[0].strip()
            else:
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > 0:
                    json_content = analysis_text[start_idx:end_idx]
                else:
                    raise ValueError("Could not find JSON content")
            
            analysis = json.loads(json_content)
            return analysis["agent_type"]
        except Exception as e:
            print(f"Error parsing analyzer response: {e}")
            print(f"Raw response: {analysis_text}")
            return "general" 
    
    def generate_system_message(self, agent_type, task):
        """Generate a tailored system message for the agent type and task"""
        prompt_engineer = autogen.AssistantAgent(
            name="PromptEngineer",
            llm_config=self.base_llm_config,
            system_message="""You are an expert in creating ideal system prompts for AI agents.
            You craft specialized prompts that define an agent's role, expertise, tone, and approach.
            Your prompts empower agents to excel at their specific tasks."""
        )
        
        user_proxy = autogen.UserProxyAgent(
            name="PromptProxy",
            human_input_mode="NEVER"
        )
        
        # Request a specialized system message
        prompt_request = f"""Create a system message for an AI agent of type '{agent_type}' 
        that will handle this task: '{task}'.
        
        The system message should:
        1. Define the agent's specialized role and expertise
        2. Outline the agent's approach and methodology
        3. Specify the expected output format
        4. Include specific capabilities needed for this task
        
        Respond with ONLY the system message text, no additional commentary."""
        
        user_proxy.initiate_chat(prompt_engineer, message=prompt_request)
        
        # Extract the generated system message
        messages = user_proxy.chat_messages[prompt_engineer.name]
        system_message = messages[-1]['content']
        
        if "```" in system_message:
            system_message = system_message.split("```")[1].split("```")[0].strip()
        
        return system_message
    
    def create_agent(self, task):
        """Create a specialized agent dynamically based on the task"""
        # First analyze what type of agent is needed
        agent_type = self.analyze_task(task)
        
        # Then generate a specialized system message
        system_message = self.generate_system_message(agent_type, task)
        
        # Create a properly named agent
        agent_name = f"{agent_type.capitalize()}Agent"
        
        # Create the specialized agent
        specialized_agent = autogen.AssistantAgent(
            name=agent_name,
            llm_config=self.base_llm_config,
            system_message=system_message
        )
        
        # Store the agent for future reference
        self.agents[agent_name] = specialized_agent
        
        return specialized_agent, agent_type, system_message

def main():
    llm_config = {
        "config_list": [{"model": "gpt-4o-mini", "api_key": openai.api_key}]
    }
    
    if not os.path.exists("working_dir"):
        os.makedirs("working_dir")
    
    agent_factory = DynamicAgentFactory(llm_config)

    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config={
            "work_dir": "working_dir",
            "use_docker": False,
        }
    )
    
    coordinator = autogen.AssistantAgent(
        name="Coordinator",
        llm_config=llm_config,
        system_message="""You coordinate task execution by:
            1. Receiving a task from the user
            2. Requesting the creation of a specialized agent for the task
            3. Delegating the task to the specialized agent
            4. Returning the results to the user

            Always report what kind of agent was created and its capabilities before sharing the results.
            """
    )
    
    def create_and_use_specialized_agent(task: str, sender) -> None:
        """Function to create and use a specialized agent for the given task"""
        specialized_agent, agent_type, system_message = agent_factory.create_agent(task)
        
        user_proxy.send(
            f"""I've created a specialized {agent_type} agent to help with this task.
            
            The agent has been configured with this system directive:
            ---
            {system_message}
            ---
            
            The agent will now work on: "{task}".""",
            coordinator
        )
        
        user_proxy.initiate_chat(
            specialized_agent,
            message=f"Please help with this task: {task}"
        )
        
        result = user_proxy.chat_messages[specialized_agent.name][-1]['content']
        
        user_proxy.send(
            f"Here's the result from the {agent_type} agent:\n\n{result}",
            coordinator
        )
    
    user_proxy.register_function(
        function_map={"create_specialized_agent": create_and_use_specialized_agent}
    )
    
    task = "Write a formal resignation letter for someone leaving a company after 5 years"
    
    user_proxy.initiate_chat(
        coordinator,
        message=f"I need help with this task: {task}. Please create a specialized agent to handle it."
    )

if __name__ == "__main__":
    main()