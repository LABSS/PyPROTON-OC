package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCInterventionTest extends OCModelSuite {

  test("Intervention on OC families") { ws =>
    ws.cmd("""
      set num-persons 550
      show "setup"
      setup
      ask all-persons [ set oc-member? false ]; ops, no crime.
      let agelist (range 0 (12 * 4) 4)
      show "setup ended"
      create-persons 1 [
        set oc-member? true
        set birth-tick -1 * ticks-per-year * 50
        set male? one-of list true false
      ]
      show "first of:"
      let kingpin one-of persons with [ oc-member? ]
      show [who] of kingpin
      create-persons 12 [
        set oc-member? false
        set birth-tick -1 * one-of agelist * ticks-per-year
        set agelist remove age agelist
        create-family-links-with turtle-set kingpin
        set male? one-of list true false
      ]
      let the-family (turtle-set kingpin [ family-link-neighbors ] of kingpin)
      let baby one-of the-family with [ age = 0 ]
      show [who] of baby
      ask the-family [ create-family-links-with other the-family ]
      ask the-family with [ age = 40 ] [ set oc-member? true ]
      set targets-addressed-percent 100
      ; the only oc-family is this one
      family-intervene
      show "intervention"
      """)
    // the baby is (one-of persons with [ age = 0  and propensity = 0])
    ws.rpt("""
      sum [ count friendship-link-neighbors ] of ([ family-link-neighbors ] of (one-of persons with [ age = 0  and propensity = 0]))
    """) shouldBe 40
    ws.rpt("""
      count [ family-link-neighbors ] of (one-of persons with [ age = 0  and propensity = 0])
    """) shouldBe 10
    ws.rpt("""
      sum [ count job-link-neighbors ] of (one-of [ family-link-neighbors ] of (persons with [ age = 0  and propensity = 0]))
    """) shouldBe 7
    ws.rpt("""
      sum [ max-education-level ] of (one-of [ family-link-neighbors ] of (persons with [ age = 0  and propensity = 0]))
    """) shouldBe 6
  }  

  
}
