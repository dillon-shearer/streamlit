import streamlit as st
import pandas as pd
import io

# Script function
def run_my_script(uploaded_file, name):

    def check_email_reason(df, name):
        output_stream = io.StringIO()  # Create a stream to capture output

        # Messages
        needs_pi_message = "Hi there,\n\nThank you for your interest in the Answer ALS dataset. We are processing your data access request, and need to gather some additional information at this time.\n\nWe need to add your PI to your request and therefore need the PI's Name, Title, and Email Address in order to proceed with your request.\n\nPlease let me know if you have any additional questions!\n\nBest wishes,\n\n" + name + "\n\n---------------------------\n\n"
        needs_bo_message = "Hi there,\n\nThank you for your interest in the Answer ALS dataset. We are processing your data access request, and need to gather some additional information at this time.\n\nWe need to add the correct Authorized Business Official to your request and therefore need your institution's Authorized Business Official Name, Title, and Email Address in order to proceed with your request.\n\nHere is some additional information regarding this role from our FAQ section (https://dataportal.answerals.org/faqs-2):\n\n'A Business Official also needs to sign on behalf of your associated entity, so please check with your contracts office or PI to ensure the correct person is identified for this role.'\n\nPlease let me know if you have any additional questions!\n\nBest wishes,\n\n" + name + "\n\n---------------------------\n\n"
        needs_pi_bo_message = "Hi there,\n\nThank you for your interest in the Answer ALS dataset. We are processing your data access request, and need to gather some additional information at this time.\n\nWe need to add your PI to your request and therefore need the PI's Name, Title, and Email Address in order to proceed with your request.\n\nAdditionally, we also need to add the correct Authorized Business Official to your request and therefore need your institution's Authorized Business Official Name, Title, and Email Address in order to proceed with your request.\n\nHere is some additional information regarding this role from our FAQ section (https://dataportal.answerals.org/faqs-2):\n\n'A Business Official also needs to sign on behalf of your associated entity, so please check with your contracts office or PI to ensure the correct person is identified for this role.'\n\nPlease let me know if you have any additional questions!\n\nBest wishes,\n\n" + name + "\n\n---------------------------\n\n"
        verify_pi_message = "Hi there,\n\nThank you for your interest in the Answer ALS dataset. We are processing your data access request, and need to verify some information regarding your PI at this time.\n\nCan you please give us the Name, Title, and Email for your PI so we can verify/update our records accordingly? This information is vital to gain approval from our Data Access Committee.\n\nPlease let me know if you have any additional questions!\n\nBest wishes,\n\n" + name + "\n\n---------------------------\n\n"
        verify_bo_message = "Hi there,\n\nThank you for your interest in the Answer ALS dataset. We are processing your data access request, and need to verify some information regarding your institutional Authorized Business Official at this time.\n\nCan you please give us the Name, Title, and Email for your institution's Authorized Business Official so we can verify/update our records accordingly? This information is vital to gain approval from our Data Access Committee.\n\nPlease let me know if you have any additional questions!\n\nBest wishes,\n\n" + name + "\n\n---------------------------\n\n"
        verify_pi_bo_message = "Hi there,\n\nThank you for your interest in the Answer ALS dataset. We are processing your data access request, and need to verify some information regarding your PI at this time.\n\nCan you please give us the Name, Title, and Email for your PI so we can verify/update our records accordingly?\n\nAdditionally, we need to verify some information regarding your institutional Authorized Business Official.\n\nCan you please give us the Name, Title, and Email for your institution's Authorized Business Official? This information (both the PI and Business Official) is vital to gain approval from our Data Access Committee.\n\nPlease let me know if you have any additional questions!\n\nBest wishes,\n\n" + name + "\n\n---------------------------\n\n"
        verify_extra_collaborators_message = "Hi there,\n\nThank you for your interest in the Answer ALS dataset. We are processing your data access request, and need to verify some information regarding any potential collaborators you may have.\n\nIf you are working with anyone who will have access to the dataset (and is not already on your DUA), then you can email back with their Name, Title, and Email and we will update your records accordingly. If you do not have any additional collaborators, then no further action is required at this time.\n\nPlease let me know if you have any additional questions!\n\nBest wishes,\n\n" + name + "\n\n---------------------------\n\n"
        expired_docusign_message = "Hi there,\n\nThank you for your interest in the Answer ALS dataset. I am reaching out to let you know that your DocuSign DUA has expired in our system due to an incomplete status after a period of 120 days.\n\nIf you wish to cancel your request, then please respond with 'Cancel my data request'. If you wish to reinstate the DocuSign and complete the process to gain data access approval, then please respond back accordingly and I will gladly assist you in the process.\n\nPlease let me know if you have any additional questions!\n\nBest wishes,\n\n" + name + "\n\n---------------------------\n\n"
        dac_approved_need_signatures_message = "Hi there,\n\nThank you for your interest in the Answer ALS dataset. I am reaching out to let you know that you have received approval from our Data Access Committee, and access will be granted once all signatures are completed on your DocuSign form.\n\nPlease let me know if you have any additional questions!\n\nBest wishes,\n\n" + name + "\n\n---------------------------\n\n"

        # Check if EMAIL_REASON column exists in the DataFrame
        if 'EMAIL_REASON' in df.columns:
            # Iterate through each row in the DataFrame
            for index, row in df.iterrows():
                if row['EMAIL_REASON'] == 'Needs PI':
                    output_stream.write("Subject: Answer ALS Data Access Request - PI Information Needed\n\n")
                    output_stream.write("Email to: " + row['EMAIL'] + "\n\n........\n\n")
                    output_stream.write(needs_pi_message)

                if row['EMAIL_REASON'] == 'Needs BO':
                    output_stream.write("Subject: Answer ALS Data Access Request - Business Official Information Needed\n\n")
                    output_stream.write("Email to: " + row['EMAIL'] + "\n\n........\n\n")
                    output_stream.write(needs_bo_message)

                if row['EMAIL_REASON'] == 'Needs PI/BO':
                    output_stream.write("Subject: Answer ALS Data Access Request - PI & Business Official Information Needed\n\n")
                    output_stream.write("Email to: " + row['EMAIL'] + "\n\n........\n\n")
                    output_stream.write(needs_pi_bo_message)

                if row['EMAIL_REASON'] == 'Verify PI':
                    output_stream.write("Subject: Answer ALS Data Access Request - PI Verification Needed\n\n")
                    output_stream.write("Email to: " + row['EMAIL'] + "\n\n........\n\n")
                    output_stream.write(verify_pi_message)

                if row['EMAIL_REASON'] == 'Verify BO':
                    output_stream.write("Subject: Answer ALS Data Access Request - Business Official Verification Needed\n\n")
                    output_stream.write("Email to: " + row['EMAIL'] + "\n\n........\n\n")
                    output_stream.write(verify_bo_message)
                    
                if row['EMAIL_REASON'] == 'Verify PI/BO':
                    output_stream.write("Subject: Answer ALS Data Access Request - PI & Business Official Verification Needed\n\n")
                    output_stream.write("Email to: " + row['EMAIL'] + "\n\n........\n\n")
                    output_stream.write(verify_pi_bo_message)

                if row['EMAIL_REASON'] == 'Verify extra collaborators':
                    output_stream.write("Subject: Answer ALS Data Access Request - Verify additional collaborators\n\n")
                    output_stream.write("Email to: " + row['EMAIL'] + "\n\n........\n\n")
                    output_stream.write(verify_extra_collaborators_message)

                if row['EMAIL_REASON'] == 'Expired docusign':
                    output_stream.write("Subject: Answer ALS Data Access Request - DocuSign Expired\n\n")
                    output_stream.write("Email to: " + row['EMAIL'] + "\n\n........\n\n")
                    output_stream.write(expired_docusign_message)

                if row['EMAIL_REASON'] == 'DAC approved, need signatures':
                    output_stream.write("Subject: Answer ALS Data Access Request - Signatures Needed\n\n")
                    output_stream.write("Email to: " + row['EMAIL'] + "\n\n........\n\n")
                    output_stream.write(dac_approved_need_signatures_message)

                if row['EMAIL_REASON'] not in ['Needs PI', 'Needs BO', 'Needs PI/BO', 'Verify PI', 'Verify BO', 'Verify PI/BO', 'Verify extra collaborators', 'Expired docusign', 'DAC approved, need signatures']:
                    output_stream.write("Reason not found for email " + row['EMAIL'] + ". Please verify that the EMAIL_REASON column contains an accepted value.")

            else:
                output_stream.write("Column EMAIL_REASON not found.")

        return output_stream.getvalue()  # Return the captured output

    df = pd.read_excel(uploaded_file)
    
    email_output = check_email_reason(df, name)

    return email_output


