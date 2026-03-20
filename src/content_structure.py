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
        


################################################################## INFORMATION and IDEAS ####################################################################################################################################

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

    def build_prompt(self, question_type: str, difficulty_level: str) -> str:
        difficulty_mapping = {
            "Easy": "Grades 6-8",
            "Medium": "Grades 9-11",
            "Hard": "Grades 12-14",
        }

        reading_band = difficulty_mapping.get(difficulty_level, "Grades 9-11")
        specific_requirement = self._get_type_specs(question_type)

        return f"""
ROLE
You are an experienced SAT Reading and Writing passage writer specializing in the "{self.DOMAIN}" domain.

TASK
Generate one original SAT-style informational passage designed specifically for a "{question_type}" question.

DOMAIN FOCUS
The passage must test the student's ability to understand, interpret, and reason about the information and ideas presented.

QUESTION-TYPE REQUIREMENTS
{specific_requirement}

GENERAL REQUIREMENTS
- Tone: academic, neutral, precise
- Topic: science, social science, history, or literature
- Difficulty: {difficulty_level}
- Reading band: {reading_band}
- Length: 50-150 words

DIFFICULTY GUIDANCE
- Easy: more explicit support, simpler syntax, more direct reasoning
- Medium: moderate abstraction, some synthesis required
- Hard: denser ideas, subtler distinctions, stronger synthesis or inference required

FORBIDDEN FAILURE MODES
- Do not make the passage vague, incomplete, or overly dependent on outside knowledge.
- Do not include questions, answer choices, or explanation text.
- Do not create a passage that could support multiple unrelated question types equally well.
- Do not make the answer trivially obvious from one isolated sentence unless the question type inherently requires that.
- For Data Interpretation, use text-only data descriptions; do not refer to any actual chart, graph, or table image.

OUTPUT
Return ONLY valid JSON:
{{
  "passage": "...",
  "domain": "{self.DOMAIN}",
  "type": "{question_type}"
}}
"""

    def build_question_prompt(self, passage: str, question_type: str) -> str:
        return f"""
ROLE
You are a strict SAT Information and Ideas passage validator and question writer.

CONTEXT
A previous agent generated a passage intended for a "{question_type}" question in the "{self.DOMAIN}" domain.

PASSAGE
{passage}

TASK
First determine whether the passage supports exactly one strong SAT-style "{question_type}" question.
Only if it passes validation, generate exactly one question.

VALIDATION RUBRIC

For "{self.CENTRAL_IDEA}", check all of the following:
1. The passage has one unifying main idea or primary claim.
2. Multiple details support that main idea.
3. The correct answer would require synthesizing the passage, not selecting one isolated sentence.
4. Plausible distractors could be written as too narrow, too broad, or secondary ideas.

For "{self.COMMAND_OF_EVIDENCE}", check all of the following:
1. The passage contains a claim, conclusion, or answerable idea that requires textual support.
2. The passage includes multiple candidate details that could serve as evidence.
3. One detail is clearly the strongest and most direct support.
4. Plausible distractors could be written using related but weaker or less direct evidence.

For "{self.INFERENCE}", check all of the following:
1. The passage supports a logical conclusion that is not explicitly stated.
2. The conclusion depends on combining two or more details from the passage.
3. The correct answer would go beyond paraphrase while remaining fully supported.
4. Plausible distractors could be written as overstatements, unsupported assumptions, or explicit restatements.

For "{self.DATA_INTERPRETATION}", check all of the following:
1. The passage includes concrete text-described data, results, comparisons, or numerical findings.
2. A question could ask what the data shows, suggests, or supports.
3. One answer would be clearly best supported by the reported data.
4. Plausible distractors could be written using misreadings, overgeneralizations, or unsupported extrapolations.

DECISION RULE
- PASS only if all rubric checks are satisfied.
- Otherwise return FAIL.
- Do not force a question from a weak passage.

QUESTION WRITING RULES
If the passage passes:
- Write exactly one SAT-style question that tests "{question_type}" specifically.
- Do not write a generic comprehension question unless that is inherently required by the skill.
- Ensure exactly one answer is correct.
- Ensure all distractors are plausible, passage-based, and definitively wrong.
- Avoid duplicate or overlapping options.
- Use only the information in the passage.

QUESTION PATTERN GUIDANCE

For "{self.CENTRAL_IDEA}", prefer stems such as:
- Which choice best states the main idea of the passage?
- Which choice best describes the central claim of the passage?
- What is the main purpose of the passage?

For "{self.COMMAND_OF_EVIDENCE}", prefer standalone evidence stems such as:
- Which choice best supports the claim that...?
- Which detail from the passage best supports the conclusion that...?
Do not write paired-question formats that depend on a previous question.

For "{self.INFERENCE}", prefer stems such as:
- Which inference is best supported by the passage?
- The passage most strongly suggests that...
- It can most reasonably be inferred that...

For "{self.DATA_INTERPRETATION}", prefer stems such as:
- Which choice best describes what the reported data shows?
- Which conclusion is best supported by the reported results?
- According to the passage, which statement is most supported by the data?

OUTPUT FORMAT
Return ONLY valid JSON.

If FAIL:
{{
  "verdict": "FAIL",
  "question_type": "{question_type}",
  "failed_checks": [],
  "reason": "",
  "minimal_fix": "",
  "rewrite_scope": "local_edit"
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

    def build_refinement_prompt(
        self,
        passage: str,
        question_type: str,
        feedback: str,
        difficulty: str
    ) -> str:
        return f"""
