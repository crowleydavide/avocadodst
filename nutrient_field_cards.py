from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import streamlit as st
from nutrient_field_visuals import render_field_surface

FIELD_FLAG_MAP = {
    "B_Mn_Zn": [
        "Review soil pH and root-zone conditions.",
        "Review irrigation, drainage/redox, and root health.",
        "Review soil/leaf B, Mn, and Zn evidence before considering nutrient-specific action.",
        "Review bicarbonate, salinity, and organic-matter context when available.",
    ],
    "Ca_Mn_Zn": [
        "Review soil pH and whether calcium supply or soil structure is actually limiting.",
        "Review irrigation, drainage/redox, salinity/sodium, and feeder-root condition.",
        "Review soil/leaf Ca, Mn, and Zn evidence before considering nutrient-specific action.",
        "Distinguish calcium supply, sodium displacement, structure improvement, and pH correction pathways.",
    ],
}

APP_KEY = {
    "N":"N", "P":"P", "K":"K", "Ca":"CA", "Mg":"MG",
    "Zn":"ZN", "Mn":"MN", "Fe":"FE", "Cu":"CU",
    "B":"B", "Cl":"CL", "S":"S",
}

@st.cache_data(show_spinner=False)
def load_nutrient_field_reference(root: Path) -> dict:
    """Load immutable Pilot 9.2 field calibration once per app process."""
    return json.loads((root / "nutrient_field_reference_9_2.json").read_text())

def classify_field(values: dict, field: dict, context_year: int) -> dict:
    missing=[n for n in field["nutrients"] if values.get(n) is None]
    if missing:
        return {"status":"unavailable","reason":"Missing measured values: "+", ".join(missing)}
    ctx=field["contexts"].get(str(int(context_year)))
    if ctx is None:
        return {"status":"unavailable","reason":"No validated development context is available for that production year."}
    z=np.array([(float(values[n])-field["robust_median"][n])/field["robust_iqr"][n] for n in field["nutrients"]])
    c=np.array([ctx["center_z"][n] for n in field["nutrients"]])
    distance=float(np.linalg.norm(z-c))
    band="Near" if distance<=ctx["near_cut"] else ("Intermediate" if distance<=ctx["far_cut"] else "Far")
    return {"status":"ok","band":band,"distance":distance,"near_cut":ctx["near_cut"],
            "far_cut":ctx["far_cut"],"context_year":int(context_year)}

def classify_context_robustness(values: dict, field: dict) -> dict:
    results=[]
    for y in sorted(map(int,field["contexts"])):
        r=classify_field(values,field,y)
        if r["status"]=="ok":
            results.append(r)
    if not results:
        return {"status":"unavailable","reason":"No validated historical context could be evaluated."}
    counts={b:sum(r["band"]==b for r in results) for b in ("Near","Intermediate","Far")}
    n=len(results); modal=max(counts,key=counts.get); share=counts[modal]/n
    headline=modal if share>=0.80 else "Context-dependent"
    return {"status":"ok","headline":headline,"counts":counts,"n_contexts":n,
            "modal_band":modal,"modal_share":share,"contexts":results}

def _robustness_text(r):
    c=r["counts"]; n=r["n_contexts"]
    return f"Near {c['Near']}/{n} · Intermediate {c['Intermediate']}/{n} · Far {c['Far']}/{n}"

def _result_support_text(r):
    if r["headline"]=="Context-dependent":
        return (
            "The nutrient-field position varies among historical production contexts, "
            "so a single Near/Intermediate/Far classification is not supported."
        )
    band=r["headline"]; n=r["n_contexts"]; count=r["counts"][band]
    if count==n:
        return (
            f"This nutrient pattern was {band} relative to the high-performance nutrient field "
            f"in all {n} validated historical contexts."
        )
    return (
        f"This nutrient pattern was {band} relative to the high-performance nutrient field "
        f"in {count} of {n} validated historical contexts."
    )

def _normalize_field_values(values: dict, measured: dict, nutrients: list[str]) -> dict:
    usable={}
    for n in nutrients:
        k=APP_KEY[n]
        is_measured=bool(measured.get(k, measured.get(n, False)))
        value=values.get(k, values.get(n))
        usable[n]=value if is_measured else None
    return usable

