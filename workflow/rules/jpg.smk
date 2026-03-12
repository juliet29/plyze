
from pathlib import Path 

configfile: "config/test.yaml"



rule jpg_create:
    input:
        unpack(make_eplus_inputs)
    output:
        jpg = "<jpg_loc>/graphs/{sample}/out.json" 
    params:
        dt = config["date_time"],
        name = lambda wildcards: wildcards.sample 
    shell:
        """
        uv run plyze jpg create \
            --graph_name {params.name} \
            --idf-path {input.idf} \
            --sql-path {input.sql} \
            --date-time {params.dt} \
            --jpg-path {output.jpg}
        """

rule jpg_create_metrics:
    input:
        jpg = "<jpg_loc>/graphs/{sample}/out.json"
    output:
        metrics = "<jpg_loc>/metrics/{sample}/out.json"
    shell:
        """
        uv run plyze jpg create-metrics \
            --jpg-path {input.jpg} \
            --metrics-path {output.metrics}
        """

rule jpg_create_target: 
    input:
        expand("<jpg_loc>/graphs/{sample}/out.json", sample=get_eplus_samples)

rule jpg_create_metrics_target: 
    input:
        expand("<jpg_loc>/metrics/{sample}/out.json", sample=get_eplus_samples)
          
rule jpg_consolidate_target:
    input:
        metrics = expand("<jpg_loc>/metrics/{sample}/out.json", sample=get_jpg_samples)
    output:
        csv = "<shared_loc>/metrics/out.csv"
    shell:
        """
        uv run plyze jpg consolidate \
            --metrics-paths {input.metrics} \
            --csv-path {output.csv}
        """

