package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCSchoolTest extends OCModelSuite {

  // note that persons have a birth tick, not an age (age is a reporter)
  // thus, after the tick, a person can be just turned 65 but not retired yet (it will be after the go)
  // that's why we use age > retirement-age and not >=.
  test("People should be in schools of the correct education level. Nobody should be both at work and in school. ") { ws =>
    ws.cmd("""
      set num-non-oc-persons 2000
      set operation "Aemilia"
      setup
      """
    )
    ws.rpt("not any? persons with [ any? school-attendance-link-neighbors and any? job-link-neighbors ]") shouldBe true 
    ws.rpt("all? persons [ not any? school-attendance-link-neighbors or education-level = ([ education-level ] of one-of school-attendance-link-neighbors) - 1 ] ") shouldBe true
    ws.rpt("all? all-persons [ not any? school-attendance-link-neighbors or ([ education-level ] of one-of school-attendance-link-neighbors = possible-school-level and education-level = possible-school-level - 1) ]") shouldBe true
    println("Initial test done, running for three years:")
    var fid = 0
    for (fid <- 1 to 36) {
        //ws.cmd("repeat 3 * ticks-per-year [ go ]")
      println(fid)
      ws.cmd("go")
      ws.rpt("not any? persons with [ any? school-attendance-link-neighbors and any? job-link-neighbors ]") shouldBe true 
      ws.rpt("all? persons [ not any? school-attendance-link-neighbors or education-level = ([ education-level ] of one-of school-attendance-link-neighbors) - 1 ] ") shouldBe true 
      ws.rpt("""all? persons [ 
        not any? school-attendance-link-neighbors or 
        education-level = (possible-school-level - 1) or 
        (birth-tick mod ticks-per-year = 0 and
          (age > 25 or 
          education-level = (possible-school-level - 2))) 
      ]""") shouldBe true   
    }
  }
}
