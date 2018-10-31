extensions [nw table csv profiler rnd]

breed [jobs      job]
breed [employers employer]
breed [schools   school]
breed [persons   person]
breed [prisoners prisoner]

undirected-link-breed [family-links       family-link]       ; person <--> person
undirected-link-breed [friendship-links   friendship-link]   ; person <--> person
undirected-link-breed [criminal-links     criminal-link]     ; person <--> person
undirected-link-breed [professional-links professional-link] ; person <--> person
undirected-link-breed [school-links       school-link]       ; person <--> person
undirected-link-breed [meta-links         meta-link]         ; person <--> person


undirected-link-breed [positions-links         position-link]          ; job <--> employer
undirected-link-breed [job-links               job-link]               ; person <--> job
undirected-link-breed [school-attendance-links school-attendance-link] ; person <--> school


persons-own [
  num-crimes-committed
  education-level
  my-job               ; could be known from `one-of job-link-neighbors`, but is stored directly for performance - need to be kept in sync
  birth-tick
  male?
  propensity
  oc-member?
  cached-oc-embeddedness
]

prisoners-own [
  num-crimes-committed
  education-level
  my-job               ; could be known from `one-of job-link-neighbors`, but is stored directly for performance - need to be kept in sync
  birth-tick
  male?
  propensity
  oc-member?
  cached-oc-embeddedness
  sentence-countdown
]

jobs-own [
  salary
  education-level-required
]
schools-own [
  education-level
]

criminal-links-own [
  num-co-offenses
]

meta-links-own [
  dist ; the "distance cost" of traversing that link
       ; (the stronger the link, the samller the distance cost)
]

globals [
  network-saving-interval      ; every how many we save networks structure
  network-saving-list          ; the networks that should be saved
  model-saving-interval        ; every how many we save model structure
  breed-colors           ; a table from breeds to turtle colors
  num-co-offenders-dist  ; a list of probability for different crime sizes
]

to profile-setup
  profiler:reset         ; clear the data
  profiler:start         ; start profiling
  setup                  ; set up the model
  profiler:stop          ; stop profiling
  print profiler:report  ; view the results
  profiler:reset         ; clear the data
end

to profile-go
  profiler:reset         ; clear the data
  profiler:start         ; start profiling
  setup                  ; set up the model
  repeat 20 [ go ]
  profiler:stop          ; stop profiling
  print profiler:report  ; view the results
  profiler:reset         ; clear the data
end

to setup
  clear-all
  set num-co-offenders-dist but-first csv:from-file "inputs/general/data/num_co_offenders_dist.csv"
  nw:set-context persons links
  ask patches [ set pcolor white ]
  setup-default-shapes
  setup-oc-groups
  setup-population
  reset-ticks ; so age can be computed
  setup-employers
  assign-jobs
  setup-schools
  init-students
  init-professional-links
  init-breed-colors
  ask turtles [
    set-turtle-color
    setxy random-xcor random-ycor
  ]
  reset-oc-embeddedness
  repeat 30 [ layout-spring turtles links 1 0.1 0.1 ]
  let networks-output-parameters csv:from-file "./networks/parameters.csv"
  set network-saving-list []
  foreach networks-output-parameters [ p ->
    let parameterkey (item 0 p)
    let parametervalue (item 1 p)
    if parameterkey = "network-saving-interval" [ set network-saving-interval parametervalue]
    if parametervalue = "yes" [set network-saving-list lput parameterkey network-saving-list]
  ]
  let model-output-parameters csv:from-file "./outputs/parameters.csv"
  foreach model-output-parameters [ p ->
    let parameterkey (item 0 p)
    let parametervalue (item 1 p)
    if parameterkey = "model-saving-interval" [ set model-saving-interval parametervalue]
  ]
  update-plots
end

to go
  if (network-saving-interval > 0) and ((ticks mod network-saving-interval) = 0) [
    foreach network-saving-list [listname ->
      let network-agentset links with [breed = runresult listname]
      if any? network-agentset[
         let network-file-name (word "networks/" ticks  "_"  listname  ".graphml")
         nw:set-context turtles runresult listname
         nw:save-graphml network-file-name
      ]
    ]
  ]
  if (model-saving-interval > 0 ) and ((ticks mod model-saving-interval) = 0)[
    let model-file-name (word "outputs/" ticks "_model_" ".world")
    export-world model-file-name
  ]
  commit-crimes
  ask prisoners [
    set sentence-countdown sentence-countdown - 1
    if sentence-countdown = 0 [ set breed persons ]
  ]
  tick
