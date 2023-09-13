def valid_values_to_list(df, attribute):

    valid_values = df.query(f'Attribute == "{attribute}"')[
        'Valid Values'].str.split(',').values[0]

    return valid_values

def get_random_value(list_of_vv):
    return random.choice(list_of_vv)


def get_rand_integer(min=0, max=100):
    return random.randint(min, max)

def get_rand_float(min=0, max=100):
    return round(random.uniform(0.0, 100.0), 2)


import lorem


def get_random_string():
    t = lorem.sentence().split(" ")[0]
    return t


t = get_random_string()

def introduce_random_NAs(df, N=5):
    """ Another test to see if columns can handle empty values or if they will flag the empty value"""

    rows, cols = df.shape

    row_index = [get_rand_integer(max=rows-1) for _ in range(N)]

    col_index = [get_rand_integer(max=cols - 1) for _ in range(N)]

    indexes = list(zip(row_index, col_index))

    # Print indexes to check where values got replaced
    print(indexes)
    # for i in indexes
    df.iloc[row_index, col_index] = np.NaN

    return df

# find attribute column, fill in with value
def fill_in_attribute(df, index, attribute, value):
    df.loc[index, attribute] = value
    return df


def gen_mixed_string_with_length(N=12):
    # initializing size of string

    # using random.choices()
    # generating random strings
    res = ''.join(random.choices(string.ascii_uppercase +
                                 string.digits, k=N))

    # print result
    return res


def random_change():
    # list of functions to choose from
    choices = [introduce_random_NAs, gen_mixed_string_with_length,
               get_rand_integer, get_random_string, get_rand_float]

    choice = random.choice(choices)

    print(choice.__name__)

    return choice()

def partition(list_in, n):
    random.shuffle(list_in)
    return [list_in[i::n] for i in range(n)]