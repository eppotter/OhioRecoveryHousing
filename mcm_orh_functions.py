import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def merge_orh(input_data, id_columns, id_name):

    input_data[id_name] = input_data[id_columns].bfill(axis=1).iloc[:, 0]


def format_orh_cols(input_data, column_path):

    orh_columns = pd.read_csv(column_path)

    orh_columns = orh_columns['Columns'].tolist()

    input_data.columns = orh_columns

    return(input_data)


def format_orh(input_data):

    path = '/Users/epotter/Desktop/ORH/orh_cols.csv'

    format_orh_cols(input_data, path)
    

    # Format comletion stages
    mask_in = input_data['frm_completion_stage'].str.contains('This form is being completed as a part of MOVE-IN to this recovery home, and I recently moved in.')
    mask_out = input_data['frm_completion_stage'].str.contains('This form is being completed as a part of MOVE-OUT from this recovery home.')
    mask_follow = input_data['frm_completion_stage'].str.contains('This form is being completed as a part of an IN-HOUSE FOLLOW UP SIX MONTHS after move-in.')

    in_new = 'Move In'
    out_new = 'Move Out'
    follow_new = 'Follow Up'

    input_data.loc[mask_in, 
                   'frm_completion_stage'] = in_new
    input_data.loc[mask_out, 
                   'frm_completion_stage'] = out_new
    input_data.loc[mask_follow, 
                   'frm_completion_stage'] = follow_new

    input_data = input_data.rename(columns = {'frm_completion_stage': 'Stage'})

    # Format initials for later data matching
    input_data['mother_first_i'] = input_data['mother_first_i'].str.upper()
    input_data['father_first_i'] = input_data['father_first_i'].str.upper()

    # Drop unwanted columns
    input_data.drop('survey_id', 
                    axis = 1, 
                    inplace = True)
    input_data.drop('consent_indicator', 
                    axis = 1, 
                    inplace = True)

    # Create Gender ID Column
    gender_id = ['gender_identify_agender','gender_identify_genderqueer',
                 'gender_identify_gender_fluid','gender_identify_man',
                 'gender_identify_non-binary','gender_identify_questioning',
                 'gender_identify_transgender','gender_identify_trans_man',
                 'gender_identify_trans_woman','gender_identify_woman',
                 'gender_identify_no_answer','gender_identify_other']

    merge_orh(input_data, gender_id, 'Gender')

    # Create Sexuality ID Column
    sexuality_id = ['sexual_identity_asexual','sexual_identity_bisexual',
                    'sexual_identity_gay','sexual_identity_heterosexual',
                    'sexual_identity_lesbian','sexual_identity_pansexual',
                    'sexual_identity_queer','sexual_identity_questioning',
                    'sexual_identity_same_gender_loving','sexual_identity_no_answer',
                    'sexual_identity_other']

    merge_orh(input_data, sexuality_id, 'Sexuality')

    # Create Race ID Column
    race_id = ['race_id_white','race_id_black_or_african_american',
               'race_id_american_indian_or_alaska_native','race_id_chinese',
               'race_id_vietnamese','race_id_native_hawaiian',
               'race_id_filipino','race_id_korean',
               'race_id_samoan','race_id_asian_indian',
               'race_id_japanese','race_id_chamorro',
               'race_id_other_asian','race_id_other_pacific_islander',
               'rad_id_no_answer','race_id_other']
    
    merge_orh(input_data, race_id, 'Race')

    # Create Criminal Justice ID Column
    crim_hist_id = ['curr_status_cjs_parole_probation','curr_status_cjs_drug_court',
                    'curr_status_cjs_no_involvement','curr_status_cjs_no_answer']
    
    merge_orh(input_data, crim_hist_id, 'CJS')

    return(input_data)



def orh_ages(input_data, stage, graph_title = ""):

        df = input_data[input_data['Stage'] == stage]

        df['age_range'] = df['age'].str.replace(' years', '')

        df = df.groupby('age_range').size().reset_index(name='count')

        # Include only age ranges
        df = df[df['age_range'] != 'Prefer not to answer']
        df = df[df['age_range'] != 'Unknown']

        # Set the plot style and color palette
        sns.set_style('whitegrid')
        sns.set_palette('muted')

        fig, ax = plt.subplots()
        ax.bar(df['age_range'],
                df['count'])
        ax.set_xticklabels(df['age_range'],
                        rotation=45, 
                        ha='right')
        ax.set_xlabel('Age Range')
        ax.set_ylabel('Percentage')
        if graph_title == "":
            ax.set_title(f'ORH Age Breakdown: {stage}')
        else :
             ax.set_title(f'{graph_title} - ORH Age Breakdown: {stage}')

        # display percent above each bar
        df['percent'] = df['count']/df['count'].sum() * 100

        for i, percent in enumerate(df['percent']):
                ax.text(i, 
                        df['count'][i]+0.5, 
                        f'{percent:.2f}%', 
                        ha='center', 
                        va='bottom')
                
        # Customize plot
        fig.set_size_inches(8, 6)
        ax.tick_params(axis = 'both',
                        which='major',
                        labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True)

        plt.tight_layout()
        plt.show()

 
