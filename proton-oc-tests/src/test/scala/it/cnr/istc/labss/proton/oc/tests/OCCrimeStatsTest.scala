package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCCrimeStatsTest extends OCModelSuite {

  test("Stats on crime accurate to one SD") { ws =>
    ws.cmd("""
      set num-persons 2000
      setup
      """)
    for (fid <- 1 to 20) {
      println(fid)
      ws.cmd("go")
      ws.rpt("""
      reduce [ [ i j ] -> i and j ] runresult [
      ->  map [
        cell ->
        ifelse-value ((any? all-persons with [
          age > last cell and age <= first last table:get c-range-by-age-and-sex cell and male? = first cell
        ]) and (sum [ num-crimes-committed ] of all-persons with [
          age > last cell and age <= first last table:get c-range-by-age-and-sex cell and male? = first cell
        ] > 0))
        [
          abs last last table:get c-range-by-age-and-sex cell * ticks -
          (mean [ num-crimes-committed ] of all-persons with [
            age > last cell and age <= first last table:get c-range-by-age-and-sex cell and male? = first cell
          ] ) < standard-deviation [ num-crimes-committed ] of all-persons with [
            age > last cell and age <= first last table:get c-range-by-age-and-sex cell and male? = first cell
          ]
        ] [
          true
        ]
      ] table:keys c-range-by-age-and-sex
    ] any? persons with [ any? job-link-neighbors and age < 18 ] ") shouldBe false
    """) shouldBe true
    } 
  } 
}
