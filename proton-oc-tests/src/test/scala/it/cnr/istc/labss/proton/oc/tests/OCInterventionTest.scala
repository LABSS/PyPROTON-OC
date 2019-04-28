package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCInterventionTest extends OCModelSuite {

  test("Intervention on OC families") { ws =>
    ws.cmd("""
      set num-persons 550
      setup
      ask all-persons [ set oc-member? false ]
      let agelist (range 0 (12 * 4) 4)
      create-persons 1 [
        set oc-member? true
        set birth-tick -1 * ticks-per-year * 50
        set male? true
        set c-t-fresh? false
      ]
      let kingpin one-of persons with [ oc-member? ]
      show [ who ] of kingpin
      create-persons 12 [
        set oc-member? false
        set birth-tick -1 * one-of agelist * ticks-per-year
        set agelist remove age agelist
        create-offspring-link-from kingpin
        set male? true
        set c-t-fresh? false
      ]
      let the-family ([ family-link-neighbors ] of kingpin)
      let baby one-of the-family with [ age = 0 ]
      show [who] of baby
      ask the-family [ create-sibling-links-with other the-family ]
      set targets-addressed-percent 100
      set family-intervention "remove-if-OC-member"
      family-intervene
      """)
    // the baby is (one-of persons with [ age = 0  and propensity = 0])
    ws.rpt("""
      sum [ count friendship-link-neighbors ] of ([ family-link-neighbors ] of (one-of persons with [ age = 0  and propensity = 0])) >= 40
    """) shouldBe true
    ws.rpt("""
      count [ family-link-neighbors ] of (one-of persons with [ age = 16  and propensity = 0])
    """) shouldBe 11
    ws.rpt("""
      sum [ count job-link-neighbors ] of (one-of [ family-link-neighbors ] of (persons with [ age = 0  and propensity = 0]))
    """) shouldBe 8
    ws.rpt("""
      sum [ max-education-level ] of (one-of [ family-link-neighbors ] of (persons with [ age = 0  and propensity = 0]))
    """) shouldBe 6
  }  

test("Educational intervention works.") { ws =>
    ws.cmd("""
      set num-persons 1000
      setup
      set targets-addressed-percent 0
      set family-intervention "none"
      set social-support "none"
      set welfare-support "none"
      repeat 5 [ go ]
      set family-intervention "none"
      set social-support "educational"
      set welfare-support "none"      
      set ticks-between-intervention 2
      set targets-addressed-percent 20
      """
    )
    var targets = """
      mean [ max-education-level ] 
      of all-persons with [ age <= 18 and age >= 12 and any? school-link-neighbors ]
    """
    var before = ws.rpt(targets).asInstanceOf[Number].floatValue    
    ws.cmd("repeat 10 [ socialization-intervene ]")
    var after = ws.rpt(targets).asInstanceOf[Number].floatValue
    after > before shouldBe true
    println("educational done")
    // second test
    ws.cmd("""set social-support "psychological"""")
    targets = """sum [ count my-friendship-links ] of
        all-persons with [ age <= 18 and age >= 12 and any? school-link-neighbors ]
    """
    before = ws.rpt(targets).asInstanceOf[Number].floatValue    
    ws.cmd("repeat 10 [ socialization-intervene ]")
    after = ws.rpt(targets).asInstanceOf[Number].floatValue
    after > before shouldBe true
    println("psychological done")
    // third test
    ws.cmd("""set social-support "more friends"""")
    before = ws.rpt(targets).asInstanceOf[Number].floatValue    
    ws.cmd("repeat 10 [ socialization-intervene ]")
    after = ws.rpt(targets).asInstanceOf[Number].floatValue
    after > before shouldBe true
    println("more friends done")
  } 
  
}
