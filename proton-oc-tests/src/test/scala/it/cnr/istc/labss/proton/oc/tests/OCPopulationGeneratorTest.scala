package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCPopulationGeneratorTest extends OCModelSuite {

  test("Families have uniform wealth at start") { ws =>
    ws.cmd("""
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
      """
    )
    // we stop just before adding extra siblings; that means family and households are the same
    ws.rpt("all? persons [all? household-link-neighbors [ wealth-level = [ wealth-level ] of myself ] ]") shouldBe true
    ws.rpt("all? persons [all? family-link-neighbors [ wealth-level = [ wealth-level ] of myself ] ]") shouldBe true
    ws.rpt("all? persons [all? family-link-neighbors [ household-link-neighbor? myself ] ]") shouldBe true
    ws.rpt("all? persons [all? household-link-neighbors [ member? myself family-link-neighbors ] ]") shouldBe true
  }
}