def orh_education(input_data, stage, graph_title = ""):
    
    df = input_data[input_data['Stage'] == stage]
    df = df.groupby('highest_education_degree').size().reset_index(name='count')

    # Include only usable value ranges
    df = df[df['highest_education_degree'] != 'Prefer not to answer']
    df = df[df['highest_education_degree'] != 'Unknown']

    if len(df['highest_education_degree']) == 6:
        order = [3, 4, 2, 5, 1, 6]
        df['order'] = order
        df = df.sort_values('order', ascending=True)
        df = df.reset_index(drop=True)

    if len(df['highest_education_degree']) == 6:
        educ_names = ['No Degree', 'HS Diploma / GED',
                    "Associate's", "Bachelor's",
                    "Master's or Beyond", 'Tech/Vocational Cert']

        df['Education'] = educ_names
    else: df['Education'] = df['highest_education_degree']
    

    # Set the plot style and color palette
    sns.set_style('whitegrid')
    sns.set_palette('muted')

    fig, ax = plt.subplots()
    ax.bar(df['highest_education_degree'],
            df['count'])

    ax.set_xticklabels(df['Education'],rotation=45, ha='right')
    ax.set_xlabel('Education')
    ax.set_ylabel('Count')
    if graph_title == "":
        ax.set_title(f'ORH Highest Educational Degree Breakdown: {stage}')
    else:
        ax.set_title(f'{graph_title} - ORH Highest Educational Degree Breakdown: {stage}')

    # display percent above each bar
    df['percent'] = df['count']/df['count'].sum() * 100

    for i, percent in enumerate(df['percent']):
        ax.text(i, 
                df['count'][i]+0.5, 
                f'{percent:.2f}%', 
                ha='center', 
                va='bottom')
        
    ax.set_ylim([0, df['count'].max()*1.1])
        
    # Customize plot
    fig.set_size_inches(8, 6)
    ax.tick_params(axis = 'both',
                which='major',
                labelsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True)

    plt.tight_layout()
    plt.show()



def orh_race(input_data, stage, graph_title = ""):

        df = input_data[input_data['Stage'] == stage]

        rb = pd.DataFrame(df['Race'])
        rb.columns = ["Race_id"]

        df = rb.groupby('Race_id').size().reset_index(name='Count')

        df = df.sort_values('Count', ascending=True)
        df = df.reset_index(drop=True)

        # Set the plot style and color palette
        sns.set_style('whitegrid')
        sns.set_palette('muted')

        fig, ax = plt.subplots()
        ax.bar(df['Race_id'],
                df['Count'])

        ax.set_xticklabels(df['Race_id'],rotation=45, ha='right')
        ax.set_xlabel('Race: Self Identification')
        ax.set_ylabel('Count')
        if graph_title == "":
            ax.set_title(f'ORH Breakdown Race Breakdown - Self Identification: {stage}')
        else:
            ax.set_title(f'{graph_title} - ORH Breakdown Race Breakdown - Self Identification: {stage}')

        df['percent'] = df['Count']/df['Count'].sum() * 100

        for i, percent in enumerate(df['percent']):
                ax.text(i, 
                        df['Count'][i]+0.5, 
                        f'{percent:.2f}%', 
                        ha='center', 
                        va='bottom')
        
        ax.set_ylim([0, df['Count'].max()*1.1])
        
        # Customize plot
        fig.set_size_inches(8, 6)
        ax.tick_params(axis = 'both',
                which='major',
                labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True)

        plt.tight_layout()
        plt.show()


def orh_gender(input_data, stage, graph_title = ""):
        
        df = input_data[input_data['Stage'] == stage]

        gb = pd.DataFrame(df['Gender'])

        gb.columns = ["Gender_id"]

        df = gb.groupby('Gender_id').size().reset_index(name='Count')

        df = df.sort_values('Count', ascending=True)
        df = df.reset_index(drop=True)

        # Set the plot style and color palette
        sns.set_style('whitegrid')
        sns.set_palette('muted')

        fig, ax = plt.subplots()
        ax.bar(df['Gender_id'],
                df['Count'])

        ax.set_xticklabels(df['Gender_id'],rotation=45, ha='right')
        ax.set_xlabel('Gender: Self Identification')
        ax.set_ylabel('Count')
        if graph_title == "":
            ax.set_title(f'ORH Breakdown - Gender - Self Identification: {stage}')
        else:
            ax.set_title(f'{graph_title} - ORH Breakdown - Gender - Self Identification: {stage}')

        df['percent'] = round(df['Count']/df['Count'].sum(),4) * 100

        for i, percent in enumerate(df['percent']):
                ax.text(i, 
                        df['Count'][i]+0.5, 
                        f'{percent:.2f}%', 
                        ha='center', 
                        va='bottom')
                
        ax.set_ylim([0, df['Count'].max()*1.1])
        
        # Customize plot
        fig.set_size_inches(8, 6)
        ax.tick_params(axis = 'both',
                which='major',
                labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True)

        plt.tight_layout()
        plt.show()


