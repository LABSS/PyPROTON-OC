package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCPopulationGeneratorTest extends OCModelSuite {

  test("Families have coherent status at start") { ws =>
    ws.cmd("""
      set num-persons 2000
      clear-all
      reset-ticks ; so age can be computed
      load-stats-tables
      set facilitator-fails 0
      set facilitator-crimes 0
      nw:set-context persons links
      ask patches [ set pcolor white ]
      setup-default-shapes
      setup-education-levels
      init-breed-colors
      setup-persons-and-friendship
      generate-households
    """)
    // we stop just before adding extra siblings; that means family and households are the same
    ws.rpt("all? persons [all? household-link-neighbors [ wealth-level = [ wealth-level ] of myself ] ]") shouldBe true
    ws.rpt("all? persons [all? family-link-neighbors [ wealth-level = [ wealth-level ] of myself ] ]") shouldBe true
    ws.rpt("all? persons [all? family-link-neighbors [ household-link-neighbor? myself ] ]") shouldBe true
    ws.rpt("all? persons [all? household-link-neighbors [ member? myself family-link-neighbors ] ]") shouldBe true
    // nobody shoud have more than one father and one mather
    ws.rpt("""
        all? persons [ count in-offspring-link-neighbors with [ not male? ] <= 1 ]
    """) shouldBe true
    ws.rpt("""
        all? persons [ count in-offspring-link-neighbors with [     male? ] <= 1 ]
    """) shouldBe true
     // the brother of my brother is my brother
    ws.rpt("""
      all? persons [ all? other (turtle-set [ sibling-link-neighbors ] of sibling-link-neighbors) [ sibling-link-neighbor? myself ] ]
      """) shouldBe true
    // I can only have one link with relatives
    ws.rpt("""
      all? persons [ all? family-link-neighbors [ count link-set sibling-link-with myself + count link-set partner-link-with myself + count link-set offspring-link-with myself  = 1 ] ]
      """) shouldBe true
  }

 test("Families keep coherent status while running") { ws =>
    ws.cmd("""
      set num-persons 1000
      setup
      """
    )
    for (fid <- 1 to 36) {
      println(fid)
      ws.cmd("go")
      // nobody shoud have more than one father and one mather
      ws.rpt("""
          all? persons [ count in-offspring-link-neighbors with [ not male? ] <= 1 ]
      """) shouldBe true
      ws.rpt("""
          all? persons [ count in-offspring-link-neighbors with [     male? ] <= 1 ]
      """) shouldBe true
      // the brother of my brother is my brother
      ws.rpt("""
        all? persons [ all? other (turtle-set [ sibling-link-neighbors ] of sibling-link-neighbors) [ sibling-link-neighbor? myself ] ]
        """) shouldBe true
      // I can only have one link with relatives
      ws.rpt("""
        all? persons [ all? family-link-neighbors [ count link-set sibling-link-with myself + count link-set partner-link-with myself + count link-set offspring-link-with myself  = 1 ] ]
        """) shouldBe true
    }
  }
 
}
