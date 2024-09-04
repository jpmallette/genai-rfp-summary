# client = OpenAI(api_key="sk-proj-1u26fJFcTdtHvoMjKpgVT3BlbkFJm9iEwzwNkIMbHCFlqnzL")
# Data/Prompt/input_prompt.txt

import streamlit as st
from openai import OpenAI
import pandas as pd
import re
import json
import tempfile

# Initialize OpenAI client
client = OpenAI(api_key="")

def read_txt_file():
    # Placeholder function to read the prompt string from a text file
    # Replace with the actual implementation as needed
    with open('Data/Prompt/input_prompt.txt', 'r') as file:
        return file.read()
def parse_assistant_output_into_dict(messages):
    def extract_json(text):
        # Regular expression pattern to find JSON starting with `{` and ending with `}`
        pattern = r'\{.*\}'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(0)  # Return the matched JSON string
        return None  # Return None if no JSON is found

    latest_message = messages[0]
    json_list = [block.text.value for block in latest_message.content]
    cleaned_json_strings = [extract_json(text) for text in json_list if extract_json(text) is not None]
    dictionaries = [json.loads(jstring) for jstring in cleaned_json_strings] 
    return dictionaries
def parse_assistant_output_dict_into_df(dictionaries):
    df_chatgpt_values = pd.DataFrame(dictionaries)
    df_chatgpt_values_transposed = df_chatgpt_values.transpose()
    df_chatgpt_values_transposed.reset_index(inplace=True)
    df_chatgpt_values_transposed.columns = ['field', 'chatgpt_value']
    return df_chatgpt_values_transposed
def replace_values_no_information_string_to_nan(df_chatgpt):
    values_to_replace = re.compile(r'\b(no|not specified|not provided|not explicit|in the document)\b', re.IGNORECASE)
    return df_chatgpt['chatgpt_value'].replace(values_to_replace, pd.NA)
def retrieve_category(df_chatgpt):
    df_field_category = pd.read_csv('Data/Supplemental/field_category.csv')
    df_chatgpt_category = pd.merge(df_chatgpt, df_field_category, on='field')
    return df_chatgpt_category
