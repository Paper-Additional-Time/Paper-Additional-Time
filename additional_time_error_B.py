import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression
from pandas.plotting import scatter_matrix
import scipy.stats as stats
from scipy.stats import kruskal, norm
from datetime import timedelta
import scikit_posthocs as sp
import pingouin as pg
import contextlib

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'left')
pd.set_option('display.precision', 3)


data = pd.read_csv('Data/additional_time_time_spss.csv')
data = data[data['half'] == 0]


data['Goals'] = data['GoalHome'] + data['GoalAway']

draw_df_home = data[data['Goal_difference_final'] == 0].reset_index(drop=True)
draw_interruption = draw_df_home['Additional Time Error']

one_df_home = data[data['Goal_difference_final'] == -1].reset_index(drop=True)
one_interruption_home = one_df_home['Additional Time Error']

other_df_home = data[data['Goal_difference_final'] < -1].reset_index(drop=True)
other_interruption_home = other_df_home['Additional Time Error']

one_df_away = data[data['Goal_difference_final'] == 1].reset_index(drop=True)
one_interruption_away = one_df_away['Additional Time Error']

other_df_away = data[data['Goal_difference_final'] > 1].reset_index(drop=True)
other_interruption_away = other_df_away['Additional Time Error']



draw_mean = draw_interruption.mean()
draw_std = draw_interruption.std()

one_home_mean = one_interruption_home.mean()
one_home_std = one_interruption_home.std()

other_home_mean = other_interruption_home.mean()
other_home_std = other_interruption_home.std()

one_away_mean = one_interruption_away.mean()
one_away_std = one_interruption_away.std()

other_away_mean = other_interruption_away.mean()
other_away_std = other_interruption_away.std()


def format_time(seconds):
    if seconds < 0:
        seconds = abs(seconds)
        minutes = seconds // 60
        seconds %= 60
        return f"-{int(minutes)}:{int(seconds):02d}"
    else:
        minutes = seconds // 60
        seconds %= 60
        return f"{int(minutes)}:{int(seconds):02d}"


draw_mean_std = f'{format_time(draw_mean)}±{format_time(draw_std)}'
one_home_mean_std = f'{format_time(one_home_mean)}±{format_time(one_home_std)}'
other_home_mean_std = f'{format_time(other_home_mean)}±{format_time(other_home_std)}'
one_away_mean_std = f'{format_time(one_away_mean)}±{format_time(one_away_std)}'
other_away_mean_std = f'{format_time(other_away_mean)}±{format_time(other_away_std)}'

descriptive_df = pd.DataFrame({'Home one more ahead': other_away_mean_std,
                               'Home one ahead': one_away_mean_std,
                               'Draw': draw_mean_std,
                               'Home one behind': one_home_mean_std,
                               'Home one more behind': other_home_mean_std
                               }
                              , index=[0]
                              )
print(descriptive_df)

interruption_df = pd.concat([other_interruption_away, one_interruption_away, draw_interruption, one_interruption_home, other_interruption_home], axis=1).reset_index(drop=True)
interruption_df.columns = ['Home one more ahead', 'Home one ahead', 'Draw', 'Home one behind', 'Home one more behind']
# kw test
statistic, p_value = kruskal(other_interruption_away, one_interruption_away, draw_interruption, one_interruption_home, other_interruption_home)
print('Statistic:', statistic)
print('p-value:', p_value)

eta_squared = (statistic - 5 + 1) / 153
print("Eta squared:", eta_squared)

interruption_df = interruption_df.melt(var_name='Group', value_name='Value')
interruption_df = interruption_df.dropna(axis=0)
posthocs = pg.pairwise_tests(data=interruption_df, dv='Value', between='Group', parametric=False, padjust='bonf', effsize='eta-square')
print(posthocs)
posthocs.to_csv('Posthoc_home_advantage.csv', index=False)

with open('Outputs/output_Goal_Difference_B.txt', 'w') as f:
    with contextlib.redirect_stdout(f):
        print(descriptive_df)
        print('Statistic:', statistic)
        print('p-value:', p_value)
        print("Eta squared:", eta_squared)
        print(posthocs)

# Draw Figure 1(a)
plt.figure(figsize=(10, 10))
sns.boxplot(x='Group', y='Value', data=interruption_df
            # , patch_artist=True
                      , showmeans=True
                      , medianprops={'color': 'black'
                                     , 'linestyle': '--'}
                      , boxprops={'facecolor': '#1f77b4'}
                      , meanprops={'markerfacecolor': 'black'
                         , 'markeredgecolor': 'black'
                       , 'linestyle': '-'})


label = [str(timedelta(seconds=x))[-5:] for x in range(-120, 601, 120)]
label[0] = '-02:00'
plt.axhline(interruption_df['Value'].mean(), color='r', linestyle='dashed', linewidth=1)
plt.xticks(range(0, 5), ['GD>1', "GD=1", "GD=0", "GD=-1", "GD<-1"], fontsize=18)
plt.yticks(ticks=list(range(-120, 601, 120))
           , labels=label
           , fontsize=18)
plt.title('Home Goal Difference Additional Time Error', fontsize=25)
plt.xlabel('Home Goal Difference', fontsize=18)
plt.ylabel('Additional Time Error (min)', fontsize=18)
# plt.savefig('Match outcome 5 groups.svg')
plt.show()