ROLE
You are a Senior SAT Information and Ideas Passage Editor.

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
You must carefully analyze the validator feedback and modify the passage so that all identified issues are resolved.

Your job is NOT to paraphrase the passage.
Your job is to fix the exact problems described in the feedback.

Follow this process:

Step 1 — Analyze the feedback
Identify the specific reasons the passage failed.

Step 2 — Decide repair strategy
- If the issues are limited and local, apply LOCAL EDITS.
- If the passage is fundamentally unsuitable for the question type, perform a FULL REWRITE while keeping the topic similar.

Step 3 — Apply targeted corrections
Every issue mentioned in the feedback must be addressed directly.

REFINEMENT REQUIREMENTS BY QUESTION TYPE

For "{self.CENTRAL_IDEA}":
- Ensure the passage has one clear central idea or primary claim.
- Ensure two or more details support that central idea.
- Ensure the main idea must be synthesized from the passage as a whole.

For "{self.COMMAND_OF_EVIDENCE}":
- Ensure the passage includes a claim, conclusion, or answerable idea that requires support.
- Ensure the passage includes multiple candidate details that could serve as evidence.
- Ensure one detail is clearly the strongest support.

For "{self.INFERENCE}":
- Ensure the passage supports a logical conclusion that is not explicitly stated.
- Ensure the inference depends on combining multiple clues.
- Ensure the correct inference does not depend on outside knowledge.

For "{self.DATA_INTERPRETATION}":
- Ensure the passage includes concrete text-only data, results, or comparisons.
- Ensure the data is specific enough to support interpretation.
- Ensure a question could ask what the data shows, suggests, or supports.
- Do not refer to any visual chart, graph, or table.

IMPORTANT RULES
- You MUST incorporate the validator feedback into the revision.
- Do not repeat the same failure pattern.
- Preserve academic tone.
- Maintain the requested difficulty level.
- Keep the passage between 50 and 150 words.

