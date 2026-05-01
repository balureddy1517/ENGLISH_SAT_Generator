from src.workflow import main_workflow
from src.utils import save_to_excel,shuffle_mcq_excel,append_results_to_excel,final_state_to_row
from src.stateflow import QuestionStatus
import mlflow
import uuid

mlflow.set_tracking_uri("http://127.0.0.1:5001")
mlflow.set_experiment("SAT_Generation_Project")



def build_inputs():
    craft_and_structure_inputs = [
        {
            "domain": "Craft and Structure",
            "question_type": "Words in Context",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Craft and Structure",
            "question_type": "Text Structure",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Craft and Structure",
            "question_type": "Cross-Text",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ]

    information_and_ideas_inputs = [
        {
            "domain": "Information and Ideas",
            "question_type": "Central Idea",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Information and Ideas",
            "question_type": "Command of Evidence",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Information and Ideas",
            "question_type": "Inference",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Information and Ideas",
            "question_type": "Data Interpretation",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ]

    standard_english_inputs = [
        {
            "domain": "Standard English Conventions",
            "question_type": "Boundaries",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Standard English Conventions",
            "question_type": "Form, Structure, and Sense",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Standard English Conventions",
            "question_type": "Modifiers",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Standard English Conventions",
            "question_type": "Punctuation",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ]

    expression_of_ideas_inputs = [
        {
            "domain": "Expression of Ideas",
            "question_type": "Transitions",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Expression of Ideas",
            "question_type": "Organization",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Expression of Ideas",
            "question_type": "Concision and Precision",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ] + [
        {
            "domain": "Expression of Ideas",
            "question_type": "Rhetorical Synthesis",
            "difficulty": d,
            "iterations": 0,
            "status": "INITIALISED",
            "recent_items": []
        }
        for d in ["Easy", "Medium", "Hard"]
    ]

    return (
       
       craft_and_structure_inputs
        + information_and_ideas_inputs
    )
    

def run_sat_generation():
    all_inputs = build_inputs()
    app = main_workflow()
    results = []

    shared_recent_items = {
        "Craft and Structure": [],
        "Information and Ideas": [],
        "Standard English Conventions": [],
        "Expression of Ideas": [],
    }

    with mlflow.start_run(run_name="SAT_Generation_Full_Cycle"):
        for idx, inp in enumerate(all_inputs, start=1):
            domain = inp["domain"]
            inp["recent_items"] = shared_recent_items[domain]

            item_id = f"{domain[:3]}-{inp['question_type'][:3]}-{inp['difficulty']}-{idx}-{uuid.uuid4().hex[:8]}"
            inp["item_id"] = item_id

            print(f"Running: {domain} | {inp['question_type']} | {inp['difficulty']} | {item_id}")

            final_state = None

            with mlflow.start_span(name=f"SAT_Graph_Execution::{item_id}") as span:
                mlflow.update_current_trace(
                    tags={
                        "item_id": item_id,
                        "domain": inp["domain"],
                        "question_type": inp["question_type"]
                    },
                    metadata={
                        "input_index": str(idx),
                        "workflow": "SAT_Generation",
                    },
                )

                try:
                    for state in app.stream(inp, stream_mode="values"):
                        final_state = state

                    if final_state:
                        save_to_excel(final_state)
                        shared_recent_items[domain] = final_state.get(
                            "recent_items",
                            shared_recent_items[domain]
                        )

                        mlflow.update_current_trace(
                            tags={
                                "final_status": final_state.get("status", ""),
                                "final_question_type": final_state.get("question_type", ""),
                                "final_difficulty": final_state.get("difficulty", ""),
                            },
                            metadata={
                                "raw_passage_preview": (final_state.get("raw_passage", "") or "")[:160],
                                "sentence_preview": (final_state.get("sentence", "") or "")[:160],
                                "editable_portion": final_state.get("editable_portion", ""),
                            },
                        )

                        results.append(final_state)

                        print(
                            f"Finished: status={final_state.get('status')}, "
                            f"question_type={final_state.get('question_type')}, "
                            f"difficulty={final_state.get('difficulty')}"
                        )

                except Exception as e:
                    mlflow.update_current_trace(
                        tags={
                            "final_status": "FAILED",
                            "item_id": item_id,
                        },
                        metadata={
                            "error": str(e),
                        },
                    )

                    print(f"Error while processing {inp}: {e}")
                    results.append({
                        **inp,
                        "status": "FAILED",
                        "error": str(e)
                    })

    return results


if __name__=="__main__":

    results=run_sat_generation()
    # append_results_to_excel(results=results,file_path="Data/new_sat_generation_results.xlsx")
        


# #     inputs = {
# #     "domain": "Standard English Conventions",
# #     "question_type": "Boundaries",
# #     "difficulty": "Medium",
# #     "iterations": 0,
# #     "status": "INITIALISED"
# # }


#     app = main_workflow()
    

#     with mlflow.start_run(run_name="SAT_Generation_Full_Cycle"):
#         with mlflow.start_span(name="SAT_Graph_Execution") as root_span:
#                 final_state=app.invoke(inputs)
#                 #  print(final_state) 

    

#     #     inputs = {
# #     "domain": "Information and Ideas",   # "Information and Ideas"
# #     "question_type": "DATA_INTERPRETATION",
# #     "difficulty": "Hard",
# #     "iterations": 0,
# #     "status": QuestionStatus.INITIALISED.value
# # }
        
#     #     inputs = {
#     # "domain": "Expression of Ideas",
#     # "question_type": "Transitions",
#     # "difficulty": "Medium",

#     # "status": "INITIALISED",
#     # "iterations": 0
#     #     }
# #         inputs = {
# #     "domain": "Standard English Conventions",
# #     "question_type": "Boundaries",
# #     "difficulty": "Medium",
# #     "iterations": 0,
# #     "status": "INITIALISED"
# # }
        

#     #     inputs = {
#     #     "domain": "Craft and Structure",   #. "Craft and Structure"
#     #     "question_type": "Words in Context",
#     #     "difficulty": "Hard",
#     #     "iterations": 0,
#     #     "status": QuestionStatus.INITIALISED.value
#     # }



# # if __name__=="__main__":


# # #     inputs = {
# # #     "domain": "Expression of Ideas",
# # #     "question_type": "Transitions",
# # #     "difficulty": "Medium",

# # #     "status": "INITIALISED",
# # #     "iterations": 0,

   
# # # }

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
    

#     with mlflow.start_run(run_name="SAT_Generation_Full_Cycle"):
#         with mlflow.start_span(name="SAT_Graph_Execution") as root_span:
#                 final_state=app.invoke(inputs)
   
#     app = main_workflow()

 
#     for inp in all_inputs:
#         print(f"Running: {inp}")
        
#         final_state = None
#         for state in app.stream(inp, stream_mode="values"):
#             final_state = state
        
#         if final_state:
#             save_to_excel(final_state)

# #     # example usage
# #     #  input_file = "Data/sat_items.xlsx"
# #     #  output_file = "Data/shuffled_sat_items.xlsx"

# #     #  shuffle_mcq_excel(input_file, output_file)
# #     #  print(f"Shuffled file saved as: {output_file}")

    



# #     # inputs = {
# #     #     "domain": "Craft and Structure",   #. "Craft and Structure"
# #     #     "question_type": "Words in Context",
# #     #     "difficulty": "Easy",
# #     #     "iterations": 0,
# #     #     "status": QuestionStatus.INITIALISED.value
# #     # }

# # #     inputs = {
# # #     "domain": "Information and Ideas",   # "Information and Ideas"
# # #     "question_type": "DATA_INTERPRETATION",
# # #     "difficulty": "Hard",
# # #     "iterations": 0,
# # #     "status": QuestionStatus.INITIALISED.value
# # # }





    
   

       