def orh_sexuality(input_data, stage, graph_title = ""):

        df = input_data[input_data['Stage'] == stage]

        sb = pd.DataFrame(df['Sexuality'])

        sb.columns = ["Sexuality_Id"]

        df = sb.groupby('Sexuality_Id').size().reset_index(name='Count')

        df = df.sort_values('Count', ascending=True)
        df = df.reset_index(drop=True)

        # Set the plot style and color palette
        sns.set_style('whitegrid')
        sns.set_palette('muted')

        fig, ax = plt.subplots()
        ax.bar(df['Sexuality_Id'],
                df['Count'])

        ax.set_xticklabels(df['Sexuality_Id'],rotation=45, ha='right')
        ax.set_xlabel('Sexuality: Self Identification')
        ax.set_ylabel('Count')
        if graph_title == "":
            ax.set_title(f'ORH Breakdown - Sexuality - Self Identification: {stage}')
        else:
            ax.set_title(f'{graph_title} - ORH Breakdown - Sexuality - Self Identification: {stage}')

        df['percent'] = round(df['Count']/df['Count'].sum(),4) * 100

        for i, percent in enumerate(df['percent']):
                ax.text(i, 
                        df['Count'][i]+0.5, 
                        f'{percent:.2f}%', 
                        ha='center', 
                        va='bottom')
                
        ax.set_ylim([0, df['Count'].max()*1.1])
        
        # Customize plot
        fig.set_size_inches(8, 6)
        ax.tick_params(axis = 'both',
                which='major',
                labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True)

        plt.tight_layout()
        plt.show()



def orh_outcome_sub(input_data, graph_title = ""):
    # Substance User
    out_sub = input_data[['Stage','input_type','last_30_alcohol_use','last_30_illegal_drugs_non_prescribed_medications']]
    out_sub.columns = ['Stage','Input Type', 'Alcohol Use', 'Drug Use']

    out_sub = out_sub[out_sub['Input Type'] == 'Client']
    out_sub = out_sub[out_sub['Stage'] != 'Follow Up']
    alc_out_sub = out_sub[out_sub['Alcohol Use'] != 'Prefer not to answer']

    counts = alc_out_sub.groupby(['Alcohol Use', 'Stage']).size().unstack()

    perc = counts.div(counts.sum(axis=0),axis=1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Alcohol Use Last 30 Days: Move In vs Move Out')
    else:
        ax.set_title(f'{graph_title} - Alcohol Use Last 30 Days: Move In vs Move Out')

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)


    dr_out_sub = out_sub[out_sub['Drug Use'] != 'Prefer not to answer']

    counts = dr_out_sub.groupby(['Drug Use', 'Stage']).size().unstack()

    perc = counts.div(counts.sum(axis=0),axis=1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Drug Use Last 30 Days: Move In vs Move Out')
    else:
        ax.set_title(f'{graph_title} - Drug Use Last 30 Days: Move In vs Move Out')    


    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)

    return out_sub



def orh_outcome_prog(input_data, graph_title = ""):
    # Participation in Recovery Programs
    out_progs = input_data[['Stage','input_type','last_30_attendance_12_step','last_30_attendance_organized_religious_group','last_30_attendance_other_support_group',
                        'last_30_attendance_sober_support_outing','last_30_attendance_activities_sponsored_by_recovery_residence',
                        'last_30_attendance_activities_provided_while_incarcerated','last_30_attendance_none', 'last_30_attendance_no_answer',
                        'last_30_attendance_working_with_sponsor','last_30_attendance_in_home_group','last_30_received_peer_support']]
    update_cols = out_progs.columns[2:]
    for col in update_cols:
        out_progs[col] = out_progs[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)
    out_progs.columns = ['Stage','Input Type','Last 30: 12 Step','Last 30: Attended Religious Group','Last 30: Attended Other Support Group','Last 30: Attended Sober Support Outing','Last 30: Attended Recovery Residence Activity','Last 30: Attnded Activity while Incarcerated','Last 30: Attended No Program','Last 30: No Answer on Attendance','Last 30: Worked with Sponsor', 'Last 30: Attended Home Group', 'Last 30: Received Peer Support']

    out_progs = out_progs[out_progs['Input Type'] == 'Client']
    out_progs = out_progs[out_progs['Stage'] != 'Follow Up']

    
    grouped = out_progs.groupby("Stage").sum()

    # Calculate the percentage of total for each column
    total = grouped.sum(axis=1)
    percentage = grouped.div(total, axis=0) * 100

    # Transpose the DataFrame to have the "last 30" columns as rows
    percentage_t = percentage.transpose()

    # Create a horizontal stacked bar chart
    ax = percentage_t.plot(kind="bar", stacked=False)

    # Set the chart title and labels
    if graph_title == "":
        ax.set_title(f"Program Usage Comparison for 'Last 30' Columns: Move In vs Move Out")
    else:
        ax.set_title(f"{graph_title} - Program Usage Comparison for 'Last 30' Columns: Move In vs Move Out")    
    ax.set_xlabel("Percentage of Total (%)")
    ax.set_ylabel("Last 30 Columns")


    # Add percentage labels above each bar
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}%',
                    ha='center', va='bottom')

    # Show the chart
    plt.show()

    return out_progs


