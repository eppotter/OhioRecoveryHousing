import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import date
import os


def merge_orh(input_data, id_columns, id_name):

    input_data[id_name] = input_data[id_columns].bfill(axis=1).iloc[:, 0]


def format_orh_cols(input_data, column_path):

    orh_columns = pd.read_csv(column_path)

    orh_columns = orh_columns['Columns'].tolist()

    input_data.columns = orh_columns

    return input_data


def format_orh(input_data):

    path = './orh_cols.csv'

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

    input_data = input_data.rename(columns={'frm_completion_stage': 'Stage'})

    # Format initials for later data matching
    input_data['mother_first_i'] = input_data['mother_first_i'].str.upper()
    input_data['father_first_i'] = input_data['father_first_i'].str.upper()

    # Drop unwanted columns
    input_data.drop('survey_id',
                    axis=1,
                    inplace=True)
    input_data.drop('consent_indicator',
                    axis=1,
                    inplace=True)

    # Create Gender ID Column
    gender_id = ['gender_identify_agender', 'gender_identify_genderqueer',
                 'gender_identify_gender_fluid', 'gender_identify_man',
                 'gender_identify_non-binary', 'gender_identify_questioning',
                 'gender_identify_transgender', 'gender_identify_trans_man',
                 'gender_identify_trans_woman', 'gender_identify_woman',
                 'gender_identify_no_answer', 'gender_identify_other']

    merge_orh(input_data, gender_id, 'Gender')

    # Create Sexuality ID Column
    sexuality_id = ['sexual_identity_asexual', 'sexual_identity_bisexual',
                    'sexual_identity_gay', 'sexual_identity_heterosexual',
                    'sexual_identity_lesbian', 'sexual_identity_pansexual',
                    'sexual_identity_queer', 'sexual_identity_questioning',
                    'sexual_identity_same_gender_loving',
                    'sexual_identity_no_answer', 'sexual_identity_other']

    merge_orh(input_data, sexuality_id, 'Sexuality')

    # Create Race ID Column
    race_id = ['race_id_white', 'race_id_black_or_african_american',
               'race_id_american_indian_or_alaska_native',
               'race_id_chinese', 'race_id_vietnamese',
               'race_id_native_hawaiian', 'race_id_filipino', 'race_id_korean',
               'race_id_samoan', 'race_id_asian_indian',
               'race_id_japanese', 'race_id_chamorro',
               'race_id_other_asian', 'race_id_other_pacific_islander',
               'rad_id_no_answer', 'race_id_other']
    
    merge_orh(input_data, race_id, 'Race')

    # Create Criminal Justice ID Column
    crim_hist_id = ['curr_status_cjs_parole_probation',
                    'curr_status_cjs_drug_court',
                    'curr_status_cjs_no_involvement',
                    'curr_status_cjs_no_answer']

    merge_orh(input_data, crim_hist_id, 'CJS')

    return input_data


def orh_ages(input_data, stage, plot=False, title=""):

    method_title = "Age Breakdown"
    df = input_data[input_data['Stage'] == stage]

    df['age_range'] = df['age'].str.replace(' years', '')

    df = df.groupby('age_range').size().reset_index(name='count')

    # Include only age ranges
    df = df[df['age_range'] != 'Prefer not to answer']
    df = df[df['age_range'] != 'Unknown']
    df['percent'] = df['count']/df['count'].sum() * 100
    output_table = df.copy()
    output_table[f'Total Sample Size {title}'] = output_table['count'].sum()
    print(f"{method_title} {title}: Sample Size = {df['count'].sum()}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{df}")
    print("============================================\n\n")

    if plot is True:
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
        if title == "":
            ax.set_title(f'ORH Age Breakdown: {stage}')
        else:
            ax.set_title(f'{title} - ORH Age Breakdown: {stage}')

        # display percent above each bar
        for i, percent in enumerate(df['percent']):
            ax.text(i,
                    df['count'][i]+0.5,
                    f'{percent:.2f}%',
                    ha='center',
                    va='bottom')

            # Customize plot
        fig.set_size_inches(8, 6)
        ax.tick_params(axis='both',
                       which='major',
                       labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True)

        plt.tight_layout()
        plt.show()

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Cohort_Comparisons/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_table.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')


def orh_education(input_data, stage, plot=False, title=""):

    method_title = "Highest Educational Degree"

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
    else:
        df['Education'] = df['highest_education_degree']

    df['percent'] = df['count']/df['count'].sum() * 100
    output_table = df.copy()
    output_table[f'Total Sample Size {title}'] = output_table['count'].sum()
    print(f"{method_title} {title}: Sample Size = {df['count'].sum()}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{df}")
    print("============================================\n\n")
    if plot is True:
        # Set the plot style and color palette
        sns.set_style('whitegrid')
        sns.set_palette('muted')

        fig, ax = plt.subplots()
        ax.bar(df['highest_education_degree'],
               df['count'])

        ax.set_xticklabels(df['Education'],rotation=45, ha='right')
        ax.set_xlabel('Education')
        ax.set_ylabel('Count')
        if title == "":
            ax.set_title(f'ORH Highest Educational Degree Breakdown: {stage}')
        else:
            ax.set_title(f'{title} - ORH Highest Educational Degree Breakdown: {stage}')

        # display percent above each bar
        for i, percent in enumerate(df['percent']):
            ax.text(i,
                    df['count'][i]+0.5,
                    f'{percent:.2f}%',
                    ha='center',
                    va='bottom')

        ax.set_ylim([0, df['count'].max()*1.1])

        # Customize plot
        fig.set_size_inches(8, 6)
        ax.tick_params(axis='both',
                       which='major',
                       labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True)

        plt.tight_layout()
        plt.show()

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Cohort_Comparisons/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_table.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')


