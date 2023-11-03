with open("../configs/notebook_config.yaml", 'r') as f:
    config = yaml.safe_load(f)

# paths to import files
root_path = config['paths']['root']
schematic_config = config['paths']['schematic']
csv_model = config['file_names']['csv_model']
json_model = config['file_names']['json_model']

print(
    "Schematic config: ", schematic_config,
    "\n", "CSV model: ", csv_model,
    "\n", "JSON LD Model: ", json_model)

with open(json_model, 'r') as jf:
    jo = json.load(jf)


# Manifest names in data model
manifest_names_extracted = []

for i in jo['@graph']:
    if i['@id'] == "bts:dataType":
        manifest_names_extracted.append(
            i["schema:domainIncludes"]["@id"].replace('bts:', ''))

manifest_names_extracted

# display names extracted
manifest_display_names_extracted = []

for i in jo['@graph']:
    if i['@id'].strip("bts:") in (manifest_names_extracted):
        manifest_display_names_extracted.append(
            i["sms:displayName"])


# Create dictionary for lookup later
manifest_name_relationships = dict(
    zip(manifest_names_extracted, manifest_display_names_extracted))

# manifest_name_relationships

import random
import string
from pathlib import Path


# number of rows to fill in
nrows = 10
random.seed = 27

# last minute chaos
chaos = False


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


gen_mixed_string_with_length()
def partition(list_in, n):
    random.shuffle(list_in)
    return [list_in[i::n] for i in range(n)]
# Create individual and biospecimen ids from random text

# for individaul IDs and specimenIDs
individaulIds = [gen_mixed_string_with_length(N=5) for _ in range(1, 100)]
specimenIds = [gen_mixed_string_with_length() for _ in range(1, 1000)]
specimenIds_partitioned = partition(specimenIds, 100)
ind_bio_map = []

for i, v in enumerate(individaulIds):
    for s in specimenIds_partitioned[i]:
        ind_bio_map.append(
            {
                'individualID': v,
                'specimenID': s

            }
        )

ind_bio_map = pd.DataFrame(ind_bio_map)
# Manifests
# Get all the RFC file paths
manifest_paths = glob(
    r"C:\Users\nlee\Documents\Projects\ELITE-DCC\ELITE-data-models\manifests\*.csv")

manifest_paths
Tested:

- scRNAseq : Passed (Need to add validation for biospecimenId)

# load data model
data_model_path = r'C:\Users\nlee\Documents\Projects\ELITE-DCC\ELITE-data-models\models\EL_data_model_v3.csv'

dm = pd.read_csv(data_model_path).iloc[:, 1:].fillna('')

dm.head()
# load manifest
manifest_path = 'C:\\Users\\nlee\\Documents\\Projects\\ELITE-DCC\\ELITE-data-models\\manifests\\WholeGenomeSequencing.csv'

df = pd.read_csv(manifest_path)

df.head()
manifest_name = Path(manifest_path).stem

parent_name = manifest_name_relationships[manifest_name]

df['Component'] = manifest_name
# Attributes from data model
attrs_to_fill = dm[dm['Attribute'] == (
    parent_name)]['DependsOn'].values[0].split(',')

attrs_to_fill
dm_attrs = dm[(dm['Attribute'].isin(attrs_to_fill))
              ].drop_duplicates(subset=['Attribute']).copy()

dm_attrs
# find values in dm_attrrs with valid values filled in
vv_attrs = dm_attrs[dm_attrs['Valid Values'] != '']['Attribute'].tolist()
for attribute in vv_attrs:
    for i in range(nrows):
        index = i
        temp_vv = valid_values_to_list(dm_attrs, attribute)
        new_val = get_random_value(temp_vv)
        df = fill_in_attribute(df, index, attribute, new_val)
# update df with sample of individual and biospecimen sample ids
ind_sample = ind_bio_map.sample(nrows, replace=True)[
    ['individualID', 'specimenID']].reset_index(drop=True)

df.update(ind_sample)
swap_validation_coder = {v: k for k, v in validation_coder.items()}

# column coding for values
dm_attrs['swapper'] = dm_attrs['Validation Rules'].fillna(
    'number').replace(swap_validation_coder)

dm_attrs['swapper'] = dm_attrs['swapper'].apply(lambda x: re.sub(
    '(regex search)|[' + re.escape('([0-9]+\.[0-9]*.?)|([0-9]+)') + ']', 'number', x))

# need a better regex later
dm_attrs['swapper'] = dm_attrs['swapper'].apply(lambda x: re.sub(
    'number numbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumber', 'number', x))

print(dm_attrs['swapper'].unique())

dm_attrs.head()
free_form_attrs = dm_attrs[(dm_attrs['Valid Values'] == '') & (
    ~dm_attrs['Attribute'].isin(['individualID', 'specimenID']))]

free_form_attrs
def generate_values(value):
    if value == 'string':
        # generate string
        return get_random_string()
    elif value == 'number':
        # generate random number
        return get_rand_integer()
for attribute in free_form_attrs['Attribute'].tolist():
    for i in range(nrows):
        index = i
        test = free_form_attrs.query(f'Attribute == "{attribute}"')
        new_val = test['swapper'].apply(generate_values).values[0]
        df = fill_in_attribute(df, index, attribute, new_val)
# write out test manifest to file for testing in DCA
df['Component'] = manifest_name

if chaos:
    df = introduce_random_NAs(df)
# Write out manifest
csv_path = os.path.join(
    r'C:\Users\nlee\Documents\Projects\ELITE-DCC\ELITE-data-models\test_manifests', manifest_name + '_test.csv')

df.to_csv(csv_path)
df.head()
# Run Validation Test

# manifest_path = "C:/Users/nlee/Documents/Projects/schematic/schematic/tests/data/mock_manifests/example_biospecimen_test.csv"
!schematic model --config {schematic_config} validate --manifest_path {file_path} --data_type {manifest_name}
# Submit Manifest

print(csv_path)
print(schematic_config)
print(manifest_name)
dataset_id = 'syn51753850'
dataset_id = 'syn51753844'

!schematic model --config C:/Users/nlee/Documents/Projects/schematic/schematic/config.yml submit -mp C:/Users/nlee/Documents/Projects/ELITE-DCC/ELITE-data-models/test_manifests/WholeGenomeSequencing_test.csv -d syn51753853 -vc WholeGenomeSequencing -mrt table --verbosity DEBUG