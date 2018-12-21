package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCBigCrimesSmallFishTest extends OCModelSuite {

  // note that persons have a birth tick, not an age (age is a reporter)
  // thus, after the tick, a person can be just turned 65 but not retired yet (it will be after the go)
  // that's why we use age > retirement-age and not >=.
  test("A large crime organized by a small fish is reported.") { ws =>
    ws.cmd("""
      set num-non-oc-persons 100
      set operation "Aemilia"
      set retirement-age 65
      set mean-accomplices-needed 6.0
      setup
      repeat 50 * ticks-per-year [ go ]
      """
    )
    ws.rpt("big-crime-from-small-fish > 0") shouldBe true
  }
}