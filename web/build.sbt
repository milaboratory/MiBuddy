name := "mibuddy-web"

version := "1.0-SNAPSHOT"

scalaVersion := "2.11.8"

lazy val root = project.
  enablePlugins(ScalaJSPlugin)

libraryDependencies += "org.scalatest" %%% "scalatest" % "3.0.1" % "test"

