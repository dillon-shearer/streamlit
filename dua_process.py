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

    # Function to prepare tasks for the Gantt chart
    def prepare_gantt_chart_data(df):
        # Handle non-date strings and convert dates
        df['Date Requested'] = pd.to_datetime(df['Date Requested'], errors='coerce')
        df['Date Added to Tracker'] = pd.to_datetime(df['Date Added to Tracker'], errors='coerce')
        df['DS Send Date'] = pd.to_datetime(df['DS Send Date'], errors='coerce')
        df['Last Collaborator Sign Date'] = pd.to_datetime(df['Last Collaborator Sign Date'], errors='coerce')
        df['Foundation Sign Date'] = pd.to_datetime(df['Foundation Sign Date'], errors='coerce')

        tasks = []
        for index, row in df.iterrows():
            request_id = f"Request {index + 1}"
            start = row['Date Requested']
            finish = adjust_finish_time(start, row['Date Added to Tracker'])
            tasks.append(dict(Task=request_id, Start=start, Finish=finish, Resource='Req to Tracker'))

            start = row['Date Added to Tracker']
            finish = adjust_finish_time(start, row['DS Send Date'])
            tasks.append(dict(Task=request_id, Start=start, Finish=finish, Resource='Tracker to DS'))

            if pd.notna(row['Last Collaborator Sign Date']):
                start = row['DS Send Date']
                finish = adjust_finish_time(start, row['Last Collaborator Sign Date'])
                tasks.append(dict(Task=request_id, Start=start, Finish=finish, Resource='DS to Final User Sign'))

            start = row['Last Collaborator Sign Date'] if pd.notna(row['Last Collaborator Sign Date']) else row['DS Send Date']
            finish = adjust_finish_time(start, row['Foundation Sign Date'])
            tasks.append(dict(Task=request_id, Start=start, Finish=finish, Resource='Final User to Foundation'))

        return tasks

    # Function to create the Gantt chart
    def create_gantt_chart(tasks):
        colors = {
            'Req to Tracker': 'rgb(46, 137, 205)',
            'Tracker to DS': 'rgb(114, 44, 121)',
            'DS to Final User Sign': 'rgb(198, 47, 105)',
            'Final User to Foundation': 'rgb(58, 149, 136)'
        }
        fig = ff.create_gantt(tasks, colors=colors, index_col='Resource', show_colorbar=True, group_tasks=True)
        # Update layout to hide y-axis labels
        fig.update_layout(yaxis=dict(showticklabels=False))
        return fig
    
    def calculate_durations(df):
        # Calculate durations in days
        df['Req to Tracker Duration'] = (df['Date Added to Tracker'] - df['Date Requested']).dt.days
        df['Tracker to DS Duration'] = (df['DS Send Date'] - df['Date Added to Tracker']).dt.days
        df['DS to Final User Sign Duration'] = (df['Last Collaborator Sign Date'] - df['DS Send Date']).dt.days
        df['Final User to Foundation Duration'] = (df['Foundation Sign Date'] - df['Last Collaborator Sign Date']).dt.days

        # Calculate aggregate metrics
        durations_summary = {
            'Req to Tracker': df['Req to Tracker Duration'].sum(),
            'Tracker to DS': df['Tracker to DS Duration'].sum(),
            'DS to Final User Sign': df['DS to Final User Sign Duration'].sum(),
            'Final User to Foundation': df['Final User to Foundation Duration'].sum()
        }
        return durations_summary

    def calculate_average_durations(df):
        # Calculate average durations
        average_durations = {
            'Req to Tracker': df['Req to Tracker Duration'].mean(),
            'Tracker to DS': df['Tracker to DS Duration'].mean(),
            'DS to Final User Sign': df['DS to Final User Sign Duration'].mean(),
            'Final User to Foundation': df['Final User to Foundation Duration'].mean()
        }
        return average_durations
    
    def display_pie_chart(durations):
        labels = list(durations.keys())
        values = list(durations.values())

        # Define colors corresponding to the Gantt chart phases
        colors = ['rgb(46, 137, 205)',  # Req to Tracker
                'rgb(114, 44, 121)',  # Tracker to DS
                'rgb(198, 47, 105)',  # DS to Final User Sign
                'rgb(58, 149, 136)']  # Final User to Foundation

        # Creating the pie chart with custom colors
        fig = px.pie(names=labels, values=values, title="Total Days Spent in Each Phase", hole=0.3)
        fig.update_traces(textinfo='label+value', marker=dict(colors=colors))
        fig.update_layout(
            autosize=False,
            width=1250,  # You can adjust this width according to your layout needs
            height=750   # You can adjust this height according to your layout needs
        )
        st.plotly_chart(fig, use_container_width=True)
        
    def display_colored_metrics(durations, label_prefix):
        # Define CSS styles and container layout
        metric_html = """
        <style>
            .metrics-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                flex-wrap: wrap;
                margin: 0 auto;
                width: 100%;
            }}
            .metric-box {{
                text-align: center;
                padding: 10px;
                border-radius: 0;
                color: white;
                background-color: inherit;  /* Inherits background-color from style attribute */
                flex-grow: 1;
                min-width: 100px;
                height: 120px;
                margin: 1px;
            }}
            .metric-value {{
                font-size: 25px;
                margin: 2px 0;
            }}
            .metric-label {{
                font-size: 16px;
                margin: 0;
            }}
        </style>
        <div class="metrics-container">
            {metrics}
        </div>
        """

        # Individual metric box format
        individual_metric_html = """
        <div class="metric-box" style="background-color: {color};">
            <h2 class="metric-value">{value:.1f}</h2>
            <h4 class="metric-label">{label}</h4>
        </div>
        """

        # Colors for each phase
        colors = {
            'Req to Tracker': 'rgb(46, 137, 205)',
            'Tracker to DS': 'rgb(114, 44, 121)',
            'DS to Final User Sign': 'rgb(198, 47, 105)',
            'Final User to Foundation': 'rgb(58, 149, 136)'
        }

        # Generating individual metrics
        metrics = ''.join([
            individual_metric_html.format(color=colors[key], value=durations[key], label=key + " " + label_prefix)
            for key in durations
        ])

        # Rendering the full metrics container with all boxes
        st.markdown(metric_html.format(metrics=metrics), unsafe_allow_html=True)


    # File uploader for the data file in Excel format
    data_file = st.file_uploader("Upload your data file in Excel format:", type=["xlsx"])
    if data_file is not None:
        if data_file is not None:
            df = pd.read_excel(data_file)  # Reading the Excel file
            tasks = prepare_gantt_chart_data(df)
            gantt_chart_fig = create_gantt_chart(tasks)
            st.plotly_chart(gantt_chart_fig, use_container_width=True)
            
            # Calculate and display total durations
            total_durations = calculate_durations(df)
            display_pie_chart(total_durations)  # This line calls the pie chart display function with the total durations

            # Calculate and display average durations
            average_durations = calculate_average_durations(df)
            display_colored_metrics(average_durations, "Avg Days")