# Main function for the analysis pages
def show():
    # Set up the page
    st.title("Answer ALS Data Scripts: Email Generator")
    st.write("*Generate emails for users in bulk.*")
    st.write("------")
    st.write("If you need the email_template.xlsx file, click the button below.")

    # Button Creation
    # Path to your file
    file_path = 'streamlit/data/email_template.xlsx'

    # Open the file in binary mode
    with open(file_path, "rb") as file:
        btn = st.download_button(
                label="Download Email Template",
                data=file,
                file_name="email_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
    # Space
    st.write(" ")
    st.write(" ")
        
    # Accepted values/definition section
    with st.expander("Email classification (accepted values in EMAIL_REASON column):"):
        st.write('1. **Needs PI** <br> *Used when you need to get the user\'s PI information.*', unsafe_allow_html=True)
        st.write('2. **Needs BO** <br> *Used when you need to get the user\'s Business Official information.*', unsafe_allow_html=True)
        st.write('3. **Needs PI/BO** <br> *Used when you need to get the user\'s PI **and** Business Official information.*', unsafe_allow_html=True)
        st.write('4. **Verify PI** <br> *Used when you need to verify the user\'s PI information.*', unsafe_allow_html=True)
        st.write('5. **Verify BO** <br> *Used when you need to verify the user\'s Business Official information.*', unsafe_allow_html=True)
        st.write('6. **Verify PI/BO** <br> *Used when you need to verify the user\'s PI **and** Business Official information.*', unsafe_allow_html=True)
        st.write('7. **Verify extra collaborators** <br> *Used when you need to verify that the user does not have any additional collaborators.*', unsafe_allow_html=True)
        st.write('8. **Expired docusign** <br> *Used when the user\'s DocuSign has voided.*', unsafe_allow_html=True)
        st.write('9. **DAC approved, need signatures** <br> *Used the user\'s request is Approved by the DAC, and they only need to sign the DUA to gain approval.*', unsafe_allow_html=True)
    
    st.write("#### Run Script Here")

    # Text input for name
    name = st.text_input("Enter your name:", "")

    # File uploader
    uploaded_file = st.file_uploader("Fill out email_template.xlsx and insert it back here to start the script")
    if uploaded_file is not None:
        output = run_my_script(uploaded_file, name)
        st.write(output)  # Display the output of the script using st.write
