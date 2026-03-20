from src.content_structure import Craft_and_Structure,Information_and_Ideas,Standard_English_Conventions,Expression_of_Ideas
from src.stateflow import GraphState,StandardEnglishState
from openpyxl import Workbook, load_workbook
from pathlib import Path
import pandas as pd
import os
import random
import shutil


MAX_REVISIONS=3

def get_domain_handler(domain: str):
    if domain == "Craft and Structure":
        return Craft_and_Structure()
    elif domain == "Information and Ideas":
        return Information_and_Ideas()
    elif domain == "Standard English Conventions":
        return Standard_English_Conventions()
    elif domain == "Expression of Ideas":
        return Expression_of_Ideas()
    else:
        raise ValueError(f"Unsupported domain: {domain}")
    


def route_domain(state: GraphState) -> str:
    if state["domain"] in {"Craft and Structure", "Information and Ideas"}:
        return "passage_branch"
    elif state["domain"] in {"Standard English Conventions","Expression of Ideas"}:
        return "sentence_english_branch"
    else:
        raise ValueError(f"Unsupported domain: {state['domain']}")
    

def route_passage_after_validation(state: GraphState) -> str:
    if state["status"] == "validated":
        return "done"
    
    if state["status"]=="failed_validation" or state["status"]=="Failed":
        return "fail"

    if state.get("iterations", 0) >= MAX_REVISIONS:
        return "give_up"

    return "refine"


def route_standard_english_after_validation(state: StandardEnglishState) -> str:
    if state["status"] == "validated":
        return "done"
    
    if state["status"]=="failed_validation" or state["status"]=="Failed":
        return "fail"


    if state.get("iterations", 0) >= MAX_REVISIONS:
        return "give_up"

    return "refine"



def save_to_excel(state, file_path="Data/sat_items.xlsx"):

    q = state.get("question_data", {}) or {}

    row = {
        "domain": state.get("domain", ""),
        "question_type": state.get("question_type", ""),
        "difficulty": state.get("difficulty", ""),

        "source_text": state.get("sentence", "") or state.get("raw_passage", ""),
        "sentence": state.get("sentence", ""),
        "editable_portion": state.get("editable_portion", ""),

        "question": q.get("question", ""),
        "option_a": q.get("option_a", ""),
        "option_b": q.get("option_b", ""),
        "option_c": q.get("option_c", ""),
        "option_d": q.get("option_d", ""),
        "correct_answer": q.get("correct_answer", ""),
        "explanation": q.get("explanation", "")
    }

    df = pd.DataFrame([row])

    if os.path.exists(file_path):
        df_existing = pd.read_excel(file_path)
        df = pd.concat([df_existing, df], ignore_index=True)

    df.to_excel(file_path, index=False)




def shuffle_mcq_excel(input_file, output_file):
    # 1. make a copy of the original file
    shutil.copy(input_file, output_file)

    # 2. read the copied file
    df = pd.read_excel(output_file)

    # expected columns
    option_cols = ["option_a", "option_b", "option_c", "option_d"]

    for i, row in df.iterrows():
        # get original correct answer letter
        correct_letter = str(row["correct_answer"]).strip().upper()

        # map letter -> column
        letter_to_col = {
            "A": "option_a",
            "B": "option_b",
            "C": "option_c",
            "D": "option_d"
        }

        if correct_letter not in letter_to_col:
            continue

        # original correct option text
        correct_text = row[letter_to_col[correct_letter]]

        # collect options
        options = [
            row["option_a"],
            row["option_b"],
            row["option_c"],
            row["option_d"]
        ]

        # shuffle
        random.shuffle(options)

        # write shuffled options back
        df.at[i, "option_a"] = options[0]
        df.at[i, "option_b"] = options[1]
        df.at[i, "option_c"] = options[2]
        df.at[i, "option_d"] = options[3]

        # update correct answer
        if options[0] == correct_text:
            df.at[i, "correct_answer"] = "A"
        elif options[1] == correct_text:
            df.at[i, "correct_answer"] = "B"
        elif options[2] == correct_text:
            df.at[i, "correct_answer"] = "C"
        elif options[3] == correct_text:
            df.at[i, "correct_answer"] = "D"

    # 3. save back to copied file
    df.to_excel(output_file, index=False)


