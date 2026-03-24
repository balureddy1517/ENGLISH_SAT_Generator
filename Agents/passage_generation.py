from tools.auth import client
from src.stateflow import GraphState,QuestionStatus,StandardEnglishState
from src.content_structure import Craft_and_Structure,Expression_of_Ideas
import json
from src.utils import get_domain_handler
import time
import mlflow


@mlflow.trace
def passage_generation_node(state: GraphState) -> GraphState:

    creator = get_domain_handler(state["domain"])
    prompt = creator.build_prompt(state["question_type"], state["difficulty"])
    timestamp = int(time.time())
    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano", 
            messages=[
                {
                    "role": "system", 
                    "content": prompt
                },
               
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
        
        # response.choices[0].message.content is a STRING that looks like JSON
        raw_content = response.choices[0].message.content
        parsed_data = json.loads(raw_content) # Convert string to python dict
        
        # Extract the passage from the JSON key we defined in the prompt
        passage_text = parsed_data.get("passage", "")
        question_type=parsed_data.get("type","")
        
        return {
            **state,             # This now works because 'state' is a dict
            "raw_passage": passage_text,
            "question_type":question_type,
            "status": QuestionStatus.GENERATED.value 
        }
        
    except Exception as e:
        print(f"Error during passage generation: {e}")
        return {
            **state, # Keep existing state
            "status": QuestionStatus.FAILED.value,
        }
    

@mlflow.trace
def standard_english_generation_node(state: StandardEnglishState) -> StandardEnglishState:
    creator = get_domain_handler(state["domain"])

    prompt = creator.build_prompt(
        question_type=state["question_type"],
        difficulty_level=state["difficulty"]
    )

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano", 
            messages=[
                {
                    "role": "system", 
                    "content": prompt
                },
               
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
            
        # response.choices[0].message.content is a STRING that looks like JSON
        raw_content = response.choices[0].message.content
        parsed_data = json.loads(raw_content) # Convert string to python dict
        
        # Extract the passage from the JSON key we defined in the prompt
        sentence = parsed_data.get("sentence", "")
        editable_portion=parsed_data.get("editable_portion","")
        
        return {
        **state,
        "sentence": sentence,
        "editable_portion": editable_portion,
        "status": QuestionStatus.GENERATED.value 
    }
        
    except Exception as e:
        print(f"Error during passage generation: {e}")
        return {
            **state, # Keep existing state
            "status": QuestionStatus.FAILED.value,
        }

if __name__=="__main__":
    
    creator = Craft_and_Structure()
    final_prompt = creator.build_prompt("Words in Context", "Hard")
    # print(final_prompt)
    # initial_state = {"raw_passage": "", "status": None}
    initial_state={
        'raw_passage': 'The historian’s account of the treaty negotiations, while ostensibly impartial, subtly privileges the perspectives of the dominant parties. By consistently referring to the less powerful nations’ objections as ‘supplementary remarks’ rather than substantive critiques, the narrative marginalizes their agency. This linguistic choice is not incidental; rather, it reflects an underlying assumption about the hierarchy of diplomatic influence, shaping the reader’s perception of which actors deserve attention and legitimacy.'

    }
    out = passage_generation_node(initial_state,prompt=final_prompt)
    # print(out["raw_passage"])
    print(out)
