import streamlit as st
import pandas as pd

st.set_page_config(page_title="SAT Question Viewer", layout="wide")

st.title("SAT Question Viewer")

file_path = st.text_input("Excel file path", "Data/shuffled_sat_items.xlsx")

try:
    df = pd.read_excel(file_path)

    st.success(f"Loaded {len(df)} rows")

    col1, col2, col3 = st.columns(3)

    with col1:
        domain_filter = st.selectbox(
            "Domain",
            ["All"] + sorted(df["domain"].dropna().astype(str).unique().tolist())
            if "domain" in df.columns else ["All"]
        )

    with col2:
        qtype_filter = st.selectbox(
            "Question Type",
            ["All"] + sorted(df["question_type"].dropna().astype(str).unique().tolist())
            if "question_type" in df.columns else ["All"]
        )

    with col3:
        difficulty_filter = st.selectbox(
            "Difficulty",
            ["All"] + sorted(df["difficulty"].dropna().astype(str).unique().tolist())
            if "difficulty" in df.columns else ["All"]
        )

    filtered_df = df.copy()

    if domain_filter != "All":
        filtered_df = filtered_df[filtered_df["domain"] == domain_filter]

    if qtype_filter != "All":
        filtered_df = filtered_df[filtered_df["question_type"] == qtype_filter]

    if difficulty_filter != "All":
        filtered_df = filtered_df[filtered_df["difficulty"] == difficulty_filter]

    st.subheader("Table View")
    st.dataframe(filtered_df, use_container_width=True)

    st.subheader("Question Viewer")

    if len(filtered_df) > 0:
        row_index = st.number_input(
            "Select row number",
            min_value=0,
            max_value=len(filtered_df) - 1,
            value=0,
            step=1
        )

        row = filtered_df.iloc[row_index]

        st.markdown(f"**Domain:** {row.get('domain', '')}")
        st.markdown(f"**Question Type:** {row.get('question_type', '')}")
        st.markdown(f"**Difficulty:** {row.get('difficulty', '')}")

        source_text = row.get("source_text", "") if "source_text" in row else ""
        if pd.notna(source_text) and str(source_text).strip():
            st.markdown("### Source Text")
            st.write(source_text)

        sentence = row.get("sentence", "") if "sentence" in row else ""
        if pd.notna(sentence) and str(sentence).strip():
            st.markdown("### Sentence")
            st.write(sentence)

        editable_portion = row.get("editable_portion", "") if "editable_portion" in row else ""
        if pd.notna(editable_portion) and str(editable_portion).strip():
            st.markdown("**Editable Portion:**")
            st.write(editable_portion)

        st.markdown("### Question")
        st.write(row.get("question", ""))

        st.markdown("### Options")
        st.write(f"A. {row.get('option_a', '')}")
        st.write(f"B. {row.get('option_b', '')}")
        st.write(f"C. {row.get('option_c', '')}")
        st.write(f"D. {row.get('option_d', '')}")

        st.markdown(f"**Correct Answer:** {row.get('correct_answer', '')}")

        st.markdown("### Explanation")
        st.write(row.get("explanation", ""))

    else:
        st.info("No rows match the selected filters.")

except Exception as e:
    st.error(f"Could not read file: {e}")