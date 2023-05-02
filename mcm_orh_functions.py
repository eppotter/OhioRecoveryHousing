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

    # # Create Gender ID Column
    # gender_id = ['gender_identify_agender', 'gender_identify_genderqueer',
    #              'gender_identify_gender_fluid', 'gender_identify_man',
    #              'gender_identify_non-binary', 'gender_identify_questioning',
    #              'gender_identify_transgender', 'gender_identify_trans_man',
    #              'gender_identify_trans_woman', 'gender_identify_woman',
    #              'gender_identify_no_answer', 'gender_identify_other']

    # merge_orh(input_data, gender_id, 'Gender')

    # # Create Sexuality ID Column
    # sexuality_id = ['sexual_identity_asexual', 'sexual_identity_bisexual',
    #                 'sexual_identity_gay', 'sexual_identity_heterosexual',
    #                 'sexual_identity_lesbian', 'sexual_identity_pansexual',
    #                 'sexual_identity_queer', 'sexual_identity_questioning',
    #                 'sexual_identity_same_gender_loving',
    #                 'sexual_identity_no_answer', 'sexual_identity_other']

    # merge_orh(input_data, sexuality_id, 'Sexuality')

    # # Create Race ID Column
    # race_id = ['race_id_white', 'race_id_black_or_african_american',
    #            'race_id_american_indian_or_alaska_native',
    #            'race_id_chinese', 'race_id_vietnamese',
    #            'race_id_native_hawaiian', 'race_id_filipino', 'race_id_korean',
    #            'race_id_samoan', 'race_id_asian_indian',
    #            'race_id_japanese', 'race_id_chamorro',
    #            'race_id_other_asian', 'race_id_other_pacific_islander',
    #            'rad_id_no_answer', 'race_id_other']
    
    # merge_orh(input_data, race_id, 'Race')

    # # Create Criminal Justice ID Column
    # crim_hist_id = ['curr_status_cjs_parole_probation',
    #                 'curr_status_cjs_drug_court',
    #                 'curr_status_cjs_no_involvement',
    #                 'curr_status_cjs_no_answer']

    # merge_orh(input_data, crim_hist_id, 'CJS')

    return input_data

# ----------------------------------------------------------------------------------------- #
#                                     COHORT FUNCTIONS                                      #
# ----------------------------------------------------------------------------------------- #


def cohortAges(input_data, stage, plot=False, title=""):

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


def cohortEducation(input_data, stage, plot=False, title=""):

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


def cohortRace(input_data, stage, plot=False, title=""):

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


def cohortGender(input_data, stage, plot=False, title=""):

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


