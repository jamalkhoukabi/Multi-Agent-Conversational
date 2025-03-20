# src/main.py

import os
import json
import logging
from dotenv import load_dotenv

from src.agents.base_agent import AgentConfig
from src.agents.question_agent import QuestionAgent
from src.agents.update_agent import UpdateAgent
from src.models.state import ConversationState
from src.models.schema import JSONSchema
from src.langchain_flow import build_conversation_flow  # if using a flow

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def main():
    configure_logging()
    logger = logging.getLogger("MainApp")
    
    try:
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY in .env")
        
        config_agent = AgentConfig(api_key=api_key)
        schema = JSONSchema()
        
        question_agent = QuestionAgent(config_agent, schema)
        update_agent = UpdateAgent(config_agent, schema)
        
        # Optionally build a conversation flow.
        conversation_flow = build_conversation_flow(question_agent, update_agent)
        logger.info("Conversation flow ready.")
        
        cs = ConversationState()
        
        stop_phrases = {"stop", "no", "n", "quit", "end", "that's all", "thats all", "that's it", "that is all"}
        
        logger.info("Starting conversation to fill out Job Details JSON...")
        while not cs.complete and cs.iteration < cs.max_iterations and cs.remaining_steps > 0:
            q = question_agent.next_question(cs.json_data, cs.history)
            cs = cs.model_copy(update={"question": q})
            
            print(f"\n[Progress] Iteration: {cs.iteration}")
            print(f"Current Job Data: {json.dumps(cs.json_data, indent=2)}")
            print(f"Remaining Steps: {cs.remaining_steps}")
            print(f"\nAGENT: {cs.question}")
            
            user_input = input("YOU: ").strip()
            if user_input.lower() in stop_phrases:
                cs = cs.model_copy(update={"complete": True, "question": ""})
                break
            
            cs.history.append({"question": q, "answer": user_input})
            
            new_data = update_agent.update_state(cs.json_data, user_input, cs.history)
            if "jobDetails" in new_data and "clarification" in new_data["jobDetails"]:
                clarification = new_data["jobDetails"].pop("clarification")
                cs = cs.model_copy(update={"question": clarification})
                print(f"\nAGENT: {clarification}")
                user_input = input("YOU: ").strip()
                if user_input.lower() in stop_phrases:
                    cs = cs.model_copy(update={"complete": True, "question": ""})
                    break
                cs.history.append({"question": clarification, "answer": user_input})
                new_data = update_agent.update_state(cs.json_data, user_input, cs.history)
            
            cs = cs.model_copy(update={
                "json_data": new_data,
                "iteration": cs.iteration + 1,
                "remaining_steps": cs.remaining_steps - 1,
                "question": None
            })
            
            if cs.is_complete(schema):
                follow_up = question_agent.next_question(cs.json_data, cs.history)
                print(f"\nAGENT: {follow_up}")
                extra_input = input("YOU: ").strip()
                if extra_input.lower() in stop_phrases:
                    cs = cs.model_copy(update={"complete": True})
                    break
                cs.history.append({"question": follow_up, "answer": extra_input})
                new_data = update_agent.update_state(cs.json_data, extra_input, cs.history)
                cs = cs.model_copy(update={
                    "json_data": new_data,
                    "iteration": cs.iteration + 1,
                    "remaining_steps": cs.remaining_steps - 1,
                    "question": None,
                    "complete": True
                })
        
        print("\n*** Job Details JSON Collection Complete! ***")
        print("Final Data:")
        print(json.dumps(cs.json_data, indent=2))
                
    except Exception as e:
        logger.error(f"Application failed: {e}")
        try:
            print("\nFinal state:", json.dumps(cs.json_data, indent=2))
        except NameError:
            print("\nNo conversation state available.")
        raise

if __name__ == "__main__":
    main()
