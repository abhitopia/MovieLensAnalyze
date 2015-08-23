import sys
from operator import itemgetter
import math

MOVIES_FILE = './Data/ml-1m/movies.dat'
RATINGS_FILE = './Data/ml-1m/ratings.dat'
USERS_FILE = './Data/ml-1m/users.dat'


class Table:
    def __init__(self, columns, file_path=None, data=None):
        self.columns = columns
        self.file_path = file_path
        self.data = data
        if data is None:
            self.load_from_file()

    def load_from_file(self):
        # reads the file into the memory
        with open(self.file_path, 'r') as csv_file:
            self.data = [list(row.split('::')) for row in csv_file.readlines()]

    def __hash_on(self, column):
        key_index = self.columns.index(column)
        result = {}
        for row in self.data:
            hash_val = row[key_index]
            if hash_val not in result:
                result[hash_val] = []
            result[hash_val].append(row)

        return result

    def join(self, other_table, column):
        # in place joins the other_table on column
        key_index = self.columns.index(column)
        other_table_dict = other_table.__hash_on(column)
        self.data = [row + other_table_dict[row[key_index]][0] for row in self.data]
        self.columns = self.columns + other_table.columns

    def group_by(self, column):
        # groups by "column" and returns dictionary of Tables for each group by value
        group_by_index = self.columns.index(column)
        result = {}
        for row in self.data:
            group_by_val = row[group_by_index]
            if group_by_val not in result:
                result[row[group_by_index]] = Table(columns=self.columns, data=[])
            result[group_by_val].data.append(row)
        return result

    def order_by(self, columns, desc=False):
        # in place order by on columns in the order specified
        sort_by_indices = [self.columns.index(column) for column in columns]
        self.data = sorted(self.data, key=itemgetter(*sort_by_indices), reverse=desc)

    def pretty_print(self, start, end):
        print "\n" + '-' * 137 + '\n' + "|{0:^10}|{1:^10}|{2:^80}|{3:^10}|{4:^10}|{5:^10}|".format(
            'Index', *self.columns) + '\n' + '-' * 137
        for idx in range(start, min(end, len(self))):
            print "|{0:^10}|{1:^10}|{2:^80}|{3:^10.4f}|{4:^10}|{5:^10.4f}|".format(idx+1, *self.data[idx])
        print '-' * 137

    def __len__(self):
        # return number of rows in table
        return len(self.data)

    def __getitem__(self, key):
        # return either complete column or slice of rows.
        if isinstance(key, str):
            idx = self.columns.index(key)
            return [row[idx] for row in self.data]
        elif isinstance(key, slice):
            return self.data[key]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage:  python ./analyze_movies.py (Gender|Age) <number>"
        sys.exit(1)
    else:
        # Reading command line arguments
        group_by, num_rows = sys.argv[1], int(sys.argv[2])

    # Joining the three files (movies, ratings and users) together
    movies = Table(columns=['MovieID', 'Title', 'Genres'], file_path=MOVIES_FILE)
    users = Table(columns=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code'], file_path=USERS_FILE)
    ratings = Table(columns=['UserID', 'MovieID', 'Rating', 'Timestamp'], file_path=RATINGS_FILE)
    ratings.join(movies, 'MovieID')
    ratings.join(users, 'UserID')

    # Actual group by here
    result = ratings.group_by(group_by)
    for group in result.keys():
        # Withing each group, all movies are further grouped by title
        movies_agg = result[group].group_by('Title')
        movie_avg_rating = Table(columns=['Group', 'Title', 'AvgRating', 'NumUsers', 'Score'], data=[])
        for title, movie_table in movies_agg.items():
            # calculating score for each movie within a group
            num_users = len(movie_table)
            avg_rating = sum(int(val) for val in movie_table['Rating']) / float(num_users)
            score = avg_rating*math.log(num_users)
            movie_avg_rating.data.append([group, title, avg_rating, num_users, score])

        # Order by 'Score'
        movie_avg_rating.order_by(['Score', 'AvgRating', 'NumUsers'], desc=True)
        movie_avg_rating.pretty_print(0, num_rows)
