package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCNetTests extends OCModelSuite {

  test("General coherency of network structure") { ws =>
    ws.cmd("""
      set num-persons 3000
      set intervention "disruptive"
      setup
      """
    )
    for (fid <- 1 to 36) {
      println(fid)
      ws.cmd("go")
      ws.cmd("nw:set-context all-persons person-links")
      // general coherency checks
      ws.rpt("""
        all? all-persons [ count other (turtle-set nw:turtles-in-radius 1 nw:turtles-in-reverse-radius 1) = count person-link-neighbors ]
        """) shouldBe true
    }
  }
}
/*
to show-calc-degree-correction-for-bosses
  let gang persons with [ oc-member? ]
  if any? gang [
    let to-sum []
    ask gang [
      let n count person-link-neighbors with [ oc-member? ]
      set to-sum lput ((n / (n + 1)) ^ 2) to-sum
    ]
    show word "sum: "  to-sum
    let p-mean mean [ probability-of-getting-caught ] of gang
    set degree-correction-for-bosses p-mean / mean to-sum
    show  [(list degree-correction-for-bosses ((OC-repression-prob turtle-set self) * degree-correction-for-bosses)
      count person-link-neighbors with [ oc-member? ] ) ] of gang
    show max [ (OC-repression-prob turtle-set self) ] of gang
    show min [ (OC-repression-prob turtle-set self) ] of gang
    show sum [ probability-of-getting-caught ] of gang
    show sum [ (OC-repression-prob turtle-set self) ] of gang
  ]
end
*/
