import streamlit as st
import pandas as pd
from pandas import ExcelWriter
import numpy as np
from datetime import datetime, date
import io

# Working functions
def update_tracker(users_fp_raw):
    # Input paths
    users_fp_raw = users_fp_raw
    exclude_fp_raw = f'https://docs.google.com/spreadsheets/d/16RBz07Lor1xF94OPLWGf2C1QrtBHGwNV/edit#gid=80145408' # links to static google drive storage of exclusion ids
    tracker_fp_raw = f'https://docs.google.com/spreadsheets/d/1NYugrXX89wc3UZza7LnqNq2fp3IOhUjAbnRpqhdykXE/edit#gid=0' # UPDATE WITH CURRENT TRACKER URL
    tracker_fp_p2_raw = f'https://docs.google.com/spreadsheets/d/1NYugrXX89wc3UZza7LnqNq2fp3IOhUjAbnRpqhdykXE/edit#gid=1095299178'
    tracker_fp_p3_raw = f'https://docs.google.com/spreadsheets/d/1NYugrXX89wc3UZza7LnqNq2fp3IOhUjAbnRpqhdykXE/edit#gid=1785101483'

    # Modify filepaths of Google Sheets
    users_fp = users_fp_raw.replace('/edit#gid=', '/export?format=csv&gid=')
    exclude_fp = exclude_fp_raw.replace('/edit#gid=', '/export?format=csv&gid=')
    tracker_fp = tracker_fp_raw.replace('/edit#gid=', '/export?format=csv&gid=')
    tracker_p2_fp = tracker_fp_p2_raw.replace('/edit#gid=', '/export?format=csv&gid=')
    tracker_p3_fp = tracker_fp_p3_raw.replace('/edit#gid=', '/export?format=csv&gid=')

    # Class for email formatting
    class color:
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        DARKCYAN = '\033[36m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

    # Create dataframes
    df = pd.read_csv(users_fp)
    df2 = pd.read_csv(exclude_fp)

    df3 = pd.read_csv(tracker_fp)
    df4 = pd.read_csv(tracker_p2_fp)
    df5 = pd.read_csv(tracker_p3_fp)

# Genomics Logic
    # Define the function to create the string conditionally
    def get_genomics_level(row):
        levels = []
        if row['Access To Genomics Level 1'] is True:
            levels.append('1')
        if row['Access To Genomics Level 2'] is True:
            levels.append('2')
        if row['Access To Genomics Level 3'] is True:
            levels.append('3')
        if row['Access To Genomics Level 4'] is True:
            levels.append('4')
        if not levels:
            return 'N/A'
        else:
            return f"{' '.join(levels)}"

    # Apply the function to each row of the dataframe and store the result in a new column
    df['Genomics Access'] = df.apply(get_genomics_level, axis=1)

# Epigenomics Logic
    # Define the function to create the string conditionally
    def get_epigenomics_level(row):
        levels = []
        if row['Access To Epigenomics Level 1'] is True:
            levels.append('1')
        if row['Access To Epigenomics Level 2'] is True:
            levels.append('2')
        if row['Access To Epigenomics Level 3'] is True:
            levels.append('3')
        if row['Access To Epigenomics Level 4'] is True:
            levels.append('4')
        if not levels:
            return 'N/A'
        else:
            return f"{' '.join(levels)}"

    # Apply the function to each row of the dataframe and store the result in a new column
    df['Epigenomics Access'] = df.apply(get_epigenomics_level, axis=1)

# Transcriptomics Logic
    # Define the function to create the string conditionally
    def get_transcriptomics_level(row):
        levels = []
        if row['Access To Transcriptomics Level 1'] is True:
            levels.append('1')
        if row['Access To Transcriptomics Level 2'] is True:
            levels.append('2')
        if row['Access To Transcriptomics Level 3'] is True:
            levels.append('3')
        if row['Access To Transcriptomics Level 4'] is True:
            levels.append('4')
        if not levels:
            return 'N/A'
        else:
            return f"{' '.join(levels)}"

    # Apply the function to each row of the dataframe and store the result in a new column
    df['Transcriptomics Access'] = df.apply(get_transcriptomics_level, axis=1)

