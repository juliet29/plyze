
from pathlib import Path 

configfile: "config/test.yaml"

def get_samples(wildcards):
  loc = Path(config["pathvars"]["samples_loc"])
  path = loc / "{sample}" / "eplusout.sql" 
  # TODO: need to consider that there are many paths => data is in buckets... but can keep in buckets? 

  samples, = glob_wildcards(path)
  return samples



rule all:
    input:
        "<shared_loc>/metrics/out.csv"

rule create_jpg:
    input:
        idf = "<samples_loc>/{{sample}}/out.idf",
        sql = "<samples_loc>/{{sample}}/results/eplusout.sql"
    output:
        jpg = "<jpg_loc>/graphs/{{sample}}/out.json" 
    params:
        dt = config["date_time"]
        name = lambda wildcards: wilcards.sample 
    shell:
        """
        uv run plys create-jpg \
            --idf-path {input.idf} \
            --sql-path {input.sql} \
            --date-time {params.dt} \
            --casename {params.name} \
            --jpg-path {output.jpg}
        """

rule create_jpg_metrics:
    input:
        jpg = "<jpg_loc>/graphs/{{sample}}/out.json"
    output:
        metrics = "<jpg_loc>/metrics/{{sample}}/out.json"
    shell:
        """
        uv run plys create-jpg-metrics \
            --jpg-path {input.jpg} \
            --metrics-path {output.metrics}
        """

rule consolidate_metrics:
    input:
        metrics = expand(f"<jpg_loc>/metrics/{{sample}}/out.json", sample=get_samples)
    output:
        csv = "<shared_loc>/metrics/out.csv"
    shell:
        """
        uv run plys consolidate-cases-jpg-metrics \
            --metrics-paths {input.metrics} \
            --case-names {params.names} \
            --csv-path {output.csv}
        """
