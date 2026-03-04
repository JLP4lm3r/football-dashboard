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

    # Convert wide to long
    df_long = df.melt(
        id_vars=["Player"],
        var_name="Week",
        value_name="Value"
    )

    df_long["Week"] = pd.to_numeric(df_long["Week"], errors="coerce")
    df_long = df_long.dropna(subset=["Week"])

    # 🔥 MULTI-SELECT instead of selectbox
    player_list = sorted(df_long["Player"].unique())
    selected_players = st.multiselect(
        "Select Players",
        player_list,
        default=player_list[:1]  # default first player selected
    )

    if not selected_players:
        st.warning("Please select at least one player.")
        st.stop()

    filtered_df = df_long[df_long["Player"].isin(selected_players)]
    filtered_df = filtered_df.sort_values("Week")

    # Optional: ignore zeros
    ignore_zeros = st.checkbox("Ignore Zero Values in Calculations", value=True)

    fig = go.Figure()

    # --- Plot Each Player ---
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

    # --- Optional Team Mean Line ---
    show_team_mean = st.checkbox("Show Team Mean Line", value=False)

    if show_team_mean:

        if ignore_zeros:
            calc_df = filtered_df[filtered_df["Value"] > 0]
        else:
            calc_df = filtered_df

        team_mean_by_week = (
            calc_df.groupby("Week")["Value"]
            .mean()
            .reset_index()
        )

        fig.add_trace(
            go.Scatter(
                x=team_mean_by_week["Week"],
                y=team_mean_by_week["Value"],
                mode="lines",
                name="Team Weekly Mean",
                line=dict(dash="dash", width=3)
            )
        )

    fig.update_layout(
        title="Weekly Player Comparison",
        xaxis_title="Week",
        yaxis_title="Value",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)