end

to setup-oc-groups
  let data filter [ row ->
    first row = operation
  ] but-first csv:from-file "inputs/general/data/oc_groups.csv"
  let groups table:make
  let families table:make
  foreach data [ row ->
    create-persons 1 [
      init-person ; we start with regular init but will override a few vars
      put-self-in-table groups   (item 1 row)
      put-self-in-table families (item 2 row)
      set birth-tick 0 - ((item 3 row) * ticks-per-year)
      set male? (item 4 row)
      set oc-member? true
    ]
  ]
  foreach agentsets-from-table groups [ agents ->
    ask agents [ create-criminal-links-with other agents [ set num-co-offenses 1 ]]
  ]
  foreach agentsets-from-table families [ agents ->
    ask agents [ create-family-links-with other agents ]
  ]
end

to-report agentsets-from-table [ the-table ]
  ; given a table havings lists of agents as values,
  ; reports a list of agentsets.
  report map [ k ->
    turtle-set table:get the-table k
  ] filter [ k -> k != "NA" ] table:keys the-table
end

to put-self-in-table [ the-table the-key ] ; person command
  let the-list table:get-or-default the-table the-key []
  table:put the-table the-key lput self the-list
end

to reset-oc-embeddedness
  ask meta-links [ die ]
  ask persons [ set cached-oc-embeddedness nobody ]
end

to setup-default-shapes
  foreach (list
    (list persons         "person")
    (list jobs            "circle")
    (list employers       "pentagon")
    (list schools         "house colonial")
  ) [ p -> set-default-shape first p last p ]
end

to init-breed-colors
  let breeds map [ b -> (word b) ] remove-duplicates [ breed ] of turtles
  set breed-colors table:from-list (map [ [b i] ->
    (list b lput 80 (hsb ((360 / length breeds) * i) 50 80))
  ] breeds (range length breeds))
end

to set-turtle-color ; turtle command
  set color table:get-or-default breed-colors (word breed) grey
  set label-color hsb (item 0 extract-hsb color) 50 20
end

to setup-population
  output "Setting up population"

  ; Using Watts-Strogatz is a bit arbitrary, but it should at least give us
  ; some clustering to start with. The network structure should evolve as the
  ; model runs anyway. Still, if we could find some data on the properties of
  ; real world friendship networks, we could use something like
  ; http://jasss.soc.surrey.ac.uk/13/1/11.html instead.
  nw:generate-watts-strogatz persons friendship-links num-non-oc-persons 2 0.1 [ init-person ]
  ask persons [
    create-family-links-with n-of 3 other persons ; TODO use https://doi.org/10.1371/journal.pone.0008828 instead...
  ]
end

to init-person ; person command
  set my-job nobody                                     ; jobs will be assigned in `assign-jobs`
  set birth-tick 0 - random (70 * ticks-per-year)       ; TODO use a realistic distribution
  set male? one-of [true false]                         ; TODO use a realistic distribution // could also be 0/1 if it makes things easier
  set education-level random (num-education-levels - 1) ; TODO use a realistic distribution
  set propensity 0                                      ; TODO find out how this should be initialised
  set oc-member? false                                  ; the seed OC network are initialised separately
  set num-crimes-committed 0                            ; some agents should probably have a few initial crimes at start
end

to-report age
  report floor ((ticks - birth-tick) / ticks-per-year)
end

to setup-employers
  output "Setting up employers"
  let job-counts reduce sentence csv:from-file (word "inputs/" data-folder "employer_sizes.csv")
  foreach job-counts [ n ->
    create-employers 1 [
      hatch-jobs n [
        create-position-link-with myself
        set education-level-required random (num-education-levels - 1) ; TODO: use a realistic distribution
        set salary max (list 10000 (random-normal 30000 1000))         ; TODO: use a realistic distribution
        set label self
      ]
      set label self
    ]
  ]
end

