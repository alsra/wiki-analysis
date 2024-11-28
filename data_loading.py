import datetime
def main():
    pass
def parse_line(line):
    ''' Parse lines from the dataset into a dictionary'''
    return {
        'title': line[0],
        'time': datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S'),
        'revert': int(line[2]),
        'version': int(line[3]),
        'user': line[4]
    }

def load_data(file_path):
    ''' Load data from the dataset into a list of dictionaries
        Input: file_path - path to the dataset
        Output: a list of dictionaries'''
    with open(file_path, 'r') as file:
        lines = file.readlines()[1:]  # Skip header line
    return [parse_line(line.strip().split('\t')) for line in lines]

if __name__ == '__main__':
    main()