def orh_outcome_docs(input_data, graph_title = ""):
    # Personal Documents
    out_docs = input_data[['Stage','input_type','doc_status_drivers_license','doc_status_state_id','doc_status_social_security_card','doc_status_birth_certificate']]
    #out_docs.columns = [['Stage', 'Input Type', 'Drivers License', 'State ID', 'Social Security Card', 'Birth Certificate']]

    out_docs = out_docs[out_docs['input_type'] == 'Client']
    out_docs = out_docs[out_docs['Stage'] != 'Follow Up']

    # Drivers License
    out_docs_dl = out_docs[out_docs['doc_status_drivers_license'] != 'Prefer not to answer']
    out_docs_dl = out_docs_dl.groupby(['doc_status_drivers_license', 'Stage']).size().unstack()

    perc = out_docs_dl.div(out_docs_dl.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Document Status: Drivers License')
    else:
        ax.set_title(f'{graph_title} - Document Status: Drivers License')    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)

    # State ID
    out_docs_id = out_docs[out_docs['doc_status_state_id'] != 'Prefer not to answer']
    out_docs_id = out_docs_id.groupby(['doc_status_state_id', 'Stage']).size().unstack()

    perc = out_docs_id.div(out_docs_id.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Document Status: State ID')
    else:
        ax.set_title(f'{graph_title} - Document Status: State ID')    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)


    # Social Security Card
    out_docs_ss = out_docs[out_docs['doc_status_social_security_card'] != 'Prefer not to answer']
    out_docs_ss = out_docs_ss.groupby(['doc_status_social_security_card', 'Stage']).size().unstack()

    perc = out_docs_ss.div(out_docs_ss.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Document Status: Social Security Card')
    else:
        ax.set_title(f'{graph_title} - Document Status: Social Security Card')    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)


    # Birth Certificate
    out_docs_bc = out_docs[out_docs['doc_status_birth_certificate'] != 'Prefer not to answer']
    out_docs_bc = out_docs_bc.groupby(['doc_status_birth_certificate', 'Stage']).size().unstack()

    perc = out_docs_bc.div(out_docs_bc.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Document Status: Birth Certificate')
    else:
        ax.set_title(f'{graph_title} - Document Status: Birth Certificate')    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)

    return out_docs


# Update these to include graphs!

def orh_outcome_educ(input_data, graph_title = ""):
    # Education Progress
    out_educ = input_data[['Stage','input_type','last_30_education_progress_ged',
    'last_30_education_progress_vocational_school',
    'last_30_education_progress_skilled_training',
    'last_30_education_progress_college',
    'last_30_education_progress_not_involved']]
    update_cols = out_educ.columns[2:]
    for col in update_cols:
        out_educ[col] = out_educ[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)
    #out_educ.columns = [['Stage', 'Input Type', 'Last 30: GED', 'Last 30: Vocational School', 'Last 30: Skilled Training', 'Last 30: College', 'Last 30: No Involvement']]


    out_educ = out_educ[out_educ['input_type'] == 'Client']
    out_educ = out_educ[out_educ['Stage'] != 'Follow Up']

    grouped = out_educ.groupby("Stage").sum()
    grouped.columns = ['Last 30: GED', 'Last 30: Vocational School', 'Last 30: Skilled Training', 'Last 30: College', 'Last 30: No Involvement']

    # Calculate the percentage of total for each column
    total = grouped.sum(axis=1)
    percentage = grouped.div(total, axis=0) * 100

    # Transpose the DataFrame to have the "last 30" columns as rows
    percentage_t = percentage.transpose()

    # Create a horizontal stacked bar chart
    ax = percentage_t.plot(kind="bar", stacked=False)

    # Set the chart title and labels
    if graph_title == "":
        ax.set_title(f"Education Comparison for 'Last 30' Columns: Move In vs Move Out")
    else:
        ax.set_title(f"{graph_title} - Education Comparison for 'Last 30' Columns: Move In vs Move Out")    
    ax.set_xlabel("Percentage of Total (%)")
    ax.set_ylabel("Last 30 Columns")


    # Add percentage labels above each bar
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}%',
                    ha='center', va='bottom')

    # Show the chart
    plt.show()


    return out_educ


def orh_outcome_employ(input_data, graph_title = ""):
    # Employment Status
    out_emp = input_data[['Stage','input_type','last_30_employment_status',
    'last_30_volunteering_status']]

    out_emp = out_emp[out_emp['input_type'] == 'Client']
    out_emp = out_emp[out_emp['Stage'] != 'Follow Up']

    #out_emp.columns = [['Stage', 'Input Type', 'Last 30: Employment Status', 'Last 30: Volunteering Status']]

    # Employment Status
    out_emp_emp = out_emp[out_emp['last_30_employment_status'] != 'Prefer not to answer']
    out_emp_emp = out_emp_emp.groupby(['last_30_employment_status', 'Stage']).size().unstack()

    perc = out_emp_emp.div(out_emp_emp.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f"Employment Status")
    else:
        ax.set_title(f"{graph_title} - Employment Status")    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Volunteer Status
    out_emp_vol = out_emp[out_emp['last_30_volunteering_status'] != 'Prefer not to answer']
    out_emp_vol = out_emp_vol.groupby(['last_30_volunteering_status', 'Stage']).size().unstack()

    perc = out_emp_vol.div(out_emp_vol.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f"Volunteering Status")
    else:
        ax.set_title(f"{graph_title} - Volunteering Status")    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')


    return out_emp