to assign-jobs
  output "Assigning jobs"
  let find-jobs-to-fill [ -> jobs with [ not any? my-job-links ] ]
  let old-jobs-to-fill no-turtles
  let jobs-to-fill runresult find-jobs-to-fill
  while [ any? jobs-to-fill and jobs-to-fill != old-jobs-to-fill ] [
    foreach sort-on [ 0 - salary ] jobs-to-fill [ the-job ->
      ; start with highest salary jobs, the decrease the amount of job hopping
      ask the-job [ assign-job ]
    ]
    set old-jobs-to-fill jobs-to-fill
    set jobs-to-fill runresult find-jobs-to-fill
  ]
end

to assign-job ; job command

  assert [ -> not any? my-job-links ]

  let the-employer one-of position-link-neighbors
  assert [ -> is-employer? the-employer ]

  let employees [ current-employees ] of the-employer

  let candidate-pools (list
    ; First give a chance to current employees to upgrade if they are qualified.
    [ -> employees ]
    ; Then, look for candidates in the immediate network of current employees.
    [ -> turtle-set [ person-neighbors ] of employees ]
    ; Then look for anyone qualified in the general population.
    [ -> persons ]
  )

  let new-employee nobody
  while [ new-employee = nobody and not empty? candidate-pools ] [
    let candidates runresult first candidate-pools
    set candidate-pools but-first candidate-pools
    set new-employee pick-new-employee-from candidates
  ]

  ask turtle-set new-employee [
    ask my-job-links [ die ]
    set my-job myself
    create-job-link-with myself
  ]

end

to-report person-neighbors ; turtle reporter
  report link-neighbors with [ is-person? self ]
end

to-report current-employees ; employer reporter
  report turtle-set [ job-link-neighbors ] of position-link-neighbors
end

to-report pick-new-employee-from [ the-candidates ] ; job reporter
  let the-job self
  report one-of the-candidates with [
    interested-in? the-job and qualified-for? the-job
  ]
end

to-report qualified-for? [ the-job ] ; person reporter
  report education-level >= [ education-level-required ] of the-job
end

to-report interested-in? [ the-job ] ; person reporter
  report ifelse-value (my-job = nobody) [ true ] [
    [ salary ] of the-job > [ salary ] of my-job
  ]
end

to init-professional-links
  ask employers [
    let employees current-employees
    ask employees [ create-professional-links-with other employees ]
  ]
end

to assert [ f ]
  if not runresult f [ error (word "Assertion failed: " f) ]
end

to output [ str ]
  if output? [ output-show str ]
end

to-report education-levels
  ; TODO this should come from real data
  report table:from-list (list
    ;     level            start-age  end-age  prob-of-attending  num-schools
    (list     1   (list            6       11                1.0           10))
    (list     2   (list           12       17                1.0            5))
    (list     3   (list           18       25                0.1            1))
  )
end

to setup-schools
  foreach table:keys education-levels [ level ->
    create-schools item 3 table:get education-levels level [
      set education-level level
    ]
  ]
end

to init-students
  foreach table:keys education-levels [ level ->
    let row table:get education-levels level
    let start-age item 0 row
    let end-age   item 1 row
    let prob      item 2 row
    ask persons with [ age >= start-age and age <= end-age ] [
      maybe-enroll-to-school level
    ]
  ]
  ask schools [
    let students school-attendance-link-neighbors
    ask students [ create-school-links-with other students ]
  ]
end

to maybe-enroll-to-school [ level ] ; person command
  let prob item 2 table:get education-levels level
  if random-float 1 < prob [
    create-school-attendance-link-with one-of schools with [ education-level = level ]
  ]
end

to graduate
  let levels table:from-list map [ row -> list first row row ] education-levels
  ask schools [
    let end-age item 2 table:get levels education-level
    ask school-attendance-link-neighbors with [ age > end-age ] [
      ask link-with myself [ die ]
      if table:has-key? education-levels (education-level + 1) [
        maybe-enroll-to-school (education-level + 1)
      ]
    ]
  ]
end

to-report link-color
  report [50 50 50 50]
end

