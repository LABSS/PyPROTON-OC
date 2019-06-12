package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCProfiler extends OCModelSuite {

  test("Running the profiler") { ws =>
    ws.cmd("""
      profile-go
      """
    )
  }
}
