package it.cnr.istc.labss.proton.oc

import org.nlogo.headless.HeadlessWorkspace
import org.scalatest.BeforeAndAfter
import org.scalatest.fixture.FunSuite
import org.scalatest.Matchers
import org.scalactic.Snapshots.snap

package object tests {

  org.nlogo.headless.Main.setHeadlessProperty()

  trait OCModelSuite extends FunSuite with Matchers with BeforeAndAfter {

    type FixtureParam = HeadlessWorkspace

    def withFixture(test: OneArgTest) = {
      val workspace = HeadlessWorkspace.newInstance
      workspace.open("../PROTON-OC.nlogo")
      try {
        withFixture(test.toNoArgTest(workspace))
      } catch {
        case ex: Serializable => throw ex
        case ex: Exception =>
          // ScalaTest chokes on non-Serializable exceptions
          // so we wrap it in a generic exception if needed
          val msg = ex.getMessage + "\n" +
            ex.getStackTrace.map("  " + _).mkString("\n")
          throw new Exception(msg)
      } finally {
        workspace.dispose()
      }
    }

    implicit class RichWorkspace(ws: HeadlessWorkspace) {
      private def concat(str: String): String =
        str.lines.map(_.trim).filter(_.nonEmpty).mkString(" ")
      def cmd(str: String): Unit = ws.command(concat(str))
      def rpt(str: String): AnyRef = ws.report(concat(str))
      def show(str: String): Unit = println(concat(str) + " : " + rpt(str))
    }
  }

}
