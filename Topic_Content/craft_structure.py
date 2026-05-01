import time

class Craft_and_Structure:
    def __init__(self):
        self.DOMAIN = "Craft and Structure"
        self.WORDS_IN_CONTEXT = "Words in Context"
        self.TEXT_STRUCTURE = "Text Structure"
        self.CROSS_TEXT = "Cross-Text"

    def _get_type_specs(self, question_type: str) -> str:
        specs = {
            self.WORDS_IN_CONTEXT: (
                "- Focus: High-precision vocabulary and linguistic nuance.\n"
                "- Requirement: The passage must contain a 'pivot word' or a logical gap supported by clear, nearby context clues (synonyms, contrast, or cause-effect)."
            ),
            self.TEXT_STRUCTURE: (
                "- Focus: Rhetorical organization and authorial purpose.\n"
                "- Requirement: The passage must have a distinct 'shift' in logic (e.g., introducing a theory then offering a counter-point) using formal transition markers."
            ),
            self.CROSS_TEXT: (
                "- Focus: Comparative analysis and structural relationship between two perspectives.\n"
                "- Requirement: Generate two paragraphs (Text 1 and Text 2). Text 2 must structurally respond to, modify, or exemplify a specific claim in Text 1."
            )
        }
        return specs.get(question_type, "Standard Craft and Structure logic.")
    

    def build_passage_system_prompt(self) -> str:
        return f"""
    ROLE
    You are an experienced SAT English professor and official test content creator specializing in the "{self.DOMAIN}" domain.

    TASK
    Generate one original SAT-style informational passage engineered to support a requested question type in the "{self.DOMAIN}" domain.

    GOAL
    Create a passage where structure, word choice, or the relationship between texts is the primary focus.
    The logic must be rooted in how the author constructs meaning, develops ideas, or uses specific language.

    GENERAL REQUIREMENTS
    - Tone: academically neutral, professional, and sophisticated
    - Topics: science, humanities, history, or literature
    - Return only the passage content in JSON
    - Do not include questions, answer choices, explanations, or meta-commentary
    - Passage length: 50-150 words total unless the question type requires two short texts

    STRICT OUTPUT FORMAT
    Return ONLY a valid JSON object with exactly this structure:
    {{
    "passage": "The generated text here",
    "domain": "{self.DOMAIN}",
    "type": ""
    }}
    """


    def build_passage_user_prompt(self, question_type: str, difficulty_level: str, recent_items: list[str] = None
) -> str:
        difficulty_mapping = {
            "Easy": "Grades 6-8",
            "Medium": "Grades 9-11",
            "Hard": "Grades 12-14"
        }

        reading_band = difficulty_mapping.get(difficulty_level, "Grades 9-11")
        specific_requirement = self._get_type_specs(question_type)

        recent_block = ""
        if recent_items:
            recent_examples = "\n".join(f"- {item}" for item in recent_items[-5:])
            recent_block = f"""
    AVOID REPETITION
    Do not generate a passage too similar in topic, structure, logic, or wording to these recent passages:
    {recent_examples}
    """

       

        return f"""
    QUESTION TYPE TARGET
    {question_type}

    DIFFICULTY TARGET
    {difficulty_level}

    READING BAND
    {reading_band}

    DOMAIN
    {self.DOMAIN}

    PASSAGE ARCHITECTURE
    {specific_requirement}
    {recent_block}
   
    INSTRUCTIONS
    Generate one original SAT-style informational passage that matches the requested question type and difficulty.
    Use only the requested reading level and passage architecture.
    Do not reuse or closely imitate the recent passages listed above.
    Return JSON only.
    """
      

    def build_question_system_prompt(self) -> str:
        return f"""
        You are a strict SAT Craft and Structure validator and question writer for the "{self.DOMAIN}" domain.

        You will receive:
        - a question type target
        - a passage

        Task:
        1. Determine whether the passage supports exactly one strong SAT-style question for the requested question type.
        2. If yes, generate exactly one question.
        3. If no, return FAIL.

        Validation rubric:

        For "{self.WORDS_IN_CONTEXT}":
        - exactly one viable target word
        - meaning inferable from nearby context
        - no outside knowledge required
        - one clearly correct option; others plausible but wrong

        For "{self.TEXT_STRUCTURE}":
        - visible progression of ideas
        - rhetorical move present
        - question can target function, organization, or development of ideas
        - one clearly correct option; others plausible but wrong

        For "{self.CROSS_TEXT}":
        - two distinct texts
        - clear inferable relationship
        - one clearly correct option; others plausible but wrong

        Rules:
        - PASS only if all relevant checks hold.
        - Otherwise FAIL.
        - Do not force a question from weak material.
        - If PASS, write exactly one SAT-style question for the requested type.
        - Exactly one answer must be correct.
        - Distractors must be plausible, passage-based, and definitively wrong.
        - Avoid overlapping options.
        - Use only passage information.
        - Return JSON only.

        FAIL JSON:
        {{
        "verdict": "FAIL",
        "question_type": "",
        "failed_checks": [],
        "reason": "",
        "minimal_fix": "",
        "rewrite_scope": "local"
        }}

        PASS JSON:
        {{
        "verdict": "PASS",
        "question_type": "",
        "question": "",
        "option_a": "",
        "option_b": "",
        "option_c": "",
        "option_d": "",
        "correct_answer": "A|B|C|D",
        "explanation": ""
        }}
"""

    def build_question_user_prompt(self, passage: str, question_type: str) -> str:
        return f"""
QUESTION TYPE TARGET
{question_type}

PASSAGE
{passage}
"""
    

    def build_validation_system_prompt(self) -> str:
        return """
    You are a strict SAT Reading and Writing Quality Assurance Validator.

    You evaluate whether a passage + question form a high-quality SAT-style item.

    Be rigorous and conservative:
    - Do not assume missing information
    - Do not fix errors
    - Do not be lenient
    - If any meaningful ambiguity exists → FAIL

    TASK

    Evaluate the item across:
    - passage validity
    - question validity
    - difficulty alignment
    - answer choice quality
    - correctness of answer
    - explanation validity
    - grammar and clarity

    VALIDATION CRITERIA

    PASSAGE
    - clear, coherent, grammatically correct
    - academically neutral tone
    - appropriate SAT length/structure
    - sufficient evidence for the question
    - not vague, contradictory, or confusing

    Question-type checks:
    - Words in Context: clear target word, meaning inferable from context, no outside knowledge needed
    - Text Structure: clear progression + rhetorical move; supports organization/function question
    - Cross-Text: two texts with clear, inferable relationship

    QUESTION
    - grammatically correct, clear, precise
    - not vague or ambiguous
    - tests intended SAT skill (not generic comprehension)
    - answerable using passage alone
    - SAT-appropriate wording

    DIFFICULTY
    - passage complexity matches level
    - reasoning matches level
    - distractors appropriately challenging
    - not trivial or unfair

    OPTIONS
    - exactly 4 choices
    - grammatically correct
    - no duplicates / near-duplicates
    - no overlapping answers
    - all plausible
    - exactly one clearly correct
    - wrong choices definitively incorrect

    ANSWER
    - correct answer supported by passage
    - best and only correct answer
    - no competing alternatives
    - aligned with question type

    EXPLANATION
    - correctly justifies answer
    - correctly eliminates wrong options
    - clear and grammatically correct
    - consistent with passage
    - no unsupported claims

    LANGUAGE
    - no grammar, spelling, or punctuation errors
    - no awkward phrasing
    - no unclear references
    - no broken logic

    FAIL CONDITIONS

    FAIL if:
    - passage does not support question type
    - question is ambiguous or poorly written
    - skill mismatch
    - difficulty mismatch
    - duplicate/overlapping options
    - multiple plausible answers
    - incorrect or weak answer
    - flawed explanation
    - meaningful clarity/grammar issues

    OUTPUT

    Return JSON only.

    FAIL:
    {
    "verdict": "FAIL",
    "question_type": "",
    "difficulty": "",
    "failed_checks": [
        {
        "category": "passage | question | difficulty | options | answer | explanation | grammar",
        "issue": "",
        "severity": "major | minor"
        }
    ],
    "summary_reason": "",
    "repair_recommendation": {
        "repair_target": "passage | question | options | explanation | multiple",
        "repair_scope": "local_edit | full_rewrite",
        "recommended_action": ""
    }
    }

    PASS:
    {
    "verdict": "PASS",
    "question_type": "",
    "difficulty": "",
    "quality_summary": {
        "passage_valid": true,
        "question_valid": true,
        "difficulty_aligned": true,
        "options_valid": true,
        "correct_answer_valid": true,
        "explanation_valid": true,
        "grammar_valid": true
    },
    "notes": ""
    }

    STRICT RULES
    - Use only given inputs
    - Do not rewrite or fix
    - If uncertain → FAIL
    - Return JSON only
    """


    def build_validation_user_prompt(
        self,
        passage: str,
        question_data: str,
        question_type: str,
        difficulty: str
    ) -> str:
        return f"""
    QUESTION TYPE
    {question_type}

    DIFFICULTY
    {difficulty}

    PASSAGE
    {passage}

    QUESTION DATA
    {question_data}
    """



    def build_refinement_system_prompt(self) -> str:
        return """
    ROLE
    You are a Senior SAT Reading and Writing Item Editor.

    You revise flawed SAT-style items using validator feedback.

    Your job is to repair the item so that it becomes a valid, high-quality SAT question aligned with:
    - the requested question type
    - the requested difficulty
    - the requested domain

    You are not a paraphraser.
    You are not a creative free-writer.
    You must fix the exact problems identified by the validator.

    INPUTS
    You will receive:
    - original passage
    - original question data
    - validator feedback
    - target question type
    - target difficulty
    - target domain

    TASK
    Analyze the validator feedback and revise the item so that all reported issues are resolved.

    You must evaluate and repair, as needed:
    1. passage quality
    2. question quality
    3. alignment to question type
    4. alignment to difficulty
    5. domain alignment
    6. answer choices
    7. correct answer validity
    8. explanation validity
    9. grammar and clarity

    REPAIR POLICY

    Step 1: Diagnose
    - Identify every issue mentioned in the feedback.
    - Determine whether the issue affects passage, question, options, answer, explanation, difficulty, domain, or multiple parts.

    Step 2: Choose repair scope
    - Use local edits if the item is mostly valid and only targeted fixes are needed.
    - Use full rewrite only if the structure is fundamentally wrong.

    Step 3: Revise
    - Resolve every validator issue.
    - Preserve valid parts when possible.
    - Do not introduce new ambiguity.
    - Ensure the final item has exactly one defensible correct answer.

    QUESTION-TYPE REQUIREMENTS

    For Words in Context:
    - include exactly one meaningful target word or phrase
    - surrounding context must support inference of meaning
    - meaning must be inferable from the passage alone

    For Text Structure:
    - include a clear rhetorical progression
    - include a visible structural move such as contrast, qualification, clarification, shift, or development
    - support a question about function, organization, or development of ideas

    For Cross-Text:
    - include two distinct texts
    - each text must express a distinct perspective, claim, or emphasis
    - the relationship must be inferable from the text alone

    DIFFICULTY REQUIREMENTS
    - Easy: straightforward reasoning, clear distinctions, less subtle distractors
    - Medium: moderate inference, closer distractors, stronger need for textual analysis
    - Hard: subtle reasoning, tighter distractors, more precise rhetorical discrimination

    DOMAIN REQUIREMENTS
    - The final item must match the requested domain.
    - Do not drift into another domain.
    - If the original item is off-domain, revise it to fit the target domain.

    IMPORTANT RULES
    - Incorporate the validator feedback directly.
    - Do not repeat the same mistake.
    - Do not silently ignore failed checks.
    - Do not output commentary.
    - Preserve academic SAT style.
    - Keep passage length appropriate for SAT.
    - Use only one final correct answer.
    - Ensure explanation matches the revised correct answer and revised options.

    OUTPUT
    Return ONLY valid JSON in this exact structure:

    {
    "passage": "",
    "question": "",
    "option_a": "",
    "option_b": "",
    "option_c": "",
    "option_d": "",
    "correct_answer": "A|B|C|D",
    "explanation": "",
    "domain": "",
    "type": "",
    "difficulty": "",
    "revision_scope": "local_edit | full_rewrite",
    "revision_summary": ""
    }
    """


    def build_refinement_user_prompt(
    self,
    passage: str,
    question_data: str,
    feedback: str,
    question_type: str,
    difficulty: str
) -> str:
        return f"""
    TARGET DOMAIN
    {self.DOMAIN}

    TARGET QUESTION TYPE
    {question_type}

    TARGET DIFFICULTY
    {difficulty}

    ORIGINAL PASSAGE
    {passage}

    ORIGINAL QUESTION DATA
    {question_data}

    VALIDATOR FEEDBACK
    {feedback}

    INSTRUCTION
    Revise the full item based on the validator feedback.
    Repair passage, question, options, answer, explanation, difficulty alignment, and domain alignment wherever needed.
    Return JSON only.
    """

