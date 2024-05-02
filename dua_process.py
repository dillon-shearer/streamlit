import pandas as pd
import streamlit as st
import plotly.figure_factory as ff
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
        return fig

    # File uploader for the data file in Excel format
    data_file = st.file_uploader("Upload your data file in Excel format:", type=["xlsx"])
    if data_file is not None:
        df = pd.read_excel(data_file)  # Reading the Excel file
        tasks = prepare_gantt_chart_data(df)
        gantt_chart_fig = create_gantt_chart(tasks)
        st.plotly_chart(gantt_chart_fig, use_container_width=True)

show()
