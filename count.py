import pandas as pd



file_path = "voter_data_with_school_districts_final1.csv"
df = pd.read_csv(file_path)

# Final step: Create a file with district name and number of Muslims in each district
district_counts = df.groupby('School District').size().reset_index(name='Muslim Count')
output_path_counts = "district_muslim_counts2.csv"
district_counts.to_csv(output_path_counts, index=False)

print(f"District counts saved to {output_path_counts}")

