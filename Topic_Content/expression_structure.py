
class Expression_of_Ideas:
    def __init__(self):
        self.DOMAIN = "Expression of Ideas"

        self.TRANSITIONS = "Transitions"
        self.RHETORICAL_SYNTHESIS = "Rhetorical Synthesis"
        self.ORGANIZATION = "Organization"
        self.CONCISION_AND_PRECISION = "Concision and Precision"

    def _get_type_specs(self, question_type: str) -> str:
        specs = {
            self.TRANSITIONS: (
                "- Focus: Selecting the transition that best expresses the logical relationship between ideas.\n"
                "- Requirement: The sentence or short passage must contain two ideas whose relationship is clear from context, such as contrast, continuation, cause-effect, example, or conclusion.\n"
                "- Exactly one transition choice must correctly express that relationship.\n"
                "- Distractors should use plausible but incorrect logical relationships."
            ),
            self.RHETORICAL_SYNTHESIS: (
                "- Focus: Choosing the sentence that best accomplishes a specific rhetorical goal using provided notes or context.\n"
                "- Requirement: The item must establish a writing goal such as introducing a topic, emphasizing a contrast, summarizing relevant findings, or highlighting a key detail.\n"
                "- Exactly one choice must best satisfy the stated goal while remaining accurate and relevant.\n"
                "- Distractors should be factually possible but less relevant, too broad, too narrow, or misaligned with the rhetorical goal."
            ),
            self.ORGANIZATION: (
                "- Focus: Improving the logical placement of information or selecting wording that best maintains coherence.\n"
                "- Requirement: The sentence or short passage must involve a meaningful decision about sequence, placement, or flow.\n"
                "- Exactly one option must best improve logical progression or maintain coherence.\n"
                "- Distractors should reflect plausible but weaker organizational choices."
            ),
            self.CONCISION_AND_PRECISION: (
                "- Focus: Choosing wording that is clear, economical, and precise without changing meaning inappropriately.\n"
                "- Requirement: The sentence or short passage must contain an opportunity to revise for clarity, precision, or concision.\n"
                "- Exactly one option must be the clearest and most effective under standard SAT writing expectations.\n"
                "- Distractors should include redundancy, vagueness, wordiness, or imprecise phrasing."
            ),
        }
        return specs.get(question_type, "Expression of Ideas logic.")
    

    def build_system_prompt(self) -> str:
        return f"""
    You are an SAT "{self.DOMAIN}" item writer.

    Goal:
    Generate one sentence-level item that supports exactly ONE question of a specified type.

    Focus:
    Test effectiveness of language, organization, or rhetorical purpose.

    Requirements:
    - academic, neutral tone
    - 20–90 words
    - exactly ONE editable portion or revision target
    - no outside knowledge required
    - exactly one correct answer (no ambiguity)

    Difficulty:
    - Easy → clearer logic, simpler distinctions
    - Medium → moderate subtlety, plausible distractors
    - Hard → nuanced distinctions, tighter distractors

    Quality rules:
    - do not generate full reading passages
    - do not create multiple revision issues
    - do not create multiple valid answers
    - do not rely on style preference alone
    - do not make item purely grammatical (focus must be rhetorical effectiveness)

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
    1. Decide whether the given sentence or short passage supports exactly one strong SAT-style question of the requested type.
    2. If yes, generate exactly one question.
    3. If not, return FAIL.

    Be conservative:
    - do not assume missing information
    - do not force a weak or ambiguous item to work
    - if more than one answer could reasonably work, return FAIL

    Validation rules by question type:

    For "{self.TRANSITIONS}":
    - the text contains two ideas with a clear logical relationship inferable from context
    - exactly one transition correctly expresses that relationship
    - the decision is rhetorical/logical, not merely grammatical
    - distractors may reflect plausible but incorrect relationships

    For "{self.RHETORICAL_SYNTHESIS}":
    - the item establishes a clear writing goal
    - the context is sufficient to judge which option best serves that goal
    - exactly one option is most relevant, accurate, and rhetorically effective
    - distractors may be plausible but less relevant, less focused, or less aligned with the goal

    For "{self.ORGANIZATION}":
    - the text contains a real issue involving sequence, placement, or flow
    - exactly one option best improves coherence or logical progression
    - the decision depends on organization/development of ideas, not mainly grammar
    - distractors may be reasonable but less coherent revisions

    For "{self.CONCISION_AND_PRECISION}":
    - the text contains a real opportunity to improve clarity, concision, or precision
    - exactly one option is clearly most effective
    - the correct answer avoids redundancy, vagueness, imprecision, or unnecessary wordiness
    - distractors may use plausible but weaker wording

    Question-writing rules:
    - write exactly one SAT-style question for the requested type
    - use the editable portion or revision target as the basis for the answer choices
    - exactly one answer must be correct
    - distractors must be plausible and clearly wrong
    - avoid duplicate or overlapping options
    - keep choices concise and parallel

    Preferred stem guidance:
    - "{self.TRANSITIONS}": most logical transition; best connects the ideas
    - "{self.RHETORICAL_SYNTHESIS}": most effectively accomplishes the writer's goal; best supports the writer's purpose
    - "{self.ORGANIZATION}": most logically completes the text; best improves organization
    - "{self.CONCISION_AND_PRECISION}": most effectively conveys the idea; clearest and most concise

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
    Determine whether a sentence-level item is a valid SAT question.

    Be rigorous:
    - do not assume missing information
    - do not fix errors
    - if ambiguity exists → FAIL

    Evaluate:

    ITEM
    - coherent, sentence-level, SAT-appropriate
    - clear editable portion
    - sufficient context for rhetorical decision
    - not vague, contradictory, or incomplete

    Type-specific:

    - "{self.TRANSITIONS}": clear logical relationship; one correct transition; decision based on meaning, not grammar
    - "{self.RHETORICAL_SYNTHESIS}": clear writing goal; one option best serves that goal; others less relevant
    - "{self.ORGANIZATION}": real issue in sequence/placement/flow; one best improvement
    - "{self.CONCISION_AND_PRECISION}": real wording issue; one most clear, concise, and precise option

    QUESTION
    - clear, precise, not ambiguous
    - tests intended Expression of Ideas skill (not grammar alone)
    - answerable using the text alone

    DIFFICULTY
    - reasoning and distractors match difficulty
    - not trivial or unfair

    OPTIONS
    - exactly 4 choices
    - no duplicates or overlaps
    - all plausible
    - exactly one correct
    - incorrect options clearly wrong
    - parallel in structure

    ANSWER
    - produces most effective result
    - best and only correct choice
    - aligned with question type

    EXPLANATION
    - correctly justifies answer
    - correctly eliminates alternatives
    - identifies relevant rhetorical principle
    - no contradictions

    LANGUAGE
    - no grammar, spelling, or clarity issues
    - no ambiguity enabling multiple answers

    FAIL if:
    - item does not support question type
    - question is unclear or misaligned
    - difficulty mismatch
    - duplicate/overlapping options
    - multiple valid answers
    - weak/incorrect answer
    - flawed explanation
    - depends on style preference instead of rhetorical principle

    Return JSON only.

    FAIL:
    {{
    "verdict": "FAIL",
    "question_type": "",
    "difficulty": "",
    "failed_checks": [
        {{
        "category": "item | question | difficulty | options | answer | explanation | clarity",
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
        "clarity_valid": true
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
    Revise a failed SAT item using validator feedback so the final item is valid, unambiguous, and aligned with the requested question type and difficulty.

    You will receive:
    - original sentence or short passage
    - original editable portion or revision target
    - original question data
    - validator feedback
    - target question type
    - target difficulty

    Your job:
    Fix every issue identified in the feedback.

    Repair as needed:
    - sentence or passage
    - editable portion or revision target
    - question
    - answer choices
    - correct answer
    - explanation
    - question-type alignment
    - difficulty alignment
    - clarity and rhetorical effectiveness

    Repair policy:
    - use local_edit if targeted fixes are enough
    - use full_rewrite if the item is fundamentally flawed
    - preserve valid parts when possible
    - ensure exactly one correct answer
    - ensure no meaningful ambiguity remains

    Question-type requirements:

    - "{self.TRANSITIONS}": context must clearly establish a logical relationship; exactly one transition best expresses it; distractors should reflect different but plausible incorrect relationships
    - "{self.RHETORICAL_SYNTHESIS}": writer's goal must be clear; context must support judging relevance and effectiveness; exactly one option best serves the goal
    - "{self.ORGANIZATION}": item must involve a meaningful decision about sequence, placement, or flow; exactly one option best improves coherence
    - "{self.CONCISION_AND_PRECISION}": item must contain a real opportunity to improve clarity, economy, or precision; exactly one option must be the clearest and most effective

    Rules:
    - incorporate validator feedback directly
    - do not ignore failed checks
    - do not repeat the same failure pattern
    - do not rely on style preference alone
    - preserve academic tone and SAT style
    - keep the item sentence-level or very short-passage-level
    - preferred length: 20–70 words; maximum 90 words
    - ensure exactly one editable portion or clearly defined revision target
    - ensure the explanation matches the revised answer and revised options

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
    Revise the full item based on the validator feedback.
    Fix the sentence, revision target, question, options, correct answer, and explanation wherever needed.
    Return JSON only.
    """

