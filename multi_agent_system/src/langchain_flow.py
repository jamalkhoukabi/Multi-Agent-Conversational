def build_conversation_flow(question_agent, update_agent):
    def ask_question(current_data, history):
        return question_agent.next_question(current_data, history)
    def update_state(current_data, user_response, history):
        return update_agent.update_state(current_data, user_response, history)
    return {"ask_question": ask_question, "update_state": update_state}
