from tools.auth import client
from src.stateflow import GraphState,QuestionStatus
from src.content_structure import Craft_and_Structure
import json


def validation_node(state: GraphState) -> dict:


    creator = Craft_and_Structure()
    q_type = state.get("question_type")
    
    prompt = creator.build_validation_prompt(
        passage=state["raw_passage"], 
        question_type=state["question_type"] ,
        difficulty=state["difficulty"],
        question_data=state["Question_info"]
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