from collections import Counter
import requests
import streamlit as st

from database import init_db, save_results, load_history, DB_FILE

API_URL = "http://127.0.0.1:8000/analyze"

init_db()

st.title("📑 Customer Feedback Analyzer")
st.write(
    "Paste your customer reviews below, "
    "one review per line."
)

review_text = st.text_area(
    "Reviews",
    height=200
)

if st.button("Analyze"):
    reviews = [
        line.strip()
        for line in review_text.split("\n")
        if line.strip()
    ]

    if not reviews:
        st.warning("Please paste at least one review.")
    else:
        results = []

        for review in reviews:
            try:
                response = requests.post(
                    API_URL,
                    json={"text": review},
                    timeout=30
                )

                response.raise_for_status()
                data = response.json()

                results.append({
                    "review": review,
                    "label": data["label"],
                    "score": data["score"],
                    "theme": data["theme"]
                })
            except Exception as e:
                results.append({
                    "review": review,
                    "label": "error",
                    "score": 0,
                    "theme": "errro"
                })

                st.error(
                    f"Could not analyze a review: {e}"
                )
        st.session_state.results = results

# Display results if available

if "results" in st.session_state:
    results = st.session_state.results
    st.subheader("Results")
    st.dataframe(results)

    # Calculate summary statistics
    valid_results = [
        r for r in results
        if r["label"] != "error"
    ]

    scores = [
        r["score"] for r in valid_results
    ]

    positive = [
        r for r in valid_results
        if r["label"] == "positive"
    ]

    themes = [
        r["theme"] for r in valid_results
        if r["theme"] != "error"
    ]

    # Summary section
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Reviews",
        len(results)
    )

    if scores:
        col2.metric(
            "Average score",
            round(sum(scores) / len(scores), 1)
        )
        col3.metric(
            "% Positive",
            f"{round(len(positive) / len(valid_results) * 100)}%"
        )

    else:
        col2.metric("Average score", "N/A")
        col3.metric("% Positive", "N/A")

    # Most common feedback theme
    if themes:
        top_theme = Counter(themes).most_common(1)[0][0]
        st.info(
            f"Customers talk most about: **{top_theme}**"
        )

    # Save results to database
    if st.button("💾 Save to database"):
        save_results(results)
        st.success(
            f"Saved {len(results)} reviews to {DB_FILE}"
        )

# Display saved history
with st.expander("📚 Saved history (all reviews in the database)"):
    history = load_history()
    if history:
        st.write(
            f"Total saved so far: {len(history)}"
        )
        st.dataframe([
            {
                "review": row[0],
                "label": row[1],
                "score": row[2],
                "theme": row[3]
            }
            for row in history
        ])
    else:
        st.write(
            "Nothing saved yet. Analyze some reviews and click Save."
        )