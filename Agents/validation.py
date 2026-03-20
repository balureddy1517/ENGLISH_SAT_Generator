from tools.auth import client
from src.stateflow import GraphState,QuestionStatus,StandardEnglishState
from src.content_structure import Craft_and_Structure
import json
from src.utils import get_domain_handler

def validation_node(state: GraphState) -> dict:


    creator = get_domain_handler(state["domain"])
    # q_type = state.get("question_type")
    
    prompt = creator.build_validation_prompt(
        passage=state["raw_passage"], 
        question_type=state["question_type"] ,
        difficulty=state["difficulty"],
        question_data=state["question_data"]
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Or gpt-4.1
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        parsed_data = json.loads(response.choices[0].message.content)

        if parsed_data.get("verdict") == "FAIL":
            return {
                "validator_feedback": parsed_data,
                "feedback": parsed_data.get("summary_reason", ""),
                "status": QuestionStatus.FAILED_VALIDATION.value, # 
               
            }
        
        # VALIDATION PASSED
        return {
            "validator_feedback": parsed_data,
            "status": QuestionStatus.VALIDATED.value, # "questions_generated"
            "feedback": None 
        }

    except:
         return {**state, "status": QuestionStatus.FAILED.value}
    


def standard_english_validation_node(state: StandardEnglishState) -> StandardEnglishState:
    creator = get_domain_handler(state["domain"])

    prompt = creator.build_validation_prompt(
        sentence=state["sentence"],
        editable_portion=state["editable_portion"],
        question_data=state["question_data"],
        question_type=state["question_type"],
        difficulty=state["difficulty"]
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Or gpt-4.1
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        parsed_data = json.loads(response.choices[0].message.content)

        if parsed_data["verdict"] == "FAIL":

            return {
                **state,
                "validator_feedback": parsed_data,
                "feedback": parsed_data.get("summary_reason", ""),
                "status": QuestionStatus.FAILED_VALIDATION.value,
            }

        return {
            **state,
            "validator_feedback": parsed_data,
            "status": QuestionStatus.VALIDATED.value,
            "feedback": None 
        }

    except:
         return {**state, "status": QuestionStatus.FAILED.value}
    

    