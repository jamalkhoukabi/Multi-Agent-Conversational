try:
    import langraph as lg
except ImportError:
    class Graph:
        def add_node(self, name, func):
            pass
        def run(self, inputs):
            return inputs
    lg = type("lg", (), {"Graph": Graph})

def build_conversation_graph(question_agent, update_agent):
    graph = lg.Graph()

    def ask_question(data):
        current_data = data.get("current_data", {})
        history = data.get("history", [])
        return question_agent.next_question(current_data, history)

    def update_state(data):
        current_data = data.get("current_data", {})
        user_response = data.get("user_response", "")
        history = data.get("history", [])
        return update_agent.update_state(current_data, user_response, history)

    graph.add_node("ask_question", ask_question)
    graph.add_node("update_state", update_state)
    return graph
