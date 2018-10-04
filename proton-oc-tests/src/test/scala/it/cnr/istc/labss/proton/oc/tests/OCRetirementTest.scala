package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCRetirementTest extends OCModelSuite {

  // note that persons have a birth tick, not an age (age is a reporter)
  // thus, after the tick, a person can be just turned 65 but not retired yet (it will be after the go)
  // that's why we use age > retirement-age and not >=.
  test("Old people do not have a job, Young people are not retired, Retired people are old") { ws =>
    ws.cmd("setup")
    ws.rpt("not any? persons with [age > retirement-age and any? my-professional-links]") shouldBe true
    ws.rpt("not any? persons with [age < retirement-age and retired?]") shouldBe true
    ws.rpt("not any? persons with [age > retirement-age and not retired?] ") shouldBe true  
  }
  test("Same, but after a while") { ws =>
    ws.cmd("setup")
    ws.cmd("go")
    ws.cmd("go")
    ws.cmd("go")
    ws.rpt("not any? persons with [age > retirement-age and any? my-professional-links]") shouldBe true
    ws.rpt("not any? persons with [age < retirement-age and retired?]") shouldBe true
    ws.rpt("not any? persons with [age > retirement-age and not retired?] ") shouldBe true  
  }
}
