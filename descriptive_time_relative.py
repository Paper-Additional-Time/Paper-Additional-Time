import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('Data/additional_time_time_spss.csv')

columns = ['Gross time played event data', 'Net time played event data',	'Additional time played',	'Additional time calculated'
           , 'Subs_all', 'Injury_all', 'Penalties_all', 'Goal Celebr._all', 'Disciplinary Sanc._all'
           , 'VAR_all', 'Other_all', 'Multiple Causes_all'
           ]

variables = ['Subs_all', 'Injury_all', 'Penalties_all', 'Goal Celebr._all', 'Disciplinary Sanc._all'
           , 'VAR_all', 'Other_all', 'Multiple Causes_all']

data['Additional time calculated_regular'] = data[variables].sum(axis=1)
for var in variables:
    data[var] = data[var] / data['Additional time calculated_regular']

full_time = data[data['half'] == 0].reset_index(drop=True)
first_half = data[data['half'] == 1].reset_index(drop=True)
second_half = data[data['half'] == 2].reset_index(drop=True)


df_list = []


for column in variables:
    full = full_time[column].dropna()
    first = first_half[column].dropna()
    second = second_half[column].dropna()
    full_mean = full.mean()
    first_mean = first.mean()
    second_mean = second.mean()
    full_std = full.std()
    first_std = first.std()
    second_std = second.std()
    full_mean_std = f'{round(full_mean, 4)}±{round(full_std, 4)}'
    first_mean_std = f'{round(first_mean, 4)}±{round(first_std, 4)}'
    second_mean_std = f'{round(second_mean, 4)}±{round(second_std, 4)}'
    df = pd.DataFrame({'full time': full_mean_std,
                       '1st half': first_mean_std,
                       '2nd half': second_mean_std,
                       }
                      , index=[column]
                      )
    df_list.append(df)
df = pd.concat(df_list, axis=0)
df.to_csv('Outputs/descriptive_time_relative.csv', encoding='gbk')
