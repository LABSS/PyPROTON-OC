package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCJobTest extends OCModelSuite {

  test("Work system stays coherent ") { ws =>
    ws.cmd("""
      set num-persons 1000
      setup
      """
    )
    for (fid <- 1 to 36) {
      println(fid)
      ws.cmd("go")
      // no minors working
      ws.rpt("any? persons with [ any? job-link-neighbors and age < 18 ] ") shouldBe false
      // unemployed stay so
      ws.rpt("any? persons with [ job-level = 1 and any? my-job-links ] ") shouldBe false
      // job levels are coherent
      ws.rpt("""
        all? persons with [ any? my-job-links ] [ job-level = [ job-level ] of one-of job-link-neighbors ]
      """) shouldBe true      
    }
  }
}
