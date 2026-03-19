
configfile: "config/test.yaml"


rule temporal_test_input:
    input:
      samples = [make_eplus_sql_inputs(i) for i in get_eplus_samples_no_wildcard()]
    shell:
        "echo {input.samples}"


rule temporal_test_samples:
    input:
      samples = [make_eplus_sql_inputs(i) for i in get_eplus_samples_no_wildcard()]
    params:
      names =  lambda wildcards, input: [extract_from_sql(i) for i in input.samples]
    shell:
        "echo {input.samples} &&   echo hello && echo {params.names}"

rule temporal_test_time_select:
    shell:
      """
      uv run plyze temporal study-time-select \
          --ts.year {config[time_selection][year]} \
          --ts.month {config[time_selection][month]} \
          --ts.days {config[time_selection][days]} \
          --ts.hours {config[time_selection][hours]}
          """

rule temporal_create_target:
    input:
      samples = [make_eplus_sql_inputs(i) for i in get_eplus_samples_no_wildcard()]
    params:
      names =  lambda wildcards, input: [extract_from_sql(i) for i in input.samples]
    output:
      outpath = "<shared_loc>/temporal/out.csv"
    shell:
        """
        uv run plyze temporal create \
          --case-names {params.names} \
          --sqls {input.samples} \
          --ts.year {config[time_selection][year]} \
          --ts.month {config[time_selection][month]} \
          --ts.days {config[time_selection][days]} \
          --ts.hours {config[time_selection][hours]} \
          --outpath {output.outpath}
        """
