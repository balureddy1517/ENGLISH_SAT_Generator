from tools.auth import client
from src.stateflow import GraphState,QuestionStatus,StandardEnglishState
# from src.content_structure import Craft_and_Structure,Expression_of_Ideas
from Topic_Content.craft_structure import Craft_and_Structure
import json
from src.utils import get_domain_handler,is_too_similar,update_recent_items,MAX_GENERATION_RETRIES
import time
import mlflow


@mlflow.trace
def passage_generation_node(state: GraphState) -> GraphState:
    creator = get_domain_handler(state["domain"])
    recent_items = state.get("recent_items", [])

    try:
        for attempt in range(MAX_GENERATION_RETRIES):
            response = client.chat.completions.create(
                model="gpt-5.4-nano",
                messages=[
                    {"role": "system", "content": creator.build_passage_system_prompt()},
                    {
                        "role": "user",
                        "content": creator.build_passage_user_prompt(
                            state["question_type"],
                            state["difficulty"]
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )

            span = mlflow.get_current_active_span()
            usage = response.usage
            if span and usage:
                span.set_attribute("llm.model", response.model)
                span.set_attribute("llm.prompt_tokens", usage.prompt_tokens)
                span.set_attribute("llm.completion_tokens", usage.completion_tokens)
                span.set_attribute("llm.total_tokens", usage.total_tokens)
                span.set_attribute("llm.raw_output", response.choices[0].message.content)

            raw_content = response.choices[0].message.content
            parsed_data = json.loads(raw_content)

            passage_text = parsed_data.get("passage", "").strip()
            question_type = parsed_data.get("type", state["question_type"])

            if not passage_text:
                continue

            if is_too_similar(passage_text, recent_items):
                print(f"[passage_generation_node] Similar passage detected. Retrying {attempt + 1}/{MAX_GENERATION_RETRIES}")
                continue

            return {
                **state,
                "raw_passage": passage_text,
                "question_type": question_type,
                "recent_items": update_recent_items(recent_items, passage_text),
                "status": QuestionStatus.GENERATED.value,
            }

        return {
            **state,
            "status": QuestionStatus.FAILED.value,
            "validator_feedback": "Failed to generate a sufficiently distinct passage after multiple attempts.",
        }

    except Exception as e:
        print(f"Error during passage generation: {e}")
        return {
            **state,
            "status": QuestionStatus.FAILED.value,
        }

@mlflow.trace
def standard_english_generation_node(state: StandardEnglishState) -> StandardEnglishState:
    creator = get_domain_handler(state["domain"])
    recent_items = state.get("recent_items", [])

    try:
        for attempt in range(MAX_GENERATION_RETRIES):
            response = client.chat.completions.create(
                model="gpt-5.4-nano",
                messages=[
                    {"role": "system", "content": creator.build_system_prompt()},
                    {
                        "role": "user",
                        "content": creator.build_user_prompt(
                            question_type=state["question_type"],
                            difficulty_level=state["difficulty"]
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )

            span = mlflow.get_current_active_span()
            usage = response.usage
            if span and usage:
                span.set_attribute("llm.model", response.model)
                span.set_attribute("llm.prompt_tokens", usage.prompt_tokens)
                span.set_attribute("llm.completion_tokens", usage.completion_tokens)
                span.set_attribute("llm.total_tokens", usage.total_tokens)
                span.set_attribute("llm.raw_output", response.choices[0].message.content)

            raw_content = response.choices[0].message.content
            parsed_data = json.loads(raw_content)

            sentence = parsed_data.get("sentence", "").strip()
            editable_portion = parsed_data.get("editable_portion", "").strip()

            if not sentence:
                continue

            if is_too_similar(sentence, recent_items):
                print(f"[standard_english_generation_node] Similar sentence detected. Retrying {attempt + 1}/{MAX_GENERATION_RETRIES}")
                continue

            return {
                **state,
                "sentence": sentence,
                "editable_portion": editable_portion,
                "recent_items": update_recent_items(recent_items, sentence),
                "status": QuestionStatus.GENERATED.value,
            }

        return {
            **state,
            "status": QuestionStatus.FAILED.value,
            "validator_feedback": "Failed to generate a sufficiently distinct sentence after multiple attempts.",
        }

    except Exception as e:
        print(f"Error during sentence generation: {e}")
        return {
            **state,
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
