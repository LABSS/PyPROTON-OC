package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCJobTest extends OCModelSuite {

  // note that persons have a birth tick, not an age (age is a reporter)
  // thus, after the tick, a person can be just turned 65 but not retired yet (it will be after the go)
  // that's why we use age > retirement-age and not >=.
  test("People should not work underage ") { ws =>
    ws.cmd("""
      set num-non-oc-persons 1000
      set operation "Aemilia"
      setup
      """
    )
    ws.rpt("any? persons with [ any? job-link-neighbors and age < 18 ] ") shouldBe false
    ws.cmd("repeat 2 * ticks-per-year [ go ]")
    ws.rpt("any? persons with [ any? job-link-neighbors and age < 18 ] ") shouldBe false
  }
}
