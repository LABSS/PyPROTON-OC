package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCPersonRedundancyTest extends OCModelSuite {

  test("equivalence between person links and connected links") { ws =>
    ws.cmd("""
      set num-persons 100
      setup
      """)
    for (fid <- 1 to 20) {
      ws.cmd("go")
      ws.rpt("""
        all? (links with [ member? (word breed) [ "sibling-links" "offspring-links" "partner-links" "household-links" "friendship-links" "professional-links" "school-links" ] ]) [ any? person-links with [ both-ends = [ both-ends ] of myself ] ]
      """) shouldBe true
      ws.rpt("""
        all? all-persons [ not any? person-link-neighbors with [ not sibling-link-neighbor? myself  and not offspring-link-neighbor?  myself and not partner-link-neighbor? myself and not household-link-neighbor? myself and not friendship-link-neighbor? myself and not professional-link-neighbor? myself and not school-link-neighbor? myself ] ]
      """) shouldBe true
      println(fid)
    } 
  } 
}
