package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCEmbeddednessTests extends OCModelSuite {

  def setup(ws: HeadlessWorkspace): Unit = {
    ws.cmd("""
      clear-all
      nw:set-context persons links
      set oc-embeddedness-radius 2
    """)
  }

  test("A single non-OC person") { ws =>
    setup(ws)
    ws.cmd("""
      create-persons 1 [
        set cached-oc-embeddedness nobody
        set oc-member? false
      ]
    """)
    ws.rpt("[ oc-embbededness ] of person 0") shouldBe 0
  }

  test("A single OC person") { ws =>
    setup(ws)
    ws.cmd("""
      create-persons 1 [
        set cached-oc-embeddedness nobody
        set oc-member? true
      ]
    """)
    ws.rpt("[ oc-embbededness ] of person 0") shouldBe 0
  }

  test("A single non-OC person with one family OC member") { ws =>
    setup(ws)
    ws.cmd("""
      create-persons 2 [
        set cached-oc-embeddedness nobody
      ]
      ask person 0 [ set oc-member? false ]
      ask person 1 [ set oc-member? true ]
      ask person 0 [ create-family-link-with person 1 ]
    """)
    ws.rpt("[ oc-embbededness ] of person 0") shouldBe 1
    ws.rpt("[ w ] of meta-links") shouldBe Seq(1.0).toLogoList
  }

  test("A non-OC person with its family being OC member") { ws =>
    setup(ws)
    ws.cmd("""
      create-persons 11 [
        set cached-oc-embeddedness nobody
        set oc-member? false
      ]
      ask person 0 [
        ask n-of 5 other persons [ set oc-member? true ]
      ]
      ask person 0 [ create-family-links-with other persons ]
    """)
    ws.rpt("[ oc-embbededness ] of person 0") shouldBe 0.5
    ws.rpt("sort [ w ] of meta-links") shouldBe Seq.fill(10)(1.0).toLogoList
  }

  test("A non-OC person with one OC member at distance 2") { ws =>
    setup(ws)
    ws.cmd("""
      create-persons 3 [
        set cached-oc-embeddedness nobody
        set oc-member? false
      ]
      ask person 0 [ create-family-link-with person 1 ]
      ask person 1 [ create-family-link-with person 2 ]
      ask person 2 [ set oc-member? true ]
    """)
    ws.rpt("[ oc-embbededness ] of person 0") shouldBe (1.0 / 3.0)
    ws.rpt("sort [ w ] of meta-links") shouldBe Seq(1.0, 1.0).toLogoList
  }

  test("A non-OC person with one double link to an OC member") { ws =>
    setup(ws)
    ws.cmd("""
      create-persons 3 [
        set cached-oc-embeddedness nobody
        set oc-member? false
      ]
      ask person 0 [
        create-family-link-with person 1
        create-family-link-with person 2
        create-friendship-link-with person 2
      ]
      ask person 2 [ set oc-member? true ]
    """)
    ws.rpt("[ oc-embbededness ] of person 0") shouldBe (2.0 / 3.0)
    ws.rpt("sort [ w ] of meta-links") shouldBe Seq(0.5, 1.0).toLogoList
  }

  test("A non-OC person with one double link to a non-OC member") { ws =>
    setup(ws)
    ws.cmd("""
      create-persons 3 [
        set cached-oc-embeddedness nobody
        set oc-member? false
      ]
      ask person 0 [
        create-family-link-with person 1
        create-friendship-link-with person 1
        create-friendship-link-with person 2
      ]
      ask person 2 [ set oc-member? true ]
    """)
    ws.rpt("[ oc-embbededness ] of person 0") shouldBe (1.0 / 3.0)
    ws.rpt("sort [ w ] of meta-links") shouldBe Seq(0.5, 1.0).toLogoList
  }

  test("A non-OC person with a strong co-offending link to an OC member") { ws =>
    setup(ws)
    ws.cmd("""
      create-persons 3 [
        set cached-oc-embeddedness nobody
        set oc-member? false
      ]
      ask person 0 [
        create-family-link-with person 1
        create-criminal-link-with person 2 [ set num-co-offenses 4 ]
      ]
      ask person 2 [ set oc-member? true ]
    """)
    ws.rpt("[ oc-embbededness ] of person 0") shouldBe (4.0 / 5.0)
    ws.rpt("sort [ w ] of meta-links") shouldBe Seq(0.25, 1.0).toLogoList
  }

  test("A non-OC person with all types of links") { ws =>
    setup(ws)
    ws.cmd("""
      create-persons 6 [
        set cached-oc-embeddedness nobody
        set oc-member? false
      ]
      ask person 0 [
        create-family-link-with person 1
        create-friendship-link-with person 2
        create-professional-link-with person 3
        create-school-link-with person 4
        create-criminal-link-with person 5 [ set num-co-offenses 4 ]
      ]
      ask person 5 [ set oc-member? true ]
    """)
    ws.rpt("[ oc-embbededness ] of person 0") shouldBe 0.5
    ws.rpt("sort [ w ] of meta-links") shouldBe Seq(0.25, 1.0, 1.0, 1.0, 1.0).toLogoList
  }

}
