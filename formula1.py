#https://theoehrly.github.io/Fast-F1/examples/index.html
#https://medium.com/towards-formula-1-analysis/how-to-recreate-the-formula-1-aws-corner-analysis-in-python-37c26363c47b


import fastf1 as ff1
import numpy as np
from fastf1 import plotting
from fastf1 import utils
from matplotlib import pyplot as plt

ff1.Cache.enable_cache('cache')

year, grand_prix, session = 2023, 'Bahrain', 'R'

quali = ff1.get_session(year, grand_prix, session)
quali.load()

# Setting parameters

driver_1, driver_2 = 'ALO', 'HAM'

distance_min, distance_max = 4800, 5500

# Extracting the laps

# Laps can now be accessed through the .laps object coming from the session
laps_driver_1 = quali.laps.pick_driver(driver_1)
laps_driver_2 = quali.laps.pick_driver(driver_2)

# Select the fastest lap
fastest_driver_1 = laps_driver_1.pick_fastest()
fastest_driver_2 = laps_driver_2.pick_fastest()

# Retrieve the telemetry and add the distance column
telemetry_driver_1 = fastest_driver_1.get_telemetry().add_distance()
telemetry_driver_2 = fastest_driver_2.get_telemetry().add_distance()


# Make sure whe know the team name for coloring
team_driver_1 = fastest_driver_1['Team']
team_driver_2 = fastest_driver_2['Team']

delta_time, ref_tel, compare_tel = utils.delta_time(fastest_driver_1, fastest_driver_2)

# Assigning labels to what the drivers are currently doing
telemetry_driver_1.loc[telemetry_driver_1['Brake'] > 0, 'CurrentAction'] = 'Brake'
telemetry_driver_1.loc[telemetry_driver_1['Throttle'] == 100, 'CurrentAction'] = 'Full Throttle'
telemetry_driver_1.loc[(telemetry_driver_1['Brake'] == 0) & (telemetry_driver_1['Throttle'] < 100), 'CurrentAction'] = 'Cornering'

telemetry_driver_2.loc[telemetry_driver_2['Brake'] > 0, 'CurrentAction'] = 'Brake'
telemetry_driver_2.loc[telemetry_driver_2['Throttle'] == 100, 'CurrentAction'] = 'Full Throttle'
telemetry_driver_2.loc[(telemetry_driver_2['Brake'] == 0) & (telemetry_driver_2['Throttle'] < 100), 'CurrentAction'] = 'Cornering'


# Numbering each unique action to identify changes, so that we can group later on
telemetry_driver_1['ActionID'] = (telemetry_driver_1['CurrentAction'] != telemetry_driver_1['CurrentAction'].shift(1)).cumsum()
telemetry_driver_2['ActionID'] = (telemetry_driver_2['CurrentAction'] != telemetry_driver_2['CurrentAction'].shift(1)).cumsum()


# Identifying all unique actions
actions_driver_1 = telemetry_driver_1[['ActionID', 'CurrentAction', 'Distance']].groupby(['ActionID', 'CurrentAction']).max('Distance').reset_index()
actions_driver_2 = telemetry_driver_2[['ActionID', 'CurrentAction', 'Distance']].groupby(['ActionID', 'CurrentAction']).max('Distance').reset_index()

actions_driver_1['Driver'] = driver_1
actions_driver_2['Driver'] = driver_2


# Calculating the distance between each action, so that we know how long the bar should be
actions_driver_1['DistanceDelta'] = actions_driver_1['Distance'] - actions_driver_1['Distance'].shift(1)
actions_driver_1.loc[0, 'DistanceDelta'] = actions_driver_1.loc[0, 'Distance']

actions_driver_2['DistanceDelta'] = actions_driver_2['Distance'] - actions_driver_2['Distance'].shift(1)
actions_driver_2.loc[0, 'DistanceDelta'] = actions_driver_2.loc[0, 'Distance']


# Merging together
all_actions = actions_driver_1.append(actions_driver_2)

# Calculating average speed
avg_speed_driver_1 = np.mean(telemetry_driver_1['Speed'].loc[
    (telemetry_driver_1['Distance'] >= distance_min) &
        (telemetry_driver_1['Distance'] <= distance_max)
])


avg_speed_driver_2 = np.mean(telemetry_driver_2['Speed'].loc[
    (telemetry_driver_2['Distance'] >= distance_min) &
        (telemetry_driver_2['Distance'] <= distance_max)
])

if avg_speed_driver_1 > avg_speed_driver_2:
    speed_text = f"{driver_1} {round(avg_speed_driver_1 - avg_speed_driver_2,2)}km/h faster"
else:
    speed_text = f"{driver_2} {round(avg_speed_driver_2 - avg_speed_driver_1,2)}km/h faster"


plot_size = [15, 15]
plot_title = f"{quali.event.year} {quali.event.EventName} - {quali.name} - {driver_1} VS {driver_2}"
plot_ratios = [1, 3, 2, 1, 1, 2, 1]
plot_filename = plot_title.replace(" ", "") + ".png"

# Make plot a bit bigger
plt.rcParams['figure.figsize'] = plot_size

# Create subplots with different sizes
fig, ax = plt.subplots(7, gridspec_kw={'height_ratios': plot_ratios})