def orh_race(input_data, stage, plot=False, title=""):

    method_title = "Race Breakdown"
    df = input_data[input_data['Stage'] == stage]

    orh_race = df[['race_id_white', 'race_id_black_or_african_american',
                     'race_id_american_indian_or_alaska_native', 'race_id_chinese',
                     'race_id_vietnamese', 'race_id_native_hawaiian', 'race_id_filipino',
                     'race_id_korean', 'race_id_samoan', 'race_id_asian_indian',
                     'race_id_japanese','race_id_chamorro', 'race_id_other_asian',
                     'race_id_other_pacific_islander', 'rad_id_no_answer', 'race_id_other']]

    orh_race.fillna(0, inplace=True)

    orh_race = orh_race.astype(bool).astype(int)

    new_col_names = [col_name.replace('race_id_', '').replace('rad_id_', '') for col_name in orh_race.columns]
    orh_race.columns = new_col_names

    r_sum = orh_race.sum()
    r_count = orh_race.count()
    r_perc = r_sum/r_count

    r_brkdwn = pd.concat([r_sum, r_count, r_perc], axis=1)
    r_brkdwn = r_brkdwn.reset_index().rename(columns={'index': 'race',
                                                      0: 'Total',
                                                      1: 'Surveys',
                                                      2: 'Percent Surveyed'})
    # Create new dataframe for graph display
    r_graphs = r_brkdwn.copy()
    r_graphs['g_perc'] = r_graphs['Percent Surveyed']*100

    # Create output dataframe for export
    output_table = r_brkdwn



    print(f"{method_title} {title}: Sample Size = {r_count[0]}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{r_brkdwn}")
    print("============================================\n\n")

    if plot is True:
        # Set the plot style and color palette
        sns.set_style('whitegrid')
        sns.set_palette('muted')

        fig, ax = plt.subplots()
        ax.bar(r_graphs['race'],
               r_graphs['Total'])

        ax.set_xticklabels(r_graphs['race'],rotation=45, ha='right')
        ax.set_xlabel('Race: Self Identification - Percentage of Surveys')
        ax.set_ylabel('Total')
        if title == "":
            ax.set_title(f'ORH Breakdown Race Breakdown - Self Identification: {stage}')
        else:
            ax.set_title(f'{title} - ORH Breakdown Race Breakdown - Self Identification: {stage}')

        for i, percent in enumerate(r_graphs['g_perc']):
            ax.text(i,
                    r_graphs['Total'][i]+0.5,
                    f'{percent:.2f}%',
                    ha='center',
                    va='bottom')

        ax.set_ylim([0, r_graphs['Total'].max()*1.1])

        # Customize plot
        fig.set_size_inches(8, 6)
        ax.tick_params(axis='both',
                       which='major',
                       labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True)

        plt.tight_layout()
        plt.show()

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Cohort_Comparisons/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_table.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')


def orh_gender(input_data, stage, plot=False, title=""):

    method_title = "Gender Breakdown"
    df = input_data[input_data['Stage'] == stage]

    orh_gender = df[['gender_identify_agender', 'gender_identify_genderqueer',
    'gender_identify_gender_fluid', 'gender_identify_man',
    'gender_identify_non-binary', 'gender_identify_questioning',
    'gender_identify_transgender', 'gender_identify_trans_man',
    'gender_identify_trans_woman', 'gender_identify_woman',
    'gender_identify_no_answer', 'gender_identify_other']]

    orh_gender.fillna(0, inplace = True)

    orh_gender = orh_gender.astype(bool).astype(int)

    new_col_names = [col_name.replace('gender_identity_', '') for col_name in orh_gender.columns]
    orh_gender.columns = new_col_names

    g_sum = orh_gender.sum()
    g_count = orh_gender.count()
    g_perc = g_sum/g_count

    g_brkdwn = pd.concat([g_sum, g_count, g_perc], axis=1)
    g_brkdwn = g_brkdwn.reset_index().rename(columns = {'index': 'gender',
                                                        0: 'Total',
                                                        1: 'Surveys',
                                                        2: 'Percent Surveyed'})
    # Create new dataframe for graph display
    g_graphs = g_brkdwn.copy()
    g_graphs['g_perc'] = g_graphs['Percent Surveyed']*100
    
    # Create output dataframe for export
    output_table = g_brkdwn



    print(f"{method_title} {title}: Sample Size = {g_count[0]}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{g_brkdwn}")
    print("============================================\n\n")

    if plot is True:
        # Set the plot style and color palette
        sns.set_style('whitegrid')
        sns.set_palette('muted')

        fig, ax = plt.subplots()
        ax.bar(g_graphs['gender'],
               g_graphs['Total'])

        ax.set_xticklabels(g_graphs['gender'],rotation=45, ha='right')
        ax.set_xlabel('Gender: Self Identification - Percentage of Surveys')
        ax.set_ylabel('Count')
        if title == "":
            ax.set_title(f'ORH Breakdown - Gender - Self Identification: {stage}')
        else:
            ax.set_title(f'{title} - ORH Breakdown - Gender - Self Identification: {stage}')

        for i, percent in enumerate(g_graphs['g_perc']):
            ax.text(i, 
                    g_graphs['Total'][i]+0.5,
                    f'{percent:.2f}%',
                    ha='center',
                    va='bottom')

        ax.set_ylim([0, g_graphs['Total'].max()*1.1])

        # Customize plot
        fig.set_size_inches(8, 6)
        ax.tick_params(axis='both',
                       which='major',
                       labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True)

        plt.tight_layout()
        plt.show()

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Cohort_Comparisons/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_table.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')