def orh_outcome_health(input_data, graph_title = ""):

    # Health Status
    out_health = input_data[['Stage','input_type','last_30_physical_health','last_30_mental_health']]

    out_health = out_health[out_health['Stage'] != 'Follow Up']
    out_health = out_health[out_health['input_type'] == 'Client']

    # Physical Health
    out_health_phy = out_health[out_health['last_30_physical_health'] != 'Prefer not to answer']
    out_health_phy = out_health_phy.groupby(['last_30_physical_health', 'Stage']).size().unstack()

    perc = out_health_phy.div(out_health_phy.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f"Physical Health")
    else:
        ax.set_title(f"{graph_title} - Physical Health")    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)

    # Mental Health
    out_health_men = out_health[out_health['last_30_mental_health'] != 'Prefer not to answer']
    out_health_men = out_health_men.groupby(['last_30_mental_health', 'Stage']).size().unstack()

    perc = out_health_men.div(out_health_men.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f"Mental Health")
    else:
        ax.set_title(f"{graph_title} - Mental Health")

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)

    return out_health


def orh_outcome_consq(input_data, graph_title = ""):
    # Substance Use Consequences
    out_sub_consq = input_data[['Stage','input_type','last_30_substance_use_consequences_social',
        'last_30_substance_use_consequences_health_behavioral',
        'last_30_substance_use_consequences_financial',
        'last_30_substance_use_consequences_none_of_above',
        'last_30_substance_use_consequences_no_answer',
        'last_30_substance_use_consequences_other']]
    update_cols = out_sub_consq.columns[2:]
    for col in update_cols:
        out_sub_consq[col] = out_sub_consq[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)
    
    out_sub_consq = out_sub_consq[out_sub_consq['Stage'] != 'Follow Up']
    out_sub_consq = out_sub_consq[out_sub_consq['input_type'] == 'Client']

    grouped = out_sub_consq.groupby("Stage").sum()

    # Calculate the percentage of total for each column
    total = grouped.sum(axis=1)
    percentage = grouped.div(total, axis=0) * 100
    percentage.columns = ['Last 30: Substance Abuse Consequence - Social', 
                        'Last 30: Substance Abuse Consequence - Health/Behavioral', 'Last 30: Substance Abuse Consequence - Financial',
                        'Last 30: Substance Abuse Consequence - None Listed ', 'Last 30: Substance Abuse Consequence - No Answer',
                        'Last 30: Substance Abuse Consequence - Other']
    # Transpose the DataFrame to have the "last 30" columns as rows
    percentage_t = percentage.transpose()
    
    # Create a horizontal stacked bar chart
    ax = percentage_t.plot(kind="bar", stacked=False)

    # Set the chart title and labels
    if graph_title == "":
        ax.set_title(f"Outcome Substance Consequences for 'Last 30' Columns: Move In vs Move Out")
    else:
        ax.set_title(f"{graph_title} - Outcome Substance Consequences for 'Last 30' Columns: Move In vs Move Out")
    ax.set_xlabel("Percentage of Total (%)")
    ax.set_ylabel("Last 30 Columns")

    # Add percentage labels above each bar
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}%',
                    ha='center', va='bottom')
            
    # Show the chart
    plt.show()

    return out_sub_consq

def orh_all_outcome_sub(input_data, graph_title = ""):
    # Substance User
    out_sub = input_data[['Stage','input_type','last_30_alcohol_use','last_30_illegal_drugs_non_prescribed_medications']]
    out_sub.columns = ['Stage','Input Type', 'Alcohol Use', 'Drug Use']

    #out_sub = out_sub[out_sub['Input Type'] == 'Client']
    out_sub = out_sub[out_sub['Stage'] != 'Follow Up']
    alc_out_sub = out_sub[out_sub['Alcohol Use'] != 'Prefer not to answer']

    counts = alc_out_sub.groupby(['Alcohol Use', 'Stage']).size().unstack()

    perc = counts.div(counts.sum(axis=0),axis=1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Alcohol Use Last 30 Days: Move In vs Move Out')
    else:
        ax.set_title(f'{graph_title} - Alcohol Use Last 30 Days: Move In vs Move Out')

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)


    dr_out_sub = out_sub[out_sub['Drug Use'] != 'Prefer not to answer']

    counts = dr_out_sub.groupby(['Drug Use', 'Stage']).size().unstack()

    perc = counts.div(counts.sum(axis=0),axis=1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Drug Use Last 30 Days: Move In vs Move Out')
    else:
        ax.set_title(f'{graph_title} - Drug Use Last 30 Days: Move In vs Move Out')    


    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)

    return out_sub



