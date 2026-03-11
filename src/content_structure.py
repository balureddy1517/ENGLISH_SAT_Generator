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

    def build_prompt(self, question_type: str, difficulty_level: str,feedback: str = None) -> str:
        # Mapping your difficulty labels to Grade Bands
        difficulty_mapping = {
            "Easy": "Grades 6-8",
            "Medium": "Grades 9-11",
            "Hard": "Grades 12-14"
        }
        
        reading_band = difficulty_mapping.get(difficulty_level, "Grades 9-11")
        specific_requirement = self._get_type_specs(question_type)

        # Updated Template with "Craft and Structure" explicitly integrated
       
        PROMPT_TEMPLATE = f"""
            ROLE
            You are an experienced SAT English professor and official test content creator specializing in the "{self.DOMAIN}" domain.

            TASK
            Generate one original SAT-style informational passage at the {difficulty_level} ({reading_band}) level. 
            The passage must be specifically engineered to support a "{question_type}" question.

            DOMAIN FOCUS: {self.DOMAIN}
            Your goal is to create a text where the *structure*, *word choice*, or *relationship between texts* is the primary focus. 
            The logic must be rooted in how the author constructs the argument or uses specific language.

            PASSAGE ARCHITECTURE
            {specific_requirement}

            GENERAL REQUIREMENTS
            • Tone: Academically neutral, professional, and sophisticated.
            • Topics: Science, Humanities, History, or Literature.
            • Language: Use {reading_band} appropriate sentence complexity and abstract vocabulary.

            STRICT RULES
            • Return ONLY the passage text. 
            • Do not include questions, answer choices, or meta-commentary.
            • The passage must be 50-150 words total (unless Cross-Text, which requires two shorter paragraphs).

            OUTPUT
            Return ONLY a JSON object with this exact structure:
            {{
            "passage": "The generated text here",
            "domain": "{self.DOMAIN}",
            "type": "{question_type}"
            }}
"""
        
        return PROMPT_TEMPLATE
    
    def build_question_prompt(self, passage: str, question_type: str) -> str:
        return f"""
    ROLE
    You are a strict SAT Craft and Structure Validator and Question Writer.

    CONTEXT
    A previous agent generated a passage intended for a "{question_type}" question in the "{self.DOMAIN}" domain.

    PASSAGE
    {passage}

    TASK
    First, evaluate whether this passage supports exactly one strong SAT-style "{question_type}" question.
    Only if it passes validation, generate exactly one question.

    VALIDATION RUBRIC

    If question_type = "{self.WORDS_IN_CONTEXT}", check all of the following:
    1. The passage contains exactly one viable target word for contextual meaning analysis.
    2. The target word's meaning can be determined from nearby context clues.
    3. The meaning does not depend on outside knowledge.
    4. One answer choice can be clearly correct while the others are plausible but wrong.

    If question_type = "{self.TEXT_STRUCTURE}", check all of the following:
    1. The passage shows a visible progression of ideas.
    2. The passage includes a rhetorical move such as contrast, qualification, shift, or clarification.
    3. A question could target function, organization, or development of ideas rather than main idea alone.
    4. One answer choice can be clearly correct while the others are plausible but wrong.

    If question_type = "{self.CROSS_TEXT}", check all of the following:
    1. The passage contains two distinct texts.
    2. The two texts have a clear relationship such as agreement, disagreement, qualification, or contrast in emphasis.
    3. That relationship is inferable from the text alone.
    4. One answer choice can be clearly correct while the others are plausible but wrong.

    DECISION RULE
    - PASS only if all rubric checks are satisfied.
    - Otherwise return FAIL.
    - Do not force a question from a weak passage.

    QUESTION WRITING RULES
    If the passage passes:
    - Write exactly one SAT-style question that tests "{question_type}" specifically.
    - Do not write a general comprehension or main idea question unless that is inherently required by the target skill.
    - Ensure exactly one answer is correct.
    - Ensure all distractors are passage-based, plausible, and definitively wrong.
    - Avoid overlapping answer choices.
    - Use only the information in the passage.

    OUTPUT FORMAT
    Return ONLY valid JSON in exactly one of the two formats below.

    If FAIL:
    {{
    "verdict": "FAIL",
    "question_type": "{question_type}",
    "failed_checks": [],
    "reason": "",
    "minimal_fix": "",
    "rewrite_scope": "local"
    }}

    If PASS:
    {{
    "verdict": "PASS",
    "question_type": "{question_type}",
    "question": "",
    "option_a": "",
    "option_b": "",
    "option_c": "",
    "option_d": "",
    "correct_answer": "A",
    "explanation": ""
    }}
    """
        

    def build_refinement_prompt(self, passage: str, question_type: str, feedback: str, difficulty: str) -> str:

        return f"""
ROLE
You are a Senior SAT Craft and Structure Passage Editor.

Your responsibility is to repair or rewrite a passage so that it successfully supports a valid "{question_type}" SAT-style question.

INPUTS

ORIGINAL PASSAGE
{passage}

VALIDATOR FEEDBACK
{feedback}

QUESTION TYPE TARGET
{question_type}

DIFFICULTY LEVEL
{difficulty}


TASK

You must carefully analyze the validator feedback and modify the passage so that the issues are fully resolved.

Your job is NOT to simply paraphrase the passage.  
Your job is to **fix the exact structural problems described in the feedback**.

Follow this process:

Step 1 — Analyze the feedback  
Identify what specific issues caused the passage to fail validation.

Step 2 — Decide repair strategy

If the issues are small (missing clues, weak transition, unclear relationship):
→ Apply **LOCAL EDITS** to the passage.

If the passage structure is fundamentally wrong for the question type:
→ Perform a **FULL REWRITE** while keeping the topic similar.

Step 3 — Apply targeted corrections  
Every issue mentioned in the feedback must be addressed.


REFINEMENT REQUIREMENTS BY QUESTION TYPE

For **Words in Context**
• Include exactly one meaningful pivot word.
• Provide strong contextual clues around the word.
• Ensure the meaning can be inferred from nearby sentences.

For **Text Structure**
• Ensure the passage contains a clear rhetorical progression.
• Include a visible structural movement such as:
  - claim → qualification
  - assumption → correction
  - phenomenon → explanation
  - old idea → new evidence
• A question about organization or function must be clearly answerable.

For **Cross-Text**
• The passage must contain two short texts.
• Each text must express a distinct perspective or claim.
• The relationship between the texts must be clear (agreement, contrast, qualification, etc.).


IMPORTANT RULES

• You MUST incorporate the validator feedback into the revision.
• Do not repeat the same structural mistake.
• Preserve the academic tone.
• Maintain the requested difficulty level.
• Keep passage length between 50–150 words (unless Cross-Text).


OUTPUT FORMAT

Return ONLY valid JSON.

{{
  "passage": "The improved or rewritten passage",
  "domain": "{self.DOMAIN}",
  "type": "{question_type}"
 
  ]
}}
"""
    
    def build_validation_prompt(
    self,
    passage: str,
    question_data: str,
    question_type: str,
    difficulty: str
) -> str:
        return f"""
    ROLE
    You are a strict SAT Reading and Writing Quality Assurance Validator.

    You are responsible for validating whether the provided passage and question together form a high-quality SAT-style item.

    You must act as a rigorous evaluator, not as a creative writer.
    Do not be lenient.
    Do not assume missing information.
    Do not try to "make it work" if the item is flawed.

    INPUTS

    QUESTION TYPE TARGET
    {question_type}

    DIFFICULTY TARGET
    {difficulty}

    PASSAGE
    {passage}

    QUESTION DATA
    {question_data}

    TASK

    Evaluate the SAT item across all required quality dimensions:

    1. Passage validity
    2. Question validity
    3. Alignment with the requested question type
    4. Alignment with the requested difficulty level
    5. Grammar and clarity
    6. Answer choice quality
    7. Correct answer validity
    8. Explanation validity

    You must determine whether this item should PASS or FAIL.

    --------------------------------------------------
    VALIDATION RUBRIC
    --------------------------------------------------

    A. PASSAGE VALIDITY

    Check all of the following:

    1. The passage is clear, coherent, and grammatically correct.
    2. The passage is academically neutral in tone.
    3. The passage length and structure are appropriate for SAT style.
    4. The passage contains enough textual evidence to support the question.
    5. The passage is not vague, incomplete, self-contradictory, or overly confusing.

    Question-type-specific passage checks:

    For Words in Context:
    - The passage contains a clear target word or phrase whose meaning can be inferred from context.
    - The surrounding context provides enough evidence to determine meaning.
    - The meaning does not depend mainly on outside knowledge.

    For Text Structure:
    - The passage contains a visible progression of ideas.
    - The passage has a clear rhetorical move such as contrast, qualification, shift, clarification, or development.
    - The passage supports a question about organization, function, or development of ideas.

    For Cross-Text:
    - The passage contains two distinct texts.
    - The two texts have a clear relationship such as agreement, disagreement, contrast, or qualification.
    - The relationship is inferable from the text alone.

    B. QUESTION VALIDITY

    Check all of the following:

    1. The question is grammatically correct.
    2. The question is clear and precise.
    3. The question is not vague, overly broad, or ambiguous.
    4. The question tests the intended SAT skill rather than generic comprehension.
    5. The question can be answered using the passage alone.
    6. The question wording is natural and SAT-appropriate.

    C. DIFFICULTY ALIGNMENT

    Check all of the following:

    1. The passage complexity matches the requested difficulty: "{difficulty}".
    2. The reasoning required by the question matches the requested difficulty.
    3. The distractors are appropriately challenging for the requested difficulty.
    4. The item is neither trivially easy nor unfairly difficult.

    D. ANSWER OPTION QUALITY

    Check all of the following:

    1. There are exactly four answer choices.
    2. Each answer choice is grammatically correct.
    3. No answer choice is duplicated or near-duplicated.
    4. No answer choice overlaps so much with another that both could seem correct.
    5. All answer choices are plausible in context.
    6. Exactly one answer choice is clearly correct.
    7. The incorrect choices are definitively wrong, not merely less precise.
    8. No answer choice is irrelevant, absurd, or obviously eliminable.

    E. CORRECT ANSWER VALIDITY

    Check all of the following:

    1. The marked correct answer is actually supported by the passage.
    2. The correct answer is the best and only correct answer.
    3. None of the incorrect answers can reasonably compete with the correct answer.
    4. The correct answer matches the intended question type.

    F. EXPLANATION VALIDITY

    Check all of the following:

    1. The explanation correctly justifies why the correct answer is correct.
    2. The explanation correctly explains why each incorrect answer is wrong.
    3. The explanation is grammatically correct and clear.
    4. The explanation does not contradict the passage.
    5. The explanation does not rely on unsupported claims or outside knowledge.

    G. LANGUAGE AND GRAMMAR CHECK

    Check all of the following across the passage, question, options, and explanation:

    1. No grammar errors
    2. No spelling errors
    3. No awkward or unnatural phrasing
    4. No punctuation issues that affect meaning
    5. No unclear pronoun references
    6. No broken logic or incomplete sentences

    --------------------------------------------------
    FAIL CONDITIONS
    --------------------------------------------------

    The item must FAIL if any of the following are true:

    - The passage does not support the requested question type
    - The question is vague, ambiguous, or poorly worded
    - The question does not match the requested SAT skill
    - The difficulty does not match the requested level
    - There are duplicate or near-duplicate options
    - More than one answer could reasonably be correct
    - The marked correct answer is wrong or weak
    - The explanation is incomplete, wrong, or misleading
    - There are meaningful grammar or clarity issues

    --------------------------------------------------
    OUTPUT INSTRUCTIONS
    --------------------------------------------------

    Return ONLY valid JSON.

    If the item FAILS, return:

    {{
    "verdict": "FAIL",
    "question_type": "{question_type}",
    "difficulty": "{difficulty}",
    "failed_checks": [
        {{
        "category": "passage | question | difficulty | options | answer | explanation | grammar",
        "issue": "Specific problem",
        "severity": "major | minor"
        }}
    ],
    "summary_reason": "Brief overall reason for failure",
    "repair_recommendation": {{
        "repair_target": "passage | question | options | explanation | multiple",
        "repair_scope": "local_edit | full_rewrite",
        "recommended_action": "Precise action needed to fix the item"
    }}
    }}

    If the item PASSES, return:

    {{
    "verdict": "PASS",
    "question_type": "{question_type}",
    "difficulty": "{difficulty}",
    "quality_summary": {{
        "passage_valid": true,
        "question_valid": true,
        "difficulty_aligned": true,
        "options_valid": true,
        "correct_answer_valid": true,
        "explanation_valid": true,
        "grammar_valid": true
    }},
    "notes": "Brief explanation of why the item passes"
    }}

    STRICT RULES

    - Use only the provided passage and question data.
    - Do not rewrite the item.
    - Do not generate a new question.
    - Do not silently fix errors.
    - If there is any meaningful ambiguity, return FAIL.
    - Be conservative: a weak SAT item should not pass.
    - Return JSON only.
    """
        


# creator = Craft_and_Structure()
# final_prompt = creator.build_prompt("Words in Context", "Hard")
# print(final_prompt)