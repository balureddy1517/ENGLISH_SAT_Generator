from tools.auth import client
from src.stateflow import GraphState,QuestionStatus,StandardEnglishState
# from src.content_structure import Craft_and_Structure
from Topic_Content.craft_structure import Craft_and_Structure
import json
from src.utils import get_domain_handler
import mlflow


@mlflow.trace
def question_generation_node(state: GraphState) -> dict: # Return a dict to merge
    creator = get_domain_handler(state["domain"])
    q_type = state.get("question_type")
    
    # prompt = creator.build_question_prompt(
    #     passage=state["raw_passage"], 
    #     question_type=q_type 
    # )
    
    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano", # Or gpt-4.1
            messages=[
                {"role": "system", "content": creator.build_question_system_prompt()},
    {"role": "user", "content": creator.build_question_user_prompt( passage=state["raw_passage"], question_type=q_type  )}
               
            ],
           
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        span = mlflow.get_current_active_span()
        usage = response.usage
        if span:
            span.set_attribute("llm.model", response.model)
            span.set_attribute("llm.prompt_tokens", usage.prompt_tokens)
            span.set_attribute("llm.completion_tokens", usage.completion_tokens)
            span.set_attribute("llm.total_tokens", usage.total_tokens)
            
            # 2. LOG THE RAW OUTPUT FOR AUDIT
            # This is safer than logging to a file because it stays inside the trace
            span.set_attribute("llm.raw_output", response.choices[0].message.content)
        
        parsed_data = json.loads(response.choices[0].message.content)
        
        # VALIDATION FAILED
        if parsed_data.get("verdict") == "FAIL":
            return {
                "feedback": parsed_data,
                "status": QuestionStatus.PASSAGE_REDO.value, # "Passage_Redo"
                # "iterations": state.get("iterations", 0) + 1
            }
        
        # VALIDATION PASSED
        return {
            "question_data": parsed_data,
            "status": QuestionStatus.QUESTIONS_GENERATED.value, # "questions_generated"
            "feedback": None 
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"status": QuestionStatus.FAILED.value}
    


@mlflow.trace
def standard_english_question_generation_node(state: StandardEnglishState) -> StandardEnglishState:
    creator =  get_domain_handler(state["domain"])

    # prompt = creator.build_question_prompt(
    #     sentence=state["sentence"],
    #     editable_portion=state["editable_portion"],
    #     question_type=state["question_type"]
    # )

    try:  #build_sentence_english_question_system_prompt
        response = client.chat.completions.create(
            model="gpt-5.4-nano", # Or gpt-4.1
           messages=[
                {"role": "system", "content": creator.build_question_system_prompt()},
    {"role": "user", "content": creator.build_question_user_prompt( sentence=state["sentence"],
        editable_portion=state["editable_portion"],
        question_type=state["question_type"] )}
               
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        span = mlflow.get_current_active_span()
        usage = response.usage
        if span:
            span.set_attribute("llm.model", response.model)
            span.set_attribute("llm.prompt_tokens", usage.prompt_tokens)
            span.set_attribute("llm.completion_tokens", usage.completion_tokens)
            span.set_attribute("llm.total_tokens", usage.total_tokens)
            
            # 2. LOG THE RAW OUTPUT FOR AUDIT
            # This is safer than logging to a file because it stays inside the trace
            span.set_attribute("llm.raw_output", response.choices[0].message.content)
        
        parsed_data = json.loads(response.choices[0].message.content)
        
        # VALIDATION FAILED
        if parsed_data.get("verdict") == "FAIL":
            return {
                "feedback": parsed_data,
                "status": QuestionStatus.PASSAGE_REDO.value, # "Passage_Redo"
                # "iterations": state.get("iterations", 0) + 1
            }
        
        # VALIDATION PASSED
        return {
            "question_data": parsed_data,
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
