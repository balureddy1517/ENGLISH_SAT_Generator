from langgraph.graph import StateGraph, START, END

from src.stateflow import GraphState,QuestionStatus,StandardEnglishState
from Agents.passage_generation import passage_generation_node,standard_english_generation_node
from Agents.question_generation import question_generation_node,standard_english_question_generation_node
from Agents.refinement import refinement_node,standard_english_refinement_node
from Agents.validation import validation_node,standard_english_validation_node
import json
from src.utils import route_standard_english_after_validation,route_passage_after_validation,route_domain
import mlflow


@mlflow.trace
def finalize_output_node(state: GraphState) -> GraphState:
    if state["domain"] == "Standard English Conventions":
        source_text = state.get("sentence", "")
    else:
        source_text = state.get("raw_passage", "")

    return {
        **state,
        "source_text": source_text
    }

@mlflow.trace
def sentence_english_subgraph_node(state: GraphState) -> GraphState:
    sub_input: StandardEnglishState = {
        "domain": state["domain"],
        "question_type": state["question_type"],
        "difficulty": state["difficulty"],
        "iterations": state.get("iterations", 0),
        "status": state.get("status", "INITIALISED"),
    }

    standard_english_app=sentence_english_workflow()

    sub_result = standard_english_app.invoke(sub_input)

    return {
        **state,
        "sentence": sub_result.get("sentence"),
        "editable_portion": sub_result.get("editable_portion"),
        "question_data": sub_result.get("question_data"),
        "validator_feedback": sub_result.get("validator_feedback"),
        "feedback": sub_result.get("feedback", ""),
        "iterations": sub_result.get("iterations", state.get("iterations", 0)),
        "status": sub_result.get("status", "FAILED")
    }

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

def sentence_english_workflow():
    se_builder = StateGraph(StandardEnglishState)

    se_builder.add_node("generate_sentence", standard_english_generation_node)
    se_builder.add_node("generate_question", standard_english_question_generation_node)
    se_builder.add_node("validate_item", standard_english_validation_node)
    se_builder.add_node("refine_item", standard_english_refinement_node)

    se_builder.add_edge(START, "generate_sentence")
    se_builder.add_edge("generate_sentence", "generate_question")
    se_builder.add_conditional_edges(
        "generate_question",
        should_continue,
    {
        "refine": "generate_sentence",
        "go_for_validation":"validate_item" 
    }
    )

    se_builder.add_conditional_edges(
        "validate_item",
        route_standard_english_after_validation,
        {
            "done": END,
        "refine": "refine_item",
        "give_up": END,
        "fail": END,
        },
    )
    se_builder.add_edge("refine_item", "validate_item")


    sentence_english_app = se_builder.compile()

    return sentence_english_app



def main_workflow():
    main_builder = StateGraph(GraphState)

    main_builder.add_node("passage_generation", passage_generation_node)
    main_builder.add_node("passage_question_generation", question_generation_node)
    main_builder.add_node("passage_validation", validation_node)
    main_builder.add_node("passage_refinement", refinement_node)

    main_builder.add_node("sentence_english_subgraph", sentence_english_subgraph_node)
    main_builder.add_node("finalize_output", finalize_output_node)

    main_builder.add_conditional_edges(
        START,
        route_domain,
        {
            "passage_branch": "passage_generation",
            "sentence_english_branch": "sentence_english_subgraph",
        }
    )

    main_builder.add_edge("passage_generation", "passage_question_generation")

    main_builder.add_conditional_edges(
        "passage_question_generation",
        should_continue,
        {
              "refine": "passage_generation",
            "go_for_validation":"passage_validation" 
           
        }
    )

    # main_builder.add_edge("passage_refinement", "passage_question_generation")

    main_builder.add_conditional_edges(
    "passage_validation",
    route_passage_after_validation,
    {
        "done": "finalize_output",
        "refine": "passage_refinement",
        "give_up": "finalize_output",
        "fail": "finalize_output",
    }
)
    
    main_builder.add_edge("passage_refinement", "passage_validation")

    main_builder.add_edge("sentence_english_subgraph", "finalize_output")
    main_builder.add_edge("finalize_output", END)

    app = main_builder.compile()
    return app




# if __name__=="__main__":
# #     inputs = {
# #     "domain": "Craft and Structure",
# #     "question_type": "Words in Context",
# #     "difficulty": "Hard",
# #     "iterations": 0,
# #     "status": "INITIALISED"
# # }
    
# #     inputs = {
# #     "domain": "Information and Ideas",
# #     "question_type": "Inference",
# #     "difficulty": "Medium",
# #     "iterations": 0,
# #     "status": "INITIALISED"
# # }
# #     inputs = {
# #     "domain": "Standard English Conventions",
# #     "question_type": "Boundaries",
# #     "difficulty": "Medium",
# #     "iterations": 0,
# #     "status": "INITIALISED"
# # }
    
#     inputs = {
#     "domain": "Expression of Ideas",
#     "question_type": "Transitions",
#     "difficulty": "Medium",

#     "status": "INITIALISED",
#     "iterations": 0,

   
# }


#     craft_and_structure_inputs = [
#     {"domain": "Craft and Structure", "question_type": "Words in Context", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Craft and Structure", "question_type": "Text Structure", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Craft and Structure", "question_type": "Cross-Text", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ]
#     information_and_ideas_inputs = [
#     {"domain": "Information and Ideas", "question_type": "Central Idea", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Information and Ideas", "question_type": "Command of Evidence", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Information and Ideas", "question_type": "Inference", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Information and Ideas", "question_type": "Data Interpretation", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ]
#     standard_english_inputs = [
#     {"domain": "Standard English Conventions", "question_type": "Boundaries", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Standard English Conventions", "question_type": "Form, Structure, and Sense", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Standard English Conventions", "question_type": "Modifiers", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Standard English Conventions", "question_type": "Punctuation", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ]
    
#     expression_of_ideas_inputs = [
#     {"domain": "Expression of Ideas", "question_type": "Transitions", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Expression of Ideas", "question_type": "Organization", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Expression of Ideas", "question_type": "Concision and Precision", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Expression of Ideas", "question_type": "Rhetorical Synthesis", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ]
#     all_inputs = (
#     craft_and_structure_inputs +
#     information_and_ideas_inputs +
#     standard_english_inputs +
#     expression_of_ideas_inputs
# )
#     app = main_workflow()

# for inp in all_inputs:
#     print(f"Running: {inp}")
    
#     final_state = None
#     for state in app.stream(inp, stream_mode="values"):
#         final_state = state
    
#     if final_state:

#         save_to_excel(final_state)
  