to commit-crimes ; person procedure
  reset-oc-embeddedness
  let co-offender-groups []
  ask persons [
    if random-float 1 < criminal-tendency [
      let accomplices find-accomplices number-of-accomplices
      set co-offender-groups lput (turtle-set self accomplices) co-offender-groups
    ]
  ]
  foreach co-offender-groups commit-crime
  let oc-co-offender-groups filter [ co-offenders ->
    any? co-offenders with [ oc-member? ]
  ] co-offender-groups
  foreach oc-co-offender-groups [ co-offenders ->
    ask co-offenders [ set oc-member? true ]
  ]
  foreach co-offender-groups [ co-offenders ->
    if random-float 1 < probability-of-getting-caught [ get-caught co-offenders ]
  ]
end

to-report find-accomplices [ n ] ; person reporter
  let d 1 ; start with a network distance of 1
  let accomplices []
  while [ length accomplices < n and d < max-accomplice-radius ] [
    let candidates sort-on [
      candidate-weight
    ] (nw:turtles-in-radius d) with [ nw:distance-to myself = d ]
    while [ length accomplices < n and not empty? candidates ] [
      let candidate first candidates
      set candidates but-first candidates
      if random-float 1 < [ criminal-tendency ] of candidate [
        set accomplices lput candidate accomplices
      ]
    ]
    set d d + 1
  ]
  report accomplices
end

to commit-crime [ co-offenders ] ; observer command
  ask co-offenders [
    set num-crimes-committed num-crimes-committed + 1
    create-criminal-links-with other co-offenders
  ]
  nw:with-context co-offenders criminal-links [
    ask last nw:get-context [ set num-co-offenses num-co-offenses + 1 ]
  ]
end

to get-caught [ co-offenders ]
  ask co-offenders [
    set breed prisoners
    set sentence-countdown random-poisson 3 * ticks-per-year
    ask my-job-links [ die ]
    ask my-school-attendance-links [die ]
    ask my-professional-links [ die ]
    ask my-school-links [ die ]
    ; we keep the friendship links for the moment
  ]
end

to-report candidate-weight ; person reporter
  let r ifelse-value [ oc-member? ] of myself [ oc-embeddedness ] [ 0 ]
  report -1 * (social-proximity-with myself + r)
end

to-report criminal-tendency ; person reporter
  report 0.05 ; TODO
end

to-report social-proximity-with [ target ] ; person reporter
  report random-float 1 ; TODO
end

to-report oc-embeddedness ; person reporter
  if cached-oc-embeddedness = nobody [
    ; only calculate oc-embeddedness if we don't have a cached value
    set cached-oc-embeddedness 0 ; start with an hypothesis of 0
    let agents nw:turtles-in-radius oc-embeddedness-radius
    let oc-members agents with [ oc-member? ]
    if any? other oc-members [
      update-meta-links agents
      nw:with-context agents meta-links [
        set cached-oc-embeddedness (
          sum [ 1 / nw:weighted-distance-to myself dist ] of other oc-members /
          sum [ 1 / nw:weighted-distance-to myself dist ] of other agents
        )
      ]
    ]
  ]
  report cached-oc-embeddedness
end

to-report number-of-accomplices
  ; pick a group size from the num. co-offenders distribution
  ; and substract one to get the number of accomplices
  report (first rnd:weighted-one-of-list num-co-offenders-dist last) - 1
end

to update-meta-links [ agents ]
  nw:with-context agents links [ ; limit the context to the agents in the radius of interest
    ask agents [
      ask other nw:turtles-in-radius 1 [
        create-meta-link-with myself [ ; if that link already exists, it won't be re-created
          let w 0
          if [ family-link-with other-end ] of myself       != nobody [ set w w + 1 ]
          if [ friendship-link-with other-end ] of myself   != nobody [ set w w + 1 ]
          if [ school-link-with other-end ] of myself       != nobody [ set w w + 1 ]
          if [ professional-link-with other-end ] of myself != nobody [ set w w + 1 ]
          if [ criminal-link-with other-end ] of myself     != nobody [
            set w w + [ num-co-offenses ] of [ criminal-link-with other-end ] of myself
          ]
          set dist 1 / w ; the distance cost of the link is the inverse of its weight
        ]
      ]
    ]
  ]
end

