import json
import re

import joblib
import numpy as np
import streamlit as st


st.set_page_config(
    page_title="Avocado Nutrient Yield Potential DST",
    page_icon="🥑",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Model and metadata
# ---------------------------------------------------------------------------

@st.cache_resource
def load_assets():
    model = joblib.load("yield_model.joblib")

    with open("model_metadata.json", "r", encoding="utf-8") as file:
        metadata = json.load(file)

    return model, metadata


try:
    model, meta = load_assets()
except Exception as error:
    st.error(
        "The yield model could not be loaded. Confirm that yield_model.joblib "
        "and model_metadata.json are in the same GitHub folder as app.py."
    )
    st.exception(error)
    st.stop()


# ---------------------------------------------------------------------------
# Weighted nutrient-profile reference values
#
# Method:
#   1. Each nutrient scores 100% inside its modeled high-yield range.
#   2. Outside that range, the score declines linearly toward 0% at an
#      outer reference boundary.
#   3. Overall nutrient yield potential is the weighted average of all
#      12 nutrient scores.
#
# Copper note:
# The earlier spreadsheet listed a high-yield low of 4 ppm and an outer-low
# anchor of 5 ppm. Because an outer boundary cannot sit inside the high-yield
# range, the observed low value of 1.8 ppm is used here as the lower anchor.
# The copper weight and high-yield range remain unchanged.
# ---------------------------------------------------------------------------

NUTRIENTS = [
    {
        "id": "N",
        "name": "Nitrogen",
        "unit": "%",
        "default": 2.52,
        "low": 2.165,
        "high": 2.80,
        "outer_low": 1.90,
        "outer_high": 3.025,
        "weight": 0.08878529631430536,
        "step": 0.01,
        "format": "%.3f",
    },
    {
        "id": "P",
        "name": "Phosphorus",
        "unit": "%",
        "default": 0.14,
        "low": 0.13,
        "high": 0.158,
        "outer_low": 0.11,
        "outer_high": 0.24,
        "weight": 0.10206464090615894,
        "step": 0.001,
        "format": "%.3f",
    },
    {
        "id": "K",
        "name": "Potassium",
        "unit": "%",
        "default": 0.85,
        "low": 0.72,
        "high": 1.00,
        "outer_low": 0.47,
        "outer_high": 1.65,
        "weight": 0.07200285888370470,
        "step": 0.01,
        "format": "%.3f",
    },
    {
        "id": "Ca",
        "name": "Calcium",
        "unit": "%",
        "default": 2.00,
        "low": 1.535,
        "high": 2.20,
        "outer_low": 0.91,
        "outer_high": 2.38,
        "weight": 0.14505003572801944,
        "step": 0.01,
        "format": "%.3f",
    },
    {
        "id": "Mg",
        "name": "Magnesium",
        "unit": "%",
        "default": 0.59,
        "low": 0.54,
        "high": 0.65,
        "outer_low": 0.36,
        "outer_high": 0.96,
        "weight": 0.07715444384878066,
        "step": 0.01,
        "format": "%.3f",
    },
    {
        "id": "Zn",
        "name": "Zinc",
        "unit": "ppm",
        "default": 30.8,
        "low": 24.0,
        "high": 55.0,
        "outer_low": 18.0,
        "outer_high": 99.6,
        "weight": 0.14322431944543490,
        "step": 0.1,
        "format": "%.1f",
    },
    {
        "id": "Mn",
        "name": "Manganese",
        "unit": "ppm",
        "default": 84.0,
        "low": 64.5,
        "high": 140.5,
        "outer_low": 39.0,
        "outer_high": 253.4,
        "weight": 0.09443066043366831,
        "step": 1.0,
        "format": "%.1f",
    },
    {
        "id": "Fe",
        "name": "Iron",
        "unit": "ppm",
        "default": 57.0,
        "low": 51.0,
        "high": 69.05,
        "outer_low": 45.0,
        "outer_high": 112.9,
        "weight": 0.07744318350671484,
        "step": 0.1,
        "format": "%.1f",
    },
    {
        "id": "Cu",
        "name": "Copper",
        "unit": "ppm",
        "default": 7.1,
        "low": 4.0,
        "high": 10.0,
        "outer_low": 1.8,
        "outer_high": 12.0,
        "weight": 0.056303049654797516,
        "step": 0.1,
        "format": "%.1f",
    },
    {
        "id": "B",
        "name": "Boron",
        "unit": "ppm",
        "default": 37.0,
        "low": 29.0,
        "high": 45.0,
        "outer_low": 15.9,
        "outer_high": 84.0,
        "weight": 0.07225987287962840,
        "step": 0.1,
        "format": "%.1f",
    },
    {
        "id": "S",
        "name": "Sulfur",
        "unit": "%",
        "default": 0.40,
        "low": 0.34,
        "high": 0.447,
        "outer_low": 0.23,
        "outer_high": 0.51,
        "weight": 0.04098846957115350,
        "step": 0.001,
        "format": "%.3f",
    },
    {
        "id": "Cl",
        "name": "Chloride",
        "unit": "%",
        "default": 0.345,
        "low": 0.26,
        "high": 0.671,
        "outer_low": 0.07243,
        "outer_high": 0.8989,
        "weight": 0.03029316882763348,
        "step": 0.001,
        "format": "%.3f",
    },
]


# ---------------------------------------------------------------------------
# Scoring and model helper functions
# ---------------------------------------------------------------------------

def clamp(value, minimum=0.0, maximum=1.0):
    return max(minimum, min(maximum, value))


def element_score(nutrient, value):
    """Return a nutrient suitability score between 0.0 and 1.0."""
    if not np.isfinite(value):
        return 0.0

    low = nutrient["low"]
    high = nutrient["high"]
    outer_low = nutrient["outer_low"]
    outer_high = nutrient["outer_high"]

    if low <= value <= high:
        return 1.0

    if value < low:
        if outer_low >= low:
            return 0.0

        return clamp((value - outer_low) / (low - outer_low))

    if outer_high <= high:
        return 0.0

    return clamp((outer_high - value) / (outer_high - high))


def score_status(nutrient, value, score):
    """Return a direction-aware nutrient status and display color."""
    if nutrient["low"] <= value <= nutrient["high"]:
        return "Optimal", "#4c9b57"

    if value < nutrient["low"]:
        if score >= 0.70:
            return "Slightly limiting", "#b18d18"

        if score >= 0.40:
            return "Limiting", "#d87827"

        return "Strongly limiting", "#bd493d"

    if score >= 0.70:
        return "Slightly in excess", "#b18d18"

    if score >= 0.40:
        return "Excess", "#d87827"

    return "Strongly in excess", "#bd493d"


def overall_interpretation(potential):
    if potential >= 90:
        return (
            "Very high potential",
            "#4c9b57",
            "The nutrient profile closely matches the modeled high-yield "
            "profile. Other orchard factors may still constrain production.",
        )

    if potential >= 75:
        return (
            "High potential",
            "#7c9638",
            "The overall nutrient profile is favorable, but one or more "
            "elements may be below the target range or in excess. Review "
            "the lowest scores.",
        )

    if potential >= 55:
        return (
            "Moderate potential",
            "#d87827",
            "Several nutrient values differ from the modeled high-yield "
            "profile. Prioritize diagnosis of the most limiting or excessive "
            "elements.",
        )

    return (
        "Low potential",
        "#bd493d",
        "The nutrient profile differs substantially from the modeled "
        "high-yield profile. Confirm sampling, units and laboratory results "
        "before changing management.",
    )


def normalized_text(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def nutrient_id_for_feature(feature):
    """Match model feature names to the 12 nutrient input IDs."""
    text = normalized_text(feature)

    if "chloride" in text or "chlorine" in text or text in {
        "cl",
        "clpct",
        "clpercent",
    }:
        return "Cl"

    if "nitrogen" in text or text in {"n", "npct", "npercent"}:
        return "N"

    if "phosphorus" in text or text in {"p", "ppct", "ppercent"}:
        return "P"

    if "potassium" in text or text in {"k", "kpct", "kpercent"}:
        return "K"

    if "calcium" in text or text in {"ca", "capct", "capercent"}:
        return "Ca"

    if "magnesium" in text or text in {"mg", "mgpct", "mgpercent"}:
        return "Mg"

    if "zinc" in text or text in {"zn", "znppm"}:
        return "Zn"

    if "manganese" in text or text in {"mn", "mnppm"}:
        return "Mn"

    if "iron" in text or text in {"fe", "feppm"}:
        return "Fe"

    if "copper" in text or text in {"cu", "cuppm"}:
        return "Cu"

    if "boron" in text or text in {"b", "bppm"}:
        return "B"

    if "sulfur" in text or "sulphur" in text or text in {
        "s",
        "spct",
        "spercent",
        "sppm",
        "sreported",
    }:
        return "S"

    return None


def predict_yield(entered_values):
    """Use model metadata order so the saved model receives the right columns."""
    model_inputs = []
    unmatched_features = []

    for feature in meta.get("features", []):
        nutrient_id = nutrient_id_for_feature(feature)

        if nutrient_id in entered_values:
            model_inputs.append(entered_values[nutrient_id])
            continue

        defaults = meta.get("defaults", {})

        if feature in defaults:
            model_inputs.append(float(defaults[feature]))
            unmatched_features.append(feature)
            continue

        raise ValueError(
            f"Could not match model feature '{feature}' to a nutrient input."
        )

    if not model_inputs:
        raise ValueError("No model features were found in model_metadata.json.")

    input_array = np.asarray([model_inputs], dtype=float)
    prediction = np.asarray(model.predict(input_array)).reshape(-1)

    if prediction.size == 0:
        raise ValueError("The model returned no prediction.")

    return max(0.0, float(prediction[0])), unmatched_features


def reset_inputs():
    for nutrient in NUTRIENTS:
        st.session_state[f"input_{nutrient['id']}"] = nutrient["default"]


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        --avocado-dark: #244b2f;
        --avocado: #4f7f3c;
        --avocado-light: #9fbe63;
        --flesh: #d9e98a;
        --cream: #fffdf5;
        --gold: #f3c969;
        --ink: #213126;
        --muted: #667269;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 3%, rgba(217, 233, 138, 0.42), transparent 24%),
            radial-gradient(circle at 92% 0%, rgba(159, 190, 99, 0.28), transparent 22%),
            linear-gradient(180deg, #f9faed 0%, #eef4df 46%, #fffdf7 100%);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #1f452b 0%, #4f7f3c 60%, #7e9f4c 100%);
        color: white;
        padding: 30px 34px;
        border-radius: 24px;
        margin-bottom: 18px;
        box-shadow: 0 18px 45px rgba(36, 75, 47, 0.22);
    }

    .hero::after {
        content: "🥑";
        position: absolute;
        right: 32px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 7.2rem;
        filter: drop-shadow(0 14px 18px rgba(0, 0, 0, 0.22));
    }

    .hero-kicker {
        display: inline-block;
        padding: 7px 11px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.13);
        border: 1px solid rgba(255, 255, 255, 0.20);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hero h1 {
        max-width: 780px;
        margin: 13px 0 8px;
        font-size: clamp(2rem, 4vw, 3.6rem);
        line-height: 1.02;
    }

    .hero p {
        max-width: 760px;
        margin: 0;
        color: rgba(255, 255, 255, 0.88);
        font-size: 1rem;
        line-height: 1.55;
    }

    .notice {
        background: #fff8dc;
        border: 1px solid #ecd886;
        border-radius: 15px;
        padding: 13px 16px;
        color: #5b4b1f;
        margin: 4px 0 20px;
        line-height: 1.5;
    }

    .section-card {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid rgba(79, 127, 60, 0.16);
        border-radius: 20px;
        padding: 18px 20px 8px;
        margin-bottom: 14px;
        box-shadow: 0 12px 34px rgba(36, 75, 47, 0.09);
    }

    .section-card h2 {
        color: var(--avocado-dark);
        margin: 0;
        font-size: 1.35rem;
    }

    .section-card p {
        color: var(--muted);
        margin: 5px 0 4px;
        font-size: 0.92rem;
    }

    div[data-testid="stNumberInput"] {
        background: rgba(255, 255, 255, 0.70);
        border: 1px solid #dfe8d5;
        border-radius: 15px;
        padding: 11px 12px 8px;
        min-height: 126px;
    }

    div[data-testid="stNumberInput"] input {
        background: #fffceb;
        border-color: #cad7bf;
        font-weight: 750;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(79, 127, 60, 0.18);
        border-radius: 17px;
        padding: 16px 18px;
        box-shadow: 0 10px 26px rgba(36, 75, 47, 0.08);
    }

    .potential-card {
        background: linear-gradient(145deg, #ffffff, #f0f7e8);
        border: 1px solid #bfd5ae;
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 16px 38px rgba(36, 75, 47, 0.12);
        text-align: center;
    }

    .gauge {
        --score: 0;
        --gauge-color: #4c9b57;
        width: 210px;
        height: 210px;
        margin: 4px auto 16px;
        border-radius: 50%;
        background: conic-gradient(
            var(--gauge-color) calc(var(--score) * 1%),
            #e5ebdf 0
        );
        display: grid;
        place-items: center;
        position: relative;
    }

    .gauge::before {
        content: "";
        width: 158px;
        height: 158px;
        border-radius: 50%;
        background: linear-gradient(180deg, #ffffff, #f8fbf4);
        box-shadow: inset 0 0 0 1px #e2eadb;
    }

    .gauge-content {
        position: absolute;
        text-align: center;
    }

    .gauge-score {
        display: block;
        color: var(--avocado-dark);
        font-size: 3rem;
        font-weight: 850;
        line-height: 1;
    }

    .gauge-label {
        color: var(--muted);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .category {
        display: inline-block;
        border-radius: 13px;
        padding: 9px 14px;
        font-weight: 850;
        margin-bottom: 10px;
    }

    .interpretation {
        color: var(--muted);
        line-height: 1.55;
        margin: 3px auto 0;
        max-width: 720px;
    }

    .priority-item {
        background: #f8faf5;
        border: 1px solid #e1e9dc;
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 9px;
    }

    .priority-row {
        display: flex;
        justify-content: space-between;
        gap: 14px;
        align-items: center;
    }

    .priority-name {
        color: var(--avocado-dark);
        font-weight: 800;
    }

    .priority-score {
        font-weight: 850;
        white-space: nowrap;
    }

    .priority-meta {
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 3px;
    }

    .score-bar {
        height: 8px;
        background: #e8eee3;
        border-radius: 999px;
        overflow: hidden;
        margin-top: 9px;
    }

    .score-fill {
        height: 100%;
        border-radius: inherit;
    }

    .small-note {
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.45;
    }

    .footer-note {
        color: var(--muted);
        text-align: center;
        font-size: 0.80rem;
        padding-top: 22px;
    }

    div.stButton > button[kind="primary"] {
        background: var(--avocado-dark);
        border-color: var(--avocado-dark);
        font-weight: 800;
        border-radius: 13px;
        min-height: 46px;
    }

    div.stButton > button[kind="secondary"] {
        border-radius: 13px;
        font-weight: 750;
        min-height: 42px;
    }

    @media (max-width: 760px) {
        .hero {
            padding: 25px 22px;
        }

        .hero::after {
            opacity: 0.20;
            right: 12px;
            font-size: 5.5rem;
        }

        .hero h1,
        .hero p {
            position: relative;
            z-index: 1;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">🥑 Grower Decision Support Tool</div>
        <h1>Avocado Nutrient Yield Potential</h1>
        <p>
            Enter leaf-analysis values for 12 nutrients. The main Yield
            Potential score is a model-weighted measure of how closely the
            nutrient profile matches the modeled high-yield profile.
        </p>
    </div>

    <div class="notice">
        <strong>Important:</strong> This tool estimates nutrient-profile
        suitability. It does not guarantee actual yield, which can also be
        constrained by irrigation, crop load, climate, salinity, pests,
        disease, rootstock, cultivar and tree age.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Nutrient inputs
# ---------------------------------------------------------------------------

header_col, reset_col = st.columns([4, 1])

with header_col:
    st.markdown(
        """
        <div class="section-card">
            <h2>Leaf nutrient inputs</h2>
            <p>
                Enter N, P, K, Ca, Mg, S and Cl as percent. Enter Zn, Mn,
                Fe, Cu and B as ppm. Modeled high-yield ranges are shown
                beneath each field.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with reset_col:
    st.write("")
    st.write("")
    st.button(
        "Reset defaults",
        on_click=reset_inputs,
        use_container_width=True,
    )


entered = {}
input_columns = st.columns(3)

for index, nutrient in enumerate(NUTRIENTS):
    key = f"input_{nutrient['id']}"

    if key not in st.session_state:
        st.session_state[key] = nutrient["default"]

    with input_columns[index % 3]:
        entered[nutrient["id"]] = float(
            st.number_input(
                f"{nutrient['name']} ({nutrient['id']}) — {nutrient['unit']}",
                min_value=0.0,
                step=nutrient["step"],
                format=nutrient["format"],
                key=key,
                help=(
                    f"Modeled high-yield range: {nutrient['low']:g} to "
                    f"{nutrient['high']:g} {nutrient['unit']}"
                ),
            )
        )

        st.caption(
            f"High-yield range: {nutrient['low']:g}–"
            f"{nutrient['high']:g} {nutrient['unit']}"
        )


analyze = st.button(
    "Analyze nutrient yield potential",
    type="primary",
    use_container_width=True,
)


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

if analyze:
    scored_nutrients = []
    weighted_total = 0.0

    for nutrient in NUTRIENTS:
        score = element_score(nutrient, entered[nutrient["id"]])
        status, color = score_status(
            nutrient,
            entered[nutrient["id"]],
            score,
        )
        contribution = score * nutrient["weight"]
        weighted_total += contribution

        scored_nutrients.append(
            {
                **nutrient,
                "entered": entered[nutrient["id"]],
                "score": score,
                "status": status,
                "color": color,
                "contribution": contribution,
            }
        )

    nutrient_potential = clamp(weighted_total) * 100.0
    category, category_color, interpretation = overall_interpretation(
        nutrient_potential
    )

    predicted_yield = None
    unmatched_features = []
    prediction_error = None

    try:
        predicted_yield, unmatched_features = predict_yield(entered)
    except Exception as error:
        prediction_error = str(error)

    reference_maximum = meta.get("yield_practical_max_95th_percentile")

    st.markdown("---")
    st.subheader("Results")

    with st.container(border=True):
        st.metric(
            label="Yield potential",
            value=f"{nutrient_potential:.0f}%",
            help=(
                "Weighted nutrient-profile suitability based on the 12 "
                "model-derived nutrient weights."
            ),
        )
        st.progress(int(round(nutrient_potential)))

        if nutrient_potential >= 90:
            st.success(f"**{category}**")
        elif nutrient_potential >= 75:
            st.info(f"**{category}**")
        elif nutrient_potential >= 55:
            st.warning(f"**{category}**")
        else:
            st.error(f"**{category}**")

        st.write(interpretation)

    st.write("")

    metric_columns = st.columns(3)

    with metric_columns[0]:
        st.metric(
            "Weighted nutrient potential",
            f"{nutrient_potential:.0f}%",
            help=(
                "Weighted average of the 12 individual nutrient suitability "
                "scores."
            ),
        )

    with metric_columns[1]:
        if predicted_yield is not None:
            st.metric(
                "Predicted yield",
                f"{predicted_yield:,.1f} kg",
                help=(
                    "Separate prediction from the saved nutrient-interaction "
                    "yield model."
                ),
            )
        else:
            st.metric("Predicted yield", "Unavailable")

    with metric_columns[2]:
        if reference_maximum is not None:
            st.metric(
                "Reference maximum",
                f"{float(reference_maximum):,.1f} kg",
                help=(
                    "The practical 95th-percentile reference stored in the "
                    "model metadata."
                ),
            )
        else:
            st.metric("Reference maximum", "Not listed")

    st.progress(int(round(nutrient_potential)))

    if prediction_error:
        st.warning(
            "The weighted nutrient score was calculated successfully, but "
            f"the separate kilogram prediction was unavailable: "
            f"{prediction_error}"
        )

    if unmatched_features:
        st.caption(
            "The saved model used metadata defaults for these unmatched "
            "features: " + ", ".join(unmatched_features)
        )

    st.write("")
    result_left, result_right = st.columns([1.15, 0.85])

    with result_left:
        st.subheader("Nutrient suitability scores")

        for nutrient in scored_nutrients:
            score_percent = int(round(nutrient["score"] * 100))

            with st.container(border=True):
                st.markdown(
                    f"**{nutrient['name']} ({nutrient['id']}) — "
                    f"{score_percent}% suitability**"
                )
                st.caption(
                    f"{nutrient['status']}  |  "
                    f"Entered: {nutrient['entered']:g} "
                    f"{nutrient['unit']}  |  "
                    f"Target: {nutrient['low']:g}–"
                    f"{nutrient['high']:g} {nutrient['unit']}  |  "
                    f"Weight: {nutrient['weight'] * 100:.1f}%"
                )
                st.progress(score_percent)

    with result_right:
        st.subheader("Priority review")

        priorities = sorted(
            scored_nutrients,
            key=lambda item: (item["score"], -item["weight"]),
        )[:4]

        for rank, nutrient in enumerate(priorities, start=1):
            direction = "within range"

            if nutrient["entered"] < nutrient["low"]:
                direction = "below modeled range"
            elif nutrient["entered"] > nutrient["high"]:
                direction = "above modeled range"

            score_percent = int(round(nutrient["score"] * 100))

            with st.container(border=True):
                st.markdown(
                    f"**{rank}) {nutrient['name']} — "
                    f"{score_percent}% suitability**"
                )
                st.caption(
                    f"{nutrient['status']} · {direction}"
                )
                st.progress(score_percent)

        st.caption(
            "Begin investigation with the lowest-scoring elements, but "
            "consider soil conditions, irrigation water, salinity, crop "
            "load and local agronomic advice before changing fertilizer "
            "rates."
        )

    with st.expander("How the weighted Yield Potential score is calculated"):
        st.write(
            "Each nutrient receives a 0–100% suitability score. A value "
            "inside its modeled high-yield range receives 100%. Outside that "
            "range, the score declines linearly toward zero at the outer "
            "reference boundary."
        )

        st.write(
            "The 12 scores are multiplied by their model-derived importance "
            "weights and added together. The weights sum to 100%, so the "
            "result is the overall nutrient-based Yield Potential percentage."
        )

        st.write(
            "This weighted percentage measures nutrient-profile suitability. "
            "It is separate from the interaction model's predicted yield in "
            "kilograms."
        )

    with st.expander("Model information"):
        model_information = {
            "Selected model": meta.get("model_name", "Not listed"),
            "Training records": meta.get("training_records", "Not listed"),
            "Holdout metrics": meta.get("test_metrics", "Not listed"),
            "Weighted nutrient count": len(NUTRIENTS),
            "Excluded": ["Year", "Sodium"],
            "Included with caution": [
                "Chloride — fewer usable observations"
            ],
            "Sulfur unit": "Percent",
            "Yield-potential method": (
                "Weighted average of 12 nutrient suitability scores"
            ),
        }

        st.json(model_information)


st.markdown(
    """
    <div class="footer-note">
        Avocado Nutrient Yield-Potential DST · Sodium excluded · Chloride
        included · Sulfur entered as percent · Screening and prioritization
        tool, not a stand-alone fertilizer prescription
    </div>
    """,
    unsafe_allow_html=True,
)
