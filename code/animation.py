import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
from matplotlib.animation import FuncAnimation

root = 'C:/Users/tpros/PycharmProjects/Projects/'
games = pd.read_csv(f'{root}datasets/nfl-big-data-bowl-2025/games.csv')
plays = pd.read_csv(f'{root}datasets/nfl-big-data-bowl-2025/plays.csv')
players = pd.read_csv(f'{root}datasets/nfl-big-data-bowl-2025/players.csv')
tackles = pd.read_csv(f'{root}datasets/nfl-big-data-bowl-2025/tackles.csv')


tracking = pd.DataFrame()
for i in range(1, 10):

    tracking_temp = pd.read_csv(f'{root}datasets/nfl-big-data-bowl-2025/tracking_week_' + str(i) + '.csv')
    tracking = pd.concat([tracking_temp, tracking], ignore_index=True)

scat_home = None
scat_away = None
scat_ball = None
scat_num = None
scat_tackler = None
scat_missed_tackle = None
scat_ball_carrier = None
scat_forced_fumble = None


# Create the football field
def create_field():
    fig, ax = plt.subplots(figsize=(10, 5))  # Adjust the fig-size as needed

    # Set the dimensions of the football field (120 yards x 53.3 yards)
    field_length = 120
    field_width = 53.3
    hash_right = 38.35  # yards
    hash_left = 12  # yards

    field = patches.Rectangle((0, 0), field_length, field_width, linewidth=2,
                              edgecolor='white', facecolor='green')
    ax.add_patch(field)

    # Create end zones
    endzone_left = patches.Rectangle((0, 0), 10, field_width, linewidth=2,
                                     edgecolor='white', facecolor='lightgray')
    endzone_right = patches.Rectangle((field_length - 10, 0), 10, field_width, linewidth=2,
                                      edgecolor='white', facecolor='lightgray')
    ax.add_patch(endzone_left)
    ax.add_patch(endzone_right)

    # Drawing the yard lines
    for i in range(2, 23):
        ax.plot([i * 5, i * 5], [0, field_width], color="white")

    for i in range(10, (field_length - 10) + 1):
        ax.scatter([i, i], [0, field_width], marker='|', color='white')

    # Draw hash marks
    for i in range(1, 11):
        ax.scatter([i * 10] * 2, [hash_left, hash_right], marker="_", color="white")

    # Adding yard numbers at hash marks
    for i in range(1, 10):
        if i <= 5:
            ax.text(10 + (i * 10), hash_left - 1, s=f"{i * 10}", color="white", ha="center", va="top", fontsize=15)
            ax.text(10 + (i * 10), hash_right + 1, s=f"{i * 10}", color="white", ha="center", va="bottom",
                    fontsize=15)
        else:
            ax.text(10 + (i * 10), hash_left - 1, s=f"{(10 - i) * 10}", color="white", ha="center", va="top",
                    fontsize=15)
            ax.text(10 + (i * 10), hash_right + 1, s=f"{(10 - i) * 10}", color="white", ha="center", va="bottom",
                    fontsize=15)

    # Set the aspect ratio, labels, and remove ticks
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('Home Sideline', fontsize=12)

    # Set the plot limits
    ax.set_xlim(0, field_length)
    ax.set_ylim(0, field_width)

    plt.title('Football Field', fontsize=16)
    return fig, ax


def find_play():
    team = input('Team you would like to search for (Enter Abbr): ')
    team_specific_games = games[(games['homeTeamAbbr'] == team) | (games['visitorTeamAbbr'] == team)]

    for i, g in team_specific_games.iterrows():
        print(f'Game ID: {g["gameId"]} | {g["homeTeamAbbr"]} vs. {g["visitorTeamAbbr"]}')

    game_to_search = int(input('Enter Game ID: '))

    specific_game = plays[plays['gameId'] == game_to_search]
    for i, g in specific_game.iterrows():
        print(f'Play ID: {g["playId"]} | {g["playDescription"]}')

    play_to_animate = int(input('Enter which play you would like to animate: '))
    return game_to_search, play_to_animate


