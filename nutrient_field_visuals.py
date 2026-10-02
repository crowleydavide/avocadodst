from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

@st.cache_data(show_spinner=False)
def _load_points(root: Path) -> pd.DataFrame:
    """Load immutable development visualization points once per app process."""
    return pd.read_csv(root / "nutrient_field_visual_points_9_2.csv")

def _weighted_surface(df, xnut, ynut, znut, zslice, xgrid, ygrid):
    """Observed-performance surface: local weighted mean within-year yield percentile.
    Third nutrient acts as a continuous slice weight; this is descriptive, not a model prediction."""
    x=df[xnut].to_numpy(float); y=df[ynut].to_numpy(float); z=df[znut].to_numpy(float)
    perf=df["yield_pct"].to_numpy(float)
    sx=max(np.subtract(*np.nanpercentile(x,[75,25])),1e-9)
    sy=max(np.subtract(*np.nanpercentile(y,[75,25])),1e-9)
    sz=max(np.subtract(*np.nanpercentile(z,[75,25])),1e-9)
    out=np.full((len(ygrid),len(xgrid)),np.nan)
    for j,yg in enumerate(ygrid):
        dx=((x[None,:]-xgrid[:,None])/sx)**2
        dy=((y-yg)/sy)**2
        dz=((z-zslice)/sz)**2
        dist2=dx+dy+dz
        w=np.exp(-dist2/(2*0.65**2))
        den=w.sum(axis=1)
        vals=(w*perf).sum(axis=1)/np.maximum(den,1e-12)
        vals[den<1.5]=np.nan
        out[j,:]=vals
    return out

def render_field_surface(
    field_id: str,
    field: dict,
    values: dict,
    context_year: int,
    root: Path,
    chart_key: str | None = None,
):
    ns=field["nutrients"]
    # For both current prototypes, put the less labile/macronutrient-like axis first where applicable.
    if field_id=="B_Mn_Zn":
        xnut,ynut,znut="B","Zn","Mn"
    else:
        xnut,ynut,znut="Ca","Zn","Mn"
    df=_load_points(root)
    df=df[(df.field_id==field_id)&(df.Year==int(context_year))].dropna(subset=[xnut,ynut,znut,"yield_pct"])
    if len(df)<12:
        st.info("Not enough development observations to render this historical field surface.")
        return
    qx=np.quantile(df[xnut],[.05,.95]); qy=np.quantile(df[ynut],[.05,.95])
    xg=np.linspace(qx[0],qx[1],45); yg=np.linspace(qy[0],qy[1],45)
    sx=float(values[xnut]); sy=float(values[ynut])
    xpad=max((qx[1]-qx[0])*.08,1e-9); ypad=max((qy[1]-qy[0])*.08,1e-9)
    xview=(min(qx[0]-xpad,sx-xpad),max(qx[1]+xpad,sx+xpad))
    yview=(min(qy[0]-ypad,sy-ypad),max(qy[1]+ypad,sy+ypad))
    outside=not (qx[0]<=sx<=qx[1] and qy[0]<=sy<=qy[1])
    zslice=float(values[znut])
    surf=_weighted_surface(df,xnut,ynut,znut,zslice,xg,yg)
    fig=go.Figure()
    fig.add_trace(go.Contour(
        x=xg,y=yg,z=surf,
        colorscale="Viridis",zmin=0,zmax=1,
        contours=dict(start=.2,end=.8,size=.1,showlabels=False),
        colorbar=dict(title="Historical<br>yield percentile"),
        hovertemplate=f"{xnut}: %{{x:.3g}}<br>{ynut}: %{{y:.3g}}<br>Local performance percentile: %{{z:.2f}}<extra></extra>",
    ))
    high=df[df.yield_pct>=2/3]
    fig.add_trace(go.Scatter(
        x=high[xnut],y=high[ynut],mode="markers",
        marker=dict(size=5,color="rgba(255,255,255,0.45)",line=dict(width=.5,color="rgba(0,0,0,.35)")),
        name="Higher-performing observations",
        hovertemplate=f"{xnut}: %{{x:.3g}}<br>{ynut}: %{{y:.3g}}<extra>Top-third observation</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[float(values[xnut])],y=[float(values[ynut])],mode="markers+text",
        marker=dict(size=16,symbol="diamond",color="red",line=dict(width=2,color="white")),
        text=["Your sample"],textposition="top center",name="Your sample",
        hovertemplate=f"Your sample<br>{xnut}: %{{x:.3g}}<br>{ynut}: %{{y:.3g}}<extra></extra>",
    ))
    fig.update_layout(
        title=f"{field['label']} historical nutrient field · example context {context_year}",
        height=430,margin=dict(l=30,r=20,t=60,b=30),
        xaxis=dict(title=f"{xnut} ({'ppm' if xnut in ['B','Zn','Mn'] else '%'})",range=list(xview)),
        yaxis=dict(title=f"{ynut} ({'ppm' if ynut in ['B','Zn','Mn'] else '%'})",range=list(yview)),
        legend=dict(orientation="h",y=-.2),
    )
    # Explicit keys prevent Streamlit DuplicateElementId when the representative
    # context and the exploratory selector happen to render the same year/figure
    # during a single app run.
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        key=chart_key,
    )
    if outside:
        st.warning("Your sample lies outside the central empirical support shown by the colored surface. The axes are expanded to keep the sample visible, but the historical performance surface is not extrapolated into unsupported space.")
    st.caption(
        f"{znut} slice = {zslice:g} {'ppm' if znut in ['B','Zn','Mn'] else '%'}. "
        "Background shows smoothed historical yield percentile within this production year; higher colors indicate higher observed yield rank. "
        "This is descriptive development data, not model-predicted yield. "
        "White points are higher-performing observations (top third within the year); the red diamond is this sample."
    )
