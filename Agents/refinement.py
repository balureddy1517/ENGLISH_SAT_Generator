from tools.auth import client
from src.stateflow import GraphState,QuestionStatus,StandardEnglishState
from src.content_structure import Craft_and_Structure
import json
from src.utils import get_domain_handler
import mlflow

@mlflow.trace
def refinement_node(state: GraphState) -> GraphState:
    creator = get_domain_handler(state["domain"])
    
    # Generate the prompt using the existing passage and the feedback captured earlier
    prompt = creator.build_refinement_prompt(
        passage=state["raw_passage"],
        question_type=state["question_type"],
        feedback=state["feedback"],
        difficulty=state.get("difficulty", "Medium")
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano", 
            messages=[{"role": "system", "content": prompt}],
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
        
        return {
            **state,
            "raw_passage": data["passage"],
            "iterations": state.get("iterations", 0) + 1,
            "status": QuestionStatus.REFINED.value, # Set to a status that routes back to the Question Agent
            "feedback": None      # Clear feedback once addressed
        }
    except Exception as e:
        return {**state, "status": QuestionStatus.FAILED.value}
    


@mlflow.trace
def standard_english_refinement_node(state: StandardEnglishState) -> StandardEnglishState:
    creator = get_domain_handler(state["domain"])

    prompt = creator.build_refinement_prompt(
        sentence=state["sentence"],
        editable_portion=state["editable_portion"],
        question_type=state["question_type"],
        feedback=state["validator_feedback"],
        difficulty=state["difficulty"]
    )

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano", 
            messages=[{"role": "system", "content": prompt}],
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
        
        return {
        **state,
        "sentence": data["sentence"],
        "editable_portion": data["editable_portion"],
        "iterations": state.get("iterations", 0) + 1,
        "status": QuestionStatus.REFINED.value,
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