def set_plot_title(play_id, game):
    play_description = plays[plays['playId'] == play_id]['playDescription'].values[0]
    home_team = game['homeTeamAbbr'].str.strip().values[0]
    visitor_team = game['visitorTeamAbbr'].str.strip().values[0]
    home_team_score = plays['preSnapHomeScore'].values[0]
    visitor_team_score = plays['preSnapVisitorScore'].values[0]
    plt.title(f'{play_description} - {home_team} {home_team_score} : {visitor_team} {visitor_team_score}')


def loading_bar(play_data, frame_id):
    frames = play_data['frameId'].unique()
    frames = len(frames)
    progress = (frame_id / frames) * 100
    num_hashes = min(int(10 * (progress/100)), 10)
    loading_bar_str = '[' + '#'*num_hashes + ' '*(10-num_hashes) + ']'
    print(f'{loading_bar_str} | {progress:.2f}%')


def plot_player_positions(frame_id, ax, play_data, home_team, visitor_team):
    global scat_home, scat_away, scat_ball, scat_num  # Access the global scat variables
    frame_data = play_data[(play_data['frameId'] == frame_id)]
    loading_bar(play_data, frame_id)

    if scat_home is not None:
        scat_home.remove()  # Remove the previous home team scatter plot if it exists
    if scat_away is not None:
        scat_away.remove()  # Remove the previous away team scatter plot if it exists
    if scat_ball is not None:
        scat_ball.remove()
    if scat_num is not None:
        for text in scat_num:
            text.remove()  # Remove the previous player number texts
    if scat_tackler is not None:
        scat_tackler.remove()
    if scat_missed_tackle is not None:
        scat_missed_tackle.remove()
    if scat_ball_carrier is not None:
        scat_ball_carrier.remove()
    if scat_forced_fumble is not None:
        scat_forced_fumble.remove()

    for team, group in frame_data.groupby('club'):
        color = 'black' if team == home_team else 'white' if team == visitor_team else 'brown'
        if team == home_team:
            scat_home = ax.scatter(group['x'], group['y'], s=70, c=color, alpha=0.5)
            scat_num = []  # Create a list to hold player number texts
            for i, p in group.iterrows():
                text = ax.text(p['x'], p['y'], str(int(p['jerseyNumber'])),
                               color='white', ha='center', va='center', fontsize=6)
                scat_num.append(text)  # Append the player number text to the list
        elif team == visitor_team:
            scat_away = ax.scatter(group['x'], group['y'], s=70, c=color, alpha=0.5)
            for i, p in group.iterrows():
                text = ax.text(p['x'], p['y'], str(int(p['jerseyNumber'])),
                               color='black', ha='center', va='center', fontsize=6)
                scat_num.append(text)  # Append the player number text to the list
        else:
            scat_ball = ax.scatter(group['x'], group['y'], s=30, c=color, alpha=0.5)


def animate(frame_id, ax, play_data, home_team, visitor_team):
    plot_player_positions(frame_id, ax, play_data, home_team, visitor_team)


def add_legend(ax):
    # Create legend for key players
    ax.scatter([], [], s=70, c='red', label='Tackler')
    ax.scatter([], [], s=70, c='yellow', label='Missed Tackle')
    ax.scatter([], [], s=70, c='green', label='Ball Carrier')
    ax.scatter([], [], s=70, c='purple', label='Forced Fumble')
    ax.legend()


def main():
    fig, ax = create_field()
    game_id, play_id = find_play()
    play_data = tracking[(tracking['gameId'] == game_id) & (tracking['playId'] == play_id)]
    game = games[games['gameId'] == game_id]
    home_team = game['homeTeamAbbr'].str.strip().values[0]
    visitor_team = game['visitorTeamAbbr'].str.strip().values[0]

    ani = FuncAnimation(fig, animate, frames=play_data['frameId'].unique(),
                        fargs=(ax, play_data, home_team, visitor_team), repeat=True)

    set_plot_title(play_id, game)
    add_legend(ax)
    ani.save(f'Play ID - {play_id}.gif', writer='Pillow')


if __name__ == '__main__':
    main()
