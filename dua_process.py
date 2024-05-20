import pandas as pd
import streamlit as st
import plotly.figure_factory as ff
import plotly.express as px
from datetime import timedelta

def show():
    st.title("Gantt Chart for Project Timeline")

    # Function to adjust start and finish times for zero-duration tasks
    def adjust_finish_time(start, finish):
        if pd.isna(finish):
            finish = start
        return finish if finish > start else start + timedelta(hours=1)  # Adding 1 hour for visibility
    
    # Custom function to display a static legend
    def display_custom_legend():
        legend_html = """
        <style>
            .legend-container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 20px;
                width: 100%;
            }
            .legend-item {
                display: flex;
                align-items: center;
                margin-right: 20px;
            }
            .legend-box {
                width: 20px;
                height: 20px;
                margin-right: 5px;
            }
            .legend-label {
                font-size: 16px;
            }
        </style>
        <div class="legend-container">
            <div class="legend-item">
                <div class="legend-box" style="background-color: rgb(46, 137, 205);"></div>
                <span class="legend-label">Req to Tracker</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: rgb(114, 44, 121);"></div>
                <span class="legend-label">Data Verification</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: rgb(198, 47, 105);"></div>
                <span class="legend-label">Verified to DAC Send</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: rgb(58, 149, 136);"></div>
                <span class="legend-label">DAC Turn-Around</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: rgb(255, 165, 0);"></div>
                <span class="legend-label">Send DocuSign</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: rgb(75, 0, 130);"></div>
                <span class="legend-label">User DocuSign</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: rgb(220, 20, 60);"></div>
                <span class="legend-label">Foundation Signature</span>
            </div>
        </div>
        """
        st.markdown(legend_html, unsafe_allow_html=True)

    # Function to prepare tasks for the Gantt chart
    def prepare_gantt_chart_data(df):
        # Strip any leading or trailing spaces from column names
        df.columns = df.columns.str.strip()

        # Handle non-date strings and convert dates
        date_columns = [
            'Date Requested', 'Date Added to Tracker', 'Data Verified Date', 'DAC Send Date', 
            'DAC Approval Date', 'DS Send Date', 'Requestor Sign Date', 'BO Sign Date', 
            'Last Collaborator Sign Date', 'Foundation Sign Date'
        ]

        for col in date_columns:
            if col not in df.columns:
                st.error(f"Missing column: {col}")
                return None

            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Calculate the last sign date
        df['Last Sign Date'] = df[['Requestor Sign Date', 'BO Sign Date', 'Last Collaborator Sign Date']].max(axis=1)

        tasks = []
        for index, row in df.iterrows():
            request_id = f"Request {index + 1}"
            phases = [
                ('Req to Tracker', row['Date Requested'], row['Date Added to Tracker']),
                ('Data Verification', row['Date Added to Tracker'], row['Data Verified Date']),
                ('Verified to DAC Send', row['Data Verified Date'], row['DAC Send Date']),
                ('DAC Turn-Around', row['DAC Send Date'], row['DAC Approval Date']),
                ('Send DocuSign', row['DAC Approval Date'], row['DS Send Date']),
                ('User DocuSign', row['DS Send Date'], row['Last Sign Date']),
                ('Foundation Signature', row['Last Sign Date'], row['Foundation Sign Date'])
            ]

            for phase in phases:
                resource, start, finish = phase
                start = pd.to_datetime(start, errors='coerce')
                finish = pd.to_datetime(finish, errors='coerce')
                if pd.notna(start) and pd.notna(finish):
                    finish = adjust_finish_time(start, finish)
                    tasks.append(dict(Task=request_id, Start=start, Finish=finish, Resource=resource))

        return tasks

    # Function to create the Gantt chart without internal legend
    def create_gantt_chart(tasks):
        colors = {
            'Req to Tracker': 'rgb(46, 137, 205)',
            'Data Verification': 'rgb(114, 44, 121)',
            'Verified to DAC Send': 'rgb(198, 47, 105)',
            'DAC Turn-Around': 'rgb(58, 149, 136)',
            'Send DocuSign': 'rgb(255, 165, 0)',
            'User DocuSign': 'rgb(75, 0, 130)',
            'Foundation Signature': 'rgb(220, 20, 60)'
        }
        fig = ff.create_gantt(tasks, colors=colors, index_col='Resource', show_colorbar=False, group_tasks=True)
        fig.update_layout(showlegend=False, yaxis=dict(showticklabels=False))
        return fig
    
    def calculate_durations(df):
        # Ensure all date columns are datetime and handle NaT by filling with previous valid date
        date_columns = [
            'Date Requested', 'Date Added to Tracker', 'Data Verified Date', 'DAC Send Date', 
            'DAC Approval Date', 'DS Send Date', 'Requestor Sign Date', 'BO Sign Date', 
            'Last Collaborator Sign Date', 'Foundation Sign Date'
        ]

        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Calculate the last sign date
        df['Last Sign Date'] = df[['Requestor Sign Date', 'BO Sign Date', 'Last Collaborator Sign Date']].max(axis=1)

        # Calculate durations in days
        df['Req to Tracker Duration'] = (df['Date Added to Tracker'] - df['Date Requested']).dt.days
        df['Data Verification Duration'] = (df['Data Verified Date'] - df['Date Added to Tracker']).dt.days
        df['Verified to DAC Send Duration'] = (df['DAC Send Date'] - df['Data Verified Date']).dt.days
        df['DAC Turn-Around Duration'] = (df['DAC Approval Date'] - df['DAC Send Date']).dt.days
        df['Send DocuSign Duration'] = (df['DS Send Date'] - df['DAC Approval Date']).dt.days
        df['User DocuSign Duration'] = (df['Last Sign Date'] - df['DS Send Date']).dt.days
        df['Foundation Signature Duration'] = (df['Foundation Sign Date'] - df['Last Sign Date']).dt.days

        # Calculate aggregate metrics
        durations_summary = {
            'Req to Tracker': df['Req to Tracker Duration'].sum(),
            'Data Verification': df['Data Verification Duration'].sum(),
            'Verified to DAC Send': df['Verified to DAC Send Duration'].sum(),
            'DAC Turn-Around': df['DAC Turn-Around Duration'].sum(),
            'Send DocuSign': df['Send DocuSign Duration'].sum(),
            'User DocuSign': df['User DocuSign Duration'].sum(),
            'Foundation Signature': df['Foundation Signature Duration'].sum()
        }
        return durations_summary

    def calculate_average_durations(df):
        # Ensure all date columns are datetime and handle NaT by filling with previous valid date
        date_columns = [
            'Date Requested', 'Date Added to Tracker', 'Data Verified Date', 'DAC Send Date', 
            'DAC Approval Date', 'DS Send Date', 'Requestor Sign Date', 'BO Sign Date', 
            'Last Collaborator Sign Date', 'Foundation Sign Date'
        ]

        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Calculate the last sign date
        df['Last Sign Date'] = df[['Requestor Sign Date', 'BO Sign Date', 'Last Collaborator Sign Date']].max(axis=1)

        # Calculate durations in days
        df['Req to Tracker Duration'] = (df['Date Added to Tracker'] - df['Date Requested']).dt.days
        df['Data Verification Duration'] = (df['Data Verified Date'] - df['Date Added to Tracker']).dt.days
        df['Verified to DAC Send Duration'] = (df['DAC Send Date'] - df['Data Verified Date']).dt.days
        df['DAC Turn-Around Duration'] = (df['DAC Approval Date'] - df['DAC Send Date']).dt.days
        df['Send DocuSign Duration'] = (df['DS Send Date'] - df['DAC Approval Date']).dt.days
        df['User DocuSign Duration'] = (df['Last Sign Date'] - df['DS Send Date']).dt.days
        df['Foundation Signature Duration'] = (df['Foundation Sign Date'] - df['Last Sign Date']).dt.days

        # Calculate average durations
        average_durations = {
            'Req to Tracker': df['Req to Tracker Duration'].mean(),
            'Data Verification': df['Data Verification Duration'].mean(),
            'Verified to DAC Send': df['Verified to DAC Send Duration'].mean(),
            'DAC Turn-Around': df['DAC Turn-Around Duration'].mean(),
            'Send DocuSign': df['Send DocuSign Duration'].mean(),
            'User DocuSign': df['User DocuSign Duration'].mean(),
            'Foundation Signature': df['Foundation Signature Duration'].mean()
        }
        return average_durations

    # Function to display pie chart with average durations
    def display_pie_chart(durations):
        labels = list(durations.keys())
        values = list(durations.values())
        colors = ['rgb(46, 137, 205)', 'rgb(114, 44, 121)', 'rgb(198, 47, 105)', 'rgb(58, 149, 136)',
                  'rgb(255, 165, 0)', 'rgb(75, 0, 130)', 'rgb(220, 20, 60)']
        fig = px.pie(names=labels, values=values, title="Average Days Spent in Each Phase", hole=0.3)
        fig.update_traces(texttemplate='%{label}: %{value:.2f}', textinfo='label+value', marker=dict(colors=colors))
        fig.update_layout(showlegend=False, autosize=False, width=1250, height=750)
        st.plotly_chart(fig, use_container_width=True)

    # File uploader and chart logic
    # Define the information to be displayed
    phases = {
        "Added to Tracker": "Date Added to Tracker - Date Requested",
        "Data Verification": "Data Verified Date - Date Added to Tracker",
        "Verified to DAC Send": "DAC Send Date - Data Verified Date",
        "DAC Turn-Around": "DAC Approval Date - DAC Send Date",
        "Send DocuSign": "DS Send Date - DAC Approval Date",
        "User DocuSign": "Last Sign (between requester, BO, Collabs) - DS Send Date",
        "Foundation Signature": "Foundation Signature - Last Sign (between requester, BO, Collabs)"
    }

    # Display the information under an accordion
    with st.expander("**Phases Information**"):
        for phase, description in phases.items():
            st.write(f"**{phase}**: {description}")
    data_file = st.file_uploader("Upload your data file in Excel format:", type=["xlsx"])
    if data_file is not None:
        df = pd.read_excel(data_file)
        tasks = prepare_gantt_chart_data(df)
        if tasks:
            gantt_chart_fig = create_gantt_chart(tasks)
            display_custom_legend()  # Display custom legend
            st.plotly_chart(gantt_chart_fig, use_container_width=True)

            average_durations = calculate_average_durations(df)
            display_pie_chart(average_durations)