# Set the plot title
ax[0].title.set_text(plot_title)

# Delta line
ax[0].plot(ref_tel['Distance'], delta_time)
ax[0].axhline(0)
ax[0].set(ylabel=f"Gap to {driver_2} (s)")

# Speed trace
ax[1].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Speed'], label=driver_1,
           color=ff1.plotting.team_color(team_driver_1))
ax[1].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Speed'], label=driver_2,
           color=ff1.plotting.team_color(team_driver_2))
ax[1].set(ylabel='Speed')
ax[1].legend(loc="lower right")

# Throttle trace
ax[2].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Throttle'], label=driver_1,
           color=ff1.plotting.team_color(team_driver_1))
ax[2].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Throttle'], label=driver_2,
           color=ff1.plotting.team_color(team_driver_2))
ax[2].set(ylabel='Throttle')

# Brake trace
ax[3].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Brake'], label=driver_1,
           color=ff1.plotting.team_color(team_driver_1))
ax[3].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Brake'], label=driver_2,
           color=ff1.plotting.team_color(team_driver_2))
ax[3].set(ylabel='Brake')

# Gear trace
ax[4].plot(telemetry_driver_1['Distance'], telemetry_driver_1['nGear'], label=driver_1,
           color=ff1.plotting.team_color(team_driver_1))
ax[4].plot(telemetry_driver_2['Distance'], telemetry_driver_2['nGear'], label=driver_2,
           color=ff1.plotting.team_color(team_driver_2))
ax[4].set(ylabel='Gear')

# RPM trace
ax[5].plot(telemetry_driver_1['Distance'], telemetry_driver_1['RPM'], label=driver_1,
           color=ff1.plotting.team_color(team_driver_1))
ax[5].plot(telemetry_driver_2['Distance'], telemetry_driver_2['RPM'], label=driver_2,
           color=ff1.plotting.team_color(team_driver_2))
ax[5].set(ylabel='RPM')

# DRS trace
ax[6].plot(telemetry_driver_1['Distance'], telemetry_driver_1['DRS'], label=driver_1,
           color=ff1.plotting.team_color(team_driver_1))
ax[6].plot(telemetry_driver_2['Distance'], telemetry_driver_2['DRS'], label=driver_2,
           color=ff1.plotting.team_color(team_driver_2))
ax[6].set(ylabel='DRS')
ax[6].set(xlabel='Lap distance (meters)')

# Hide x labels and tick labels for top plots and y ticks for right plots.
for a in ax.flat:
    a.label_outer()

# Store figure
plt.savefig(plot_filename, dpi=300)
plt.show()































































##############################
# #
# # Setting everything up
# #
# ##############################
# plt.rcParams["figure.figsize"] = [13, 4]
# plt.rcParams["figure.autolayout"] = True
#
# telemetry_colors = {
#     'Full Throttle': 'green',
#     'Cornering': 'grey',
#     'Brake': 'red',
# }
#
# fig, ax = plt.subplots(2)
#
# ##############################
# #
# # Lineplot for speed
# #
# ##############################
# ax[0].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Speed'], label=driver_1,
#            color=ff1.plotting.team_color(team_driver_1))
# ax[0].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Speed'], label=driver_2,
#            color=ff1.plotting.team_color(team_driver_2))
#
# # Speed difference
# ax[0].text(distance_min + 15, 200, speed_text, fontsize=15)
#
# ax[0].set(ylabel='Speed')
# ax[0].legend(loc="lower right")
#
# ##############################
# #
# # Horizontal barplot for telemetry
# #
# ##############################
# for driver in [driver_1, driver_2]:
#     driver_actions = all_actions.loc[all_actions['Driver'] == driver]
#
#     previous_action_end = 0
#     for _, action in driver_actions.iterrows():
#         ax[1].barh(
#             [driver],
#             action['DistanceDelta'],
#             left=previous_action_end,
#             color=telemetry_colors[action['CurrentAction']]
#         )
#
#         previous_action_end = previous_action_end + action['DistanceDelta']
#
# ##############################
# #
# # Styling of the plot
# #
# ##############################
# # Set x-label
# plt.xlabel('Distance')
#
# # Invert y-axis
# plt.gca().invert_yaxis()
#
# # Remove frame from plot
# ax[1].spines['top'].set_visible(False)
# ax[1].spines['right'].set_visible(False)
# ax[1].spines['left'].set_visible(False)
#
# # Add legend
# labels = list(telemetry_colors.keys())
# handles = [plt.Rectangle((0, 0), 1, 1, color=telemetry_colors[label]) for label in labels]
# ax[1].legend(handles, labels)
#
# # Zoom in on the specific part we want to see
# ax[0].set_xlim(distance_min, distance_max)
# ax[1].set_xlim(distance_min, distance_max)
#
# # Save the plot
# plt.savefig('analisis telemetrias', dpi=300)
#





























# fig, ax = plt.subplots()
# ax.plot(lec['LapNumber'], lec['LapTime'], color='red')
# ax.plot(ham['LapNumber'], ham['LapTime'], color='cyan')
# ax.set_title("LEC vs HAM")
# ax.set_xlabel("Lap Number")
# ax.set_ylabel("Lap Time")
# plt.show()