def orh_all_outcome_prog(input_data, graph_title = ""):
    # Participation in Recovery Programs
    out_progs = input_data[['Stage','input_type','last_30_attendance_12_step','last_30_attendance_organized_religious_group','last_30_attendance_other_support_group',
                        'last_30_attendance_sober_support_outing','last_30_attendance_activities_sponsored_by_recovery_residence',
                        'last_30_attendance_activities_provided_while_incarcerated','last_30_attendance_none', 'last_30_attendance_no_answer',
                        'last_30_attendance_working_with_sponsor','last_30_attendance_in_home_group','last_30_received_peer_support']]
    update_cols = out_progs.columns[2:]
    for col in update_cols:
        out_progs[col] = out_progs[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)
    out_progs.columns = ['Stage','Input Type','Last 30: 12 Step','Last 30: Attended Religious Group','Last 30: Attended Other Support Group','Last 30: Attended Sober Support Outing','Last 30: Attended Recovery Residence Activity','Last 30: Attnded Activity while Incarcerated','Last 30: Attended No Program','Last 30: No Answer on Attendance','Last 30: Worked with Sponsor', 'Last 30: Attended Home Group', 'Last 30: Received Peer Support']

    #out_progs = out_progs[out_progs['Input Type'] == 'Client']
    out_progs = out_progs[out_progs['Stage'] != 'Follow Up']

    
    grouped = out_progs.groupby("Stage").sum()

    # Calculate the percentage of total for each column
    total = grouped.sum(axis=1)
    percentage = grouped.div(total, axis=0) * 100

    # Transpose the DataFrame to have the "last 30" columns as rows
    percentage_t = percentage.transpose()

    # Create a horizontal stacked bar chart
    ax = percentage_t.plot(kind="bar", stacked=False)

    # Set the chart title and labels
    if graph_title == "":
        ax.set_title(f"Program Usage Comparison for 'Last 30' Columns: Move In vs Move Out")
    else:
        ax.set_title(f"{graph_title} - Program Usage Comparison for 'Last 30' Columns: Move In vs Move Out")    
    ax.set_xlabel("Percentage of Total (%)")
    ax.set_ylabel("Last 30 Columns")


    # Add percentage labels above each bar
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}%',
                    ha='center', va='bottom')

    # Show the chart
    plt.show()

    return out_progs


def orh_all_outcome_docs(input_data, graph_title = ""):
    # Personal Documents
    out_docs = input_data[['Stage','input_type','doc_status_drivers_license','doc_status_state_id','doc_status_social_security_card','doc_status_birth_certificate']]
    #out_docs.columns = [['Stage', 'Input Type', 'Drivers License', 'State ID', 'Social Security Card', 'Birth Certificate']]

    #out_docs = out_docs[out_docs['input_type'] == 'Client']
    out_docs = out_docs[out_docs['Stage'] != 'Follow Up']

    # Drivers License
    out_docs_dl = out_docs[out_docs['doc_status_drivers_license'] != 'Prefer not to answer']
    out_docs_dl = out_docs_dl.groupby(['doc_status_drivers_license', 'Stage']).size().unstack()

    perc = out_docs_dl.div(out_docs_dl.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Document Status: Drivers License')
    else:
        ax.set_title(f'{graph_title} - Document Status: Drivers License')    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)

    # State ID
    out_docs_id = out_docs[out_docs['doc_status_state_id'] != 'Prefer not to answer']
    out_docs_id = out_docs_id.groupby(['doc_status_state_id', 'Stage']).size().unstack()

    perc = out_docs_id.div(out_docs_id.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Document Status: State ID')
    else:
        ax.set_title(f'{graph_title} - Document Status: State ID')    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)


    # Social Security Card
    out_docs_ss = out_docs[out_docs['doc_status_social_security_card'] != 'Prefer not to answer']
    out_docs_ss = out_docs_ss.groupby(['doc_status_social_security_card', 'Stage']).size().unstack()

    perc = out_docs_ss.div(out_docs_ss.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Document Status: Social Security Card')
    else:
        ax.set_title(f'{graph_title} - Document Status: Social Security Card')    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)


    # Birth Certificate
    out_docs_bc = out_docs[out_docs['doc_status_birth_certificate'] != 'Prefer not to answer']
    out_docs_bc = out_docs_bc.groupby(['doc_status_birth_certificate', 'Stage']).size().unstack()

    perc = out_docs_bc.div(out_docs_bc.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f'Document Status: Birth Certificate')
    else:
        ax.set_title(f'{graph_title} - Document Status: Birth Certificate')    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)

    return out_docs


# Update these to include graphs!

def orh_all_outcome_educ(input_data, graph_title = ""):
    # Education Progress
    out_educ = input_data[['Stage','input_type','last_30_education_progress_ged',
    'last_30_education_progress_vocational_school',
    'last_30_education_progress_skilled_training',
    'last_30_education_progress_college',
    'last_30_education_progress_not_involved']]
    update_cols = out_educ.columns[2:]
    for col in update_cols:
        out_educ[col] = out_educ[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)
    #out_educ.columns = [['Stage', 'Input Type', 'Last 30: GED', 'Last 30: Vocational School', 'Last 30: Skilled Training', 'Last 30: College', 'Last 30: No Involvement']]


    #out_educ = out_educ[out_educ['input_type'] == 'Client']
    out_educ = out_educ[out_educ['Stage'] != 'Follow Up']

    grouped = out_educ.groupby("Stage").sum()
    grouped.columns = ['Last 30: GED', 'Last 30: Vocational School', 'Last 30: Skilled Training', 'Last 30: College', 'Last 30: No Involvement']

    # Calculate the percentage of total for each column
    total = grouped.sum(axis=1)
    percentage = grouped.div(total, axis=0) * 100

    # Transpose the DataFrame to have the "last 30" columns as rows
    percentage_t = percentage.transpose()

    # Create a horizontal stacked bar chart
    ax = percentage_t.plot(kind="bar", stacked=False)

    # Set the chart title and labels
    if graph_title == "":
        ax.set_title(f"Education Comparison for 'Last 30' Columns: Move In vs Move Out")
    else:
        ax.set_title(f"{graph_title} - Education Comparison for 'Last 30' Columns: Move In vs Move Out")    
    ax.set_xlabel("Percentage of Total (%)")
    ax.set_ylabel("Last 30 Columns")


    # Add percentage labels above each bar
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}%',
                    ha='center', va='bottom')

    # Show the chart
    plt.show()


    return out_educ


