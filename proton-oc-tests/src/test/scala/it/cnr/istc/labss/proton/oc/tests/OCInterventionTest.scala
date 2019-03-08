package it.cnr.istc.labss.proton.oc.tests

import org.nlogo.headless.HeadlessWorkspace
import org.nlogo.core.LogoList
import org.nlogo.api.ScalaConversions.RichSeq

class OCInterventionTest extends OCModelSuite {

  test("Educational intervention works.") { ws =>
    ws.cmd("""
      set num-persons 1500
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

  test("Intervention on OC families") { ws =>
    ws.cmd("""
      set num-persons 500
      setup
      ask all-persons [ set oc-member? false ]; ops
      let agelist list (range 0 (12 * 4) 4) 
      create-persons 1 [
        set oc-member? true
        set birth-year -50
      ]
      let kingpin one-of persons with [ oc-member? ]
      create-persons 12 [
        set oc-member? false
        set birth-year -1 * one-of agelist
        set agelist remove-value age agelist
        create-family-links-with kingpin
      ]
      ask family-link-neighbors

      ask person 0 [
        ask n-of 5 other persons [ set oc-member? true ]
      ]
      ask person 0 [ create-family-links-with other persons ]
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
