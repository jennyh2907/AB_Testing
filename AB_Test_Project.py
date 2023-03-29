# %%
import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats import shapiro
import matplotlib.pyplot as plt

# %% [markdown]
# ### Step 1: Data Exploration

# %%
# Read in the data
game = pd.read_csv("cookie_cats.csv")

# Turn into df
original_df = pd.DataFrame(game)

# Copy the df
game_df = original_df.copy()

# %%
# Look at the first five rows
game_df.head()

# %%
# Check the shape of data
game_df.shape

# %%
# Check the data type and null value
game_df.info()

# %%
# Check summary statistics for numeric column
game_df.describe()

# %%
# Target Variable: Version
# See if the number of both groups are similar, and observe the difference in mean, std, min, max
game_df.groupby("version").sum_gamerounds.agg(["count", "median", "mean", "std", "min", "max"])

# %%
# Check data distribution for both group
fig, (ax1, ax2) = plt.subplots(1, 2)

game_gate_30 = game_df[(game_df.version == "gate_30")]
ax1.hist(game_gate_30["sum_gamerounds"])
ax1.set_title('Gate_30 sum_gamerounds')

game_gate_40 = game_df[(game_df.version == "gate_40")]
ax2.hist(game_gate_40["sum_gamerounds"])
ax2.set_title('Gate_40 sum_gamerounds')

# %%
# Visualize the distribution of game rounds
game_gate_30.reset_index().set_index("index").sum_gamerounds.plot(legend = True, label = "Gate 30", figsize = (20,5))
game_gate_40.reset_index().set_index("index").sum_gamerounds.plot(legend = True, label = "Gate 40")
plt.suptitle("Original Game Rounds Distribution", fontsize = 20);

# %%
# Remove the outlier (max in gate_30 = 49854)
game_gate_30 = game_gate_30.loc[game_gate_30['sum_gamerounds'] < game_gate_30['sum_gamerounds'].max()]
game_df = game_df.loc[game_df['sum_gamerounds'] < game_df['sum_gamerounds'].max()]

# %%
game_df.sum_gamerounds.agg(["count", "median", "mean", "std", "min", "max"])

# %%
# Check the summary statistics
game_gate_30.sum_gamerounds.agg(["count", "median", "mean", "std", "min", "max"])

# %%
# Check data distribution for both group
fig, (ax1, ax2) = plt.subplots(1, 2)

ax1.hist(game_gate_30["sum_gamerounds"])
ax1.set_title('Gate_30 sum_gamerounds')

ax2.hist(game_gate_40["sum_gamerounds"])
ax2.set_title('Gate_40 sum_gamerounds')

# %%
# Visualize the distribution of game rounds
game_gate_30.reset_index().set_index("index").sum_gamerounds.plot(legend = True, label = "Gate 30", figsize = (20,5))
game_gate_40.reset_index().set_index("index").sum_gamerounds.plot(legend = True, label = "Gate 40")
plt.suptitle("Game Rounds Distribution After Remove the Outliers", fontsize = 20);

# %%
# Game Rounds vs Number of Users > Most of the users remain under 5 rounds
game_df.groupby("sum_gamerounds").userid.count().reset_index(name="count").sort_values(by="count", ascending=False).head()

# %%
# How many users are there in first 100 rounds?
game_df.groupby("sum_gamerounds").userid.count()[:100].plot()

# %%
# How many users reach Level 30 and 40?
game_df.groupby("sum_gamerounds").userid.count().loc[[30,40]]

# %%
# How many users come back and play 1/7 days after installing?
game_df["retention_1"].value_counts()/len(game_df)

# %%
# How many users come back and play 1/7 days after installing?
game_df["retention_7"].value_counts()/len(game_df)

# %%
# In gate_30 version, what proportion of user come back and play 1 day after installing?
game_gate_30.groupby("retention_1").sum_gamerounds.agg("count")/len(game_gate_30)

