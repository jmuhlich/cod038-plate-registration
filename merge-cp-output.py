import pandas as pd
import pathlib
import re
import sys


def msg(s=""):
    print(s, file=sys.stderr)


csv_glob_pattern = "output/batch*/cp.out/*.csv"

if len(sys.argv) != 3:
    msg("Usage: merge-cp-output.py INPUT_PROJECT OUTPUT_CSV")
    msg()
    msg(f"INPUT_PROJECT directory must contain {csv_glob_pattern}")
    msg(f"OUTPUT_CSV filename must end with '.csv'")
    sys.exit(1)

project_path = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])

csv_paths = list(project_path.glob(csv_glob_pattern))
if not csv_paths:
    msg(f"No CSV files found at: {project_path / csv_glob_pattern}")
    sys.exit(1)
if out_path.suffix != ".csv":
    msg(f"Output filename does not end with '.csv': {out_path}")
    sys.exit(1)

msg("Found CSV files:")
for p in csv_paths:
    msg(f"  {p}")
df = pd.concat(
    [pd.read_csv(p, header=[0, 1]) for p in csv_paths],
    axis=0,
    ignore_index=True,
)

# Collapse column MultiIndex by joining levels on underscore.
df.columns = pd.Series(df.columns.values).apply("_".join)

# Fix up columns containing the repr of a bytes object, i.e. b'lorem ipsum'.
# This seems like the result of a CellProfiler bug.
bytes_regex = r"^b'([^'\\]+)'$"
for c in df:
    if df.dtypes[c] == object and df[c].str.fullmatch(bytes_regex).all():
        df[c] = df[c].str.replace(bytes_regex, r"\1", regex=True)

# Delete duplicate .1 .2 etc. columns as long as their values match the original
# column.
dup_name_regex = r"\.\d$"
for c in df.columns:
    if re.search(dup_name_regex, c):
        oc = re.sub(dup_name_regex, "", c)
        if (df[c] == df[oc]).all():
            del df[c]

df = df.sort_values([
    "Image_Metadata_Plate",
    "Image_Metadata_Well",
    "Image_Metadata_Site",
    "NucShrinked_ObjectNumber",
])

print()
if out_path.exists():
    msg(f"Overwriting csv file: {out_path}")
else:
    msg(f"Writing merged table: {out_path}")
df.to_csv(out_path, index=False)
