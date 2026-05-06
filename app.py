
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import itertools

# -----------------------------
# UI STYLE
# -----------------------------
st.set_page_config(page_title="Lernanalyse Dashboard", layout="wide")

st.markdown("""
<style>
.stApp { background-color: white; color: black;}
.block-container { padding-top: 2rem; }
h1,h2,h3 { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DEMO DATA
# -----------------------------
def generate_demo_data():
    np.random.seed(42)
    from datetime import datetime
    import calendar

    today = datetime.today()

    start_date = pd.Timestamp(today.year, today.month, 1)
    end_date = pd.Timestamp(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

    dates = pd.date_range(start=start_date, end=end_date)
    students = ["Lena", "Marvin", "Sara", "Abu"]
    topics = ["Addition & Subtraktion", "Multiplikation"]

    data = []
    for s in students:
        base = np.random.uniform(40, 60)
        trend = np.random.uniform(0.2, 1.0)

        for i, d in enumerate(dates):
            score = base + trend * i + np.random.normal(0, 3)
            data.append([
                s, d,
                max(0, min(100, score)),
                np.random.uniform(10, 60),
                np.random.uniform(20, 80),
                np.random.choice(topics)
            ])

    return pd.DataFrame(data, columns=[
        "student_id", "date", "score", "learning_time", "logged_time", "topic"
    ])

# -----------------------------
# LERNTYPEN
# -----------------------------
def classify_learning_types(df):
    mean = df.groupby("student_id")["score"].mean()
    q1, q2 = mean.quantile(0.33), mean.quantile(0.66)

    def lab(x):
        if x <= q1:
            return "Leistungsschwach"
        elif x <= q2:
            return "Durchschnittlich"
        return "Stark"

    return {k: lab(v) for k, v in mean.items()}

# -----------------------------
# MEAN
# -----------------------------
def mean_df(df):
    return df.groupby("date")["score"].mean().reset_index()

# -----------------------------
# APP
# -----------------------------
def main():
    st.title("📊 Lernanalyse Dashboard")

    df = generate_demo_data()
    types_global = classify_learning_types(df)

    # FILTER
    topics = df["topic"].unique()
    sel_topics = st.sidebar.multiselect("📚 Themen", topics, list(topics))

    plot_topics = st.sidebar.multiselect("📈 Themen im Graph", topics, list(topics))

    date_range = st.sidebar.date_input(
        "📅 Zeitraum (z. B. 01. Jun 24 – 30. Jun 24)",
        [df["date"].min(), df["date"].max()]
)

    students = df["student_id"].unique()

    sel_students = st.sidebar.multiselect(
        "👩‍🎓 Schüler",
        students,
        list(students)
    )

    type_opts = sorted(set(types_global.values()))
    sel_types = st.sidebar.multiselect("🧠 Performanz", type_opts, type_opts)

    # FILTER DATA
    df_f = df.copy()
    df_f = df_f[df_f["topic"].isin(sel_topics)]

    if len(date_range) == 2:
        df_f = df_f[
            (df_f["date"] >= pd.to_datetime(date_range[0])) &
            (df_f["date"] <= pd.to_datetime(date_range[1]))
        ]

    df_f = df_f[df_f["student_id"].isin(sel_students)]

    sel_students_graph = [s for s in sel_students if types_global[s] in sel_types]

    # ---------------- GRAPH ----------------
    students_u = df["student_id"].unique()
    topics_u = df["topic"].unique()

    combinations = list(itertools.product(students_u, topics_u))

    palette = [
        "blue", "cyan", "green", "lime",
        "red", "silver", "orange", "yellow"
    ]

    color_map = dict(zip(combinations, palette))

    fig = go.Figure()

    for s in sel_students_graph:
        for t in plot_topics:
            d = df_f[(df_f["student_id"] == s) & (df_f["topic"] == t)]
            if len(d) == 0:
                continue

            fig.add_trace(go.Scatter(
                 x=d["date"],
                y=d["score"],
                mode="lines+markers",
                name=f"{s} | {t}",
                line=dict(color=color_map.get((s, t)))
            ))
#Gesammtmittelwert
    m = mean_df(df)

    fig.add_trace(go.Scatter(
        x=m["date"],
        y=m["score"],
        name="Gesamtmittelwert",
        line=dict(
            color="pink", dash="dash", width=3
            )
    ))

    st.plotly_chart(fig, use_container_width=True)

    # TABS
    tab1, tab3, tab4 = st.tabs(["📊 Daten", "🧠 Performanz", "⏱ Zeiten"])

    with tab1:
        df_display = df_f.copy()

        # Datum formatieren
        df_display["date"] = pd.to_datetime(df_display["date"]).dt.strftime("%d. %B %y")

        # Minuten-Spalten formatieren
        for col in ["learning_time", "logged_time"]:
            df_display[col] = df_display[col].round(0).astype(int).astype(str) + " Min."

        st.dataframe(df_display)


    with tab3:
        st.write(pd.DataFrame(list(types_global.items()), columns=["Schüler", "Typ"]))

    with tab4:
        time_df = df_f.groupby("student_id")[["learning_time", "logged_time"]].mean().round(0)

        for col in time_df.columns:
            time_df[col] = time_df[col].map(lambda x: f"{int(x)} Min.")

        st.dataframe(time_df)

    st.markdown("""
<style>
/* MAIN AREA */
.stApp {
    background-color: white;
    color: black;
}

.block-container {
    padding-top: 2rem;
}

/* SIDEBAR HINTERGRUND */
[data-testid="stSidebar"] {
    background-color: #000000;
}

/* SIDEBAR TEXT */
[data-testid="stSidebar"] * {
    color: white;
}

/* HEADINGS */
h1, h2, h3, p, span, label {
    color: black;
}

/* TABLES */
th, td {
    color: black;
}
</style>
""", unsafe_allow_html=True)
if __name__ == "__main__":
    main()
