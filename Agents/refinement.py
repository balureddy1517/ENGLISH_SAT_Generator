from tools.auth import client
from src.stateflow import GraphState,QuestionStatus,StandardEnglishState
# from src.content_structure import Craft_and_Structure
from Topic_Content.craft_structure import Craft_and_Structure
import json
from src.utils import get_domain_handler
import mlflow

@mlflow.trace
def refinement_node(state: GraphState) -> GraphState:
    creator = get_domain_handler(state["domain"])

    max_refinements = 3
    current_iterations = state.get("iterations", 0)

    # Stop refinement if limit is reached
    if current_iterations >= max_refinements:
        return {
            **state,
            "status": QuestionStatus.Iterations.value,   # or GIVE_UP if you have that status
            "summary_refinement": "Refinement limit reached.",
        }

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano",
            messages=[
                {"role": "system", "content": creator.build_refinement_system_prompt()},
                {
                    "role": "user",
                    "content": creator.build_refinement_user_prompt(
                        passage=state["raw_passage"],
                        question_type=state["question_type"],
                        feedback=state["validator_feedback"],
                        difficulty=state.get("difficulty", "Medium"),
                        question_data=state["question_data"],
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )

        span = mlflow.get_current_active_span()
        usage = response.usage
        if span and usage:
            span.set_attribute("llm.model", response.model)
            span.set_attribute("llm.prompt_tokens", usage.prompt_tokens)
            span.set_attribute("llm.completion_tokens", usage.completion_tokens)
            span.set_attribute("llm.total_tokens", usage.total_tokens)
            span.set_attribute("llm.raw_output", response.choices[0].message.content)

        data = json.loads(response.choices[0].message.content)
        question_data = extract_question_data(data)

        return {
            **state,
            "raw_passage": data.get("passage", state["raw_passage"]),
            "question_data": question_data,
            "iterations": current_iterations + 1,
            "status": QuestionStatus.REFINED.value,
            "validator_feedback": None,
            "feedback":None,
            "summary_refinement": data.get("revision_summary", ""),
        }

    except Exception:
        return {
            **state,
            "status": QuestionStatus.FAILED.value,
        }

def extract_question_data(item_json: dict) -> dict:
    question_data = {
        "question": item_json.get("question", ""),
        "option_a": item_json.get("option_a", ""),
        "option_b": item_json.get("option_b", ""),
        "option_c": item_json.get("option_c", ""),
        "option_d": item_json.get("option_d", ""),
        "correct_answer": item_json.get("correct_answer", ""),
        "explanation": item_json.get("explanation", "")
        
    }
    return question_data


@mlflow.trace
def standard_english_refinement_node(state: StandardEnglishState) -> StandardEnglishState:
    creator = get_domain_handler(state["domain"])


    max_refinements = 3
    current_iterations = state.get("iterations", 0)

    # Stop refinement if limit is reached
    if current_iterations >= max_refinements:
        return {
            **state,
            "status": QuestionStatus.Iterations.value,   # or GIVE_UP if you have that status
            "summary_refinement": "Refinement limit reached.",
        }


    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano", 
             messages=[
                {"role": "system", "content": creator.build_refinement_system_prompt()},
                {
                    "role": "user",
                    "content": creator.build_refinement_user_prompt(
                         sentence=state["sentence"],
                        editable_portion=state["editable_portion"],
                        question_type=state["question_type"],
                        feedback=state["validator_feedback"],
                        difficulty=state["difficulty"],
                        question_data=state["question_data"]
                    ),
                },
            ],
            response_format={"type": "json_object"}
        )


        span = mlflow.get_current_active_span()
        usage = response.usage
        if span:
            span.set_attribute("llm.model", response.model)
            span.set_attribute("llm.prompt_tokens", usage.prompt_tokens)
            span.set_attribute("llm.completion_tokens", usage.completion_tokens)
            span.set_attribute("llm.total_tokens", usage.total_tokens)
            span.set_attribute("llm.raw_output", response.choices[0].message.content)
        
        data = json.loads(response.choices[0].message.content)
        question_data = extract_question_data(data)
        
        return {
        **state,
        "sentence": data["sentence"],
        "editable_portion": data["editable_portion"],
        "question_data":question_data,
        "iterations": state.get("iterations", 0) + 1,
        "status": QuestionStatus.REFINED.value,
        "validator_feedback": None,
        "feedback":None,
        "summary_refinement": data.get("changes_made", ""),
    }
    except Exception as e:
        return {**state, "status": QuestionStatus.FAILED.value}

    










if __name__=="__main__":

    initial_state = {
        "question_type": "Words in Context",
        "difficulty": "Hard",
        "raw_passage":"While early cartographers relied on rudimentary instruments and speculative reports, modern mapmakers employ sophisticated technology to render geographical data with remarkable precision. This transition did not merely enhance the accuracy of maps; it fundamentally redefined the discipline. The advent of satellite imagery obviated the need for conjecture, supplanting guesswork with empirical measurement. Consequently, the practice of cartography evolved from an art imbued with imaginative interpretation to a science governed by verifiable data.",
        "feedback": "The passage does not contain a clear 'pivot word' with strong context clues that would support a high-quality 'Words in Context' question. While it uses some academic vocabulary, none of the terms are ambiguous or lend themselves to multiple plausible meanings within the given context."
       
    }

    out=refinement_node(initial_state)
    print(out)



