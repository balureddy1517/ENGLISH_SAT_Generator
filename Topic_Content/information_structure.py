class Information_and_Ideas:
    def __init__(self):
        self.DOMAIN = "Information and Ideas"

        self.CENTRAL_IDEA = "Central Idea"
        self.COMMAND_OF_EVIDENCE = "Command of Evidence"
        self.INFERENCE = "Inference"
        self.DATA_INTERPRETATION = "Data Interpretation"

    def _get_type_specs(self, question_type: str) -> str:
        specs = {
            self.CENTRAL_IDEA: (
                "- Focus: Identifying the main idea, primary claim, or central purpose of the passage.\n"
                "- Requirement: The passage must present one unifying idea supported by two or more relevant details.\n"
                "- The correct main idea must require synthesizing multiple parts of the passage, not selecting one isolated sentence.\n"
                "- Avoid passages where the answer is stated too directly in one sentence."
            ),
            self.COMMAND_OF_EVIDENCE: (
                "- Focus: Determining which textual detail best supports a claim, conclusion, or answer.\n"
                "- Requirement: The passage must include a claim, conclusion, or answerable idea that requires support.\n"
                "- The passage must contain multiple plausible evidence candidates.\n"
                "- One piece of evidence must clearly be the strongest and most direct support, while other details may be related but weaker, incomplete, or less relevant.\n"
                "- Avoid passages where only one sentence is even remotely relevant."
            ),
            self.INFERENCE: (
                "- Focus: Drawing a logical conclusion that is strongly supported by the passage but not directly stated.\n"
                "- Requirement: The passage must contain two or more details that, when combined, support one strong inference.\n"
                "- The correct inference must go beyond paraphrase but remain tightly grounded in the passage.\n"
                "- Avoid passages where the answer is explicitly stated or depends on outside knowledge."
            ),
            self.DATA_INTERPRETATION: (
                "- Focus: Interpreting text-only quantitative information or reported results.\n"
                "- Requirement: The passage must include concrete data stated in words, such as quantities, percentages, comparisons, changes over time, or experimental findings.\n"
                "- The question must require interpreting what the text-described data shows, suggests, or supports.\n"
                "- Avoid vague references to research or results without enough specific numerical or comparative information."
            ),
        }
        return specs.get(question_type, "Standard Information and Ideas reasoning.")
    

    def build_passage_system_prompt(self) -> str:
        return f"""
    You are an SAT Reading passage writer for the "{self.DOMAIN}" domain.

    Goal:
    Generate one passage that supports exactly ONE question of a specified type.

    Requirements:
    - academic, neutral, precise tone
    - topics: science, social science, history, or literature
    - 50–150 words
    - no questions, options, or explanations
    - passage must clearly support ONE reasoning skill

    Difficulty:
    - Easy → explicit support, simpler reasoning
    - Medium → moderate abstraction, some synthesis
    - Hard → denser ideas, subtle reasoning

    Quality rules:
    - no vague or incomplete passages
    - no reliance on outside knowledge
    - avoid passages supporting multiple unrelated question types
    - avoid answers obvious from a single sentence (unless required)
    - for data interpretation: include text-based numerical/comparative data only

    Output JSON only:
    {{
    "passage": "",
    "domain": "{self.DOMAIN}",
    "type": ""
    }}
    """

    def build_passage_user_prompt(self, question_type: str, difficulty_level: str) -> str:
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
    You are a strict SAT "{self.DOMAIN}" passage validator and question writer.

    Task:
    1. Decide whether the passage supports exactly one strong SAT-style question of the requested type.
    2. If yes, generate exactly one question.
    3. If not, return FAIL.

    Be conservative:
    - do not assume missing information
    - do not force a weak passage to work
    - if meaningful ambiguity exists, return FAIL

    Validation rules by question type:

    For "{self.CENTRAL_IDEA}":
    - one clear main idea or primary claim
    - multiple details support it
    - correct answer requires synthesis, not one isolated sentence
    - distractors can be too broad, too narrow, or secondary

    For "{self.COMMAND_OF_EVIDENCE}":
    - a claim, conclusion, or answerable idea requires support
    - multiple candidate details exist
    - one detail is clearly the strongest support
    - distractors can be related but weaker or less direct

    For "{self.INFERENCE}":
    - supports a conclusion not directly stated
    - requires combining two or more details
    - correct answer goes beyond paraphrase but stays fully supported
    - distractors can be overstatements, unsupported assumptions, or explicit restatements

    For "{self.DATA_INTERPRETATION}":
    - includes concrete text-based data, results, comparisons, or numerical findings
    - supports a question about what the data shows, suggests, or supports
    - one answer is best supported by the data
    - distractors can be misreadings, overgeneralizations, or unsupported extrapolations

    Question-writing rules:
    - write exactly one SAT-style question for the requested type
    - do not write a generic comprehension question unless the skill inherently requires it
    - exactly one answer must be correct
    - distractors must be plausible, passage-based, and definitively wrong
    - avoid duplicate or overlapping options
    - use only information from the passage

    Preferred stems:
    - Central Idea: main idea, central claim, main purpose
    - Command of Evidence: best supports the claim/conclusion
    - Inference: best supported inference, most strongly suggests
    - Data Interpretation: what the data shows, suggests, or best supports

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



    def build_question_user_prompt(self, passage: str, question_type: str) -> str:
        return f"""
    question_type: {question_type}

    passage:
    {passage}
    """



    def build_validation_system_prompt(self) -> str:
        return f"""
    You are a strict SAT Reading and Writing validator.

    Goal:
    Decide if a passage + question form a valid SAT item.

    Be rigorous:
    - do not assume missing info
    - do not fix errors
    - if ambiguity exists → FAIL

    Evaluate:

    PASSAGE
    - clear, coherent, grammatically correct
    - academic tone
    - sufficient evidence for the question
    - not vague or contradictory

    Type-specific:
    - "{self.CENTRAL_IDEA}": one main idea, supported by multiple details, requires synthesis
    - "{self.COMMAND_OF_EVIDENCE}": claim/conclusion present, multiple evidence options, one strongest
    - "{self.INFERENCE}": conclusion not stated directly, requires combining clues, not paraphrase
    - "{self.DATA_INTERPRETATION}": includes concrete text-based data, supports interpretation

    QUESTION
    - clear, precise, not ambiguous
    - tests intended skill (not generic comprehension)
    - answerable using passage only

    DIFFICULTY
    - passage + reasoning match difficulty
    - distractors appropriate
    - not trivial or unfair

    OPTIONS
    - exactly 4 choices
    - no duplicates or overlaps
    - all plausible
    - exactly one correct
    - incorrect options clearly wrong

    ANSWER
    - correct answer supported by passage
    - best and only correct option

    EXPLANATION
    - correctly justifies answer
    - correctly eliminates others
    - no contradictions or unsupported claims

    LANGUAGE
    - no grammar, spelling, or clarity issues

    FAIL if:
    - passage doesn’t support question type
    - question is vague or misaligned
    - difficulty mismatch
    - duplicate/overlapping options
    - multiple valid answers
    - weak/incorrect answer
    - flawed explanation
    - clarity/grammar issues

    Return JSON only.

    FAIL:
    {{
    "verdict": "FAIL",
    "question_type": "",
    "difficulty": "",
    "failed_checks": [
        {{
        "category": "passage | question | difficulty | options | answer | explanation | grammar",
        "issue": "",
        "severity": "major | minor"
        }}
    ],
    "summary_reason": "",
    "repair_recommendation": {{
        "repair_target": "passage | question | options | explanation | multiple",
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
        "passage_valid": true,
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
    passage: str,
    question_data: str,
    question_type: str,
    difficulty: str
) -> str:
        return f"""
    question_type: {question_type}
    difficulty: {difficulty}

    passage:
    {passage}

    question_data:
    {question_data}
    """


    def build_refinement_system_prompt(self) -> str:
        return f"""
    You are a Senior SAT "{self.DOMAIN}" Item Editor.

    Goal:
    Revise a failed SAT item using validator feedback so the final item is valid, clear, and aligned with the requested question type, difficulty, and domain.

    You will receive:
    - original passage
    - original question data
    - validator feedback
    - target question type
    - target difficulty

    Your job:
    - fix every issue identified in the feedback
    - revise only what is necessary when local edits are enough
    - do a full rewrite only if the item is fundamentally flawed

    Check and repair as needed:
    - passage quality
    - question quality
    - question type alignment
    - difficulty alignment
    - answer choice quality
    - correct answer validity
    - explanation validity
    - grammar and clarity
    - domain alignment

    Question-type requirements:
    - "{self.CENTRAL_IDEA}": one clear main idea, supported by multiple details, requiring synthesis
    - "{self.COMMAND_OF_EVIDENCE}": claim/conclusion needing support, multiple evidence candidates, one strongest support
    - "{self.INFERENCE}": conclusion not directly stated, requiring multiple clues, no outside knowledge
    - "{self.DATA_INTERPRETATION}": concrete text-only data/results/comparisons, sufficient for interpretation, no visual chart/table references

    Difficulty requirements:
    - Easy: clearer support, simpler reasoning, more separated distractors
    - Medium: moderate synthesis/inference, closer distractors
    - Hard: denser reasoning, subtler distinctions, tighter distractors

    Rules:
    - incorporate validator feedback directly
    - do not ignore failed checks
    - do not repeat the same flaw
    - preserve SAT style and academic tone
    - keep passage length appropriate (50–150 words unless item structure requires otherwise)
    - ensure exactly one correct answer
    - ensure the explanation matches the revised answer and revised options
    - return JSON only

    Output JSON:
    {{
    "passage": "",
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
    passage: str,
    question_data: str,
    feedback: str,
    question_type: str,
    difficulty: str
) -> str:
        return f"""
    question_type: {question_type}
    difficulty: {difficulty}
    domain: {self.DOMAIN}

    original_passage:
    {passage}

    original_question_data:
    {question_data}

    validator_feedback:
    {feedback}

    Instruction:
    Revise the full item based on the validator feedback.
    Repair passage, question, options, answer, explanation, and alignment wherever needed.
    Return JSON only.
    """


                
    