def render_shadow_nutrient_field_cards(values: dict, measured: dict, root: Path) -> dict:
    ref=load_nutrient_field_reference(root)

    st.subheader("Nutrient-field evidence")
    st.caption("Pilot 9.2.3 shadow adviser layer")
    st.write(
        "These cards provide a second, independent view of the leaf analysis. "
        "Individual opportunity curves ask how the frozen model responds when one nutrient changes. "
        "Nutrient fields ask whether the current nutrient combination resembles states historically "
        "associated with higher performance."
    )
    st.warning(
        "Investigation evidence only. Nutrient-field results do not diagnose deficiency, prove nutrient synergy, "
        "predict fertilizer response, or calculate fertilizer rates."
    )

    with st.expander("How to read these cards", expanded=False):
        st.write(
            "The Near/Intermediate/Far result is calculated from the three-nutrient field across all validated "
            "historical contexts. It is not determined by the color underneath the sample marker in the example graphic."
        )
        st.write(
            "The graphic shows one representative historical context only. Its colored surface is a descriptive map "
            "of observed yield rank in development data, not frozen-model predicted yield."
        )
        st.write(
            "When the sample falls outside central empirical support, the axes expand to keep the sample visible but "
            "the colored surface is not extrapolated into unsupported space."
        )

    audit={"schema_version":ref["schema_version"],"mode":"adviser_shadow_context_robustness","fields":{}}

    for field_id in ("B_Mn_Zn","Ca_Mn_Zn"):
        f=ref["fields"][field_id]
        usable=_normalize_field_values(values, measured, f["nutrients"])
        missing=[n for n,v in usable.items() if v is None]

        with st.container(border=True):
            st.markdown(f"**NUTRIENT FIELD — {f['label']}**")
            st.caption("Validated historical field · SHADOW / ADVISER ONLY")

            if missing:
                st.info("Unavailable — missing measured values: "+", ".join(missing))
                audit["fields"][field_id]={"status":"unavailable","missing":missing}
                continue

            robust=classify_context_robustness(usable,f)
            audit["fields"][field_id]=robust

            st.markdown(f"### Nutrient-field result: {robust['headline'].upper()}")
            st.write(_robustness_text(robust))

            message=_result_support_text(robust)
            if robust["headline"]=="Far":
                st.warning(message)
            elif robust["headline"]=="Near":
                st.success(message)
            else:
                st.info(message)

            ordered=sorted(robust["contexts"],key=lambda x:x["distance"])
            rep=ordered[len(ordered)//2]
            mn_value=usable.get("Mn")
            st.markdown("**Historical nutrient-field example**")
            st.caption(
                f"Example context: {rep['context_year']} · Mn = {mn_value:g} ppm. "
                f"The result above uses all {robust['n_contexts']} historical contexts; this graphic shows one representative context."
            )
            render_field_surface(
                field_id,
                f,
                usable,
                rep["context_year"],
                root,
                chart_key=f"nf_rep_surface_{field_id}_{rep['context_year']}",
            )

            with st.expander("Explore historical contexts",expanded=False):
                years=sorted(map(int,f["contexts"]))
                y=st.selectbox("Historical production context",years,key=f"nf_year_{field_id}")
                one=classify_field(usable,f,y)
                st.write(f"**{y}: {one['band']}** · shadow distance {one['distance']:.2f}")
                render_field_surface(
                    field_id,
                    f,
                    usable,
                    y,
                    root,
                    chart_key=f"nf_explore_surface_{field_id}_{y}",
                )
                st.caption(
                    "Use this control to inspect how the field changes among historical contexts. "
                    "A selected year is an exploratory view, not the orchard's definitive production context."
                )

            with st.expander("What to investigate before taking action",expanded=(robust["headline"]=="Far")):
                for item in FIELD_FLAG_MAP[field_id]:
                    st.markdown(f"- {item}")
                st.caption(
                    "Existing uptake and management gates remain authoritative for action planning. "
                    "This field result does not mean that all nutrients in the field should be applied."
                )

            st.caption(
                f"Historical calibration: samples Near this nutrient field reached the top third of within-year "
                f"performance {f['near_top_third_pct']:.1f}% of the time, compared with {f['far_top_third_pct']:.1f}% "
                f"for Far samples. Association only; not a treatment effect."
            )
    return audit
