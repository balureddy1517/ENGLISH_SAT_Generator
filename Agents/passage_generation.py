from tools.auth import client
from src.stateflow import GraphState,QuestionStatus
from src.content_structure import Craft_and_Structure
import json
from src.utils import get_domain_handler


def passage_generation_node(state: GraphState) -> GraphState:

    creator = get_domain_handler(state["domain"])
    prompt = creator.build_prompt(state["question_type"], state["difficulty"])
    try:
        response = client.chat.completions.create(
            model="gpt-4.1", 
            messages=[
                {
                    "role": "system", 
                    "content": prompt
                },
               
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
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