def orh_all_outcome_employ(input_data, graph_title = ""):
    # Employment Status
    out_emp = input_data[['Stage','input_type','last_30_employment_status',
    'last_30_volunteering_status']]

    #out_emp = out_emp[out_emp['input_type'] == 'Client']
    out_emp = out_emp[out_emp['Stage'] != 'Follow Up']

    #out_emp.columns = [['Stage', 'Input Type', 'Last 30: Employment Status', 'Last 30: Volunteering Status']]

    # Employment Status
    out_emp_emp = out_emp[out_emp['last_30_employment_status'] != 'Prefer not to answer']
    out_emp_emp = out_emp_emp.groupby(['last_30_employment_status', 'Stage']).size().unstack()

    perc = out_emp_emp.div(out_emp_emp.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f"Employment Status")
    else:
        ax.set_title(f"{graph_title} - Employment Status")    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Volunteer Status
    out_emp_vol = out_emp[out_emp['last_30_volunteering_status'] != 'Prefer not to answer']
    out_emp_vol = out_emp_vol.groupby(['last_30_volunteering_status', 'Stage']).size().unstack()

    perc = out_emp_vol.div(out_emp_vol.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f"Volunteering Status")
    else:
        ax.set_title(f"{graph_title} - Volunteering Status")    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')


    return out_emp


def orh_all_outcome_health(input_data, graph_title = ""):

    # Health Status
    out_health = input_data[['Stage','input_type','last_30_physical_health','last_30_mental_health']]

    out_health = out_health[out_health['Stage'] != 'Follow Up']
    #out_health = out_health[out_health['input_type'] == 'Client']

    # Physical Health
    out_health_phy = out_health[out_health['last_30_physical_health'] != 'Prefer not to answer']
    out_health_phy = out_health_phy.groupby(['last_30_physical_health', 'Stage']).size().unstack()

    perc = out_health_phy.div(out_health_phy.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f"Physical Health")
    else:
        ax.set_title(f"{graph_title} - Physical Health")    

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)

    # Mental Health
    out_health_men = out_health[out_health['last_30_mental_health'] != 'Prefer not to answer']
    out_health_men = out_health_men.groupby(['last_30_mental_health', 'Stage']).size().unstack()

    perc = out_health_men.div(out_health_men.sum(axis = 0), axis = 1)

    ax = perc.plot(kind = 'bar')
    ax.set_ylabel('Percent Total')
    if graph_title == "":
        ax.set_title(f"Mental Health")
    else:
        ax.set_title(f"{graph_title} - Mental Health")

    # Add percentage labels above each bar
    for i in range(len(ax.containers)):
        container = ax.containers[i]
        for j, val in enumerate(container):
            height = val.get_height()
            ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                    ha='center', va='bottom')

    # Set the y-axis limits
    ax.set_ylim(0, 1)

    return out_health


def orh_all_outcome_consq(input_data, graph_title = ""):
    # Substance Use Consequences
    out_sub_consq = input_data[['Stage','input_type','last_30_substance_use_consequences_social',
        'last_30_substance_use_consequences_health_behavioral',
        'last_30_substance_use_consequences_financial',
        'last_30_substance_use_consequences_none_of_above',
        'last_30_substance_use_consequences_no_answer',
        'last_30_substance_use_consequences_other']]
    update_cols = out_sub_consq.columns[2:]
    for col in update_cols:
        out_sub_consq[col] = out_sub_consq[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)
    
    out_sub_consq = out_sub_consq[out_sub_consq['Stage'] != 'Follow Up']
    #out_sub_consq = out_sub_consq[out_sub_consq['input_type'] == 'Client']

    grouped = out_sub_consq.groupby("Stage").sum()

    # Calculate the percentage of total for each column
    total = grouped.sum(axis=1)
    percentage = grouped.div(total, axis=0) * 100
    percentage.columns = ['Last 30: Substance Abuse Consequence - Social', 
                        'Last 30: Substance Abuse Consequence - Health/Behavioral', 'Last 30: Substance Abuse Consequence - Financial',
                        'Last 30: Substance Abuse Consequence - None Listed ', 'Last 30: Substance Abuse Consequence - No Answer',
                        'Last 30: Substance Abuse Consequence - Other']
    # Transpose the DataFrame to have the "last 30" columns as rows
    percentage_t = percentage.transpose()
    
    # Create a horizontal stacked bar chart
    ax = percentage_t.plot(kind="bar", stacked=False)

    # Set the chart title and labels
    if graph_title == "":
        ax.set_title(f"Outcome Substance Consequences for 'Last 30' Columns: Move In vs Move Out")
    else:
        ax.set_title(f"{graph_title} - Outcome Substance Consequences for 'Last 30' Columns: Move In vs Move Out")
    ax.set_xlabel("Percentage of Total (%)")
    ax.set_ylabel("Last 30 Columns")

    # Add percentage labels above each bar
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}%',
                    ha='center', va='bottom')
            
    # Show the chart
    plt.show()

    return out_sub_consq
    

