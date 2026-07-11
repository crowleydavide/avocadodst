import json

import joblib

import numpy as np

import streamlit as st


st.set_page_config(
    page_title="Avocado Yield Advisor",
    page_icon="🥑",
    layout="wide",
)


@st.cache_resource
def load_assets():
    model = joblib.load("yield_model.joblib")
    with open("model_metadata.json", "r", encoding="utf-8") as file:
        meta = json.load(file)
    return model, meta


model, meta = load_assets()


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 1.5rem;
    }

    .hero {
        background: linear-gradient(135deg, #173f2a, #3f7d44);
        color: white;
        padding: 28px 32px;
        border-radius: 20px;
        margin-bottom: 20px;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.25rem;
    }

    .hero p {
        opacity: 0.92;
        margin: 0.45rem 0 0;
    }

    .result {
        background: #f1f8ed;
        border: 1px solid #bdd7ac;
        padding: 20px;
        border-radius: 16px;
    }

    .small {
        font-size: 0.88rem;
        color: #4d5e50;
    }
    </style>

    <div class="hero">
        <h1>🥑 Avocado Yield Advisor</h1>
        <p>Nutrient-interaction model trained from the supplied avocado dataset.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


st.info(
    "Research decision-support prototype. Predictions are associations in the "
    "historical dataset, not guaranteed fertilizer-response outcomes."
)


values = []
missing = []
cols = st.columns(3)

for i, feature in enumerate(meta["features"]):
    with cols[i % 3]:
        use_value = st.checkbox(
            f"Enter {feature}",
            value=True,
            key=f"use_{i}",
        )

        if use_value:
            val = st.number_input(
                feature,
                min_value=0.0,
                value=float(meta["defaults"][feature]),
                step=max(float(meta["defaults"][feature]) * 0.02, 0.001),
                format="%.4f" if "(%)" in feature else "%.2f",
                key=f"v_{i}",
            )
            values.append(float(val))
            missing.append(False)
        else:
            values.append(np.nan)
            missing.append(True)


if st.button(
    "Analyze yield potential",
    type="primary",
    use_container_width=True,
):
    x = np.array([values], dtype=float)

    pred = max(0.0, float(model.predict(x)[0]))
    ref = float(meta["yield_practical_max_95th_percentile"])
    potential = min(100.0, 100.0 * pred / ref) if ref > 0 else 0.0

    c1, c2, c3 = st.columns(3)

    c1.metric("Predicted yield", f"{pred:,.1f} kg")
    c2.metric("Yield potential", f"{potential:.0f}%")
    c3.metric("Reference maximum", f"{ref:,.1f} kg")

    st.progress(int(round(potential)))

    st.markdown('<div class="result">', unsafe_allow_html=True)
    st.markdown("### Interpretation")

    if potential >= 80:
        st.write(
            "The nutrient pattern is associated with high yield relative to "
            "the dataset."
        )
    elif potential >= 55:
        st.write(
            "The nutrient pattern is associated with moderate yield, with "
            "possible room for improvement."
        )
    else:
        st.write(
            "The nutrient pattern is associated with lower yield relative to "
            "the dataset."
        )

    st.markdown("</div>", unsafe_allow_html=True)

    flags = []

    for i, feature in enumerate(meta["features"]):
        if np.isnan(values[i]):
            flags.append(
                f"{feature}: missing; the model used its learned median and a "
                "missing-value indicator."
            )
        elif values[i] < meta["p10"][feature]:
            flags.append(
                f"{feature}: below the central historical range."
            )
        elif values[i] > meta["p90"][feature]:
            flags.append(
                f"{feature}: above the central historical range."
            )

    if flags:
        st.subheader("Values to review")

        for flag in flags:
            st.write("• " + flag)
    else:
        st.success(
            "All entered values fall within the central 10th–90th percentile "
            "ranges in the source data."
        )

    st.caption(
        "A value outside the historical range is a review flag, not "
        "automatically a fertilizer recommendation."
    )


with st.expander("Model information"):
    st.json(
        {
            "Selected model": meta["model_name"],
            "Training records": meta["training_records"],
            "Holdout metrics": meta["test_metrics"],
            "Excluded": ["Year", "Sodium"],
            "Included with sparse coverage": ["Chloride"],
            "Sulfur interpretation": "Percent",
        }
    )

