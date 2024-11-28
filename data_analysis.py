import math
from datetime import timedelta
def main():
    pass 
def sort_edits_by_article(data):
    ''' Sort edits by article title in chronological order
        Input: data - a list of dictionaries
        Output: a dictionary of lists of dictionaries, where each list of dictionaries is sorted by time'''
    articles = {}
    for edit in data:
        if edit['title'] not in articles:
            articles[edit['title']] = []
        articles[edit['title']].append(edit)
    for title in articles:
        articles[title].sort(key=lambda x: x['time'], reverse=False)
    return articles

def calculate_seniority(num_edits):
    ''' Calculate seniority of an editor based on the number of edits. Number of edits is incremented by 1 to avoid log(0)
        Input: num_edits - number of edits: int
        Output: seniority: float'''
    return math.log10(num_edits + 1)

def identify_reverts(data):
    ''' Identify reverts in the dataset and calculate the number of edits for each editor 
        Input: data - a list of dictionaries
        Output: reverts - a list of dictionaries
                editor_edits - a dictionary of editor names and the number of edits they made by the revert time'''
    sorted_articles = sort_edits_by_article(data)
    
    reverts = []
    editor_edits = {}

    for title, edits in sorted_articles.items():
        version_to_next_user = {}

        previous_version = None
        for edit in edits:
            user = edit['user']
            version = edit['version']

            # Update editor edits count
            editor_edits[user] = editor_edits.get(user, 0) + 1
            
            
            if previous_version is not None: 
                version_to_next_user[previous_version] = user

            if edit['revert']:
                if version in version_to_next_user:
                    reverted_user = version_to_next_user[version]
                    if user != reverted_user: # Exclude self-reverts
                        revert_info = {
                            'reverter': user,
                            'reverted': reverted_user,
                            'time': edit['time'],
                            'reverter_edits': editor_edits[user] - 1, # Subtract 1 to exclude the edit at the revert time
                            'reverted_edits': editor_edits[reverted_user] 
                        }
                        reverts.append(revert_info)

            previous_version = version

    return reverts, editor_edits


def construct_network(reverts):
    ''' Construct a network from the detected reverts 
        Input: reverts - a list of dictionaries
        Output: network - a list of dictionaries'''
    network = []
    # Iterate through reverts
    for revert in reverts:
        seniority_reverter = calculate_seniority(revert['reverter_edits'])
        seniority_reverted = calculate_seniority(revert['reverted_edits'])

        network.append({
            'reverter': revert['reverter'],
            'reverter_seniority': seniority_reverter,
            'reverted': revert['reverted'],
            'reverted_seniority': seniority_reverted,
            'time': revert['time']
        })

    return network
def find_ab_ba_sequences(reverts):
    ''' Find AB-BA event sequences in the data (reverts occur within 24 hours of each other) 
        Input: reverts - a list of reverts (dictionaries) 
        Output: AB-BA event sequences (dictionaries)'''
    ab_ba_sequences = []
    revert_pairs = {}  # key: (A, B), value: timestamp of AB revert
    # Iterate through reverts 
    for revert in reverts:
        reverter = revert['reverter']
        reverted = revert['reverted']
        time = revert['time']

        # Check for a BA event following an AB event
        if (reverted, reverter) in revert_pairs:
            ab_time = revert_pairs[(reverted, reverter)]
            if (time - ab_time) <= timedelta(hours=24): # Check if the BA event occurs within 24 hours of the AB event
                ab_ba_sequences.append({'AB': (reverted, reverter, ab_time), 'BA': (reverter, reverted, time)})
                del revert_pairs[(reverted, reverter)]  # Remove the AB event to only count the first BA event in the sequence
            continue

        # Add the AB event
        revert_pairs[(reverter, reverted)] = time

    return ab_ba_sequences
def calculate_abs_seniority_differences_ab_ba(ab_ba_sequences, editor_edits):
    ''' Calculate the absolute difference in seniority for each revert in AB-BA sequences
        Input: ab_ba_sequences - a list of AB-BA event sequences (dictionaries)
               editor_edits - a dictionary of editor names and the number of edits they made by the revert time
               Output: abs_diffs - a list of absolute differences in seniority'''
    abs_diffs = []
    for sequence in ab_ba_sequences:
        ab_revert = sequence['AB']
        ba_revert = sequence['BA']

        # Calculate seniority at the time of AB and BA events
        ab_seniority_reverter = calculate_seniority(editor_edits[ab_revert[0]] - 1)
        ab_seniority_reverted = calculate_seniority(editor_edits[ab_revert[1]])
        ba_seniority_reverter = calculate_seniority(editor_edits[ba_revert[0]] - 1)
        ba_seniority_reverted = calculate_seniority(editor_edits[ba_revert[1]])

        # Add the absolute differences to the list
        abs_diffs.append(abs(ab_seniority_reverter - ab_seniority_reverted))
        abs_diffs.append(abs(ba_seniority_reverter - ba_seniority_reverted))

    return abs_diffs
def calculate_abs_seniority_differences_other(reverts, ab_ba_sequences, editor_edits):
    ''' Calculate the absolute difference in seniority for reverts not in AB-BA sequences
        Input: reverts - a list of reverts (dictionaries)
               ab_ba_sequences - a list of AB-BA event sequences (dictionaries)
               editor_edits - a dictionary of editor names and the number of edits they made by the revert time
               Output: abs_diffs - a list of absolute differences in seniority'''
    ab_ba_reverts = set()
    for sequence in ab_ba_sequences:
        ab_ba_reverts.add((sequence['AB'][0], sequence['AB'][1], sequence['AB'][2]))
        ab_ba_reverts.add((sequence['BA'][0], sequence['BA'][1], sequence['BA'][2]))

    abs_diffs = []
    for revert in reverts:
        if (revert['reverter'], revert['reverted'], revert['time']) not in ab_ba_reverts:
            reverter_seniority = calculate_seniority(editor_edits[revert['reverter']] - 1)
            reverted_seniority = calculate_seniority(editor_edits[revert['reverted']])
            abs_diff = abs(reverter_seniority - reverted_seniority)
            abs_diffs.append(abs_diff)

    return abs_diffs
if __name__ == '__main__':
    main()