def orh_all_outcome_comp_summary(data1, data2 ,graph_title1 = '', graph_title2 = ''):

    orh_all_outcome_sub(data1, 
                    graph_title = graph_title1)
    orh_all_outcome_sub(data2, 
                    graph_title = graph_title2)
    print('\n'*20)

    orh_all_outcome_docs(data1, 
                     graph_title = graph_title1)
    orh_all_outcome_docs(data2, 
                     graph_title = graph_title2)

    print('\n'*20)

    orh_all_outcome_educ(data1, 
                     graph_title = graph_title1)
    orh_all_outcome_educ(data2, 
                     graph_title = graph_title2)

    print('\n'*20)

    orh_all_outcome_employ(data1, 
                       graph_title = graph_title1)
    orh_all_outcome_employ(data2, 
                       graph_title = graph_title2)

    print('\n'*20)

    orh_all_outcome_consq(data1, 
                      graph_title = graph_title1)
    orh_all_outcome_consq(data2, 
                      graph_title = graph_title2)

    print('\n'*20)

    orh_all_outcome_health(data1, 
                       graph_title = graph_title1)
    orh_all_outcome_health(data2, 
                       graph_title = graph_title2)
    
    print('\n'*20)

    orh_all_outcome_prog(data1, 
                     graph_title = graph_title1)
    orh_all_outcome_prog(data2, 
                     graph_title = graph_title2)


def orh_outcome_summary(data, graph_title = ''):

    orh_outcome_sub(data, 
                    graph_title = graph_title)
    
    print('\n'*20)

    orh_outcome_docs(data, 
                     graph_title = graph_title)

    print('\n'*20)

    orh_outcome_educ(data, 
                     graph_title = graph_title)

    print('\n'*20)

    orh_outcome_employ(data, 
                       graph_title = graph_title)

    print('\n'*20)

    orh_outcome_consq(data, 
                      graph_title = graph_title)

    print('\n'*20)

    orh_outcome_health(data, 
                       graph_title = graph_title)
    print('\n'*20)

    orh_outcome_prog(data, 
                     graph_title = graph_title)
    

def orh_outcome_comp_summary(data1, data2 ,graph_title1 = '', graph_title2 = ''):

    orh_outcome_sub(data1, 
                    graph_title = graph_title1)
    orh_outcome_sub(data2, 
                    graph_title = graph_title2)
    print('\n'*20)

    orh_outcome_docs(data1, 
                     graph_title = graph_title1)
    orh_outcome_docs(data2, 
                     graph_title = graph_title2)

    print('\n'*20)

    orh_outcome_educ(data1, 
                     graph_title = graph_title1)
    orh_outcome_educ(data2, 
                     graph_title = graph_title2)

    print('\n'*20)

    orh_outcome_employ(data1, 
                       graph_title = graph_title1)
    orh_outcome_employ(data2, 
                       graph_title = graph_title2)

    print('\n'*20)

    orh_outcome_consq(data1, 
                      graph_title = graph_title1)
    orh_outcome_consq(data2, 
                      graph_title = graph_title2)

    print('\n'*20)

    orh_outcome_health(data1, 
                       graph_title = graph_title1)
    orh_outcome_health(data2, 
                       graph_title = graph_title2)
    
    print('\n'*20)

    orh_outcome_prog(data1, 
                     graph_title = graph_title1)
    orh_outcome_prog(data2, 
                     graph_title = graph_title2)


def orh_cohort_comp_summary(data1, data2, graph_title1 = '', graph_title2 = '', stage = 'Move In'):

    orh_ages(data1, 
            stage = stage, 
            graph_title = graph_title1)
    orh_ages(data2, 
            stage = stage, 
            graph_title = graph_title2)

    print('\n'*20)

    orh_education(data1, 
                stage = stage, 
                graph_title = graph_title1)
    orh_education(data2, 
                stage = stage, 
                graph_title = graph_title2)

    print('\n'*20)

    orh_gender(data1, 
            stage = stage, 
            graph_title = graph_title1)
    orh_gender(data2, 
            stage = stage, 
            graph_title = graph_title2)

    print('\n'*20)

    orh_sexuality(data1, 
            stage = stage, 
            graph_title = graph_title1)
    orh_sexuality(data2, 
            stage = stage, 
            graph_title = graph_title2)

    print('\n'*20)

    orh_race(data1, 
            stage = stage, 
            graph_title = graph_title1)
    orh_race(data2, 
            stage = stage, 
            graph_title = graph_title2)
    

def orh_cohort_summary(data1, graph_title1 = '', stage = 'Move In'):

    orh_ages(data1, 
            stage = stage, 
            graph_title = graph_title1)

    print('\n'*20)

    orh_education(data1, 
                stage = stage, 
                graph_title = graph_title1)
    
    print('\n'*20)

    orh_gender(data1, 
            stage = stage, 
            graph_title = graph_title1)

    print('\n'*20)

    orh_sexuality(data1, 
            stage = stage, 
            graph_title = graph_title1)

    print('\n'*20)

    orh_race(data1, 
            stage = stage, 
            graph_title = graph_title1)

def orh_full_summary(data, graph_title = '', stage = 'Move In'):
        orh_cohort_summary(data, graph_title, stage)
        orh_outcome_summary(data, graph_title)

def orh_full_comparison(data1, data2, graph_title1 = '', graph_title2 = '', stage = "Move In"):
     orh_cohort_comp_summary(data1, data2, graph_title1, graph_title2, stage)
     orh_outcome_comp_summary(data1, data2, graph_title1, graph_title2)