# Proteomics Logic
    # Define the function to create the string conditionally
    def get_proteomics_level(row):
        levels = []
        if row['Access To Proteomics Level 1'] is True:
            levels.append('1')
        if row['Access To Proteomics Level 2'] is True:
            levels.append('2')
        if row['Access To Proteomics Level 4'] is True:
            levels.append('4')
        if not levels:
            return 'N/A'
        else:
            return f"{' '.join(levels)}"

    # Apply the function to each row of the dataframe and store the result in a new column
    df['Proteomics Access'] = df.apply(get_proteomics_level, axis=1)

    # Split users based on previous acceptance to data portal AND if they are existing in the current-most tracker
    # Combine the IDs from both 'Current Requests' and 'Completed Requests'
    id_list_combined = pd.concat([df3['ID'], df4['ID']]).unique().tolist()

    # Filter to those who have a "preexisting ID" and are not in the combined tracker ID list
    df_existing = df[df['Id'].isin(df2['Id'])]
    df_existing = df_existing[~df_existing['Id'].isin(id_list_combined)]

    # Filter to those who are NOT a "preexisting ID" and are not in the combined tracker ID list
    df_new = df[~df['Id'].isin(df2['Id'])]
    df_new = df_new[~df_new['Id'].isin(id_list_combined)]

    # Fill collaborator "nan" value
    df_new['Collaborators'] = df_new['Collaborators'].fillna('None')
    df_existing['Collaborators'] = df_existing['Collaborators'].fillna('None')

    # Add column for Signed status per current-most Submitted sheet
    # create a boolean mask to check if both columns are equal to 'Signed'
    mask = (df['Auth. Business Official Sign Status'] == 'Signed') & (df['User Sign Status'] == 'Signed')

    # create a new column in df based on the mask
    df['DUA Status'] = np.where(mask, 'Completed', 'In Progress')

    # Find non-existing users
    new_users = df[~df['Id'].isin(df3['ID'])]

    # Modify "new_users" df to fit Tracker schema
    # Drop extraneous columns
    new_users.loc[:, 'Full Name'] = new_users['First Name'] + ' ' + new_users['Last Name']
    new_users = new_users.drop(columns=['First Name', 'Last Name', 'Name', 'Created DateTime', 'Threshold', 'Downloaded', 'Legacy', 'Data Request Last Modified Date', 'Status', 'Credentials', 'Institution', 'Auth. Business Official Name', 'Auth. Business Official Email', 'Data Use Proposal', 'Project Timeframe', 'Collaborators', 'Access To Genomics Level 1', 'Access To Genomics Level 2', 'Access To Genomics Level 3', 'Access To Genomics Level 4', 'Access To Epigenomics Level 1', 'Access To Epigenomics Level 2', 'Access To Epigenomics Level 3', 'Access To Epigenomics Level 4', 'Access To Transcriptomics Level 1', 'Access To Transcriptomics Level 2', 'Access To Transcriptomics Level 3', 'Access To Transcriptomics Level 4', 'Access To Proteomics Level 1', 'Access To Proteomics Level 2', 'Access To Proteomics Level 4', 'Rejection Reason', 'User Sign Status', 'User Sign Date', 'Auth. Business Official Sign Status', 'Auth. Business Official Sign Date', 'Answer ALS Official Sign Status', 'Answer ALS Official Sign Date', 'Link to edit', 'Genomics Access', 'Epigenomics Access', 'Transcriptomics Access', 'Proteomics Access'])

    # Reorder remaining columns
    new_users = new_users.reindex(columns=['Full Name', 'Id', 'Email', 'Data Request Submit Date'], 
                    index=new_users.index,
                    copy=False)

    # Rename
    new_users = new_users.rename(columns={'Id': 'ID', 'Data Request Submit Date': 'Date Requested', 'Name': 'Full Name'})

    # Modify "Date Requested" column's timestamp
    # Define function for conversion
    def convert_timestamp(timestamp):
        dt_object = datetime.fromisoformat(timestamp[:-1])
        return dt_object.date().strftime('%Y-%m-%d')

    # apply function to 'Date Requested' column
    new_users['Date Requested'] = new_users['Date Requested'].apply(convert_timestamp)

    # Append new users to Tracker
    # Append
    df_tracker = pd.concat([new_users, df3], ignore_index=True)

    # Fill nulls in "DUA Status" with "In Progress"
    df_tracker['DUA Status'].fillna('In Progress', inplace=True)

    # Fill nulls in "DAC Status" with "In Progress"
    df_tracker['DAC Status'].fillna('Pending', inplace=True)

    # Fill nulls in "Status" with "Needs Action"
    df_tracker['DAC Status'].fillna('Pending', inplace=True)

    # Set date of "Date Added to Tracker" to today
    today = date.today().strftime('%Y-%m-%d')
    df_tracker['Date Added to Tracker'].fillna(today, inplace=True)
    # create a boolean mask to check if the ID is present in df2
    mask = df_tracker['ID'].isin(df2['Id'])

    # use the mask to set the 'Preapproved User?' column to 'Yes' or 'No'
    df_tracker.loc[mask, 'Preapproved User?'] = 'Yes'
    df_tracker.loc[~mask, 'Preapproved User?'] = 'No'

    #Create secondary sheet and update with completed requests
    # Define the statuses that indicate a completed request
    completed_statuses = ['Voided', 'Completed', 'User Cancelled']

    # Create a DataFrame for completed requests
    df_completed = df_tracker[df_tracker['Status'].isin(completed_statuses)]

    # Append df_completed to df4
    df_completed = pd.concat([df4, df_completed], ignore_index=True)

    ## remove rows from df_tracker that are present in df_completed
    # Get a list of IDs from df_completed
    completed_ids = df_completed['ID'].tolist()
    completed_individual_ids = df5['ID'].tolist()

    # Drop rows from df_tracker where ID is in the list of completed IDs
    df_tracker = df_tracker[~df_tracker['ID'].isin(completed_ids)]

    # drop rows from df_tracker where ID is in the list of Individual IDs
    df_tracker = df_tracker[~df_tracker['ID'].isin(completed_individual_ids)]

    # Sort df_tracker first by 'Date Added to Tracker' and then by 'ID', both in ascending order
    df_tracker.sort_values(by=['Date Added to Tracker', 'ID'], ascending=[True, True], inplace=True)

    # Message Creation

    # Drop rows in new_users where 'ID' is in either of the two lists
    new_users = new_users[~new_users['ID'].isin(completed_ids + completed_individual_ids)]

    # Filtering the DataFrame
    df_filtered = df_new[~df_new['Id'].isin(new_users)]

    st.write(completed_individual_ids)

    #Send updated Tracker to XLSX to replace current cut
    # Write to excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as excel_writer:
        # Write your DataFrame to the Excel file and specify the sheet name
        df_tracker.to_excel(excel_writer, index=False, sheet_name="Current Requests")
        df_completed.to_excel(excel_writer, index=False, sheet_name="Completed Requests")
        df5.to_excel(excel_writer, index=False, sheet_name="Individual Requests")

        # Seek start of stream
        output.seek(0)

    # return file
    return output, df_filtered

