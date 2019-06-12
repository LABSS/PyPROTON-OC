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
      ws.rpt("any? persons with [ my-job != nobody and age < 18 ] ") shouldBe false
      // unemployed stay so
      ws.rpt("any? persons with [ job-level = 1 and my-job != nobody ] ") shouldBe false
      // job levels are coherent
      ws.rpt("""
        all? persons with [ my-job != nobody ] [ job-level = [ job-level ] of my-job ]
      """) shouldBe true      
    }
  }
}
