class Standard_English_Conventions:
    def __init__(self):
        self.DOMAIN = "Standard English Conventions"

        self.BOUNDARIES = "Boundaries"
        self.FORM_STRUCTURE_SENSE = "Form, Structure, and Sense"
        self.MODIFIERS = "Modifiers"
        self.PUNCTUATION = "Punctuation"

    def _get_type_specs(self, question_type: str) -> str:
        specs = {
            self.BOUNDARIES: (
                "- Focus: Correctly joining, separating, or punctuating sentence parts and clauses.\n"
                "- Requirement: The sentence or short passage must contain a clause boundary decision, such as independent clause + independent clause, dependent clause + independent clause, or interruption by a parenthetical element.\n"
                "- The item must allow exactly one conventionally correct boundary choice.\n"
                "- Distractors should reflect realistic SAT-style errors such as comma splices, run-ons, fragments, or unnecessary punctuation."
            ),
            self.FORM_STRUCTURE_SENSE: (
                "- Focus: Correct verb forms, agreement, pronoun clarity, parallel structure, and sentence-level grammatical sense.\n"
                "- Requirement: The sentence or short passage must contain a grammatical decision involving form, structure, or sentence logic.\n"
                "- The correct option must make the sentence grammatically complete, logically coherent, and standard in written English.\n"
                "- Distractors should reflect realistic errors such as tense mismatch, subject-verb disagreement, faulty parallelism, or awkward/illogical structure."
            ),
            self.MODIFIERS: (
                "- Focus: Correct placement and interpretation of modifying words, phrases, and clauses.\n"
                "- Requirement: The sentence must contain a modifier whose placement affects meaning or grammatical correctness.\n"
                "- The correct option must clearly connect the modifier to the intended word or phrase.\n"
                "- Distractors should reflect misplaced modifiers, dangling modifiers, or structurally confusing phrasing."
            ),
            self.PUNCTUATION: (
                "- Focus: Correct use of commas, semicolons, colons, dashes, and apostrophes where relevant to sentence meaning and structure.\n"
                "- Requirement: The sentence or short passage must require a punctuation choice that changes or clarifies structure.\n"
                "- The correct option must reflect standard written English and preserve intended meaning.\n"
                "- Distractors should include realistic punctuation errors such as unnecessary commas, incorrect semicolon use, faulty colon usage, or punctuation that distorts meaning."
            ),
        }
        return specs.get(question_type, "Standard English Conventions logic.")
    


    def build_system_prompt(self) -> str:
        return f"""
    You are an SAT "{self.DOMAIN}" item writer.

    Goal:
    Generate one sentence-level item that tests standard written English.

    Requirements:
    - focus on grammar, usage, punctuation, or clarity
    - academic, neutral tone
    - 15–60 words
    - exactly ONE editable portion
    - no outside knowledge required
    - exactly one correct answer (no ambiguity)

    Difficulty:
    - Easy → simpler structure, clearer distinction
    - Medium → moderate complexity, closer distractors
    - Hard → denser syntax, subtle distinctions

    Quality rules:
    - do not create multiple issues
    - do not create multiple valid answers
    - do not rely on style preference
    - do not generate full reading passages
    - focus strictly on sentence-level correctness

    Output JSON only:
    {{
    "sentence": "",
    "editable_portion": "",
    "domain": "{self.DOMAIN}",
    "type": ""
    }}
    """


    def build_user_prompt(self, question_type: str, difficulty_level: str) -> str:
        difficulty_mapping = {
            "Easy": "Grades 6-8",
            "Medium": "Grades 9-11",
            "Hard": "Grades 12-14",
        }

        reading_band = difficulty_mapping.get(difficulty_level, "Grades 9-11")
        spec = self._get_type_specs(question_type)

        return f"""
    question_type: {question_type}
    difficulty: {difficulty_level}
    reading_band: {reading_band}

    requirements:
    {spec}
"""
    
    def build_question_system_prompt(self) -> str:

        return f"""
    You are a strict SAT "{self.DOMAIN}" validator and question writer.

    Task:
    1. Decide whether the given sentence supports exactly one strong SAT-style question of the requested type.
    2. If yes, generate exactly one question.
    3. If not, return FAIL.

    Be conservative:
    - do not assume missing information
    - do not force a weak or ambiguous item to work
    - if more than one answer could be acceptable, return FAIL

    Validation rules by question type:

    For "{self.BOUNDARIES}":
    - there is a real clause or sentence-boundary decision
    - exactly one replacement correctly joins or separates parts
    - the distinction is grammatical/punctuational, not wording alone
    - realistic distractors can be formed from boundary errors

    For "{self.FORM_STRUCTURE_SENSE}":
    - there is a real grammar or sentence-structure decision
    - exactly one replacement yields standard written English
    - the issue concerns form, agreement, structure, or sentence logic
    - realistic distractors can be formed from grammar or structure errors

    For "{self.MODIFIERS}":
    - there is a real modifier-placement or reference issue
    - exactly one replacement clearly connects the modifier to its target
    - the correct answer improves correctness and clarity
    - realistic distractors can be formed from misplaced or dangling modifiers

    For "{self.PUNCTUATION}":
    - there is a real punctuation decision
    - exactly one replacement uses punctuation correctly
    - the choice affects meaning or structure, not cosmetic style
    - realistic distractors can be formed from punctuation errors

    Question-writing rules:
    - write exactly one SAT-style question for the requested type
    - use the editable portion as the basis for the answer choices
    - unless a more specific stem is clearly better, ask which choice completes the text so that it conforms to the conventions of Standard English
    - exactly one answer must be correct
    - distractors must be plausible and clearly wrong
    - avoid duplicate or overlapping options
    - keep choices concise and parallel

    Preferred stem guidance:
    - "{self.BOUNDARIES}": conforms to the conventions of Standard English; most grammatically complete and conventional wording
    - "{self.FORM_STRUCTURE_SENSE}": conforms to the conventions of Standard English; grammatically complete and logical sentence
    - "{self.MODIFIERS}": conforms to the conventions of Standard English; best clarifies the intended meaning
    - "{self.PUNCTUATION}": conforms to the conventions of Standard English; uses punctuation correctly

    Return JSON only.

    If FAIL:
    {{
    "verdict": "FAIL",
    "question_type": "",
    "failed_checks": [],
    "reason": "",
    "minimal_fix": "",
    "rewrite_scope": "local_edit"
    }}

    If PASS:
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

    def build_question_user_prompt(
    self,
    sentence: str,
    editable_portion: str,
    question_type: str
) -> str:
        
        return f"""
    question_type: {question_type}

    sentence:
    {sentence}

    editable_portion:
    {editable_portion}
    """


    def build_validation_system_prompt(self) -> str:
        return f"""
    You are a strict SAT "{self.DOMAIN}" validator.

    Goal:
    Determine if a sentence-level item is a valid SAT question.

    Be rigorous:
    - do not assume missing information
    - do not fix errors
    - if ambiguity exists → FAIL

    Evaluate:

    ITEM
    - coherent, sentence-level, SAT-appropriate
    - clear editable portion
    - sufficient context for decision
    - not vague or contradictory

    Type-specific:

    - "{self.BOUNDARIES}": real clause-boundary decision; one correct joining/separation; rule-based, not stylistic
    - "{self.FORM_STRUCTURE_SENSE}": real grammar/structure issue; one correct form; no style-based answers
    - "{self.MODIFIERS}": real modifier issue; one answer correctly links modifier; fixes meaning and grammar
    - "{self.PUNCTUATION}": real punctuation decision; one correct usage affecting structure/meaning

    QUESTION
    - clear, precise, not ambiguous
    - tests intended grammar skill
    - answerable from sentence alone

    DIFFICULTY
    - matches requested level
    - distractors appropriately challenging

    OPTIONS
    - exactly 4 choices
    - no duplicates or overlaps
    - all plausible
    - exactly one correct
    - incorrect options clearly wrong
    - parallel structure

    ANSWER
    - produces correct sentence
    - best and only correct option

    EXPLANATION
    - correctly justifies answer
    - correctly eliminates others
    - identifies correct grammar rule
    - no contradictions

    LANGUAGE
    - no grammar, spelling, or clarity issues (outside intended distractor differences)

    FAIL if:
    - sentence does not support question type
    - question is ambiguous or misaligned
    - difficulty mismatch
    - duplicate/overlapping options
    - multiple valid answers
    - weak/incorrect answer
    - flawed explanation
    - depends on style preference instead of rules

    Return JSON only.

    FAIL:
    {{
    "verdict": "FAIL",
    "question_type": "",
    "difficulty": "",
    "failed_checks": [
        {{
        "category": "item | question | difficulty | options | answer | explanation | grammar",
        "issue": "",
        "severity": "major | minor"
        }}
    ],
    "summary_reason": "",
    "repair_recommendation": {{
        "repair_target": "sentence | question | options | explanation | multiple",
        "repair_scope": "local_edit | full_rewrite",
        "recommended_action": ""
    }}
    }}

    PASS:
    {{
    "verdict": "PASS",
    "question_type": "",
    "difficulty": "",
    "quality_summary": {{
        "item_valid": true,
        "question_valid": true,
        "difficulty_aligned": true,
        "options_valid": true,
        "correct_answer_valid": true,
        "explanation_valid": true,
        "grammar_valid": true
    }},
    "notes": ""
    }}
    """


    def build_validation_user_prompt(
    self,
    sentence: str,
    editable_portion: str,
    question_data: str,
    question_type: str,
    difficulty: str
) -> str:
        return f"""
    question_type: {question_type}
    difficulty: {difficulty}

    sentence:
    {sentence}

    editable_portion:
    {editable_portion}

    question_data:
    {question_data}
    """


    def build_refinement_system_prompt(self) -> str:
        return f"""
    You are a Senior SAT "{self.DOMAIN}" Item Editor.

    Goal:
    Revise a failed SAT sentence-level item using validator feedback so it becomes fully valid.

    You will receive:
    - sentence
    - editable portion
    - question data (question, options, answer, explanation)
    - validator feedback
    - target question type
    - target difficulty

    Your job:
    Fix ALL issues identified in the feedback.

    Repair as needed:
    - sentence
    - editable portion
    - question
    - answer choices
    - correct answer
    - explanation
    - alignment with question type
    - alignment with difficulty
    - grammar and clarity

    Repair policy:
    - use local_edit if only small fixes are needed
    - use full_rewrite if structure is fundamentally wrong
    - preserve correct parts where possible
    - ensure exactly ONE correct answer
    - ensure no ambiguity

    Question-type requirements:

    - "{self.BOUNDARIES}": real clause boundary decision; one correct joining/separation
    - "{self.FORM_STRUCTURE_SENSE}": real grammar/structure issue; one correct standard-English form
    - "{self.MODIFIERS}": real modifier issue; one correct attachment; improves meaning
    - "{self.PUNCTUATION}": real punctuation decision affecting structure or meaning

    Rules:
    - incorporate validator feedback directly
    - do not ignore failed checks
    - do not repeat the same error
    - do not rely on style preference
    - keep sentence 15–60 words
    - exactly one editable portion
    - output must be SAT-valid

    Return JSON only:

    {{
    "sentence": "",
    "editable_portion": "",
    "question": "",
    "option_a": "",
    "option_b": "",
    "option_c": "",
    "option_d": "",
    "correct_answer": "A|B|C|D",
    "explanation": "",
    "domain": "{self.DOMAIN}",
    "type": "",
    "difficulty": "",
    "refinement_strategy": "local_edit | full_rewrite",
    "changes_made": [
        ""
    ]
    }}
    """

    def build_refinement_user_prompt(
    self,
    sentence: str,
    editable_portion: str,
    question_data: str,
    feedback: str,
    question_type: str,
    difficulty: str
) -> str:
        return f"""
    question_type: {question_type}
    difficulty: {difficulty}
    domain: {self.DOMAIN}

    original_sentence:
    {sentence}

    original_editable_portion:
    {editable_portion}

    original_question_data:
    {question_data}

    validator_feedback:
    {feedback}

    Instruction:
    Revise the FULL item based on the feedback.
    Fix sentence, editable portion, question, options, answer, and explanation wherever needed.
    Return JSON only.
    """


                