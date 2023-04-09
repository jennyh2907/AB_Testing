# %%
import pandas as pd
import numpy as np

# %% [markdown]
# - Consider the data for 8 fast food restaurants that were part of a study of the effect of raising the minimum wage in NJ. The treatment group is the 2 restaurants in NJ and the control group is a set of 6 restaurants in PA (where the minimum wage was not raised). The outcome Y obs i is the number of people employed (including part time employees) at the end of the year. There are two covariates – Xi1, the identify of the fast food chain (Burger King or Kentucy Fried Chicken) and Xi2, employment at the end of the year prior to the increase in the minimum wage.

# %%
# Create a list of lists
data = [["NJ", "BK", 22.5, 30], 
        ["NJ", "KFC", 14, 12.5], 
        ["PA", "KFC", 13.8, 17],
        ["PA", "BK", 26.5, 18.5],
        ["PA", "BK", 20, 19.5], 
        ["PA", "BK", 13.5, 21],
        ["PA", "BK", 32.5, 26.5], 
        ["PA", "KFC", 21, 23]]

# Create the dataframe
fast_food = pd.DataFrame(data, columns = ["State", "Rest_Chain", "Init_Empl", "Final_Empl"])

# %%
fast_food

# %%
# Split treatment(NJ) and control(PA) group
treatment, control = fast_food[:2], fast_food[2:]

# %%
treatment

# %%
control

# %% [markdown]
# 1. We want to use matching to estimate the effect of raising the minimum wage assuming that unconfoundedness holds. We will match a single control unit with each treatment unit (without replacement). Our distance measure is D(i, j) = 100 ∗ I(Xi1 ̸ = Xj1) + |Xi2 − Xj2| where the indicator I is 1 if the two units are different chains and 0 if they are the same chain. Identify the matches for the 2 treatment units.

# %%
# Define a function to calculate distance
def distance_calc(treatment, control):
    dist = 0
    if treatment["Rest_Chain"] == control["Rest_Chain"]:
        dist = abs(treatment["Init_Empl"] - control["Init_Empl"])
    else: 
        dist = 100 + abs(treatment["Init_Empl"] - control["Init_Empl"])
    return round(dist, 1)

# %%
# Loop through treatment and control group
for t_store_index in range(0, 2):
    min_dist = 1000
    min_store_index = 0
    for c_store_index in range(0, 6):
        dist = distance_calc(treatment.iloc[t_store_index], control.iloc[c_store_index])
        if dist < min_dist:
            min_dist = dist
            min_store_index = c_store_index + 1
        print(f"Distance Between Treatment {t_store_index + 1} & Control {c_store_index + 1} is ", dist)
    print(f"The closest control store is {min_store_index}. The distance is {min_dist}")
    print("-----------------")
print("The selected store is the counterfactual observations of the treatment store.")

# %% [markdown]
# 2. What is the estimate of average treatment effect on treated (ATT)?

# %%
ATT = np.mean((treatment.iloc[0]["Final_Empl"] - control.iloc[2]["Final_Empl"]) + 
              (treatment.iloc[1]["Final_Empl"] - control.iloc[0]["Final_Empl"]))
print(f'The ATT with matching is {ATT}.')

# %% [markdown]
# 3. What is the estimate of average treatment effect (ATE)?

# %%
ATE = round(np.mean(treatment["Final_Empl"] - treatment["Init_Empl"]) - 
            np.mean(control["Final_Empl"] - control["Init_Empl"]), 1)

print(f'The ATE with matching is {ATE}.')

# %%