# %%
# In gate_40 version, what proportion of user come back and play 1 day after installing?
game_gate_40.groupby("retention_1").sum_gamerounds.agg("count")/len(game_gate_40)

# %%
# In each version, what proportion of user come back and play 7 days after installing?
game_gate_30.groupby("retention_7").sum_gamerounds.agg("count")/len(game_gate_30)

# %%
# In each version, what proportion of user come back and play 7 days after installing?
game_gate_40.groupby("retention_7").sum_gamerounds.agg("count")/len(game_gate_40)

# %%
# In each version, what proportion of user come back and play 1 and 7 days after installing?
len(game_gate_30.loc[(game_gate_30["retention_1"] == True) & (game_gate_30["retention_7"] == True)])/len(game_gate_30)


# %%
# In each version, what proportion of user come back and play 1 and 7 days after installing?
len(game_gate_40.loc[(game_gate_40["retention_1"] == True) & (game_gate_40["retention_7"] == True)])/len(game_gate_40)

# %% [markdown]
# ### Step 2: A/B Testing
# 
# a. Define control and test group
# 
# b. Check normality (Shapiro Test)
# 
# c. Check heteroeneity (Levene Test)
# 
# - Parametric + No Heterogeneity: T-Test
# 
# - Parametric + Heterogeneity: Welch Test
#     
# - Non Parametric: Mann Whitney Test

# %%
# Define control and test group (A is gate_30)
game_df["version"] = np.where(game_df["version"] == "gate_30", "A", "B")

# %%
# Check the data
game_df.head()

# %%
# A/B Test Function
def ABTest(df, group, target):
    # Split the data into A and B
    GA = df[df[group] == "A"][target]
    GB = df[df[group] == "B"][target]
    # Check the normality
    NormalA = shapiro(GA)[1] < 0.05
    NormalB = shapiro(GB)[1] < 0.05
    # Normal Distribution
    if ((NormalA == False) & (NormalB == False)):
        Heterogeneity = stats.levene(GA, GB)[1] < 0.05
        if(Heterogeneity == False):
            # p-value is for two-tailed t-test
            t_test = stats.ttest_ind(GA, GB, equal_var = True)[1]
        else:
            t_test = stats.ttest_ind(GA, GB, equal_var = False)[1]
    else:
    # Non-Parametric
        t_test = stats.mannwhitneyu(GA, GB)[1]

    # Result Dataframe
    result = pd.DataFrame({
        "Two-Tailed Hypothesis":[t_test < 0.05],
        "P-Value": [t_test],
        "One-Tailed Hypothesis":[t_test/2]
    })
    result["Test Type"] = np.where((NormalA == False) & (NormalB == False), "Parametric", "Non-Parametric")
    result["One-Tailed Hypothesis"] = np.where(result["One-Tailed Hypothesis"] < 0.05, "Reject H0", "Fail to Reject H0")
    result["Two-Tailed Hypothesis"] = np.where(result["Two-Tailed Hypothesis"] == True, "Reject H0", "Fail to Reject H0")
    result["Comment for One-Tailed Test"] = np.where(result["One-Tailed Hypothesis"] == "Reject H0", "GA and GB are not similar", "GA and GB are similar") 
    result["Comment for Two-Tailed Test"] = np.where(result["Two-Tailed Hypothesis"] == "Reject H0", "GA and GB are not similar", "GA and GB are similar") 
    if ((NormalA == False) & (NormalB == False)):
        result["Heterogeneity"] = np.where(Heterogeneity == True, "Yes", "No")
        result = result[["Test Type", "One-Tailed Hypothesis", "Two-Tailed Hypothesis", "P-Value", "Heterogeneity", "Comment for One-Tailed Test", "Comment for Two-Tailed Test"]]
    else:
        result = result[["Test Type", "One-Tailed Hypothesis", "Two-Tailed Hypothesis", "P-Value", "Comment for One-Tailed Test", "Comment for Two-Tailed Test"]]
    return result


# %%
# Apply the function
ABTest(df = game_df, group = "version", target = "sum_gamerounds")