OUTPUT FORMAT
Return ONLY valid JSON:
{{
  "passage": "The improved or rewritten passage",
  "domain": "{self.DOMAIN}",
  "type": "{question_type}",
  "refinement_strategy": "local_edit or full_rewrite",
  "changes_made": [
    "..."
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

For "{self.CENTRAL_IDEA}":
- The passage contains one unifying main idea or primary claim.
- Two or more details support that main idea.
- The main idea requires synthesis rather than retrieval of one sentence.

For "{self.COMMAND_OF_EVIDENCE}":
- The passage contains a claim, conclusion, or answerable idea that requires support.
- The passage includes multiple plausible evidence candidates.
- One candidate is clearly the strongest and most direct support.

For "{self.INFERENCE}":
- The passage supports a logical conclusion not explicitly stated.
- The conclusion depends on multiple clues in the passage.
- The correct answer is not merely a paraphrase of an explicit statement.

For "{self.DATA_INTERPRETATION}":
- The passage includes concrete text-only data, quantitative findings, or clear results.
- The information is sufficient to support interpretation.
- A correct answer can be based on what the data shows, suggests, or supports.

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
- The passage does not support the requested question type.
- The question is vague, ambiguous, or poorly worded.
- The question does not match the requested SAT skill.
- The difficulty does not match the requested level.
- There are duplicate or near-duplicate options.
- More than one answer could reasonably be correct.
- The marked correct answer is wrong or weak.
- The explanation is incomplete, wrong, or misleading.
- There are meaningful grammar or clarity issues.

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
    



##################################################################################.  STAMDARD ENGLISH.    ############################################################################################################################################################

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

    def build_prompt(self, question_type: str, difficulty_level: str) -> str:
        difficulty_mapping = {
            "Easy": "Grades 6-8",
            "Medium": "Grades 9-11",
            "Hard": "Grades 12-14",
        }

        reading_band = difficulty_mapping.get(difficulty_level, "Grades 9-11")
        specific_requirement = self._get_type_specs(question_type)

        return f"""
ROLE
You are an experienced SAT Reading and Writing item writer specializing in the "{self.DOMAIN}" domain.

TASK
Generate one original SAT-style sentence or very short passage designed specifically for a "{question_type}" question.

DOMAIN FOCUS
The item must test standard written English at the sentence level, including grammar, usage, punctuation, and clarity.

QUESTION-TYPE REQUIREMENTS
{specific_requirement}

GENERAL REQUIREMENTS
- Tone: academic, neutral, precise
- Context: science, history, literature, arts, or social science is acceptable, but the focus must remain on sentence correctness
- Difficulty: {difficulty_level}
- Reading band: {reading_band}
- Length: 15-45 words preferred, and no more than 60 words total
- The item should contain exactly one editable portion that can be replaced by one of four answer choices

DIFFICULTY GUIDANCE
- Easy: more obvious grammar distinction, shorter sentence, clearer structure
- Medium: moderate syntactic complexity, closer distractors
- Hard: denser syntax, subtler distinctions, more plausible distractors

FORBIDDEN FAILURE MODES
- Do not generate a full reading-comprehension passage.
- Do not make the question depend on outside knowledge.
- Do not create more than one editable issue.
- Do not create multiple equally acceptable answers.
- Do not make the correct answer depend on style preference rather than standard written English.

OUTPUT
Return ONLY valid JSON:
{{
  "sentence": "The full sentence or short passage with an editable portion clearly identifiable from context",
  "editable_portion": "The exact portion intended to be replaced by answer choices",
  "domain": "{self.DOMAIN}",
  "type": "{question_type}"
}}
"""

    def build_question_prompt(self, sentence: str, editable_portion: str, question_type: str) -> str:
        return f"""
ROLE
You are a strict SAT Standard English Conventions validator and question writer.

CONTEXT
A previous agent generated a sentence or short passage intended for a "{question_type}" question in the "{self.DOMAIN}" domain.

SENTENCE OR PASSAGE
{sentence}

EDITABLE PORTION
{editable_portion}

TASK
First determine whether this sentence or short passage supports exactly one strong SAT-style "{question_type}" question.
Only if it passes validation, generate exactly one question.

VALIDATION RUBRIC

For "{self.BOUNDARIES}", check all of the following:
1. The sentence contains a genuine boundary decision involving clauses or sentence parts.
2. Exactly one replacement yields correct clause joining or separation.
3. The difference among options is based on grammar/punctuation, not wording alone.
4. Plausible distractors could be written using realistic boundary errors.

For "{self.FORM_STRUCTURE_SENSE}", check all of the following:
1. The sentence contains a real grammar or sentence-structure decision.
2. Exactly one replacement yields standard written English.
3. The decision involves form, agreement, structure, or sentence-level logic rather than mere style preference.
4. Plausible distractors could be written using realistic grammar or structure errors.

For "{self.MODIFIERS}", check all of the following:
1. The sentence contains a genuine modifier-placement or modifier-reference issue.
2. Exactly one replacement clearly links the modifier to the intended target.
3. The correct answer improves both grammatical correctness and clarity of meaning.
4. Plausible distractors could be written using realistic misplaced or dangling modifier errors.

For "{self.PUNCTUATION}", check all of the following:
1. The sentence contains a real punctuation decision.
2. Exactly one replacement uses punctuation correctly under standard written English.
3. The punctuation choice affects sentence structure or meaning, not cosmetic style alone.
4. Plausible distractors could be written using realistic punctuation errors.

DECISION RULE
- PASS only if all rubric checks are satisfied.
- Otherwise return FAIL.
- Do not force a question from a weak or ambiguous sentence.

QUESTION WRITING RULES
If the item passes:
- Write exactly one SAT-style question that tests "{question_type}" specifically.
- The question should ask which choice completes the text so that it conforms to standard written English, unless a more specific punctuation or clarity stem is clearly better.
- Use the provided editable portion as the basis for the four answer choices.
- Ensure exactly one answer is correct.
- Ensure all distractors are plausible and definitively wrong.
- Avoid duplicate or overlapping options.
- Keep answer choices concise and parallel in form.

QUESTION PATTERN GUIDANCE

For "{self.BOUNDARIES}", prefer stems such as:
- Which choice completes the text so that it conforms to the conventions of Standard English?
- Which choice provides the most grammatically complete and conventional wording?

For "{self.FORM_STRUCTURE_SENSE}", prefer stems such as:
- Which choice completes the text so that it conforms to the conventions of Standard English?
- Which choice results in a grammatically complete and logical sentence?

For "{self.MODIFIERS}", prefer stems such as:
- Which choice completes the text so that it conforms to the conventions of Standard English?
- Which choice best clarifies the intended meaning while following standard written English?

For "{self.PUNCTUATION}", prefer stems such as:
- Which choice completes the text so that it conforms to the conventions of Standard English?
- Which choice uses punctuation correctly?

OUTPUT FORMAT
Return ONLY valid JSON.

If FAIL:
{{
  "verdict": "FAIL",
  "question_type": "{question_type}",
  "failed_checks": [],
  "reason": "",
  "minimal_fix": "",
  "rewrite_scope": "local_edit"
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

    def build_refinement_prompt(
        self,
        sentence: str,
        editable_portion: str,
        question_type: str,
        feedback: str,
        difficulty: str
    ) -> str:
        return f"""
ROLE
You are a Senior SAT Standard English Conventions Item Editor.

Your responsibility is to repair or rewrite a sentence-level item so that it successfully supports a valid "{question_type}" SAT-style question.

INPUTS

ORIGINAL SENTENCE OR PASSAGE
{sentence}

ORIGINAL EDITABLE PORTION
{editable_portion}

VALIDATOR FEEDBACK
{feedback}

QUESTION TYPE TARGET
{question_type}

DIFFICULTY LEVEL
{difficulty}

TASK
You must carefully analyze the validator feedback and modify the sentence-level item so that all identified issues are resolved.

Your job is NOT to paraphrase randomly.
Your job is to fix the exact grammatical, structural, punctuation, or clarity problems described in the feedback.

Follow this process:

Step 1 — Analyze the feedback
Identify the exact reasons the item failed.

Step 2 — Decide repair strategy
- If the issues are limited and local, apply LOCAL EDITS.
- If the sentence is fundamentally unsuitable for the target skill, perform a FULL REWRITE while keeping a similar topic and difficulty.

Step 3 — Apply targeted corrections
Every issue mentioned in the feedback must be addressed directly.

REFINEMENT REQUIREMENTS BY QUESTION TYPE

For "{self.BOUNDARIES}":
- Ensure the sentence contains a real clause-boundary decision.
- Ensure exactly one replacement is conventionally correct.
- Ensure distractors could reflect comma splice, fragment, run-on, or unnecessary punctuation errors.

For "{self.FORM_STRUCTURE_SENSE}":
- Ensure the sentence contains a real decision involving grammar, agreement, structure, or sentence sense.
- Ensure exactly one replacement yields a grammatically complete and logical sentence.
- Ensure the item does not depend on style preference alone.

For "{self.MODIFIERS}":
- Ensure the sentence contains a real modifier-placement or reference issue.
- Ensure exactly one replacement clearly attaches the modifier to the intended target.
- Ensure the corrected sentence is both grammatical and clear in meaning.

For "{self.PUNCTUATION}":
- Ensure the sentence contains a real punctuation decision affecting structure or meaning.
- Ensure exactly one replacement uses punctuation correctly.
- Ensure distractors remain plausible but clearly incorrect.

IMPORTANT RULES
- You MUST incorporate the validator feedback into the revision.
- Do not repeat the same failure pattern.
- Preserve academic tone and SAT style.
- Maintain the requested difficulty level.
- Keep the item sentence-level: preferred length 15-45 words, maximum 60 words.
- Ensure there is exactly one editable portion.

OUTPUT FORMAT
Return ONLY valid JSON:
{{
  "sentence": "The improved or rewritten sentence or short passage",
  "editable_portion": "The exact portion intended to be replaced by answer choices",
  "domain": "{self.DOMAIN}",
  "type": "{question_type}",
  "refinement_strategy": "local_edit or full_rewrite",
  "changes_made": [
    "..."
  ]
}}
"""

    def build_validation_prompt(
        self,
        sentence: str,
        editable_portion: str,
        question_data: str,
        question_type: str,
        difficulty: str
    ) -> str:
        return f"""
ROLE
You are a strict SAT Reading and Writing Quality Assurance Validator for the "{self.DOMAIN}" domain.

You are responsible for validating whether the provided sentence-level item forms a high-quality SAT-style question.

You must act as a rigorous evaluator, not as a creative writer.
Do not be lenient.
Do not assume missing information.
Do not try to make a flawed item work.

INPUTS

QUESTION TYPE TARGET
{question_type}

DIFFICULTY TARGET
{difficulty}

SENTENCE OR PASSAGE
{sentence}

EDITABLE PORTION
{editable_portion}

QUESTION DATA
{question_data}

TASK
Evaluate the SAT item across all required quality dimensions:

1. Sentence/item validity
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

A. ITEM VALIDITY

Check all of the following:
1. The sentence or short passage is coherent and SAT-appropriate.
2. The item is sentence-level, not a full reading-comprehension passage.
3. The editable portion is clear and specific.
4. The item contains enough context to judge the answer based on standard written English.
5. The item is not vague, incomplete, self-contradictory, or confusing.

Question-type-specific item checks:

For "{self.BOUNDARIES}":
- The item contains a genuine clause-boundary or sentence-joining decision.
- Exactly one answer choice correctly handles the boundary.
- The decision is governed by standard written English, not style preference.

For "{self.FORM_STRUCTURE_SENSE}":
- The item contains a genuine issue involving form, structure, agreement, or sentence sense.
- Exactly one answer choice makes the sentence grammatically correct and logical.
- The correct answer does not rely on a merely stylistic preference.

For "{self.MODIFIERS}":
- The item contains a genuine modifier-placement or modifier-reference issue.
- Exactly one answer choice clearly connects the modifier to the intended target.
- The correct answer resolves both grammar and meaning.

For "{self.PUNCTUATION}":
- The item contains a genuine punctuation decision affecting structure or meaning.
- Exactly one answer choice uses punctuation correctly.
- The correct punctuation is required by convention, not just by stylistic preference.

B. QUESTION VALIDITY

Check all of the following:
1. The question is grammatically correct.
2. The question is clear and precise.
3. The question is not vague, overly broad, or ambiguous.
4. The question tests the intended standard-English skill rather than general comprehension.
5. The question can be answered using the sentence or short passage alone.
6. The question wording is natural and SAT-appropriate.

C. DIFFICULTY ALIGNMENT

Check all of the following:
1. The syntactic and grammatical complexity matches the requested difficulty: "{difficulty}".
2. The distinction among answer choices matches the requested difficulty.
3. The distractors are appropriately challenging for the requested difficulty.
4. The item is neither trivially easy nor unfairly difficult.

D. ANSWER OPTION QUALITY

Check all of the following:
1. There are exactly four answer choices.
2. Each answer choice is grammatically well-formed as an option.
3. No answer choice is duplicated or near-duplicated.
4. No answer choice overlaps so much with another that both could seem correct.
5. All answer choices are plausible in context.
6. Exactly one answer choice is clearly correct.
7. The incorrect choices are definitively wrong, not merely less elegant.
8. The options are parallel enough in form to avoid giving away the answer.

E. CORRECT ANSWER VALIDITY

Check all of the following:
1. The marked correct answer actually produces the correct sentence under standard written English.
2. The correct answer is the best and only correct answer.
3. None of the incorrect answers can reasonably compete with the correct answer.
4. The correct answer matches the intended question type.

F. EXPLANATION VALIDITY

Check all of the following:
1. The explanation correctly states why the correct answer is correct.
2. The explanation correctly explains why each incorrect answer is wrong.
3. The explanation is grammatically correct and clear.
4. The explanation does not contradict the sentence.
5. The explanation identifies the relevant grammar, usage, punctuation, or modifier rule accurately.

G. LANGUAGE AND GRAMMAR CHECK

Check all of the following across the sentence, question, options, and explanation:
1. No grammar errors outside intentional distractor differences
2. No spelling errors
3. No awkward or unnatural phrasing that undermines the item
4. No punctuation issues outside intentional answer-choice differences
5. No unclear pronoun references
6. No broken logic or incomplete sentence structure

--------------------------------------------------
FAIL CONDITIONS
--------------------------------------------------

The item must FAIL if any of the following are true:
- The sentence does not support the requested question type.
- The question is vague, ambiguous, or poorly worded.
- The question does not match the requested Standard English skill.
- The difficulty does not match the requested level.
- There are duplicate or near-duplicate options.
- More than one answer could reasonably be correct.
- The marked correct answer is wrong or weak.
- The explanation is incomplete, wrong, or misleading.
- There are meaningful grammar or clarity issues.
- The item depends mainly on style preference rather than standard written English.

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
      "category": "item | question | difficulty | options | answer | explanation | grammar",
      "issue": "Specific problem",
      "severity": "major | minor"
    }}
  ],
  "summary_reason": "Brief overall reason for failure",
  "repair_recommendation": {{
    "repair_target": "sentence | question | options | explanation | multiple",
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
    "item_valid": true,
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
- Use only the provided sentence, editable portion, and question data.
- Do not rewrite the item.
- Do not generate a new question.
- Do not silently fix errors.
- If there is any meaningful ambiguity, return FAIL.
- Be conservative: a weak SAT item should not pass.
- Return JSON only.
"""
    


##################################################Exprresiion of Ideas ################################################################################################################

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

    def build_prompt(self, question_type: str, difficulty_level: str) -> str:
        difficulty_mapping = {
            "Easy": "Grades 6-8",
            "Medium": "Grades 9-11",
            "Hard": "Grades 12-14",
        }

        reading_band = difficulty_mapping.get(difficulty_level, "Grades 9-11")
        specific_requirement = self._get_type_specs(question_type)

        return f"""
ROLE
You are an experienced SAT Reading and Writing item writer specializing in the "{self.DOMAIN}" domain.

TASK
Generate one original SAT-style sentence or very short passage designed specifically for a "{question_type}" question.

DOMAIN FOCUS
The item must test how effectively language, organization, or supporting detail serves a writer's purpose.

QUESTION-TYPE REQUIREMENTS
{specific_requirement}

GENERAL REQUIREMENTS
- Tone: academic, neutral, precise
- Context: science, history, literature, arts, or social science is acceptable
- Difficulty: {difficulty_level}
- Reading band: {reading_band}
- Length: 20-70 words preferred, and no more than 90 words total
- The item should contain exactly one editable portion or one clearly defined revision decision

DIFFICULTY GUIDANCE
- Easy: clearer logical relationships, more explicit rhetorical goals, simpler wording distinctions
- Medium: moderate subtlety, plausible distractors, some synthesis or flow reasoning required
- Hard: subtler rhetorical distinctions, denser context, closer distractors, more nuanced effectiveness judgment

FORBIDDEN FAILURE MODES
- Do not generate a full reading-comprehension passage.
- Do not make the item depend on outside knowledge.
- Do not create more than one major revision issue.
- Do not create multiple equally acceptable answers.
- Do not make the correct answer depend mainly on personal style preference unless the rhetorical goal clearly resolves the choice.
- Do not create items where the answer is purely grammatical; the focus must be effectiveness, organization, or rhetorical purpose.

OUTPUT
Return ONLY valid JSON:
{{
  "sentence": "The full sentence or short passage with an editable portion or clearly defined revision target",
  "editable_portion": "The exact portion intended to be replaced by answer choices, or a short label describing the revision target",
  "domain": "{self.DOMAIN}",
  "type": "{question_type}"
}}
"""

    def build_question_prompt(self, sentence: str, editable_portion: str, question_type: str) -> str:
        return f"""
ROLE
You are a strict SAT Expression of Ideas validator and question writer.

CONTEXT
A previous agent generated a sentence or short passage intended for a "{question_type}" question in the "{self.DOMAIN}" domain.

SENTENCE OR PASSAGE
{sentence}

EDITABLE PORTION OR REVISION TARGET
{editable_portion}

TASK
First determine whether this sentence or short passage supports exactly one strong SAT-style "{question_type}" question.
Only if it passes validation, generate exactly one question.

VALIDATION RUBRIC

For "{self.TRANSITIONS}", check all of the following:
1. The passage contains two ideas whose logical relationship is inferable from context.
2. Exactly one transition correctly expresses that relationship.
3. The decision depends on rhetoric and logical connection, not merely grammar.
4. Plausible distractors could be written using realistic but incorrect relationships such as contrast, continuation, cause-effect, or conclusion.

For "{self.RHETORICAL_SYNTHESIS}", check all of the following:
1. The item establishes a clear writing goal.
2. The context provides enough information to judge which option best serves that goal.
3. Exactly one option would be most relevant, accurate, and rhetorically effective.
4. Plausible distractors could be written as factually possible but less relevant, less focused, or less aligned with the goal.

For "{self.ORGANIZATION}", check all of the following:
1. The passage contains a meaningful issue involving sequence, placement, or flow.
2. Exactly one option best improves coherence or logical progression.
3. The decision depends on organization or development of ideas, not mainly on grammar.
4. Plausible distractors could be written as reasonable but less coherent placements or revisions.

For "{self.CONCISION_AND_PRECISION}", check all of the following:
1. The passage contains a real opportunity to revise wording for clarity, concision, or precision.
2. Exactly one option is clearly the most effective.
3. The correct answer avoids redundancy, vagueness, imprecision, or unnecessary wordiness.
4. Plausible distractors could be written using realistic but weaker wording.

DECISION RULE
- PASS only if all rubric checks are satisfied.
- Otherwise return FAIL.
- Do not force a question from a weak or ambiguous item.

QUESTION WRITING RULES
If the item passes:
- Write exactly one SAT-style question that tests "{question_type}" specifically.
- Use the provided editable portion or revision target as the basis for the four answer choices.
- Ensure exactly one answer is correct.
- Ensure all distractors are plausible and definitively wrong.
- Avoid duplicate or overlapping options.
- Keep answer choices concise and parallel in form.

QUESTION PATTERN GUIDANCE

For "{self.TRANSITIONS}", prefer stems such as:
- Which choice completes the text with the most logical transition?
- Which choice best connects the ideas in the text?

For "{self.RHETORICAL_SYNTHESIS}", prefer stems such as:
- Which choice most effectively uses relevant information from the notes to accomplish the writer's goal?
- Which choice best supports the writer's purpose?

For "{self.ORGANIZATION}", prefer stems such as:
- Which choice most logically completes the text?
- Which choice best improves the organization of the passage?

For "{self.CONCISION_AND_PRECISION}", prefer stems such as:
- Which choice most effectively conveys the idea?
- Which choice is the clearest and most concise?

OUTPUT FORMAT
Return ONLY valid JSON.

If FAIL:
{{
  "verdict": "FAIL",
  "question_type": "{question_type}",
  "failed_checks": [],
  "reason": "",
  "minimal_fix": "",
  "rewrite_scope": "local_edit"
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

    def build_refinement_prompt(
        self,
        sentence: str,
        editable_portion: str,
        question_type: str,
        feedback: str,
        difficulty: str
    ) -> str:
        return f"""
ROLE
You are a Senior SAT Expression of Ideas Item Editor.

Your responsibility is to repair or rewrite a sentence-level item so that it successfully supports a valid "{question_type}" SAT-style question.

INPUTS

ORIGINAL SENTENCE OR PASSAGE
{sentence}

ORIGINAL EDITABLE PORTION OR REVISION TARGET
{editable_portion}

VALIDATOR FEEDBACK
{feedback}

QUESTION TYPE TARGET
{question_type}

DIFFICULTY LEVEL
{difficulty}

TASK
You must carefully analyze the validator feedback and modify the item so that all identified issues are resolved.

Your job is NOT to paraphrase randomly.
Your job is to fix the exact rhetorical, organizational, or wording problems described in the feedback.

Follow this process:

Step 1 — Analyze the feedback
Identify the exact reasons the item failed.

Step 2 — Decide repair strategy
- If the issues are limited and local, apply LOCAL EDITS.
- If the item is fundamentally unsuitable for the target skill, perform a FULL REWRITE while keeping a similar topic and difficulty.

Step 3 — Apply targeted corrections
Every issue mentioned in the feedback must be addressed directly.

REFINEMENT REQUIREMENTS BY QUESTION TYPE

For "{self.TRANSITIONS}":
- Ensure the context clearly establishes a logical relationship between ideas.
- Ensure exactly one transition fits that relationship best.
- Ensure distractors remain plausible but clearly represent different, incorrect relationships.

For "{self.RHETORICAL_SYNTHESIS}":
- Ensure the writer's goal is clear.
- Ensure the context provides enough information to judge relevance and effectiveness.
- Ensure exactly one option best accomplishes the rhetorical goal.

For "{self.ORGANIZATION}":
- Ensure the passage contains a meaningful issue of placement, sequencing, or flow.
- Ensure exactly one option best improves coherence or logical progression.
- Ensure the decision is rhetorical or organizational, not merely grammatical.

For "{self.CONCISION_AND_PRECISION}":
- Ensure the item contains a real opportunity to improve clarity, economy, or precision.
- Ensure exactly one option is the clearest and most effective.
- Ensure weaker options remain plausible but are redundant, vague, wordy, or imprecise.

IMPORTANT RULES
- You MUST incorporate the validator feedback into the revision.
- Do not repeat the same failure pattern.
- Preserve academic tone and SAT style.
- Maintain the requested difficulty level.
- Keep the item sentence-level or very short-passage-level: preferred length 20-70 words, maximum 90 words.
- Ensure there is exactly one editable portion or one clearly defined revision target.

OUTPUT FORMAT
Return ONLY valid JSON:
{{
  "sentence": "The improved or rewritten sentence or short passage",
  "editable_portion": "The exact portion intended to be replaced by answer choices, or a short label describing the revision target",
  "domain": "{self.DOMAIN}",
  "type": "{question_type}",
  "refinement_strategy": "local_edit or full_rewrite",
  "changes_made": [
    "..."
  ]
}}
"""

    def build_validation_prompt(
        self,
        sentence: str,
        editable_portion: str,
        question_data: str,
        question_type: str,
        difficulty: str
    ) -> str:
        return f"""
ROLE
You are a strict SAT Reading and Writing Quality Assurance Validator for the "{self.DOMAIN}" domain.

You are responsible for validating whether the provided item forms a high-quality SAT-style question.

You must act as a rigorous evaluator, not as a creative writer.
Do not be lenient.
Do not assume missing information.
Do not try to make a flawed item work.

INPUTS

QUESTION TYPE TARGET
{question_type}

DIFFICULTY TARGET
{difficulty}

SENTENCE OR PASSAGE
{sentence}

EDITABLE PORTION OR REVISION TARGET
{editable_portion}

QUESTION DATA
{question_data}

TASK
Evaluate the SAT item across all required quality dimensions:

1. Item validity
2. Question validity
3. Alignment with the requested question type
4. Alignment with the requested difficulty level
5. Clarity and rhetorical effectiveness
6. Answer choice quality
7. Correct answer validity
8. Explanation validity

You must determine whether this item should PASS or FAIL.

--------------------------------------------------
VALIDATION RUBRIC
--------------------------------------------------

A. ITEM VALIDITY

Check all of the following:
1. The sentence or short passage is coherent and SAT-appropriate.
2. The item is sentence-level or very short-passage-level, not a full reading-comprehension passage.
3. The editable portion or revision target is clear and specific.
4. The item contains enough context to judge rhetorical effectiveness, organization, transition logic, or wording quality.
5. The item is not vague, incomplete, self-contradictory, or confusing.

Question-type-specific item checks:

For "{self.TRANSITIONS}":
- The item contains a genuine logical connection decision.
- Exactly one answer choice best expresses the relationship between ideas.
- The correct choice is determined by rhetoric and meaning, not merely grammar.

For "{self.RHETORICAL_SYNTHESIS}":
- The item establishes a clear writing goal.
- The context provides enough information to determine which choice best serves that goal.
- Exactly one answer choice is most relevant, accurate, and effective.

For "{self.ORGANIZATION}":
- The item contains a genuine decision involving sequence, placement, or coherence.
- Exactly one answer choice best improves organization or flow.
- The decision is rhetorical or structural, not mainly grammatical.

For "{self.CONCISION_AND_PRECISION}":
- The item contains a genuine wording decision involving clarity, economy, or precision.
- Exactly one answer choice is the clearest and most effective.
- The correct answer is determined by effectiveness, not merely by sounding shorter.

B. QUESTION VALIDITY

Check all of the following:
1. The question is grammatically correct.
2. The question is clear and precise.
3. The question is not vague, overly broad, or ambiguous.
4. The question tests the intended Expression of Ideas skill rather than grammar or general comprehension alone.
5. The question can be answered using the provided text alone.
6. The question wording is natural and SAT-appropriate.

C. DIFFICULTY ALIGNMENT

Check all of the following:
1. The rhetorical or wording distinction matches the requested difficulty: "{difficulty}".
2. The closeness of answer choices matches the requested difficulty.
3. The distractors are appropriately challenging for the requested difficulty.
4. The item is neither trivially easy nor unfairly difficult.

D. ANSWER OPTION QUALITY

Check all of the following:
1. There are exactly four answer choices.
2. Each answer choice is well-formed and usable in context.
3. No answer choice is duplicated or near-duplicated.
4. No answer choice overlaps so much with another that both could seem correct.
5. All answer choices are plausible in context.
6. Exactly one answer choice is clearly correct.
7. The incorrect choices are definitively wrong, not merely less stylish.
8. The options are parallel enough in form to avoid giving away the answer.

E. CORRECT ANSWER VALIDITY

Check all of the following:
1. The marked correct answer actually produces the most effective result for the stated skill.
2. The correct answer is the best and only correct answer.
3. None of the incorrect answers can reasonably compete with the correct answer.
4. The correct answer matches the intended question type.

F. EXPLANATION VALIDITY

Check all of the following:
1. The explanation correctly states why the correct answer is correct.
2. The explanation correctly explains why each incorrect answer is wrong.
3. The explanation is grammatically correct and clear.
4. The explanation does not contradict the text.
5. The explanation accurately identifies the relevant rhetorical, organizational, or wording principle.

G. LANGUAGE AND CLARITY CHECK

Check all of the following across the sentence, question, options, and explanation:
1. No grammar errors outside intentional answer-choice differences
2. No spelling errors
3. No awkward or unnatural phrasing that undermines the item
4. No broken logic or incomplete structure
5. No unclear references
6. No accidental ambiguity that makes multiple answers plausible

--------------------------------------------------
FAIL CONDITIONS
--------------------------------------------------

The item must FAIL if any of the following are true:
- The sentence or passage does not support the requested question type.
- The question is vague, ambiguous, or poorly worded.
- The question does not match the requested Expression of Ideas skill.
- The difficulty does not match the requested level.
- There are duplicate or near-duplicate options.
- More than one answer could reasonably be correct.
- The marked correct answer is wrong or weak.
- The explanation is incomplete, wrong, or misleading.
- There are meaningful clarity or phrasing issues.
- The item depends mainly on arbitrary style preference rather than a defensible rhetorical principle.

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
      "category": "item | question | difficulty | options | answer | explanation | clarity",
      "issue": "Specific problem",
      "severity": "major | minor"
    }}
  ],
  "summary_reason": "Brief overall reason for failure",
  "repair_recommendation": {{
    "repair_target": "sentence | question | options | explanation | multiple",
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
    "item_valid": true,
    "question_valid": true,
    "difficulty_aligned": true,
    "options_valid": true,
    "correct_answer_valid": true,
    "explanation_valid": true,
    "clarity_valid": true
  }},
  "notes": "Brief explanation of why the item passes"
}}

STRICT RULES
- Use only the provided sentence, revision target, and question data.
- Do not rewrite the item.
- Do not generate a new question.
- Do not silently fix errors.
- If there is any meaningful ambiguity, return FAIL.
- Be conservative: a weak SAT item should not pass.
- Return JSON only.
"""