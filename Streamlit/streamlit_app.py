import streamlit as st
import pandas as pd
import os

# Page configuration
st.set_page_config(page_title="Patient Health Information Dashboard", layout="wide")

# Define the directory where your CSV files are located
data_dir = 'C:/Users/dell/Desktop/Patient_Records/'  # Update this with the correct path

def load_data(data_dir):
    encounters = pd.read_csv(os.path.join(data_dir, 'clean/cleaned_encounters.csv'))
    patients = pd.read_csv(os.path.join(data_dir, 'clean/cleaned-patients-1.csv'))
    organizations = pd.read_csv(os.path.join(data_dir, 'organizations.csv'))
    payers = pd.read_csv(os.path.join(data_dir, 'payers.csv'))
    procedures = pd.read_csv(os.path.join(data_dir, 'clean/cleaned_procedures.csv'))
    return encounters, patients, organizations, payers, procedures

encounters, patients, organizations, payers, procedures = load_data(data_dir)

# Merge data for comprehensive patient information
merged_data = encounters.merge(patients, left_on='PATIENT', right_on='Id', suffixes=('_encounter', '_patient'))

# Calculate readmitted patients
def calculate_readmitted_patients(encounters):
    encounters['START'] = pd.to_datetime(encounters['START'])
    patient_counts = encounters['PATIENT'].value_counts()
    readmitted_patients = patient_counts[patient_counts > 1].index
    readmitted_encounters = encounters[encounters['PATIENT'].isin(readmitted_patients)]
    readmitted_counts = readmitted_encounters.groupby(readmitted_encounters['START'].dt.to_period('M')).agg({'PATIENT': 'nunique'}).reset_index()
    readmitted_counts['START'] = readmitted_counts['START'].dt.to_timestamp()
    return readmitted_counts, readmitted_patients.size

readmitted_counts, num_readmitted = calculate_readmitted_patients(encounters)

# Calculate average statistics
avg_stay = (pd.to_datetime(encounters['STOP']) - pd.to_datetime(encounters['START'])).dt.total_seconds().mean() / 3600
avg_cost = pd.to_numeric(encounters['TOTAL_CLAIM_COST'].str.replace(',', ''), errors='coerce').mean()

# Calculate procedures covered by insurance
covered_encounters = encounters[encounters['PAYER'] != "b1c428d6-4f07-31e0-90f0-68ffa6ff8c76"]
num_procedures_covered = procedures[procedures['ENCOUNTER'].isin(covered_encounters['Id'])].shape[0]

# Title
st.title("Patient Health Information Dashboard")

# Display metrics in a row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Readmitted Patients", f"{num_readmitted}")

with col2:
    st.metric("Average Length of Stay (hours)", f"{avg_stay:.2f}")

with col3:
    st.metric("Average Cost per Visit", f"${avg_cost:,.2f}")

with col4:
    st.metric("Procedures Covered by Insurance", f"{num_procedures_covered}")

# Visualization of readmitted patients over time
st.subheader("Readmitted Patients Over Time")
st.line_chart(readmitted_counts.set_index('START')['PATIENT'])

# Search by Patient ID
patient_id = st.sidebar.text_input("Enter Patient ID")

if patient_id:
    # Filter data based on Patient ID
    patient_data = merged_data[merged_data['Id_patient'] == patient_id]
    
    if not patient_data.empty:
        st.subheader("Patient Information")
        st.write(patient_data[['FIRST', 'LAST', 'BIRTHDATE', 'GENDER']])
        
        st.subheader("Recent Visits")
        st.write(patient_data[['START', 'STOP']])
        
        st.subheader("Hospital Stay Duration (hours)")
        stay_duration = (pd.to_datetime(patient_data['STOP']) - pd.to_datetime(patient_data['START'])).dt.total_seconds() / 3600
        for duration in stay_duration.values:
            st.write(f"{duration:.2f} hours")
        
        st.subheader("Visit Cost")
        try:
            visit_cost = pd.to_numeric(patient_data['TOTAL_CLAIM_COST'].str.replace(',', ''), errors='coerce').sum()
            st.write(f"${visit_cost:,.2f}")
        except ValueError as e:
            st.warning(f"Error calculating visit cost: {e}")
        
        st.subheader("Procedures Covered by Insurance")
        covered_by_insurance = procedures[procedures['ENCOUNTER'].isin(patient_data['Id_patient']) & (procedures['BASE_COST'] > 0)].shape[0]
        st.write(covered_by_insurance)
    else:
        st.warning("No patient found with the given ID.")

# Additional feature: List all patients
st.sidebar.header("List of All Patients")
if st.sidebar.button("Show All Patients"):
    st.subheader("All Patients")
    st.write(patients)

# Additional feature: Search by Name
st.sidebar.header("Search by Name")
patient_name = st.sidebar.text_input("Enter Patient Name")

if patient_name:
    # Filter data based on Patient Name
    patient_data = merged_data[merged_data['FIRST'].str.contains(patient_name, case=False, na=False) | merged_data['LAST'].str.contains(patient_name, case=False, na=False)]
    
    if not patient_data.empty:
        st.subheader("Patient Information")
        st.write(patient_data)
    else:
        st.warning("No patient found with the given name.")