to load-model
  let model-file-name user-file
  if is-string? model-file-name[
     let file-ext-position position ".world" model-file-name
     ifelse is-number? file-ext-position [import-world model-file-name]
                                         [user-message "the file must have the extension .world"]
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
400
10
1083
694
-1
-1
20.455
1
10
1
1
1
0
0
0
1
-16
16
-16
16
1
1
1
ticks
30.0

BUTTON
15
215
130
248
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
15
15
260
48
num-non-oc-persons
num-non-oc-persons
1
10000
100.0
1
1
NIL
HORIZONTAL

MONITOR
265
245
375
290
NIL
count jobs
17
1
11

BUTTON
265
160
375
235
move nodes
  if mouse-down? [\n    let candidate min-one-of turtles [distancexy mouse-xcor mouse-ycor]\n    if [distancexy mouse-xcor mouse-ycor] of candidate < 1 [\n      ;; The WATCH primitive puts a \"halo\" around the watched turtle.\n      watch candidate\n      while [mouse-down?] [\n        ;; If we don't force the view to update, the user won't\n        ;; be able to see the turtle moving around.\n        display\n        ;; The SUBJECT primitive reports the turtle being watched.\n        ask subject [ setxy mouse-xcor mouse-ycor ]\n      ]\n      ;; Undoes the effects of WATCH.  Can be abbreviated RP.\n      reset-perspective\n    ]\n  ]
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

SLIDER
15
330
260
363
base-opportunity-rate
base-opportunity-rate
0
10
0.1
0.1
1
NIL
HORIZONTAL

SLIDER
15
365
260
398
mean-accomplices-needed
mean-accomplices-needed
0
10
0.1
0.1
1
NIL
HORIZONTAL

INPUTBOX
15
90
260
150
data-folder
palermo/data/
1
0
String

SWITCH
265
50
380
83
output?
output?
0
1
-1000

MONITOR
265
295
375
340
NIL
count links
17
1
11

BUTTON
135
215
260
248
NIL
profile-setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
15
50
260
83
num-education-levels
num-education-levels
1
10
3.0
1
1
NIL
HORIZONTAL

INPUTBOX
265
90
380
150
ticks-per-year
12.0
1
0
Number

SLIDER
15
295
260
328
prob-of-going-to-university
prob-of-going-to-university
0
1
0.1
0.01
1
NIL
HORIZONTAL

BUTTON
15
255
70
288
NIL
go
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

BUTTON
75
255
130
288
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

BUTTON
135
255
260
288
NIL
profile-go
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

OUTPUT
1090
10
1720
695
10

SLIDER
15
400
260
433
max-accomplice-radius
max-accomplice-radius
0
5
2.0
1
1
NIL
HORIZONTAL

SLIDER
15
435
260
468
oc-embeddedness-radius
oc-embeddedness-radius
0
5
2.0
1
1
NIL
HORIZONTAL

CHOOSER
15
155
260
200
operation
operation
"Aemilia" "Crimine" "Infinito" "Minotauro"
0

SLIDER
15
470
260
503
probability-of-getting-caught
probability-of-getting-caught
0
1
0.05
0.05
1
NIL
HORIZONTAL

MONITOR
265
345
375
390
NIL
count prisoners
17
1
11

BUTTON
265
15
382
48
NIL
load-model
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
265
400
375
445
NIL
ticks
17
1
11

@#$#@#$#@
## WHAT IS IT?

(a general understanding of what the model is trying to show or explain)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

house colonial
false
0
Rectangle -7500403 true true 270 75 285 255
Rectangle -7500403 true true 45 135 270 255
Rectangle -16777216 true false 124 195 187 256
Rectangle -16777216 true false 60 195 105 240
Rectangle -16777216 true false 60 150 105 180
Rectangle -16777216 true false 210 150 255 180
Line -16777216 false 270 135 270 255
Polygon -7500403 true true 30 135 285 135 240 90 75 90
Line -16777216 false 30 135 285 135
Line -16777216 false 255 105 285 135
Line -7500403 true 154 195 154 255
Rectangle -16777216 true false 210 195 255 240
Rectangle -16777216 true false 135 150 180 180

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Polygon -7500403 true true 30 30 270 30 270 270 30 270 30 150 60 150 60 240 240 240 240 60 60 60 60 150 30 150 30 30 60 45

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.0.4
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
1
@#$#@#$#@