def orh_sexuality(input_data, stage, plot=False, title=""):

    method_title = "Sexuality Breakdown"
    df = input_data[input_data['Stage'] == stage]

    orh_sex = df[['sexual_identity_asexual', 'sexual_identity_bisexual',
                     'sexual_identity_gay', 'sexual_identity_heterosexual',
                     'sexual_identity_lesbian', 'sexual_identity_pansexual',
                     'sexual_identity_queer', 'sexual_identity_questioning',
                     'sexual_identity_same_gender_loving', 'sexual_identity_no_answer',
                     'sexual_identity_other']]

    orh_sex.fillna(0, inplace = True)

    orh_sex = orh_sex.astype(bool).astype(int)

    new_col_names = [col_name.replace('sexual_identity_', '') for col_name in orh_sex.columns]
    orh_sex.columns = new_col_names

    s_sum = orh_sex.sum()
    s_count = orh_sex.count()
    s_perc = s_sum/s_count

    s_brkdwn = pd.concat([s_sum, s_count, s_perc], axis=1)
    s_brkdwn = s_brkdwn.reset_index().rename(columns = {'index': 'Sexuality',
                                                        0: 'Total',
                                                        1: 'Surveys',
                                                        2: 'Percent Surveyed'})
    # Create new dataframe for graph display
    s_graphs = s_brkdwn.copy()
    s_graphs['g_perc'] = s_graphs['Percent Surveyed']*100
    
    # Create output dataframe for export
    output_table = s_brkdwn


    print(f"{method_title} {title}: Sample Size = {s_count[0]}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{s_brkdwn}")
    print("============================================\n\n")

    if plot is True:
        # Set the plot style and color palette
        sns.set_style('whitegrid')
        sns.set_palette('muted')

        fig, ax = plt.subplots()
        ax.bar(s_graphs['Sexuality'],
               s_graphs['Total'])

        ax.set_xticklabels(s_graphs['Sexuality'],rotation=45, ha='right')
        ax.set_xlabel('Sexuality: Self Identification - Percentage of Surveys')
        ax.set_ylabel('Count')
        if title == "":
            ax.set_title(f'ORH Breakdown - Sexuality - Self Identification: {stage}')
        else:
            ax.set_title(f'{title} - ORH Breakdown - Sexuality - Self Identification: {stage}')

        for i, percent in enumerate(s_graphs['g_perc']):
            ax.text(i, 
                    s_graphs['Total'][i]+0.5,
                    f'{percent:.2f}%',
                    ha='center',
                    va='bottom')

        ax.set_ylim([0, s_graphs['Total'].max()*1.1])

        # Customize plot
        fig.set_size_inches(8, 6)
        ax.tick_params(axis='both',
                       which='major',
                       labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True)

        plt.tight_layout()
        plt.show()

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Cohort_Comparisons/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_table.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')


# -----------------------------------------------------------------------------------------
#                                       OUTCOMES
# -----------------------------------------------------------------------------------------


