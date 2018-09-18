lazy val root = (project in file(".")).
  settings(
    inThisBuild(List(
      organization := "it.cnr.istc.labss",
      scalaVersion := "2.12.4"
    )),
    name := "proton-oc-tests"
  )

resolvers += Resolver.bintrayRepo("netlogo", "NetLogo-JVM")

libraryDependencies ++= Seq(
  "org.scalatest" %% "scalatest" % "3.0.5" % Test,
  "org.nlogo" % "netlogo" % "6.0.4" % Test
)

lazy val downloadFromZip = taskKey[Unit]("Download zipped extensions and extract them to ./extensions")

downloadFromZip := {
  if (java.nio.file.Files.notExists(new File("extensions").toPath())) {
    println("Downloading extensions...")
    val baseURL = "https://raw.githubusercontent.com/NetLogo/NetLogo-Libraries/6.0/extensions/"
    val extensions = List(
      "nw" -> "nw-3.7.5.zip", "table" -> "table-1.3.0.zip",
      "csv" -> "csv-1.1.0.zip", "profiler" -> "profiler-1.1.0.zip"
    )
    for ((extension, file) <- extensions) {
      println("Downloading " + baseURL + file)
      IO.unzipURL(new URL(baseURL + file), new File("extensions/" + extension))
    }
  }
}

compile in Test <<= (compile in Test).dependsOn(downloadFromZip)

fork in Test := true

javaOptions in test += "-Xms512M -Xmx3000M -Xss1M -XX:+UseConcMarkSweepGC -XX:NewRatio=8"