def cohortSexuality(input_data, stage, plot=False, title=""):

    method_title = "Sexuality Breakdown"
    df = input_data[input_data['Stage'] == stage]

    orh_sex = df[['sexual_identity_asexual', 'sexual_identity_bisexual',
                  'sexual_identity_gay', 'sexual_identity_heterosexual',
                  'sexual_identity_lesbian', 'sexual_identity_pansexual',
                  'sexual_identity_queer', 'sexual_identity_questioning',
                  'sexual_identity_same_gender_loving',
                  'sexual_identity_no_answer', 'sexual_identity_other']]

    orh_sex.fillna(0, inplace=True)

    orh_sex = orh_sex.astype(bool).astype(int)

    new_col_names = [col_name.replace('sexual_identity_', '') for col_name in orh_sex.columns]
    orh_sex.columns = new_col_names

    s_sum = orh_sex.sum()
    s_count = orh_sex.count()
    s_perc = s_sum/s_count

    s_brkdwn = pd.concat([s_sum, s_count, s_perc], axis=1)
    s_brkdwn = s_brkdwn.reset_index().rename(columns={'index': 'Sexuality',
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


# ----------------------------------------------------------------------------------------- #
#                                    OUTCOME FUNCTIONS                                      #
# ----------------------------------------------------------------------------------------- #


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


def outcomeHealth(input_data,
                  title="",
                  plot=False,
                  includeStaff=False,
                  noAnswers=True):

    # Health Status
    out_health = input_data[['Stage','input_type','last_30_physical_health','last_30_mental_health']]

    out_health = out_health[out_health['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_health = out_health[out_health['input_type'] == 'Client']

    # Physical Health
    method_title_phys = "Physical Health"

    out_health_phy = out_health.copy()

    if noAnswers is False:
        out_health_phy = out_health_phy[out_health_phy['last_30_physical_health'] != 'Prefer not to answer']
        out_health_phy = out_health_phy[~out_health_phy['last_30_physical_health'].isna()]

    out_health_phy = out_health_phy.groupby(['last_30_physical_health', 'Stage']).size().unstack()

    perc = out_health_phy.div(out_health_phy.sum(axis = 0), axis = 1)

    output_phys = pd.concat([out_health_phy, perc], axis=1)
    output_phys.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']
    in_count_phys = output_phys['Move In Surveys'].sum()
    out_count_phys = output_phys['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind = 'bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f"Physical Health")
        else:
            ax.set_title(f"{title} - Physical Health")    

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
    method_title_men = "Mental Health"

    out_health_men = out_health.copy()

    if noAnswers is False:
        out_health_men = out_health_men[out_health_men['last_30_mental_health'] != 'Prefer not to answer']
        out_health_men = out_health_men[~out_health_men['last_30_mental_health'].isna()]

    out_health_men = out_health_men.groupby(['last_30_mental_health', 'Stage']).size().unstack()

    perc = out_health_men.div(out_health_men.sum(axis = 0), axis = 1)

    output_men = pd.concat([out_health_men, perc], axis=1)
    output_men.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']
    in_count_men = output_men['Move In Surveys'].sum()
    out_count_men = output_men['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind = 'bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f"Mental Health")
        else:
            ax.set_title(f"{title} - Mental Health")

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    print(f"{method_title_phys} {title}: Move In Sample Size = {in_count_phys}")
    print(f"{method_title_phys} {title}: Move Out Sample Size = {out_count_phys}")
    print(f"\n{method_title_phys} {title}: Summary Table")
    print("============================================")
    print(f"{output_phys}")
    print("============================================\n\n\n\n")

    print(f"{method_title_men} {title}: Move In Sample Size = {in_count_men}")
    print(f"{method_title_men} {title}: Move Out Sample Size = {out_count_men}")
    print(f"\n{method_title_men} {title}: Summary Table")
    print("============================================")
    print(f"{output_men}")
    print("============================================\n\n\n\n")

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title_phys}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_phys.to_csv(f'{output_directory}/{method_title_phys}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title_men}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_men.to_csv(f'{output_directory}/{method_title_men}_{title}_{date.today()}.csv')


def outcomeConsequences(input_data,
                        title="",
                        plot=False,
                        includeStaff=False,
                        noAnswers=True):

    method_title = "Substance Use Consequences"

    # Substance Use Consequences
    out_sub_consq = input_data[['Stage', 'input_type',
                                'last_30_substance_use_consequences_social',
                                'last_30_substance_use_consequences_health_behavioral',
                                'last_30_substance_use_consequences_financial',
                                'last_30_substance_use_consequences_none_of_above',
                                'last_30_substance_use_consequences_no_answer',
                                'last_30_substance_use_consequences_other']]

    update_cols = out_sub_consq.columns[2:]

    for col in update_cols:
        out_sub_consq[col] = out_sub_consq[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)

    out_sub_consq = out_sub_consq[out_sub_consq['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_sub_consq = out_sub_consq[out_sub_consq['input_type'] == 'Client']

    if noAnswers is False:
        out_sub_consq = out_sub_consq[(out_sub_consq['last_30_substance_use_consequences_social'] > 0)
                                      | (out_sub_consq['last_30_substance_use_consequences_health_behavioral'] > 0)
                                      | (out_sub_consq['last_30_substance_use_consequences_financial'] > 0)
                                      | (out_sub_consq['last_30_substance_use_consequences_none_of_above'] > 0)
                                      | (out_sub_consq['last_30_substance_use_consequences_no_answer'] > 0)
                                      | (out_sub_consq['last_30_substance_use_consequences_other'] > 0)]
        
        out_sub_consq = out_sub_consq[['Stage', 'input_type',
                                       'last_30_substance_use_consequences_social',
                                       'last_30_substance_use_consequences_health_behavioral',
                                       'last_30_substance_use_consequences_financial',
                                       'last_30_substance_use_consequences_other']]

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


def outcomeRecoveryCapital(input_data,
                     title="",
                     plot=False,
                     includeStaff=False,
                     noAnswers=False):
    # Personal Documents
    out_cap = input_data[['Stage', 'input_type', 
                           'move_out_statement_i_have_people_in_my_life_i_can_rely_on_in_support_of_my_recovery',
                           'move_out_statement_i_have_goals_and_hopes_for_my_future',
                           'move_out_statement_i_have_problem-solving_skills_and_resources_to_help_me_make_healthy_decisions',
                           'move_out_statement_i_have_a_clear_sense_of_who_i_am',
                           'move_out_statement_i_have_meaningful_positive_participation_in_my_family_and_community',
                           'move_out_statement_i_have_a_sense_of_purpose_in_my_life',
                           'move_out_statement_i_have_a_sense_of_personal_values_that_guide_me_between_right_and_wrong',
                           'move_out_statement_i_have_a_sense_of_community_and_belonging']]

    out_cap = out_cap[out_cap['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_cap = out_cap[out_cap['input_type'] == 'Client']

    # Support System
    method_title_1 = "Support System"
    out_cap_1 = out_cap.copy()

    if noAnswers is False:
        out_cap_1 = out_cap_1[out_cap_1['move_out_statement_i_have_people_in_my_life_i_can_rely_on_in_support_of_my_recovery'] != 'Prefer not to answer']
        out_cap_1 = out_cap_1[~out_cap_1['move_out_statement_i_have_people_in_my_life_i_can_rely_on_in_support_of_my_recovery'].isna()]

    out_cap_1 = out_cap_1.groupby(['move_out_statement_i_have_people_in_my_life_i_can_rely_on_in_support_of_my_recovery', 'Stage']).size().unstack()

    perc = out_cap_1.div(out_cap_1.sum(axis=0), axis=1)

    output_1 = pd.concat([out_cap_1, perc], axis=1)
    output_1.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    outcap_1_in_count = output_1['Move In Surveys'].sum()
    outcap_1_out_count = output_1['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title_1}')
        else:
            ax.set_title(f'{title} - {method_title_1}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    # Goals and Hopes
    method_title_2 = "Future Hopes and Goals"
    out_cap_2 = out_cap.copy()

    if noAnswers is False:
        out_cap_2 = out_cap_2[out_cap_2['move_out_statement_i_have_goals_and_hopes_for_my_future'] != 'Prefer not to answer']
        out_cap_2 = out_cap_2[~out_cap_2['move_out_statement_i_have_goals_and_hopes_for_my_future'].isna()]

    out_cap_2 = out_cap_2.groupby(['move_out_statement_i_have_goals_and_hopes_for_my_future', 'Stage']).size().unstack()

    perc = out_cap_2.div(out_cap_2.sum(axis=0), axis=1)

    output_2 = pd.concat([out_cap_2, perc], axis=1)
    output_2.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    outcap_2_in_count = output_2['Move In Surveys'].sum()
    outcap_2_out_count = output_2['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title_2}')
        else:
            ax.set_title(f'{title} - {method_title_2}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    # Problem Solving Skills
    method_title_3 = "Problem Solving Skills"
    out_cap_3 = out_cap.copy()

    if noAnswers is False:
        out_cap_3 = out_cap_3[out_cap_3['move_out_statement_i_have_problem-solving_skills_and_resources_to_help_me_make_healthy_decisions'] != 'Prefer not to answer']
        out_cap_3 = out_cap_3[~out_cap_3['move_out_statement_i_have_problem-solving_skills_and_resources_to_help_me_make_healthy_decisions'].isna()]

    out_cap_3 = out_cap_3.groupby(['move_out_statement_i_have_problem-solving_skills_and_resources_to_help_me_make_healthy_decisions', 'Stage']).size().unstack()

    perc = out_cap_3.div(out_cap_3.sum(axis=0), axis=1)

    output_3 = pd.concat([out_cap_3, perc], axis=1)
    output_3.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    outcap_3_in_count = output_3['Move In Surveys'].sum()
    outcap_3_out_count = output_3['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title_3}')
        else:
            ax.set_title(f'{title} - {method_title_3}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    # Problem Solving Skills
    method_title_4 = "Sense of Self"
    out_cap_4 = out_cap.copy()

    if noAnswers is False:
        out_cap_4 = out_cap_4[out_cap_4['move_out_statement_i_have_a_clear_sense_of_who_i_am'] != 'Prefer not to answer']
        out_cap_4 = out_cap_4[~out_cap_4['move_out_statement_i_have_a_clear_sense_of_who_i_am'].isna()]

    out_cap_4 = out_cap_4.groupby(['move_out_statement_i_have_a_clear_sense_of_who_i_am', 'Stage']).size().unstack()

    perc = out_cap_4.div(out_cap_4.sum(axis=0), axis=1)

    output_4 = pd.concat([out_cap_4, perc], axis=1)
    output_4.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    outcap_4_in_count = output_4['Move In Surveys'].sum()
    outcap_4_out_count = output_4['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title_4}')
        else:
            ax.set_title(f'{title} - {method_title_4}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    # Family and Community Participation
    method_title_5 = "Family and Community Participation"
    out_cap_5 = out_cap.copy()

    if noAnswers is False:
        out_cap_5 = out_cap_5[out_cap_5['move_out_statement_i_have_meaningful_positive_participation_in_my_family_and_community'] != 'Prefer not to answer']
        out_cap_5 = out_cap_5[~out_cap_5['move_out_statement_i_have_meaningful_positive_participation_in_my_family_and_community'].isna()]

    out_cap_5 = out_cap_5.groupby(['move_out_statement_i_have_meaningful_positive_participation_in_my_family_and_community', 'Stage']).size().unstack()

    perc = out_cap_5.div(out_cap_5.sum(axis=0), axis=1)

    output_5 = pd.concat([out_cap_5, perc], axis=1)
    output_5.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    outcap_5_in_count = output_5['Move In Surveys'].sum()
    outcap_5_out_count = output_5['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title_5}')
        else:
            ax.set_title(f'{title} - {method_title_5}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)    

    # Sense of Purpose
    method_title_6 = "Sense of Purpose"
    out_cap_6 = out_cap.copy()

    if noAnswers is False:
        out_cap_6 = out_cap_6[out_cap_6['move_out_statement_i_have_a_sense_of_purpose_in_my_life'] != 'Prefer not to answer']
        out_cap_6 = out_cap_6[~out_cap_6['move_out_statement_i_have_a_sense_of_purpose_in_my_life'].isna()]

    out_cap_6 = out_cap_6.groupby(['move_out_statement_i_have_a_sense_of_purpose_in_my_life', 'Stage']).size().unstack()

    perc = out_cap_6.div(out_cap_6.sum(axis=0), axis=1)

    output_6 = pd.concat([out_cap_6, perc], axis=1)
    output_6.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    outcap_6_in_count = output_6['Move In Surveys'].sum()
    outcap_6_out_count = output_6['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title_6}')
        else:
            ax.set_title(f'{title} - {method_title_6}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)    

    # Sense of Personal Values
    method_title_7 = "Sense of Personal Values"
    out_cap_7 = out_cap.copy()

    if noAnswers is False:
        out_cap_7 = out_cap_7[out_cap_7['move_out_statement_i_have_a_sense_of_personal_values_that_guide_me_between_right_and_wrong'] != 'Prefer not to answer']
        out_cap_7 = out_cap_7[~out_cap_7['move_out_statement_i_have_a_sense_of_personal_values_that_guide_me_between_right_and_wrong'].isna()]

    out_cap_7 = out_cap_7.groupby(['move_out_statement_i_have_a_sense_of_personal_values_that_guide_me_between_right_and_wrong', 'Stage']).size().unstack()

    perc = out_cap_7.div(out_cap_7.sum(axis=0), axis=1)

    output_7 = pd.concat([out_cap_7, perc], axis=1)
    output_7.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    outcap_7_in_count = output_7['Move In Surveys'].sum()
    outcap_7_out_count = output_7['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title_7}')
        else:
            ax.set_title(f'{title} - {method_title_7}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)    

    # Sense of Belonging
    method_title_8 = "Sense of Community and Belonging"
    out_cap_8 = out_cap.copy()

    if noAnswers is False:
        out_cap_8 = out_cap_8[out_cap_8['move_out_statement_i_have_a_sense_of_community_and_belonging'] != 'Prefer not to answer']
        out_cap_8 = out_cap_8[~out_cap_8['move_out_statement_i_have_a_sense_of_community_and_belonging'].isna()]

    out_cap_8 = out_cap_8.groupby(['move_out_statement_i_have_a_sense_of_community_and_belonging', 'Stage']).size().unstack()

    perc = out_cap_8.div(out_cap_8.sum(axis=0), axis=1)

    output_8 = pd.concat([out_cap_8, perc], axis=1)
    output_8.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    outcap_8_in_count = output_8['Move In Surveys'].sum()
    outcap_8_out_count = output_8['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title_8}')
        else:
            ax.set_title(f'{title} - {method_title_8}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1) 

    print(f"{method_title_1} {title}: Move In Sample Size = {outcap_1_in_count}")
    print(f"{method_title_1} {title}: Move Out Sample Size = {outcap_1_out_count}")
    print(f"\n{method_title_1} {title}: Summary Table")
    print("============================================")
    print(f"{output_1}")
    print("============================================\n\n\n\n")

    print(f"{method_title_2} {title}: Move In Sample Size = {outcap_2_in_count}")
    print(f"{method_title_2} {title}: Move Out Sample Size = {outcap_2_out_count}")
    print(f"\n{method_title_2} {title}: Summary Table")
    print("============================================")
    print(f"{output_2}")
    print("============================================\n\n\n\n")

    print(f"{method_title_3} {title}: Move In Sample Size = {outcap_3_in_count}")
    print(f"{method_title_3} {title}: Move Out Sample Size = {outcap_3_out_count}")
    print(f"\n{method_title_3} {title}: Summary Table")
    print("============================================")
    print(f"{output_3}")
    print("============================================\n\n\n\n")

    print(f"{method_title_4} {title}: Move In Sample Size = {outcap_4_in_count}")
    print(f"{method_title_4} {title}: Move Out Sample Size = {outcap_4_out_count}")
    print(f"\n{method_title_4} {title}: Summary Table")
    print("============================================")
    print(f"{output_4}")
    print("============================================\n\n\n\n")

    print(f"{method_title_5} {title}: Move In Sample Size = {outcap_5_in_count}")
    print(f"{method_title_5} {title}: Move Out Sample Size = {outcap_5_out_count}")
    print(f"\n{method_title_5} {title}: Summary Table")
    print("============================================")
    print(f"{output_5}")
    print("============================================\n\n\n\n")

    print(f"{method_title_6} {title}: Move In Sample Size = {outcap_6_in_count}")
    print(f"{method_title_6} {title}: Move Out Sample Size = {outcap_6_out_count}")
    print(f"\n{method_title_6} {title}: Summary Table")
    print("============================================")
    print(f"{output_6}")
    print("============================================\n\n\n\n")

    print(f"{method_title_7} {title}: Move In Sample Size = {outcap_7_in_count}")
    print(f"{method_title_7} {title}: Move Out Sample Size = {outcap_7_out_count}")
    print(f"\n{method_title_7} {title}: Summary Table")
    print("============================================")
    print(f"{output_3}")
    print("============================================\n\n\n\n")

    print(f"{method_title_8} {title}: Move In Sample Size = {outcap_8_in_count}")
    print(f"{method_title_8} {title}: Move Out Sample Size = {outcap_8_out_count}")
    print(f"\n{method_title_8} {title}: Summary Table")
    print("============================================")
    print(f"{output_8}")
    print("============================================\n\n\n\n")

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/Recovery_Capital/{method_title_1}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_1.to_csv(f'{output_directory}/{method_title_1}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/Recovery_Capital/{method_title_2}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_2.to_csv(f'{output_directory}/{method_title_2}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/Recovery_Capital/{method_title_3}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_3.to_csv(f'{output_directory}/{method_title_3}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/Recovery_Capital/{method_title_4}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_4.to_csv(f'{output_directory}/{method_title_4}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/Recovery_Capital/{method_title_5}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_5.to_csv(f'{output_directory}/{method_title_5}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/Recovery_Capital/{method_title_6}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_6.to_csv(f'{output_directory}/{method_title_6}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/Recovery_Capital/{method_title_7}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_7.to_csv(f'{output_directory}/{method_title_7}_{title}_{date.today()}.csv')

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/Recovery_Capital/{method_title_8}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output_8.to_csv(f'{output_directory}/{method_title_8}_{title}_{date.today()}.csv')


def outcomeSuccess(input_data,
                     title="",
                     plot=False,
                     includeStaff=False,
                     noAnswers=False):

    method_title = "Was Housing Successful?"

    out_success = input_data[['Stage', 'input_type', 
                           'move_out_recovery_housing_success']]

    out_success = out_success[out_success['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_success = out_success[out_success['input_type'] == 'Client']

    if noAnswers is False:
        out_success = out_success[out_success['move_out_recovery_housing_success'] != 'Prefer not to answer']
        out_success = out_success[~out_success['move_out_recovery_housing_success'].isna()]

    out_success = out_success.groupby(['move_out_recovery_housing_success', 'Stage']).size().unstack()

    perc = out_success.div(out_success.sum(axis=0), axis=1)

    output = pd.concat([out_success, perc], axis=1)
    output.columns = ['Move Out Surveys', '% Move Out']

    output_out_count = output['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title}')
        else:
            ax.set_title(f'{title} - {method_title}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    print(f"{method_title} {title}: Move Out Sample Size = {output_out_count}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{output}")
    print("============================================\n\n\n\n")


    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')


def outcomeMoveOutReason(input_data,
                         title="",
                         plot=False,
                         includeStaff=False,
                         noAnswers=False):

    method_title = "Move Out Reason"

    out_reason = input_data[['Stage', 'input_type', 
                             'move_out_recovery_housing_leave_reason']]

    out_reason = out_reason[out_reason['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_reason = out_reason[out_reason['input_type'] == 'Client']

    if noAnswers is False:
        out_reason = out_reason[out_reason['move_out_recovery_housing_leave_reason'] != 'Prefer not to answer']
        out_reason = out_reason[out_reason['move_out_recovery_housing_leave_reason'] != 'Unknown']
        out_reason = out_reason[~out_reason['move_out_recovery_housing_leave_reason'].isna()]

    out_reason = out_reason.groupby(['move_out_recovery_housing_leave_reason', 'Stage']).size().unstack()

    perc = out_reason.div(out_reason.sum(axis=0), axis=1)

    output = pd.concat([out_reason, perc], axis=1)
    output.columns = ['Move Out Surveys', '% Move Out']

    output_out_count = output['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title}')
        else:
            ax.set_title(f'{title} - {method_title}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    print(f"{method_title} {title}: Move Out Sample Size = {output_out_count}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{output}")
    print("============================================\n\n\n\n")


    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')


def outcomeSponsor(input_data,
                   title="",
                   plot=False,
                   includeStaff=False,
                   noAnswers=False):

    method_title = "Working with Sponsor?"

    out_sponsor = input_data[['Stage', 'input_type', 
                             'last_30_attendance_working_with_sponsor']]

    out_sponsor = out_sponsor[out_sponsor['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_sponsor = out_sponsor[out_sponsor['input_type'] == 'Client']

    if noAnswers is False:
        out_sponsor = out_sponsor[out_sponsor['last_30_attendance_working_with_sponsor'] != 'Prefer not to answer']
        out_sponsor = out_sponsor[out_sponsor['last_30_attendance_working_with_sponsor'] != 'Unknown']
        out_sponsor = out_sponsor[~out_sponsor['last_30_attendance_working_with_sponsor'].isna()]

    out_sponsor = out_sponsor.groupby(['last_30_attendance_working_with_sponsor', 'Stage']).size().unstack()

    perc = out_sponsor.div(out_sponsor.sum(axis=0), axis=1)

    output = pd.concat([out_sponsor, perc], axis=1)
    output.columns = ['Move In Surveys', 'Move Out Surveys', '% Move In', '% Move Out']

    output_out_count = output['Move Out Surveys'].sum()

    if plot is True:
        ax = perc.plot(kind='bar')
        ax.set_ylabel('Percent Total')
        if title == "":
            ax.set_title(f'{method_title}')
        else:
            ax.set_title(f'{title} - {method_title}')    

        # Add percentage labels above each bar
        for i in range(len(ax.containers)):
            container = ax.containers[i]
            for j, val in enumerate(container):
                height = val.get_height()
                ax.text(val.get_x() + val.get_width() / 2, height, f'{perc.values[j, i]:.0%}',
                        ha='center', va='bottom')

        # Set the y-axis limits
        ax.set_ylim(0, 1)

    print(f"{method_title} {title}: Move Out Sample Size = {output_out_count}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{output}")
    print("============================================\n\n\n\n")

    # Check if directory exists and create it if not
    output_directory = f'./ORH_Output_{date.today()}/Outcome_Comparison/{method_title}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output table to the new directory
    output.to_csv(f'{output_directory}/{method_title}_{title}_{date.today()}.csv')


def outcomeCriminalJustice(input_data,
                    title="",
                    plot=False,
                    includeStaff=False,
                    noAnswers=True):

    method_title = "Criminal Justice Status"

    # Criminal Justice Status
    out_cjs = input_data[['Stage', 'input_type', 'curr_status_cjs_parole_probation',
                            'curr_status_cjs_drug_court', 'curr_status_cjs_no_involvement',
                            'curr_status_cjs_no_answer']]

    update_cols = out_cjs.columns[2:]
    for col in update_cols:
        out_cjs[col] = out_cjs[col].fillna('NA').map(lambda x: 1 if x != 'NA' else 0)

    out_cjs = out_cjs[out_cjs['Stage'] != 'Follow Up']

    if includeStaff is False:
        out_cjs = out_cjs[out_cjs['input_type'] == 'Client']

    if noAnswers is False:    
        out_cjs = out_cjs[(out_cjs['curr_status_cjs_parole_probation'] > 0)
                              | (out_cjs['curr_status_cjs_drug_court'] > 0)
                              | (out_cjs['curr_status_cjs_no_involvement'] > 0)
                              | (out_cjs['curr_status_cjs_no_answer'] == 0)]
        out_cjs = out_cjs[['Stage', 'input_type', 'curr_status_cjs_parole_probation',
                            'curr_status_cjs_drug_court', 'curr_status_cjs_no_involvement']]

    grouped = out_cjs.groupby("Stage").sum()

    in_count = out_cjs[out_cjs['Stage']=='Move In']['Stage'].count()
    out_count = out_cjs[out_cjs['Stage']=='Move Out']['Stage'].count()

    grouped = grouped.transpose()

    grouped['Percent Move In'] = (grouped['Move In']/in_count)*100
    grouped['Percent Move Out'] = (grouped['Move Out']/out_count)*100

    # Reset the index of the dataframe
    grouped = grouped.reset_index()

    # Output Table
    output_table = grouped.copy()
    output_table['Move In Population'] = in_count
    output_table['Move Out Population'] = out_count
    output_table.columns = ['Criminal Justice System Status', 'Move In', 'Move Out', 'Percent Move In', 'Percent move Out', 'Move In Population', 'Move Out Population']

    prog_perc = grouped[['index', 'Percent Move In', 'Percent Move Out']]
    prog_perc.columns = ['Criminal Justice System Status', 'Move In', 'Move Out']

    print(f"{method_title} {title}: Move In Sample Size = {in_count}")
    print(f"{method_title} {title}: Move Out Sample Size = {out_count}")
    print(f"\n{method_title} {title}: Summary Table")
    print("============================================")
    print(f"{output_table}")
    print("============================================\n\n")

    if plot is True:
        # Create a horizontal stacked bar chart
        ax = prog_perc.plot(x = 'Criminal Justice System Status', kind="bar", stacked=False)

        # Set the chart title and labels
        if title == "":
            ax.set_title(f"{method_title}: Move In vs Move Out")
        else:
            ax.set_title(f"{title} - {method_title}: Move In vs Move Out")    
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


# ----------------------------------------------------------------------------------------- #
#                                  AGGREGATE FUNCTIONS                                      #
# ----------------------------------------------------------------------------------------- #


def outcomeComparison(data_1,
                      title_1,
                      data_2,
                      title_2,
                      plot=False,
                      includeStaff=True,
                      noAnswers=False):

    # Substance Use
    outcomeSubstance(input_data=data_1,
                     title=title_1,
                     plot=plot,
                     includeStaff=includeStaff,
                     noAnswers=noAnswers)
    outcomeSubstance(input_data=data_2,
                     title=title_2,
                     plot=plot,
                     includeStaff=includeStaff,
                     noAnswers=noAnswers)
    
    # Program Usage
    outcomePrograms(input_data=data_1,
                    title=title_1,
                    plot=plot,
                    includeStaff=includeStaff,
                    noAnswers=noAnswers)
    outcomePrograms(input_data=data_2,
                    title=title_2,
                    plot=plot,
                    includeStaff=includeStaff,
                    noAnswers=noAnswers)

    # Document Status
    outcomeDocuments(input_data=data_1,
                     title=title_1,
                     plot=plot,
                     includeStaff=includeStaff,
                     noAnswers=noAnswers)
    outcomeDocuments(input_data=data_2,
                     title=title_2,
                     plot=plot,
                     includeStaff=includeStaff,
                     noAnswers=noAnswers)

    # Employment Status
    outcomeEmployment(input_data=data_1,
                      title=title_1,
                      plot=plot,
                      includeStaff=includeStaff,
                      noAnswers=noAnswers)
    outcomeEmployment(input_data=data_2,
                      title=title_2,
                      plot=plot,
                      includeStaff=includeStaff,
                      noAnswers=noAnswers)

    # Health
    outcomeHealth(input_data=data_1,
                  title=title_1,
                  plot=plot,
                  includeStaff=includeStaff,
                  noAnswers=noAnswers)
    outcomeHealth(input_data=data_2,
                  title=title_2,
                  plot=plot,
                  includeStaff=includeStaff,
                  noAnswers=noAnswers)

    # Consequences
    outcomeConsequences(input_data=data_1,
                        title=title_1,
                        plot=plot,
                        includeStaff=includeStaff,
                        noAnswers=noAnswers)
    outcomeConsequences(input_data=data_2,
                        title=title_2,
                        plot=plot,
                        includeStaff=includeStaff,
                        noAnswers=noAnswers)

    # Recovery Capital
    outcomeRecoveryCapital(input_data=data_1,
                           title=title_1,
                           plot=plot,
                           includeStaff=includeStaff,
                           noAnswers=noAnswers)
    outcomeRecoveryCapital(input_data=data_2,
                           title=title_2,
                           plot=plot,
                           includeStaff=includeStaff,
                           noAnswers=noAnswers)

    # Housing Success
    outcomeSuccess(input_data=data_1,
                   title=title_1,
                   plot=plot,
                   includeStaff=includeStaff,
                   noAnswers=noAnswers)
    outcomeSuccess(input_data=data_2,
                   title=title_2,
                   plot=plot,
                   includeStaff=includeStaff,
                   noAnswers=noAnswers)

    # Move Out Reason
    outcomeMoveOutReason(input_data=data_1,
                         title=title_1,
                         plot=plot,
                         includeStaff=includeStaff,
                         noAnswers=noAnswers)
    outcomeMoveOutReason(input_data=data_2,
                         title=title_2,
                         plot=plot,
                         includeStaff=includeStaff,
                         noAnswers=noAnswers)

    # Sponsor Status
    outcomeSponsor(input_data=data_1,
                   title=title_1,
                   plot=plot,
                   includeStaff=includeStaff,
                   noAnswers=noAnswers)
    outcomeSponsor(input_data=data_2,
                   title=title_2,
                   plot=plot,
                   includeStaff=includeStaff,
                   noAnswers=noAnswers)

    # Criminal Justice Status
    outcomeCriminalJustice(input_data=data_1,
                           title=title_1,
                           plot=plot,
                           includeStaff=includeStaff,
                           noAnswers=noAnswers)
    outcomeCriminalJustice(input_data=data_2,
                           title=title_2,
                           plot=plot,
                           includeStaff=includeStaff,
                           noAnswers=noAnswers)


def cohortComparison(data_1,
                     title_1,
                     data_2,
                     title_2,
                     stage='Move In',
                     plot=False):

    # Age Comparison
    cohortAges(input_data=data_1,
               stage=stage,
               plot=plot,
               title=title_1)
    cohortAges(input_data=data_2,
               stage=stage,
               plot=plot,
               title=title_2)

    # Education Comparison
    cohortEducation(input_data=data_1,
                    stage=stage,
                    plot=plot,
                    title=title_1)
    cohortEducation(input_data=data_2,
                    stage=stage,
                    plot=plot,
                    title=title_2)

    # Race Comparison
    cohortRace(input_data=data_1,
               stage=stage,
               plot=plot,
               title=title_1)
    cohortRace(input_data=data_2,
               stage=stage,
               plot=plot,
               title=title_2)

    # Gender Comparison
    cohortGender(input_data=data_1,
                 stage=stage,
                 plot=plot,
                 title=title_1)
    cohortGender(input_data=data_2,
                 stage=stage,
                 plot=plot,
                 title=title_2)

    # Sexuality Comparison
    cohortSexuality(input_data=data_1,
                    stage=stage,
                    plot=plot,
                    title=title_1)
    cohortSexuality(input_data=data_2,
                    stage=stage,
                    plot=plot,
                    title=title_2)


def outcomeSummary(data_1,
                   title_1,
                   plot=False,
                   includeStaff=True,
                   noAnswers=False):

    # Substance Use
    outcomeSubstance(input_data=data_1,
                     title=title_1,
                     plot=plot,
                     includeStaff=includeStaff,
                     noAnswers=noAnswers)

    # Program Usage
    outcomePrograms(input_data=data_1,
                    title=title_1,
                    plot=plot,
                    includeStaff=includeStaff,
                    noAnswers=noAnswers)

    # Document Status
    outcomeDocuments(input_data=data_1,
                     title=title_1,
                     plot=plot,
                     includeStaff=includeStaff,
                     noAnswers=noAnswers)

    # Employment Status
    outcomeEmployment(input_data=data_1,
                      title=title_1,
                      plot=plot,
                      includeStaff=includeStaff,
                      noAnswers=noAnswers)

    # Health
    outcomeHealth(input_data=data_1,
                  title=title_1,
                  plot=plot,
                  includeStaff=includeStaff,
                  noAnswers=noAnswers)

    # Consequences
    outcomeConsequences(input_data=data_1,
                        title=title_1,
                        plot=plot,
                        includeStaff=includeStaff,
                        noAnswers=noAnswers)

    # Recovery Capital
    outcomeRecoveryCapital(input_data=data_1,
                           title=title_1,
                           plot=plot,
                           includeStaff=includeStaff,
                           noAnswers=noAnswers)

    # Housing Success
    outcomeSuccess(input_data=data_1,
                   title=title_1,
                   plot=plot,
                   includeStaff=includeStaff,
                   noAnswers=noAnswers)

    # Move Out Reason
    outcomeMoveOutReason(input_data=data_1,
                         title=title_1,
                         plot=plot,
                         includeStaff=includeStaff,
                         noAnswers=noAnswers)

    # Sponsor Status
    outcomeSponsor(input_data=data_1,
                   title=title_1,
                   plot=plot,
                   includeStaff=includeStaff,
                   noAnswers=noAnswers)

    # Criminal Justice Status
    outcomeCriminalJustice(input_data=data_1,
                           title=title_1,
                           plot=plot,
                           includeStaff=includeStaff,
                           noAnswers=noAnswers)


def cohortSummary(data_1,
                  title_1,
                  stage='Move In',
                  plot=False):

    # Age Comparison
    cohortAges(input_data=data_1,
               stage=stage,
               plot=plot,
               title=title_1)

    # Education Comparison
    cohortEducation(input_data=data_1,
                    stage=stage,
                    plot=plot,
                    title=title_1)

    # Race Comparison
    cohortRace(input_data=data_1,
               stage=stage,
               plot=plot,
               title=title_1)

    # Gender Comparison
    cohortGender(input_data=data_1,
                 stage=stage,
                 plot=plot,
                 title=title_1)

    # Sexuality Comparison
    cohortSexuality(input_data=data_1,
                    stage=stage,
                    plot=plot,
                    title=title_1)