def outcomeSubstance(input_data,
                     title="",
                     plot=False,
                     includeStaff=False,
                     noAnswers=False):

    method_title_a = "Alcohol Use"

    # Substance User
    out_sub = input_data[['Stage', 'input_type', 'last_30_alcohol_use',
                          'last_30_illegal_drugs_non_prescribed_medications']]
    out_sub.columns = ['Stage', 'Input Type', 'Alcohol Use', 'Drug Use']

    out_sub = out_sub[out_sub['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_sub = out_sub[out_sub['Input Type'] == 'Client']

    if noAnswers is False:
        alc_out_sub = out_sub[out_sub['Alcohol Use'] != 'Prefer not to answer']
        alc_out_sub = alc_out_sub[alc_out_sub['Alcohol Use'] != 'Unknown']
    else:
        alc_out_sub = out_sub

    counts_a = alc_out_sub.groupby(['Alcohol Use', 'Stage']).size().unstack()

    perc_a = counts_a.div(counts_a.sum(axis=0),axis=1)

    if plot is True:
        ax = perc_a.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title('Alcohol Use Last 30 Days: Move In vs Move Out')
        else:
            ax.set_title(f'{title} - Alcohol Use Last 30 Days: Move In vs Move Out')

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc_a.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    method_title_b = 'Drug Use'

    if noAnswers is False:
        dr_out_sub = out_sub[out_sub['Drug Use'] != 'Prefer not to answer']
        dr_out_sub = dr_out_sub[dr_out_sub['Drug Use'] != 'Unknown']
    else:
        dr_out_sub = out_sub

    counts_b = dr_out_sub.groupby(['Drug Use', 'Stage']).size().unstack()

    perc_b = counts_b.div(counts_b.sum(axis=0), axis=1)

    if plot is True:
        ax = perc_b.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'Drug Use Last 30 Days: Move In vs Move Out')
        else:
            ax.set_title(f'{title} - Drug Use Last 30 Days: Move In vs Move Out')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc_b.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    print(f"{method_title_a} {title}: Sample Size: {counts_a.sum(axis=0)}")
    print(f"\n{method_title_a} {title}: Summary Table")
    print("============================================")
    print(f"{perc_a}")
    print("============================================\n\n")
    print(f"{method_title_b} {title}: Sample Size: {counts_b.sum(axis=0)}")
    print(f"\n{method_title_b} {title}: Summary Table")
    print("============================================")
    print(f"{perc_b}")
    print("============================================\n\n")

    output_a = pd.concat([counts_a, perc_a], axis=1)
    output_a.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']
    output_b = pd.concat([counts_b, perc_b], axis=1)
    output_b.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title_a}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_a.to_csv(f'{output_directory}/{method_title_a}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title_b}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_b.to_csv(f'{output_directory}/{method_title_b}_{title}_{date.today()}.csv')


def outcomePrograms(input_data,
                    title="", 
                    plot=False,
                    includeStaff=False,
                    noAnswers=True):

    method_title = "Program Usage"

    # Participation in Recovery Programs
    out_progs = input_data[['Stage', 'input_type', 'last_30_attendance_12_step',
                            'last_30_attendance_organized_religious_group',
                            'last_30_attendance_other_support_group',
                            'last_30_attendance_sober_support_outing',
                            'last_30_attendance_activities_sponsored_by_recovery_residence',
                            'last_30_attendance_activities_provided_while_incarcerated',
                            'last_30_attendance_none', 'last_30_attendance_no_answer']]
    
    update_cols = out_progs.columns[2:]
    for col in update_cols:
        out_progs[col] = out_progs[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)

    out_progs.columns = ['Stage', 'Input Type', 'Last 30: 12 Step',
                         'Last 30: Attended Religious Group',
                         'Last 30: Attended Other Support Group',
                         'Last 30: Attended Sober Support Outing',
                         'Last 30: Attended Recovery Residence Activity',
                         'Last 30: Attended Activity while Incarcerated',
                         'Last 30: Attended No Program',
                         'Last 30: No Answer on Attendance']

    out_progs = out_progs[out_progs['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_progs = out_progs[out_progs['Input Type'] == 'Client']

    if noAnswers is False:
        out_progs = out_progs[out_progs['Last 30: No Answer on Attendance'] == 0]        
        out_progs = out_progs[['Stage', 'Input Type', 'Last 30: 12 Step',
                               'Last 30: Attended Religious Group',
                               'Last 30: Attended Other Support Group',
                               'Last 30: Attended Sober Support Outing',
                               'Last 30: Attended Recovery Residence Activity',
                               'Last 30: Attended Activity while Incarcerated',
                               'Last 30: Attended No Program']]
        out_progs = out_progs[(out_progs['Last 30: 12 Step'] > 0)
                              | (out_progs['Last 30: Attended Religious Group'] > 0)
                              | (out_progs['Last 30: Attended Other Support Group'] > 0)
                              | (out_progs['Last 30: Attended Sober Support Outing'] > 0)
                              | (out_progs['Last 30: Attended Recovery Residence Activity'] > 0)
                              | (out_progs['Last 30: Attended Activity while Incarcerated'] > 0)
                              | (out_progs['Last 30: Attended No Program'] > 0)]

    grouped = out_progs.groupby("Stage").sum()

    in_count = out_progs[out_progs['Stage']=='Move In']['Stage'].count()
    out_count = out_progs[out_progs['Stage']=='Move Out']['Stage'].count()

    grouped = grouped.transpose()

    grouped['Percent Move In'] = (grouped['Move In']/in_count)*100
    grouped['Percent Move Out'] = (grouped['Move Out']/out_count)*100

    # Reset the index of the dataframe
    grouped = grouped.reset_index()

    # Output Table
    output_table = grouped.copy()
    output_table['Move In Population'] = in_count
    output_table['Move Out Population'] = out_count
    output_table.columns = ['Program Usage', 'Move In', 'Move Out', 'Percent Move In', 'Percent move Out', 'Move In Population', 'Move Out Population']

    prog_perc = grouped[['index', 'Percent Move In', 'Percent Move Out']]
    prog_perc.columns = ['Program Usage', 'Move In', 'Move Out']

    print(f"{method_title} {title}: Move In Sample Size = {in_count}")
    print(f"{method_title} {title}: Move Out Sample Size = {out_count}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{output_table}")
    print("============================================\n\n")

    if plot is True:
        # Create a horizontal stacked bar chart
        ax = prog_perc.plot(x = 'Program Usage', kind="bar", stacked=False)

        # Set the chart title and labels
        if title == "":
            ax.set_title(f"Program Usage Comparison for 'Last 30' Columns: Move In vs Move Out")
        else:
            ax.set_title(f"{title} - Program Usage Comparison for 'Last 30' Columns: Move In vs Move Out")    
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

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_table.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')

def outcomeDocuments(input_data,
                     title="",
                     plot=False,
                     includeStaff=False,
                     noAnswers=False):
    # Personal Documents
    out_docs = input_data[['Stage', 'input_type', 'doc_status_drivers_license',
                           'doc_status_state_id', 'doc_status_social_security_card',
                           'doc_status_birth_certificate']]
    # out_docs.columns = [['Stage', 'Input Type', 'Drivers License', 'State ID', 'Social Security Card', 'Birth Certificate']]

    out_docs = out_docs[out_docs['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_docs = out_docs[out_docs['input_type'] == 'Client']

    # Drivers License
    method_title_dl = "Drivers License"
    out_docs_dl = out_docs.copy()

    if noAnswers is False:
        out_docs_dl = out_docs_dl[out_docs_dl['doc_status_drivers_license'] != 'Prefer not to answer']

    out_docs_dl = out_docs_dl.groupby(['doc_status_drivers_license', 'Stage']).size().unstack()

    perc = out_docs_dl.div(out_docs_dl.sum(axis=0), axis=1)

    output_dl = pd.concat([out_docs_dl, perc], axis=1)
    output_dl.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    dl_in_count = output_dl['Move In Surveys'].sum()
    dl_out_count = output_dl['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'Document Status: Drivers License')
        else:
            ax.set_title(f'{title} - Document Status: Drivers License')    

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
    method_title_id = "State ID"
    out_docs_id = out_docs.copy()

    if noAnswers is False:
        out_docs_id = out_docs_id[out_docs_id['doc_status_state_id'] != 'Prefer not to answer']

    out_docs_id = out_docs_id.groupby(['doc_status_state_id', 'Stage']).size().unstack()

    perc = out_docs_id.div(out_docs_id.sum(axis=0), axis=1)

    output_id = pd.concat([out_docs_id, perc], axis=1)
    output_id.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    id_in_count = output_id['Move In Surveys'].sum()
    id_out_count = output_id['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind = 'bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'Document Status: State ID')
        else:
            ax.set_title(f'{title} - Document Status: State ID')    

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
    method_title_ss = "Social Security Card"
    out_docs_ss = out_docs.copy()

    if noAnswers is False:
        out_docs_ss = out_docs_ss[out_docs_ss['doc_status_social_security_card'] != 'Prefer not to answer']

    out_docs_ss = out_docs_ss.groupby(['doc_status_social_security_card', 'Stage']).size().unstack()

    perc = out_docs_ss.div(out_docs_ss.sum(axis=0), axis=1)

    output_ss = pd.concat([out_docs_ss, perc], axis=1)
    output_ss.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    ss_in_count = output_ss['Move In Surveys'].sum()
    ss_out_count = output_ss['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind = 'bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'Document Status: Social Security Card')
        else:
            ax.set_title(f'{title} - Document Status: Social Security Card')    

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
    method_title_bc = "Birth Certificate"
    out_docs_bc = out_docs.copy()

    if noAnswers is False:
        out_docs_bc = out_docs_bc[out_docs_bc['doc_status_birth_certificate'] != 'Prefer not to answer']

    out_docs_bc = out_docs_bc.groupby(['doc_status_birth_certificate', 'Stage']).size().unstack()

    perc = out_docs_bc.div(out_docs_bc.sum(axis=0), axis=1)

    output_bc = pd.concat([out_docs_bc, perc], axis=1)
    output_bc.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    bc_in_count = output_bc['Move In Surveys'].sum()
    bc_out_count = output_bc['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind = 'bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'Document Status: Birth Certificate')
        else:
            ax.set_title(f'{title} - Document Status: Birth Certificate')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    print(f"{method_title_dl} {title}: Move In Sample Size = {dl_in_count}")
    print(f"{method_title_dl} {title}: Move Out Sample Size = {dl_out_count}")
    print(f"\n{method_title_dl} {title}: Summary Table")
    print("============================================")
    print(f"{output_dl}")
    print("============================================\n\n\n\n")

    print(f"{method_title_id} {title}: Move In Sample Size = {id_in_count}")
    print(f"{method_title_id} {title}: Move Out Sample Size = {id_out_count}")
    print(f"\n{method_title_id} {title}: Summary Table")
    print("============================================")
    print(f"{output_id}")
    print("============================================\n\n\n\n")

    print(f"{method_title_ss} {title}: Move In Sample Size = {ss_in_count}")
    print(f"{method_title_ss} {title}: Move Out Sample Size = {ss_out_count}")
    print(f"\n{method_title_ss} {title}: Summary Table")
    print("============================================")
    print(f"{output_ss}")
    print("============================================\n\n\n\n")

    print(f"{method_title_bc} {title}: Move In Sample Size = {bc_in_count}")
    print(f"{method_title_bc} {title}: Move Out Sample Size = {bc_out_count}")
    print(f"\n{method_title_bc} {title}: Summary Table")
    print("============================================")
    print(f"{output_bc}")
    print("============================================\n\n\n\n")

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title_dl}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_dl.to_csv(f'{output_directory}/{method_title_dl}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title_id}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_id.to_csv(f'{output_directory}/{method_title_id}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title_ss}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_ss.to_csv(f'{output_directory}/{method_title_ss}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title_bc}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_bc.to_csv(f'{output_directory}/{method_title_bc}_{title}_{date.today()}.csv')


def outcomeEducation(input_data,
                     title="",
                     plot=False,
                     includeStaff=False,
                     noAnswers=True):

    method_title = 'Education Outcome'

    # Education Progress
    out_educ = input_data[['Stage', 'input_type',
                           'last_30_education_progress_ged',
                           'last_30_education_progress_vocational_school',
                           'last_30_education_progress_skilled_training',
                           'last_30_education_progress_college',
                           'last_30_education_progress_not_involved']]

    update_cols = out_educ.columns[2:]

    for col in update_cols:
            out_educ[col] = out_educ[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)

    out_educ = out_educ[out_educ['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_educ = out_educ[out_educ['input_type'] == 'Client']

    if noAnswers is False:
        out_educ = out_educ[(out_educ['last_30_education_progress_ged'] > 0)
                            | (out_educ['last_30_education_progress_vocational_school'] > 0)
                            | (out_educ['last_30_education_progress_skilled_training'] > 0)
                            | (out_educ['last_30_education_progress_college'] > 0)
                            | (out_educ['last_30_education_progress_not_involved'] > 0)]

    grouped = out_educ.groupby("Stage").sum()
    grouped.columns = ['Last 30: GED',
                       'Last 30: Vocational School',
                       'Last 30: Skilled Training',
                       'Last 30: College',
                       'Last 30: No Involvement']

    in_count = out_educ[out_educ['Stage'] == 'Move In']['Stage'].count()
    out_count = out_educ[out_educ['Stage'] == 'Move Out']['Stage'].count()

    grouped = grouped.transpose()

    grouped['Percent Move In'] = (grouped['Move In']/in_count)*100
    grouped['Percent Move Out'] = (grouped['Move Out']/out_count)*100

    # Reset the index of the dataframe
    grouped = grouped.reset_index()

    # Output Table
    output_table = grouped.copy()
    output_table['Move In Population'] = in_count
    output_table['Move Out Population'] = out_count
    output_table.columns = ['Education Progress', 'Move In', 'Move Out', 'Percent Move In', 'Percent move Out', 'Move In Population', 'Move Out Population']

    educ_perc = grouped[['index', 'Percent Move In', 'Percent Move Out']]
    educ_perc.columns = ['Education Progress', 'Move In', 'Move Out']

    print(f"{method_title} {title}: Move In Sample Size = {in_count}")
    print(f"{method_title} {title}: Move Out Sample Size = {out_count}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{output_table}")
    print("============================================\n\n")

    if plot is True:
        # Create a horizontal stacked bar chart
        ax = educ_perc.plot(x='Education Progress', 
                            kind="bar", stacked=False)

        # Set the chart title and labels
        if title == "":
            ax.set_title(f"Education Comparison for 'Last 30' Columns: Move In vs Move Out")
        else:
            ax.set_title(f"{title} - Education Comparison for 'Last 30' Columns: Move In vs Move Out")    
        ax.set_ylabel("Percentage of Total (%)")
        ax.set_xlabel("Last 30 Columns")

        # Add percentage labels above each bar
        for container in ax.containers:
            for bar in container:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}%',
                        ha='center', va='bottom')

        # Show the chart
        plt.show()

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_table.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')

# ---------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------


def outcomeEmployment(input_data,
                      title="",
                      plot=False,
                      includeStaff=False,
                      noAnswers=True):

    out_emp_vol = input_data[['Stage', 'input_type',
                          'last_30_employment_status',
                          'last_30_volunteering_status']]

    out_emp_vol = out_emp_vol[out_emp_vol['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_emp_vol = out_emp_vol[out_emp_vol['input_type'] == 'Client']

    # Employment Status

    method_title_emp = "Employment"

    out_emp = out_emp_vol.copy()

    if noAnswers is False:
        out_emp = out_emp[out_emp['last_30_employment_status'] != 'Prefer not to answer']
        out_emp = out_emp[~out_emp['last_30_employment_status'].isna()]

    out_emp = out_emp.groupby(['last_30_employment_status', 'Stage']).size().unstack()

    perc = out_emp.div(out_emp.sum(axis=0), axis=1)

    output_emp = pd.concat([out_emp, perc], axis=1)
    output_emp.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']
    output_emp.fillna(0, inplace=True)
    output_emp['Move In Surveys'] = output_emp['Move In Surveys'].astype(int)
    output_emp['Move Out Surveys'] = output_emp['Move Out Surveys'].astype(int)
    in_count_emp = output_emp['Move In Surveys'].sum()
    out_count_emp = output_emp['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f"Employment Status")
        else:
            ax.set_title(f"{title} - Employment Status")

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

    # Volunteer Status

    method_title_vol = "Volunteering"

    out_vol = out_emp_vol.copy()

    if noAnswers is False:
        out_vol = out_vol[out_vol['last_30_volunteering_status'] != 'Prefer not to answer']
        out_vol = out_vol[~out_vol['last_30_volunteering_status'].isna()]

    out_vol = out_vol.groupby(['last_30_volunteering_status', 'Stage']).size().unstack()

    perc = out_vol.div(out_vol.sum(axis=0), axis=1)

    output_vol = pd.concat([out_vol, perc], axis=1)
    output_vol.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']
    in_count_vol = output_vol['Move In Surveys'].sum()
    out_count_vol = output_vol['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f"Volunteering Status")
        else:
            ax.set_title(f"{title} - Volunteering Status")

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

    print(f"{method_title_emp} {title}: Move In Sample Size = {in_count_emp}")
    print(f"{method_title_emp} {title}: Move Out Sample Size = {out_count_emp}")
    print(f"\n{method_title_emp} {title}: Summary Table")
    print("============================================")
    print(f"{output_emp}")
    print("============================================\n\n\n\n")

    print(f"{method_title_vol} {title}: Move In Sample Size = {in_count_vol}")
    print(f"{method_title_vol} {title}: Move Out Sample Size = {out_count_vol}")
    print(f"\n{method_title_vol} {title}: Summary Table")
    print("============================================")
    print(f"{output_vol}")
    print("============================================\n\n\n\n")

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title_emp}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_emp.to_csv(f'{output_directory}/{method_title_emp}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title_vol}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_vol.to_csv(f'{output_directory}/{method_title_vol}_{title}_{date.today()}.csv')


def orh_outcome_health(input_data, graph_title = "", plot = False):

    # Health Status
    out_health = input_data[['Stage','input_type','last_30_physical_health','last_30_mental_health']]

    out_health = out_health[out_health['Stage'] != 'Follow Up']
    out_health = out_health[out_health['input_type'] == 'Client']

    # Physical Health
    out_health_phy = out_health[out_health['last_30_physical_health'] != 'Prefer not to answer']
    out_health_phy = out_health_phy.groupby(['last_30_physical_health', 'Stage']).size().unstack()

    perc = out_health_phy.div(out_health_phy.sum(axis = 0), axis = 1)

    if plot is True:
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

    if plot is True:
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


def orh_outcome_consq(input_data, title = "", plot = False):

    method_title = "Substance Use Consequences"

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


    in_count = out_sub_consq[out_sub_consq['Stage']=='Move In']['Stage'].count()
    out_count = out_sub_consq[out_sub_consq['Stage']=='Move Out']['Stage'].count()

    grouped = grouped.transpose()

    grouped['Percent Move In'] = (grouped['Move In']/in_count)*100
    grouped['Percent Move Out'] = (grouped['Move Out']/out_count)*100

    # Reset the index of the dataframe
    grouped = grouped.reset_index()

    # Output Table
    output_table = grouped.copy()
    output_table['Move In Population'] = in_count
    output_table['Move Out Population'] = out_count
    output_table.columns = ['Consequences', 'Move In', 'Move Out', 'Percent Move In', 'Percent move Out', 'Move In Population', 'Move Out Population']

    cons_perc = grouped[['index', 'Percent Move In', 'Percent Move Out']]
    cons_perc.columns = ['Consequences', 'Move In', 'Move Out']

    print(f"{method_title} {title}: Move In Sample Size = {in_count}")
    print(f"{method_title} {title}: Move Out Sample Size = {out_count}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{output_table}")
    print("============================================\n\n")

    if plot is True:
        
        # Create a horizontal stacked bar chart
        ax = cons_perc.plot(x = 'Consequences', kind="bar", stacked=False)

        # Set the chart title and labels
        if title == "":
            ax.set_title(f"Outcome Substance Consequences for 'Last 30' Columns: Move In vs Move Out")
        else:
            ax.set_title(f"{title} - Outcome Substance Consequences for 'Last 30' Columns: Move In vs Move Out")
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

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_table.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')

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



def orh_all_outcome_prog(input_data, title = "", plot = False):

    method_title = "Program Usage"

    # Participation in Recovery Programs
    out_progs = input_data[['Stage','input_type','last_30_attendance_12_step','last_30_attendance_organized_religious_group','last_30_attendance_other_support_group',
                        'last_30_attendance_sober_support_outing','last_30_attendance_activities_sponsored_by_recovery_residence',
                        'last_30_attendance_activities_provided_while_incarcerated','last_30_attendance_none', 'last_30_attendance_no_answer']]
    update_cols = out_progs.columns[2:]
    for col in update_cols:
        out_progs[col] = out_progs[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)
    out_progs.columns = ['Stage','Input Type','Last 30: 12 Step','Last 30: Attended Religious Group','Last 30: Attended Other Support Group','Last 30: Attended Sober Support Outing','Last 30: Attended Recovery Residence Activity','Last 30: Attnded Activity while Incarcerated','Last 30: Attended No Program','Last 30: No Answer on Attendance']

    out_progs = out_progs[out_progs['Input Type'] == 'Client']
    out_progs = out_progs[out_progs['Stage'] != 'Follow Up']
    
    grouped = out_progs.groupby("Stage").sum()

    in_count = out_progs[out_progs['Stage']=='Move In']['Stage'].count()
    out_count = out_progs[out_progs['Stage']=='Move Out']['Stage'].count()

    grouped = grouped.transpose()

    grouped['Percent Move In'] = (grouped['Move In']/in_count)*100
    grouped['Percent Move Out'] = (grouped['Move Out']/out_count)*100

    # Reset the index of the dataframe
    grouped = grouped.reset_index()

    # Output Table
    output_table = grouped.copy()
    output_table['Move In Population'] = in_count
    output_table['Move Out Population'] = out_count
    output_table.columns = ['Program Usage', 'Move In', 'Move Out', 'Percent Move In', 'Percent move Out', 'Move In Population', 'Move Out Population']

    prog_perc = grouped[['index', 'Percent Move In', 'Percent Move Out']]
    prog_perc.columns = ['Program Usage', 'Move In', 'Move Out']

    print(f"{method_title} {title}: Move In Sample Size = {in_count}")
    print(f"{method_title} {title}: Move Out Sample Size = {out_count}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{output_table}")
    print("============================================\n\n")

    if plot is True:
        # Create a horizontal stacked bar chart
        ax = prog_perc.plot(x = 'Program Usage', kind="bar", stacked=False)

        # Set the chart title and labels
        if title == "":
            ax.set_title(f"Program Usage Comparison for 'Last 30' Columns: Move In vs Move Out")
        else:
            ax.set_title(f"{title} - Program Usage Comparison for 'Last 30' Columns: Move In vs Move Out")    
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

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_table.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')



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


def orh_cohort_comp_summary(data1, data2, title1='', title2='', stage='Move In', plot=True):

    orh_ages(data1, 
            stage = stage, 
            title = title1,
            plot=plot)
    orh_ages(data2, 
            stage = stage, 
            title = title2,
            plot=plot)

    print('\n'*20)

    orh_education(data1, 
                  stage = stage, 
                  title = title1,
                  plot=plot)
    orh_education(data2, 
                  stage = stage, 
                  title = title2,
                  plot=plot)

    print('\n'*20)

    orh_gender(data1, 
               stage = stage, 
               title = title1,
               plot=plot)
    orh_gender(data2, 
               stage = stage, 
               title = title2,
               plot=plot)

    print('\n'*20)

    orh_sexuality(data1, 
                  stage = stage, 
                  title = title1,
                  plot=plot)
    orh_sexuality(data2, 
                  stage = stage, 
                  title = title2,
                  plot=plot)

    print('\n'*20)

    orh_race(data1, 
             stage = stage, 
             title = title1,
             plot=plot)
    orh_race(data2, 
             stage = stage, 
             title = title2,
             plot=plot)


def orh_cohort_summary(data, title, stage = 'Move In', plot = False):

    orh_ages(data, 
            stage = stage, 
            title = title,
            plot = plot)

    print('\n'*20)

    orh_education(data, 
            stage = stage, 
            title = title,
            plot = plot)
    
    print('\n'*20)

    orh_gender(data, 
            stage = stage, 
            title = title,
            plot = plot)
    print('\n'*20)

    orh_sexuality(data, 
            stage = stage, 
            title = title,
            plot = plot)

    print('\n'*20)

    orh_race(data, 
            stage = stage, 
            title = title,
            plot = plot)

def orh_full_summary(data, graph_title = '', stage = 'Move In'):
        orh_cohort_summary(data, graph_title, stage)
        orh_outcome_summary(data, graph_title)

def orh_full_comparison(data1, data2, graph_title1 = '', graph_title2 = '', stage = "Move In"):
     orh_cohort_comp_summary(data1, data2, graph_title1, graph_title2, stage)
     orh_outcome_comp_summary(data1, data2, graph_title1, graph_title2)