def generate_html(df_chatgpt_category):
    html_output = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>Opportunity Information</title>
    <style>
        body { font-family: Arial, sans-serif; background: #fff; color: #333; }
        .category { margin-bottom: 20px; }
        .header { background: #007BFF; padding: 10px; cursor: pointer; color: #fff; }
        .content { border: 1px solid #ccc; border-top: none; padding: 10px; display: flex; flex-wrap: wrap; }
        .column { flex: 50%; }
        .field { box-sizing: border-box; padding: 5px; }
        .field-name { font-weight: bold; }
        img.logo { height: 50px; margin-bottom: 20px; display: block; }
    </style>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            var headers = document.querySelectorAll('.header');
            headers.forEach(function(header) {
                header.addEventListener('click', function() {
                    var content = this.nextElementSibling;
                    content.style.display = content.style.display === 'flex' ? 'none' : 'flex';
                });
            });
        });
    </script>
    </head>
    <body>

    <img src="HTML-CSS/buscom_logo.jpeg" class="logo" alt="Bus.com Logo">
    """

    # Define the order of categories
    category_order = [
        "Opportunity Information",
        "High Level Summary",
        "Dates and Deadlines",
        "Opportunity Team & Contacts",
        "Estimates",
        "RFP Summary",
        "Deal Specifics",
        "Additional Information",
        "Lost Opportunity Analysis"
    ]

    # Define specific field orderings for complex categories
    dates_fields_left = ["Posted Date", "Deadline for Questions", "Prebid Attendance", "Pre-Bid Conference",
                        "Proposal Deadline Date", "Interview Information", "Last Addendum Date"]
    dates_fields_right = ["Event Start Date", "Event End Date", "Contract Duration (Months)",
                        "Contract Extension Term", "Options to Renew"]
    contacts_fields = ["Contact: Title", "Contact: Email", "Contact: Phone"]
    estimates_left = ["Estimated Contract Value", "Estimated Supplier Amount"]
    estimates_right = ["Estimated Cost", "Custom Payment Terms"]
    rfp_summary_left = ["Region Area Name", "Region Area Kind", "RFP Name", "RFP Service Type", "Submission Type", "Award Type"]
    rfp_summary_right = ["Subcontracting Allowed", "Supplier Partner", "Incumbent Supplier", "Pricing Type", "Proposal Writer"]
    deal_specifics_left = ["Number of Buses", "Facility Provided by Agency", "Maintenance Provided by Agency", "Parking Provided by Agency", "Living Wage Requirements", "Disadvantaged Business Requirements", "Fleet Requirement", "Fuel Provided By", "Vehicle Fuel Type", "Technology Needed", "Technology Partner", "Bidder References Required", "Liquidated Damages"]
    deal_specifics_right = ["Number of Awarded Vendors", "Facility Notes", "Maintenance Notes", "Parking Notes", "Living Wage Comments", "Disadvantaged Business Comments", "Fleet Requirement Comments", "Fuel Notes", "Vehicle Provider", "Technology Description", "Bidder References Description", "Liquidated Damage Information"]

    # Loop through the predefined list of categories
    for category in category_order:
        if category in df_chatgpt_category['category'].values:
            filtered_df = df_chatgpt_category[df_chatgpt_category['category'] == category]
            html_output += f'<div class="category">\n    <div class="header">{category}</div>\n    <div class="content" style="display: flex;">'

            if category == "Dates and Deadlines":
                # Specific handling for Dates and Deadlines with left and right columns
                html_output += '<div class="column">\n'
                for field in dates_fields_left:
                    if field in filtered_df['field'].values:
                        value = filtered_df.loc[filtered_df['field'] == field, 'chatgpt_value'].iloc[0]
                        html_output += f'        <div class="field"><span class="field-name">{field}:</span> {value}</div>\n'
                html_output += '</div>\n<div class="column">\n'
                for field in dates_fields_right:
                    if field in filtered_df['field'].values:
                        value = filtered_df.loc[filtered_df['field'] == field, 'chatgpt_value'].iloc[0]
                        html_output += f'        <div class="field"><span class="field-name">{field}:</span> {value}</div>\n'
                html_output += '</div>\n'

            elif category == "Opportunity Team & Contacts":
                # Vertical display for contact fields
                for field in contacts_fields:
                    if field in filtered_df['field'].values:
                        value = filtered_df.loc[filtered_df['field'] == field, 'chatgpt_value'].iloc[0]
                        html_output += f'        <div class="field" style="flex: 100%;"><span class="field-name">{field}:</span> {value}</div>\n'

            elif category == "Estimates":
                # Split fields into two columns for Estimates
                html_output += '<div class="column">\n'
                for field in estimates_left:
                    if field in filtered_df['field'].values:
                        value = filtered_df.loc[filtered_df['field'] == field, 'chatgpt_value'].iloc[0]
                        html_output += f'        <div class="field"><span class="field-name">{field}:</span> {value}</div>\n'
                html_output += '</div>\n<div class="column">\n'
                for field in estimates_right:
                    if field in filtered_df['field'].values:
                        value = filtered_df.loc[filtered_df['field'] == field, 'chatgpt_value'].iloc[0]
                        html_output += f'        <div class="field"><span class="field-name">{field}:</span> {value}</div>\n'
                html_output += '</div>\n'

            elif category == "RFP Summary" or category == "Deal Specifics":
                # Handle RFP Summary and Deal Specifics with custom field orders
                html_output += '<div class="column">\n'
                fields_left = rfp_summary_left if category == "RFP Summary" else deal_specifics_left
                for field in fields_left:
                    if field in filtered_df['field'].values:
                        value = filtered_df.loc[filtered_df['field'] == field, 'chatgpt_value'].iloc[0]
                        html_output += f'        <div class="field"><span class="field-name">{field}:</span> {value}</div>\n'
                html_output += '</div>\n<div class="column">\n'
                fields_right = rfp_summary_right if category == "RFP Summary" else deal_specifics_right
                for field in fields_right:
                    if field in filtered_df['field'].values:
                        value = filtered_df.loc[filtered_df['field'] == field, 'chatgpt_value'].iloc[0]
                        html_output += f'        <div class="field"><span class="field-name">{field}:</span> {value}</div>\n'
                html_output += '</div>\n'

            elif category == "Additional Information":
                # Vertical display of all fields for Additional Information
                for index, row in filtered_df.iterrows():
                    html_output += f'        <div class="field" style="flex: 100%;"><span class="field-name">{row["field"]}:</span> {row["chatgpt_value"]}</div>\n'

            else:
                # Normal field handling for other categories
                for index, row in filtered_df.iterrows():
                    html_output += f'        <div class="field"><span class="field-name">{row["field"]}:</span> {row["chatgpt_value"]}</div>\n'

            html_output += '    </div>\n</div>\n'

    html_output += """
        </body>
        </html>
    """
    return html_output
# Streamlit app layout
logo_path = 'HTML-CSS/buscom_logo.jpeg'
assistant_name = "RFP Extractor Information"

col1, col2 = st.columns([1, 6])

with col1:
    st.image(logo_path, width=100)

with col2:
    st.title('RFP Summary Tool')

st.markdown("<br>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload RFP Bid Packages files", accept_multiple_files=True)

if st.button('Generate RFP Summary'):
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Save uploaded file to a temporary location
            with open(f"temp_{uploaded_file.name}", "wb") as temp_file:
                temp_file.write(uploaded_file.getbuffer())

            pdf_file_path = f"temp_{uploaded_file.name}"
            prompt_str = read_txt_file()

            assistant = client.beta.assistants.create(
                name=assistant_name,
                instructions=(
                    "As a BD professional in the transit industry, your task involves extracting key information from "
                    "RFP documents to prepare thorough bid responses. Use the text provided from the RFP document to extract "
                    "data for each specified field meticulously. You will return a JSON format with no additional words context."
                ),
                model="gpt-3.5-turbo",
                tools=[{"type": "file_search"}],
            )

            vector_store = client.beta.vector_stores.create(name="RFP bids packages")

            file_paths = [pdf_file_path]
            file_streams = [open(path, "rb") for path in file_paths]

            file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=file_streams
            )

            assistant = client.beta.assistants.update(
                assistant_id=assistant.id,
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
            )

            message_file = client.files.create(
                file=open(pdf_file_path, "rb"), purpose="assistants"
            )

            thread = client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Extract the values for each column and return in JSON format. "
                            f"Return only the JSON format without additional words or context: {prompt_str}"
                        ),
                        "attachments": [
                            {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
                        ],
                    }
                ]
            )

            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id, assistant_id=assistant.id
            )

            messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

            dictionaries = parse_assistant_output_into_dict(messages)
            df_chatgpt = parse_assistant_output_dict_into_df(dictionaries)
            df_chatgpt['chatgpt_value'] = replace_values_no_information_string_to_nan(df_chatgpt)
            df_chatgpt_category = retrieve_category(df_chatgpt)
            html_content = generate_html(df_chatgpt_category)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
                tmp_file.write(html_content.encode('utf-8'))
                tmp_file_path = tmp_file.name

            st.download_button(
                label="Download RFP Summary",
                data=open(tmp_file_path, 'rb'),
                file_name='rfp_summary.html',
                mime='text/html'
            )
    else:
        st.write("Please upload at least one RFP file.")
