#=

This script extracts information about firm sizes in Eindhoven from the Excel files
provided by UCSC, scales them to a population of 10_000 and writes the results
back to a CSV file as a list of individual employer sizes (one employer per row).

It was tricky to find a way to do a reasonable scaling while preserving the jobs
ratio for the general population. The logic can be inferred from the code, but
here is a quick rundown (I'm happy to add more explanations on request):

- We read the number of employees by company size (but not the number of firms)
  for both public and private sector.
- We aggregate those two datasets together, using the more precise bin sizes
  from the private sector data. The public sector jobs are distributed in those
  "sub-bins" at the same pro-rata that private sector jobs are. This relies on
  the assumption that no private sector bin overlaps with two public sector
  bins, but that is the case in our data.
- For each bin, find the "optimal" employer size, which is more or less the size
  that minimizes the number of orphan jobs. See the `find_optimal_employer_size`
  for details.
- Generate individual company sizes from numbers computed at the previous step.
- Create one more company size to capture the orphan jobs.

The result is a list of individual company sizes written to a csv file that we
can directly use to initialize the model.

The script was written for Julia 0.6.4.

-- Nicolas 2018-08-31
-- edited Simone 2019-09-20  

=#
using DataFrames, ExcelReaders

function make_df(xl_file, sheet, headers, jobs)
  function ranges(hs)
    parse_range(a) = @. parse(Int, a) + [0, 0]
    rs = @. parse_range(matchall(r"\d+", string(hs)))
    rs[end][2] = typemax(Int)
    [r[1]:r[2] for r ∈ rs]
  end
  DataFrame(
    ranges = vec(ranges(readxl(xl_file, "$(sheet)!$(headers)"))),
    jobs = vec(readxl(xl_file, "$(sheet)!$(jobs)"))
  )
end

function distribute_jobs(df_private, df_public)
  falls_within(inner, outer) = inner.start >= outer.start && inner.stop <= outer.stop
  vcat(map(eachrow(df_public)) do row
    df = df_private[falls_within.(df_private[:range], [row[:range]]), :]
    df[:jobs] = df[:jobs] + df[:jobs] / sum(df[:jobs]) * row[:jobs]
    df
  end...)
end

function aggregate_big_employers(df_total)
  # identify the ranges where the number of jobs is
  # not enough to meet the lower bound of the range
  df_total[:enough] = df_total[:jobs] .>= getfield.(df_total[:ranges], :start)
  (by(df_total, :enough) do df
    if df[:enough][1] df[[:ranges, :jobs]] else
      # and aggregate all of them in a single range
      # with the lowest lower bound and the max upper bound
      DataFrame(
        ranges = [df[:ranges][1].start:df[:ranges][end].stop],
        jobs = sum(df[:jobs])
      )
	end
	end)[[:ranges, :jobs]]
end

function find_optimal_employer_size(df_total)
  by(df_total, names(df_total)) do df
	if floor(Int, df[:jobs][1]) == 38
		ranges = df[:ranges][1].start:min(df[:ranges][1].stop, 801)
	else
		ranges = df[:ranges][1].start:min(df[:ranges][1].stop, floor(Int, df[:jobs][1]))
	end
	println(ranges)
	# debug
	#println([n for n ∈ ranges])
    # for each range, find the employer size that minimizes the number of "orphaned" jobs
    # and the reciprocal of the number of companies (doubly weighted). The latter is
    # to prevent the last category to contain one big employer, which would result in
    # way too many links in the complete job network
    scores = [rem(df[:jobs][1], n) + 2 / div(df[:jobs][1], n) for n ∈ ranges]
	# debug
	#println(scores)
	# debug
	#println(ranges[indmin(scores)])
    DataFrame(employer_size = ranges[indmin(scores)])
  end
end

xl_file    = openxl("/Users/digitaldust/Documents/clients/LABSS-ISTC-CNR/PROTON-OC/inputs/eindhoven/raw/data Eindhoven Proton.xlsx")
#df_private = make_df(xl_file, "Private sector", "C3:P3", "C7:P7")
#df_public  = make_df(xl_file, "Public sector", "C19:H19", "C22:H22")
df_total   = make_df(xl_file, "firms by size", "C1:M1", "C3:M3")

eindhoven_pop = readxl(xl_file, "1b!F24")
sim_pop     = 10_000

println(df_total)

df_total[:jobs] = df_total[:jobs] * (sim_pop / eindhoven_pop)

println(df_total)

df_total = aggregate_big_employers(df_total)

println(df_total)

df_total = find_optimal_employer_size(df_total)

println(df_total)

make_sizes(row) = fill(row[:employer_size], Int(row[:jobs] ÷ row[:employer_size]))
sizes = map(make_sizes, eachrow(df_total)) |> Iterators.flatten |> collect
orphans = round(Int, sum(rem.(df_total[:jobs], df_total[:employer_size])))
push!(sizes, orphans)

open(io -> writedlm(io, sizes), "/Users/digitaldust/Documents/clients/LABSS-ISTC-CNR/PROTON-OC/inputs/eindhoven/data/employer_sizes.csv", "w")