# Main function for page
def show():
    # Streamlit title
    st.title("Answer ALS Data Scripts: Update DUA Tracker Script")
    st.write("*This script updates the data for the DUA_Tracker_V2.xlsx file.*")
    st.write("------")

    # Instructions
    with st.expander("**Instructions for running script**"):
        st.write('1. Download weekly cut (on Mondays) of users.csv from *Data Portal > Admin > User Management* where DUA Status = "**Submitted**".', unsafe_allow_html=True)
        st.write('2. Rename file as *users YYYYMMDD.csv*.', unsafe_allow_html=True)
        st.write('3. Convert CSV file to XLSX workbook. Save.', unsafe_allow_html=True)
        st.write('4. Drop the XLSX workbook into these folders in the GDrive (https://drive.google.com/drive/folders/1DhYmbNBhXzTqw_4ALt1vb7jQZluJJv8K)', unsafe_allow_html=True)
        st.write('5. Open the workbook in the Google Drive. Wait for the URL to settle after first opening (est. 5 seconds), and then copy that URL as-is.', unsafe_allow_html=True)
        st.write('6. Paste the URL copied in step 5 into the textbox below. Press Submit.', unsafe_allow_html=True)
        st.write('7. Update data in DUA tracker with the new data downloadable after the script runs.<br>*- PLEASE!!! Do not create new sheets. Please just erase existing row data and replace it with the new. The sheet IDs are used for this script.*', unsafe_allow_html=True)
        st.write('8. Update DUA Messages page (https://docs.google.com/document/d/1Pg9roju_zzynJxYD2aE6t-tPEG2Bqbiqi3nPy5MuCso/edit) with the newly generated messages.', unsafe_allow_html=True)

    # UI elements for input
    users_fp_raw = st.text_input("Enter the URL to the GDrive stored XLSX workbook for this week's users.csv download: ")
    submit_button = st.button('Submit')
    st.write("")

    if submit_button:
        try:
            output, df_filtered = update_tracker(users_fp_raw)
            today = datetime.today()
            formatted_date = today.strftime('%Y%m%d')

            # Only show the download button if excel_file is not None
            if output is not None:
                st.download_button(
                    label="Download Updated DUA Tracker Data",
                    data=output,
                    file_name=f'DUA_Tracker_V2_{formatted_date}.xlsx',
                    mime="application/vnd.ms-excel"
                )
                st.write("-----")

                # Iterate through rows using iterrows() function
                for index, row in df_filtered.iterrows(): 
                    st.write(f"**{row['First Name']} {row['Last Name']}**" + f" ({row['Credentials']}) from **{row['Institution']}** - ")
                    st.write("**Email**" + f": {row['Email']}")
                    st.write("**Data Use Proposal**" + f": {row['Data Use Proposal']}")
                    st.write("**Project Timeframe**" + f": {row['Project Timeframe']}")
                    st.write("**Authorized Business Official Name**" + f": {row['Auth. Business Official Name']}")
                    st.write("**Authorized Business Official Email**" + f": {row['Auth. Business Official Email']}")
                    st.write("**Collaborators**" + f": {row['Collaborators']}")
                    st.write("**Genomics**" + f": {row['Genomics Access']}")
                    st.write("**Epigenomics**"+ f": {row['Epigenomics Access']}")
                    st.write("**Transcriptomics**" + f": {row['Transcriptomics Access']}")
                    st.write("**Proteomics**" + f": {row['Proteomics Access']}")
                    st.write(" ")
                    st.write("-----")
                    st.write(" ")

        except Exception as e:
                st.write("An error occurred:", e)