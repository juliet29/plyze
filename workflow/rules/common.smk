from pathlib import Path
from collections import defaultdict

configfile: "config/test.yaml"

def get_child_folders(path):
    return [i for i in path.iterdir() if i.is_dir()]


def create_case_parent_map(path):
    def handle_case(case_path, parent_path):
        sql = case_path / "results/eplusout.sql"
        if sql.exists():
            mapping[case_path.name] = parent_path.name

    parents = get_child_folders(path)
    mapping: dict[str, str] = {}

    for parent in parents:
        cases = get_child_folders(parent)
        for case in cases:
            handle_case(case, parent)


    return mapping


samples_loc = Path(config["pathvars"]["samples_loc"])
case_map = create_case_parent_map(samples_loc)



# --------  Eplus inputs and paths -----

def make_eplus_inputs(wildcards):
    loc = Path(config["pathvars"]["samples_loc"])
    parent = case_map[wildcards.sample]
    idf = loc / parent / "{wildcards.sample}/out.idf".format(wildcards=wildcards),
    sql = loc / parent / "{wildcards.sample}/results/eplusout.sql".format(wildcards=wildcards)
    return {"idf": idf, "sql": sql}



def get_eplus_samples(wildcards): 
  loc = Path(config["pathvars"]["samples_loc"])
  path = loc / "{folder}" / "{sample}" / "results/eplusout.sql" 
  results = glob_wildcards(path)

  return results.sample




# --------  Eplus inputs and samples without wild cards -----

def get_eplus_samples_no_wildcard(): 
  loc = Path(config["pathvars"]["samples_loc"])
  path = loc / "{folder}" / "{sample}" / "results/eplusout.sql" 
  results = glob_wildcards(path)
  return results.sample


def make_eplus_sql_inputs(sample):
    loc = Path(config["pathvars"]["samples_loc"])
    parent = case_map[sample]
    sql = loc / parent / f"{sample}/results/eplusout.sql" 
    return sql

def extract_from_sql(path: str):
  return Path(subpath(path, ancestor=2)).name

# --------  Further processes -----

def get_qoi_samples(wildcards): 
  loc = Path(config["pathvars"]["qoi_loc"])
  path = loc /  "{sample}" / "{subfolder}/out.parquet" 
  results = glob_wildcards(path)

  return results.sample

def get_jpg_samples(wildcards): 
  loc = Path(config["pathvars"]["jpg_loc"])
  path = loc / "metrics"/  "{sample}" / "out.json" 
  results = glob_wildcards(path)

  return results.sample





