package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCCrimeStatsTest extends OCModelSuite {

  test("Stats on crime accurate to two SD") { ws =>
    ws.cmd("""
      set num-persons 1500
      setup
      """)
    for (fid <- 1 to 20) {
      ws.cmd("go")
      ws.rpt("""
        reduce [ [ i j ] -> i and j ] runresult [
          ->  map [ 
            cell ->
            ifelse-value ((any? all-persons with [
              age > last cell and age <= first last table:get c-range-by-age-and-sex cell and male? = first cell
            ]) and (sum [ num-crimes-committed ] of all-persons with [
              age > last cell and age <= first last table:get c-range-by-age-and-sex cell and male? = first cell
            ] > 0)) [
              abs last last table:get c-range-by-age-and-sex cell * ticks -
              (mean [ num-crimes-committed ] of all-persons with [
              age > last cell and age <= first last table:get c-range-by-age-and-sex cell and male? = first cell
            ] ) < 2 * standard-deviation [ num-crimes-committed ] of all-persons with [
              age > last cell and age <= first last table:get c-range-by-age-and-sex cell and male? = first cell
            ]
            ] [
              true
            ]
          ] table:keys c-range-by-age-and-sex
        ]
      """) shouldBe true
      println(fid)
    } 
  } 
}
/* helper that could be reintroduced in case of need
to crime-stats
  foreach table:keys c-range-by-age-and-sex [ cell ->
    let value last table:get c-range-by-age-and-sex cell
    show (word
      first cell ", "
      last cell ", "
      first value ", "
      (last value * ticks) ", "
      (mean [ num-crimes-committed ] of all-persons with [
        age > last cell and age <= first value and male? = first cell
      ])
    )
  ]
end
*/

