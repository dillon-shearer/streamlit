import streamlit as st
from azure.storage.blob import BlobServiceClient
import pandas as pd
from datetime import datetime
import io

def process_data(environment, connection_string):
# STAGING ENVIRONMENT
    if environment == "Staging":

        container_names = ["epigenomics", "staging-epigenomics", "proteomics", "staging-proteomics", "transcriptomics", "staging-transcriptomics", "genomics", "staging-genomics"]
        folder_paths = ["staged/1_fastq", "1_fastq", "staged/1_wiff", "1_wiff", "staged/1_fastq", "1_fastq", "staged/3_vcf", "1_bam"]

    # Connect to Azure
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create dataframes to hold participants
        dataframes = []

        for container_name, folder_path in zip(container_names, folder_paths):
            container_client = blob_service_client.get_container_client(container_name)
            blobs_list = container_client.list_blobs(name_starts_with=folder_path)
            blob_names = [blob.name for blob in blobs_list]
            # Clean the DataFrame column to GUID (modify this part as needed)
            blob_names = [blob_name.split('/')[-1].split('-')[1].split('-')[0] for blob_name in blob_names]
            df = pd.DataFrame(blob_names, columns=["GUID"])
            df.drop_duplicates(inplace=True)
            dataframes.append(df)
            
    # Create combined dataframes for each omic with duplicates removed
        epigenomics = pd.concat([dataframes[0], dataframes[1]], axis=0, ignore_index=True)
        epigenomics.drop_duplicates(inplace=True)

        proteomics = pd.concat([dataframes[2], dataframes[3]], axis=0, ignore_index=True)
        proteomics.drop_duplicates(inplace=True)

        transcriptomics = pd.concat([dataframes[4], dataframes[5]], axis=0, ignore_index=True)
        transcriptomics.drop_duplicates(inplace=True)

        genomics = pd.concat([dataframes[6], dataframes[7]], axis=0, ignore_index=True)
        genomics.drop_duplicates(inplace=True)

    
    # Write to excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as excel_writer:
            # Write each DataFrame to a separate sheet
            dataframes[0].to_excel(excel_writer, sheet_name='epigenomics', index=False)
            dataframes[1].to_excel(excel_writer, sheet_name='staging-epigenomics', index=False)
            epigenomics.to_excel(excel_writer, sheet_name='combined-epigenomics', index=False)
            dataframes[2].to_excel(excel_writer, sheet_name='proteomics', index=False)
            dataframes[3].to_excel(excel_writer, sheet_name='staging-proteomics', index=False)
            proteomics.to_excel(excel_writer, sheet_name='combined-proteomics', index=False)
            dataframes[4].to_excel(excel_writer, sheet_name='transcriptomics', index=False)
            dataframes[5].to_excel(excel_writer, sheet_name='staging-transcriptomics', index=False)
            transcriptomics.to_excel(excel_writer, sheet_name='combined-transcriptomics', index=False)
            dataframes[6].to_excel(excel_writer, sheet_name='genomics', index=False)
            dataframes[7].to_excel(excel_writer, sheet_name='staging-genomics', index=False)
            genomics.to_excel(excel_writer, sheet_name='combined-genomics', index=False)

        # Save the Excel file
        excel_writer.save()

        # Seek start of stream
        output.seek(0)

        # return file
        return output

# RELEASED ENVIRONMENT
    if environment == "Released":
        container_names = ["epigenomics", "proteomics", "transcriptomics", "genomics"]
        folder_paths = ["1_fastq", "1_wiff", "1_fastq", "2_bam"]

    # Connect to Azure
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create dataframes to hold participants
        dataframes = []

        for container_name, folder_path in zip(container_names, folder_paths):
            container_client = blob_service_client.get_container_client(container_name)
            blobs_list = container_client.list_blobs(name_starts_with=folder_path)
            blob_names = [blob.name for blob in blobs_list]
            # Clean the DataFrame column to GUID (modify this part as needed)
            blob_names = [blob_name.split('/')[-1].split('-')[1].split('-')[0] for blob_name in blob_names]
            df = pd.DataFrame(blob_names, columns=["GUID"])
            df.drop_duplicates(inplace=True)
            dataframes.append(df)

    # Check if the first two dataframes are not empty
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as excel_writer:
            # Write each DataFrame to a separate sheet
            dataframes[0].to_excel(excel_writer, sheet_name='epigenomics', index=False)
            dataframes[1].to_excel(excel_writer, sheet_name='proteomics', index=False)
            dataframes[2].to_excel(excel_writer, sheet_name='transcriptomics', index=False)
            dataframes[3].to_excel(excel_writer, sheet_name='genomics', index=False)

            # Save the Excel file
            excel_writer.save()

            # Seek start of stream
            output.seek(0)

            # return file
            return output

# Main function for page
def show():
    # Streamlit title
    st.title("Get Azure Staging/Released")
    st.write("This script pulls participant IDs found in each Azure bucket.")

    # UI elements for input
    connection_string = st.text_input("Enter the connection string", type="password")
    environment = st.selectbox('Choose the environment:', ('Staging', 'Released'))
    submit_button = st.button('Submit')

    if submit_button:
        try:
            excel_file = process_data(environment, connection_string)
            today = datetime.today()
            formatted_date = today.strftime('%Y%m%d')

            st.download_button(
                label="Download Excel file",
                data=excel_file,
                file_name=f'azure_{environment}_Data_{formatted_date}.xlsx',
                mime="application/vnd.ms-excel"
            )