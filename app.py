import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Football Player Dashboard", layout="wide")
st.title("⚽ Player Weekly Performance Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    # Load sheets
    sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(sheets.keys())
    selected_sheet = st.selectbox("Select Data Sheet", sheet_names)

    df = sheets[selected_sheet]

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Ensure Player column exists
    if "Player" not in df.columns:
        st.error("No 'Player' column found in this sheet.")
        st.stop()

    # Convert wide format to long format
    df_long = df.melt(
        id_vars=["Player"],
        var_name="Week",
        value_name="Value"
    )

    # Convert Week to numeric
    df_long["Week"] = pd.to_numeric(df_long["Week"], errors="coerce")
    df_long = df_long.dropna(subset=["Week"])

    # Player selection
    player_list = sorted(df_long["Player"].unique())
    selected_player = st.selectbox("Select Player", player_list)

    player_df = df_long[df_long["Player"] == selected_player]
    player_df = player_df.sort_values("Week")

    # Option to ignore zero values
    ignore_zeros = st.checkbox("Ignore Zero Values in Mean/Std Calculation", value=True)

    if ignore_zeros:
        calc_series = player_df[player_df["Value"] > 0]["Value"]
    else:
        calc_series = player_df["Value"]

    mean_val = calc_series.mean()
    std_val = calc_series.std()

    upper = mean_val + std_val
    lower = mean_val - std_val

    # ---- Build Plot ----
    fig = go.Figure()

    # Std Dev Upper Line
    fig.add_trace(
        go.Scatter(
            x=player_df["Week"],
            y=[upper] * len(player_df),
            mode="lines",
            line=dict(width=0),
            showlegend=False
        )
    )

    # Std Dev Lower Line + Fill
    fig.add_trace(
        go.Scatter(
            x=player_df["Week"],
            y=[lower] * len(player_df),
            mode="lines",
            fill="tonexty",
            name="±1 Std Dev",
            fillcolor="rgba(0, 100, 80, 0.2)",
            line=dict(width=0)
        )
    )

    # Mean Line
    fig.add_trace(
        go.Scatter(
            x=player_df["Week"],
            y=[mean_val] * len(player_df),
            mode="lines",
            name="Mean",
            line=dict(dash="dash")
        )
    )

    # Player Weekly Data
    fig.add_trace(
        go.Scatter(
            x=player_df["Week"],
            y=player_df["Value"],
            mode="lines+markers",
            name="Weekly Performance"
        )
    )

    fig.update_layout(
        title=f"Player {selected_player} - Weekly Performance",
        xaxis_title="Week",
        yaxis_title="Value",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display summary stats
    st.subheader("📊 Summary Statistics")
    col1, col2, col3 = st.columns(3)

    col1.metric("Mean", f"{mean_val:,.2f}")
    col2.metric("Std Dev", f"{std_val:,.2f}")
    col3.metric("Weeks Recorded", len(player_df))