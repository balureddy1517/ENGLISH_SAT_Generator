from src.content_structure import Craft_and_Structure
from src.stateflow import GraphState,QuestionStatus
from langgraph.graph import StateGraph, END
from Agents.passage_generation import passage_generation_node
from Agents.question_generation import question_generation_node
from Agents.refinement import refinement_node
from Agents.validation import validation_node
import json

def should_continue(state: GraphState):
    current_status = state.get("status")
    
    if current_status == QuestionStatus.PASSAGE_REDO.value:
        if state.get("iterations", 0) < 3:
            return "refine"
        else:
            print("Max retries reached.")
            return "fail"
            
    if current_status == QuestionStatus.QUESTIONS_GENERATED.value:
        return "go_for_validation"
        
    return "fail"

workflow = StateGraph(GraphState)

workflow.add_node("generate_passage", passage_generation_node)
workflow.add_node("generate_question", question_generation_node)
workflow.add_node("refine_passage", refinement_node)
workflow.add_node("validate", validation_node)

workflow.set_entry_point("generate_passage")

workflow.add_edge("generate_passage", "generate_question")

workflow.add_conditional_edges(
    "generate_question",
    should_continue,
    {
        "refine": "refine_passage",
        "go_for_validation":"validate" ,
        "fail": END
    }
)

workflow.add_edge("refine_passage", "generate_question")
workflow.add_edge("validate",END)

# Compile the Graph
app = workflow.compile()


if __name__=="__main__":

    inputs = {
        "domain": "Craft and Structure",   #. "Craft and Structure"
        "question_type": "Words in Context",
        "difficulty": "Easy",
        "iterations": 0,
        "status": QuestionStatus.INITIALISED.value
    }

#     inputs = {
#     "domain": "Information and Ideas",
#     "question_type": "Inference",
#     "difficulty": "Hard",
#     "iterations": 0,
#     "status": QuestionStatus.INITIALISED.value
# }
    current_state = inputs.copy()

    for step in app.stream(inputs):
        print("NODE OUTPUT:")
        print(step)

       