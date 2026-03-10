
from pathlib import Path 

configfile: "config/test.yaml"


rule qoi_all:
  input: 
    "<shared_loc>/qois/zonal/out.parquet",
    "<shared_loc>/qois/surface/out.parquet"

rule qoi_create:
    input:
        idf = "<samples_loc>/{sample}/out.idf",
        sql = "<samples_loc>/{sample}/results/eplusout.sql"
    output:
        zonal = "<qoi_loc>/{sample}/zonal/out.parquet",
        surface = "<qoi_loc>/{sample}/surface/out.parquet" 
    params:
        name = lambda wildcards: wildcards.sample 
    shell:
        """
        uv run plyze qoi create \
            --case-name {params.name} \
            --idf-path {input.idf} \
            --sql-path {input.sql} \
            --zonal-path {output.zonal} \
            --surface-path {output.surface} \
        """
# NOTE: this can be one rule, just have two shell statements.. but two rules is nice for the dag.. 
rule qoi_consolidate_zone:
    input:
        parquets = expand("<qoi_loc>/{sample}/zonal/out.parquet", sample=get_samples)
    output:
        out = "<shared_loc>/qois/zonal/out.parquet"
    shell:
        """
        uv run plyze qoi consolidate \
            --in-paths {input.parquets} \
            --out-path {output.out}
        """

rule qoi_consolidate_surface:
    input:
        parquets = expand("<qoi_loc>/{sample}/surface/out.parquet", sample=get_samples)
    output:
        out = "<shared_loc>/qois/surface/out.parquet"
    shell:
        """
        uv run plyze qoi consolidate \
            --in-paths {input.parquets} \
            --out-path {output.out}
        """
