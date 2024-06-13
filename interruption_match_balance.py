import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu
from datetime import timedelta
import pingouin as pg
import contextlib

data = pd.read_csv('Data/additional_time_time_spss.csv')
data = data[data['half'] == 0]

data['Goals'] = data['GoalHome'] + data['GoalAway']

data['Additional Time Error'] = data['Additional time calculated'] - data['Additional time played']

other_df = data[data['Goal_difference'] <= 1].reset_index(drop=True)
other_interruption = other_df['Additional Time Error']
other_goal = other_df['Goals']

imbalance_df = data[data['Goal_difference'] > 1].reset_index(drop=True)
imbalance_interruption = imbalance_df['Additional Time Error']
imbalance_goal = imbalance_df['Goals']

other_mean = other_interruption.mean()
other_std = other_interruption.std()

imbalance_mean = imbalance_interruption.mean()
imbalance_std = imbalance_interruption.std()

other_goal_mean = other_goal.mean()
other_goal_std = other_goal.std()

imbalance_goal_mean = imbalance_goal.mean()
imbalance_goal_std = imbalance_goal.std()

other_goal_mean_std = f'{round(other_goal_mean, 2)}±{round(other_goal_std, 2)}'
imbalance_goal_mean_std = f'{round(imbalance_goal_mean, 2)}±{round(imbalance_goal_std, 2)}'


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


other_mean_std = f'{format_time(other_mean)}±{format_time(other_std)}'
imbalance_mean_std = f'{format_time(imbalance_mean)}±{format_time(imbalance_std)}'

descriptive_df = pd.DataFrame({'Close': other_mean_std,
                               'Imbalance': imbalance_mean_std,
                               }
                              , index=[0]
                              )
print(descriptive_df)


interruption_df = pd.concat([other_interruption, imbalance_interruption], axis=1).reset_index(drop=True)
interruption_df.columns = ['Other', 'Imbalance']

# manwhitney-u test
statistic, p_value = mannwhitneyu(other_interruption, imbalance_interruption)
print('Statistic:', statistic)
print('p-value:', p_value)

r = pg.compute_effsize(other_interruption, imbalance_interruption, paired=False, eftype='eta-square')
print("eta-square:", r)

interruption_df = interruption_df.melt(var_name='Group', value_name='Value')
interruption_df = interruption_df.dropna()


with open('Outputs/output_Goal_Difference_A.txt', 'w') as f:
    with contextlib.redirect_stdout(f):
        print(descriptive_df)
        print('Statistic:', statistic)
        print('p-value:', p_value)
        print("Eta squared:", r)


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
plt.xticks(range(0, 2), ['Close', 'Imbalance'], fontsize=18)
plt.yticks(ticks=list(range(-120, 601, 120))
           , labels=label
           , fontsize=18)
plt.title('Goal Difference Additional Time Error', fontsize=25)
plt.xlabel('Goal Difference', fontsize=18)
plt.ylabel('Additional Time Error (min)', fontsize=18)
# plt.savefig('Match outcome 2 groups.svg')
plt.show()

