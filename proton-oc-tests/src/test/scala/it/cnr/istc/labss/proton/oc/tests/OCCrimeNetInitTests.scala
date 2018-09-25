package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCCrimeNetInitTests extends OCModelSuite {

  
  test("All OC links have weight >= 1") { ws =>
    ws.cmd("setup")
    ws.rpt("all? criminal-links [num-co-offenses >= 1]") shouldBe true
  }

}
