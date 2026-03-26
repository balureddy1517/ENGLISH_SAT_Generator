from src.workflow import main_workflow
from src.utils import save_to_excel,shuffle_mcq_excel
from src.stateflow import QuestionStatus
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("SAT_Generation_Project")

if __name__=="__main__":
        


    inputs = {
    "domain": "Standard English Conventions",
    "question_type": "Boundaries",
    "difficulty": "Medium",
    "iterations": 0,
    "status": "INITIALISED"
}


    app = main_workflow()
    

    with mlflow.start_run(run_name="SAT_Generation_Full_Cycle"):
        with mlflow.start_span(name="SAT_Graph_Execution") as root_span:
                final_state=app.invoke(inputs)
                #  print(final_state) 

    

    #     inputs = {
#     "domain": "Information and Ideas",   # "Information and Ideas"
#     "question_type": "DATA_INTERPRETATION",
#     "difficulty": "Hard",
#     "iterations": 0,
#     "status": QuestionStatus.INITIALISED.value
# }
        
    #     inputs = {
    # "domain": "Expression of Ideas",
    # "question_type": "Transitions",
    # "difficulty": "Medium",

    # "status": "INITIALISED",
    # "iterations": 0
    #     }
#         inputs = {
#     "domain": "Standard English Conventions",
#     "question_type": "Boundaries",
#     "difficulty": "Medium",
#     "iterations": 0,
#     "status": "INITIALISED"
# }
        

    #     inputs = {
    #     "domain": "Craft and Structure",   #. "Craft and Structure"
    #     "question_type": "Words in Context",
    #     "difficulty": "Hard",
    #     "iterations": 0,
    #     "status": QuestionStatus.INITIALISED.value
    # }



# if __name__=="__main__":


# #     inputs = {
# #     "domain": "Expression of Ideas",
# #     "question_type": "Transitions",
# #     "difficulty": "Medium",

# #     "status": "INITIALISED",
# #     "iterations": 0,

   
# # }

#      craft_and_structure_inputs = [
#     {"domain": "Craft and Structure", "question_type": "Words in Context", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Craft and Structure", "question_type": "Text Structure", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ] + [
#     {"domain": "Craft and Structure", "question_type": "Cross-Text", "difficulty": d, "iterations": 0, "status": "INITIALISED"}
#     for d in ["Easy", "Medium", "Hard"]
# ]
#      information_and_ideas_inputs = [
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
#      standard_english_inputs = [
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
    
#      expression_of_ideas_inputs = [
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
#      all_inputs = (
#     craft_and_structure_inputs +
#     information_and_ideas_inputs +
#     standard_english_inputs +
#     expression_of_ideas_inputs
# )
   
#      app = main_workflow()

 
#      for inp in all_inputs:
#         print(f"Running: {inp}")
        
#         final_state = None
#         for state in app.stream(inp, stream_mode="values"):
#             final_state = state
        
#         if final_state:
#             save_to_excel(final_state)

#     # example usage
#     #  input_file = "Data/sat_items.xlsx"
#     #  output_file = "Data/shuffled_sat_items.xlsx"

#     #  shuffle_mcq_excel(input_file, output_file)
#     #  print(f"Shuffled file saved as: {output_file}")

    



#     # inputs = {
#     #     "domain": "Craft and Structure",   #. "Craft and Structure"
#     #     "question_type": "Words in Context",
#     #     "difficulty": "Easy",
#     #     "iterations": 0,
#     #     "status": QuestionStatus.INITIALISED.value
#     # }

# #     inputs = {
# #     "domain": "Information and Ideas",   # "Information and Ideas"
# #     "question_type": "DATA_INTERPRETATION",
# #     "difficulty": "Hard",
# #     "iterations": 0,
# #     "status": QuestionStatus.INITIALISED.value
# # }





    
   

       