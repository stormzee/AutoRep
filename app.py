import tkinter as tk
# import subprocess
import os
import pandas as pd
import numpy as np
import pdfkit
from pdfkit.api import configuration
from jinja2 import Environment, FileSystemLoader
import base64

def run_script():


    # provide the path to the pdf generator.
    wkhtml_path = pdfkit.configuration(wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

    # get the excel file in the current directory and use it to generate the result sheet.
    # We only want to work on one sheet at a time, and thus the excel file

    # todo-- Create a dir for all excel files and use a loop to generate results pdfs for each of them
    files = os.listdir('.')

    # Print the list of files
    
    
    def get_excelFiles(current_dir):
        # excel_file = ''
        # excelFile_name = ''
        for file in current_dir:
            if file.endswith('.xlsx') or file.endswith('.xls'):
                excel_file = file
                excelFile_name = excel_file.split('.')[0]
        return excel_file, excelFile_name
    
    result_sheet, sheet_name = get_excelFiles(files)
    
    df = pd.read_excel(result_sheet)

    def get_classNames(sheet_name):
        character_string = ''
        characters = [character_string + i for i in sheet_name]
        first_n, last_n = ''.join(characters[:3]).upper(), ''.join(characters[3:]).upper()
        return f"{first_n} {last_n}"

    class_name= get_classNames(sheet_name)

    df.replace(np.nan, 0, inplace=True)

    df = df.set_index('roll_number')

    df = df.loc[(df != 0).any(axis=1)]


    # # Start calculating the extra fields such as the totals for each subject.
    # ## english_total, math_total, science_total and for all subjects calculate the total


    df['english_total'] = df['english_class']+df['english_exam']
    df['math_total'] = df['math_class']+df['math_exam']
    df['science_total'] = df['science_class']+df['science_exam']
    df['social_total'] = df['social_class']+df['social_exam']
    df['rme_total'] = df['rme_class']+df['rme_exam']
    df['ict_total'] = df['ict_class']+df['ict_exam']
    df['french_total'] = df['french_class']+df['french_exam']
    df['twi_total'] = df['twi_class']+df['twi_exam']
    df['bdt_total'] = df['bdt_class']+df['bdt_exam']


    # ### Calculate the grade for each subject and assign it to the grade column


    # Define the function
    def get_subject_grade(subject_total):
        grading = {}
        if subject_total >= 80 and subject_total <= 100:
            grade, remark = 1, 'Excellent'
        elif subject_total >= 70 and subject_total <= 79:
            grade, remark = 2, 'Very Good'
        elif subject_total >= 60 and subject_total <= 69:
            grade, remark = 3, 'Good'
        elif subject_total >= 50 and subject_total <= 59:
            grade, remark = 4, 'Credit'
        elif subject_total >= 45 and subject_total <= 49:
            grade, remark = 5, 'Pass'
        else:
            grade, remark = 6, 'Fail'
            
        grading = {
            'grade': grade,
            'remark': remark
        }
        return grading

    # Apply the function to each subject's total score and create new columns for grade and remarks
    df['math_grade'] = df['math_total'].apply(lambda x: get_subject_grade(x)['grade'])
    df['math_remark'] = df['math_total'].apply(lambda x: get_subject_grade(x)['remark'])

    df['english_grade'] = df['english_total'].apply(lambda x: get_subject_grade(x)['grade'])
    df['english_remark'] = df['english_total'].apply(lambda x: get_subject_grade(x)['remark'])

    df['science_grade'] = df['science_total'].apply(lambda x: get_subject_grade(x)['grade'])
    df['science_remark'] = df['science_total'].apply(lambda x: get_subject_grade(x)['remark'])

    df['social_grade'] = df['social_total'].apply(lambda x: get_subject_grade(x)['grade'])
    df['social_remark'] = df['social_total'].apply(lambda x: get_subject_grade(x)['remark'])

    df['ict_grade'] = df['ict_total'].apply(lambda x: get_subject_grade(x)['grade'])
    df['ict_remark'] = df['ict_total'].apply(lambda x: get_subject_grade(x)['remark'])

    df['rme_grade'] = df['rme_total'].apply(lambda x: get_subject_grade(x)['grade'])
    df['rme_remark'] = df['rme_total'].apply(lambda x: get_subject_grade(x)['remark'])

    df['twi_grade'] = df['twi_total'].apply(lambda x: get_subject_grade(x)['grade'])
    df['twi_remark'] = df['twi_total'].apply(lambda x: get_subject_grade(x)['remark'])

    df['french_grade'] = df['french_total'].apply(lambda x: get_subject_grade(x)['grade'])
    df['french_remark'] = df['french_total'].apply(lambda x: get_subject_grade(x)['remark'])

    df['bdt_grade'] = df['bdt_total'].apply(lambda x: get_subject_grade(x)['grade'])
    df['bdt_remark'] = df['bdt_total'].apply(lambda x: get_subject_grade(x)['remark'])


    # ### Calculate the overall total marks for each student


    # 
    df['overall_total']=df['english_total']+df['math_total']+df['science_total']+df['social_total']+df['rme_total']+df['ict_total']+df['french_total']+df['twi_total']+df['bdt_total']
    # 
    df['overall_total']= round(df['overall_total'],1)


    # Get other subjects aside the 4 core subjects to get the best two


    other_subjects = ['rme_grade', 'ict_grade', 'twi_grade', 'french_grade', 'bdt_grade']
    oth_sub = df[other_subjects]


    # Get the two smallest numbers and sum them


    # Function to get the two best grades (ie, smallest integers). nsmallest() picks the first occurance of duplicate values
    def get_two_smallest(row):
        smallest_grades = row.nsmallest(2)
        return smallest_grades.sum()


    # Add grades of the core subjects for each student
    df['core_sub_grade'] = df['math_grade']+df['english_grade']+df['science_grade']+df['social_grade']

    # The best two from the rest of the subjects
    df['best_two_grade'] = oth_sub.apply(get_two_smallest, axis=1)

    # Add the two to get the overall grade for each student
    df['overall_grade'] = df['core_sub_grade'] + df['best_two_grade']


    # ### Do the rankings (position in class and for each subject)


    # 
    df['class_position'] = df['overall_total'].rank(ascending=False, method='dense')


    def add_suffix(class_position):
        if 10 <= class_position % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(class_position % 10, 'th')
        return f"{int(class_position)}{suffix}"


    # Apply the add_suffix function to the 'class_position' column
    df['class_position'] = df['class_position'].apply(add_suffix)


    # ### Do subject positions

    df['math_position'] = df['math_total'].rank(ascending=False, method='dense').apply(add_suffix)
    df['english_position'] = df['science_total'].rank(ascending=False, method='dense').apply(add_suffix)
    df['science_position'] = df['english_total'].rank(ascending=False, method='dense').apply(add_suffix)
    df['social_position'] = df['social_total'].rank(ascending=False, method='dense').apply(add_suffix)
    df['rme_position'] = df['rme_total'].rank(ascending=False, method='dense').apply(add_suffix)
    df['ict_position'] = df['ict_total'].rank(ascending=False, method='dense').apply(add_suffix)
    df['french_position'] = df['french_total'].rank(ascending=False, method='dense').apply(add_suffix)
    df['twi_position'] = df['twi_total'].rank(ascending=False, method='dense').apply(add_suffix)
    df['bdt_position'] = df['bdt_total'].rank(ascending=False, method='dense').apply(add_suffix)


    # 
    # # convert the image to a base64 encoded string for html to render
    # ## Handle all image conversion here, e.g., school logo, student photo ID etc

    def encode_image_file(image_path):
        with open(image_path, "rb") as image_file:
            # Read the image file and encode it as base64
            return base64.b64encode(image_file.read()).decode("utf-8")


    # df['encoded_image'] = df['student_photo'].apply(encode_image_file)

    school_logo = encode_image_file(r"logo.jpg")


    total_students = df.shape[0]

    # Custom HTML template path
    html_template_path = 'student_results_template.html'

    # Output PDF path
    pdf_output_path = f"{class_name}_students_results.pdf"

    # Create a Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(html_template_path)

    # Create a list to store individual HTML templates for each row
    individual_html_templates = []

    # Iterate through the DataFrame rows
    for index, row in df.iterrows():
        # Render the HTML template for each row
        html_template = template.render(school_logo=school_logo,
                                        student_name=row['student_name'], 
                                        roll_number=index, 
                                        total_students=total_students,
                                        class_name=class_name,
                                        grade=row['overall_grade'],
                                        total_score=row['overall_total'],
                                        class_position=row['class_position'],
                                        english_exam=row['english_exam'], 
                                        english_class=row['english_class'],
                                        math_exam=row['math_exam'], 
                                        math_class=row['math_class'],
                                        english_total=row['english_total'], 
                                        math_total=row['math_total'],
                                        science_total=row['science_total'],
                                        science_class=row['science_class'],
                                        science_exam=row['science_exam'],
                                        science_grade=row['science_grade'],
                                        math_grade=row['math_grade'],
                                        english_grade=row['english_grade'],
                                        science_remark=row['science_remark'],
                                        math_remark=row['math_remark'],
                                        english_remark=row['english_remark'],
                                        math_position=row['math_position'],
                                        english_position=row['english_position'],
                                        science_position=row['science_position'],
                                        social_class=row['social_class'],
                                        social_exam=row['social_exam'],
                                        social_grade=row['social_grade'],
                                        social_total=row['social_total'],
                                        social_remark=row['social_remark'],
                                        social_position=row['social_position'],
                                        twi_class=row['twi_class'],
                                        twi_exam=row['twi_exam'],
                                        twi_grade=row['twi_grade'],
                                        twi_total=row['twi_total'],
                                        twi_remark=row['twi_remark'],
                                        twi_position=row['twi_position'],
                                        ict_class=row['ict_class'],
                                        ict_exam=row['ict_exam'],
                                        ict_grade=row['ict_grade'],
                                        ict_total=row['ict_total'],
                                        ict_remark=row['ict_remark'],
                                        ict_position=row['ict_position'],
                                        french_class=row['french_class'],
                                        french_exam=row['french_exam'],
                                        french_grade=row['french_grade'],
                                        french_total=row['french_total'],
                                        french_remark=row['french_remark'],
                                        french_position=row['french_position'],
                                        rme_class=row['rme_class'],
                                        rme_exam=row['rme_exam'],
                                        rme_grade=row['rme_grade'],
                                        rme_total=row['rme_total'],
                                        rme_remark=row['rme_remark'],
                                        rme_position=row['rme_position'],
                                        bdt_class=row['bdt_class'],
                                        bdt_exam=row['bdt_exam'],
                                        bdt_grade=row['bdt_grade'],
                                        bdt_total=row['bdt_total'],
                                        bdt_remark=row['bdt_remark'],
                                        bdt_position=row['bdt_position'],
                                        )
        
        # Wrap the individual HTML template in a div with a page break
        individual_html_with_page_break = f'<div style="page-break-before: always;">{html_template}</div>'
        
        # Append the individual HTML template to the list
        individual_html_templates.append(individual_html_with_page_break)

    # Combine individual HTML templates into a single HTML document
    combined_html = "\n".join(individual_html_templates)

    # Save the combined HTML to a file
    combined_html_path = 'combined_student_results.html'
    with open(combined_html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(combined_html)

    # Generate a single PDF from the combined HTML
    pdfkit.from_file(combined_html_path, pdf_output_path, configuration=wkhtml_path, options={"enable-local-file-access": ""})

    # print(f'PDF generated: {pdf_output_path}')

    # Optional: Delete the temporary combined HTML file
    os.remove(combined_html_path)







root = tk.Tk()
root.title("App")

button = tk.Button(root, text="Generate Report", command=run_script )
button.pack()

root.mainloop()