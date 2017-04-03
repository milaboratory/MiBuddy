name := "mibuddy-web"

version := "1.0-SNAPSHOT"

scalaVersion := "2.12.1"

lazy val root = project.
  enablePlugins(ScalaJSPlugin)

libraryDependencies += "org.scalatest" %%% "scalatest" % "3.0.1" % "test"

scalacOptions ++= Seq("-Xfatal-warnings", "-Xlog-implicits")