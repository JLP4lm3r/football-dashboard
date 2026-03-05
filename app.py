import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Football Player Dashboard", layout="wide")
st.title("⚽ Player Weekly Performance Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(sheets.keys())
    selected_sheet = st.selectbox("Select Data Sheet", sheet_names)

    df = sheets[selected_sheet]
    df.columns = df.columns.astype(str).str.strip()

    if "Player" not in df.columns:
        st.error("No 'Player' column found in this sheet.")
        st.stop()

    # Convert wide format → long format
    df_long = df.melt(
        id_vars=["Player"],
        var_name="Week",
        value_name="Value"
    )

    df_long["Week"] = pd.to_numeric(df_long["Week"], errors="coerce")
    df_long = df_long.dropna(subset=["Week"])

    # Player selection
    player_list = sorted(df_long["Player"].unique())

    selected_players = st.multiselect(
        "Select Players",
        player_list,
        default=player_list[:1]
    )

    if not selected_players:
        st.warning("Please select at least one player.")
        st.stop()

    filtered_df = df_long[df_long["Player"].isin(selected_players)]
    filtered_df = filtered_df.sort_values("Week")

    ignore_zeros = st.checkbox("Ignore Zero Values in Calculations", value=True)
    show_team_mean = st.checkbox("Show Squad Mean Line", value=True)

    fig = go.Figure()

    # --- Plot selected players ---
    for player in selected_players:

        player_df = filtered_df[filtered_df["Player"] == player]

        fig.add_trace(
            go.Scatter(
                x=player_df["Week"],
                y=player_df["Value"],
                mode="lines+markers",
                name=f"Player {player}"
            )
        )

    # --- Squad mean from FULL dataset ---
    if show_team_mean:

        if ignore_zeros:
            calc_df = df_long[df_long["Value"] > 0]
        else:
            calc_df = df_long

        squad_mean_by_week = (
            calc_df.groupby("Week")["Value"]
            .mean()
            .reset_index()
        )

        fig.add_trace(
            go.Scatter(
                x=squad_mean_by_week["Week"],
                y=squad_mean_by_week["Value"],
                mode="lines",
                name="Squad Weekly Mean",
                line=dict(dash="dash", width=3)
            )
        )

    fig.update_layout(
        title="Weekly Player Comparison vs Squad Mean",
        xaxis_title="Week",
        yaxis_title="Value",
        template="plotly_white",
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)