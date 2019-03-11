package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCPopulationGeneratorTest extends OCModelSuite {

  // note that persons have a birth tick, not an age (age is a reporter)
  // thus, after the tick, a person can be just turned 65 but not retired yet (it will be after the go)
  // that's why we use age > retirement-age and not >=.
  test("Families have uniform wealth at start") { ws =>
    ws.cmd("""
      setup
      """
    )
    ws.rpt("all? persons [all? family-link-neighbors [ wealth-level = [ wealth-level ] of myself ] ]") shouldBe true
  }
}
