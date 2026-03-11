from tools.auth import client
from src.stateflow import GraphState,QuestionStatus
from src.content_structure import Craft_and_Structure
import json
from src.utils import get_domain_handler



def question_generation_node(state: GraphState) -> dict: # Return a dict to merge
    creator = get_domain_handler(state["domain"])
    q_type = state.get("question_type")
    
    prompt = creator.build_question_prompt(
        passage=state["raw_passage"], 
        question_type=q_type 
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Or gpt-4.1
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        parsed_data = json.loads(response.choices[0].message.content)
        
        # VALIDATION FAILED
        if parsed_data.get("verdict") == "FAIL":
            return {
                "feedback": parsed_data,
                "status": QuestionStatus.PASSAGE_REDO.value, # "Passage_Redo"
                "iterations": state.get("iterations", 0) + 1
            }
        
        # VALIDATION PASSED
        return {
            "Question_info": parsed_data,
            "status": QuestionStatus.QUESTIONS_GENERATED.value, # "questions_generated"
            "feedback": None 
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"status": QuestionStatus.FAILED.value}

    
if __name__=="__main__":
    initial_state={
        'raw_passage': "Early cartographers often described their work as 'navigation by imagination,' since incomplete data forced them to rely on conjecture rather than certainty. Today, however, the term 'imagination' has all but disappeared from the mapmaker's lexicon. Instead, modern cartographers ground their representations in meticulously gathered, quantifiable information, leaving little room for the intuitive leaps that once characterized the field.",
                            'status': 'generated',
            'question_type': 'Words in Context'
    }
    out=question_generation_node(initial_state)

    print(out)
