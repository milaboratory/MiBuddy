package com.milaboratory.mibuddy

import com.milaboratory.mibuddy.YAML.YList

import scala.math.Ordering

//import com.milaboratory.mibuddy.YAML.YList

class YAMLTest extends UnitSpec {
  "YAML nodes" should "have fixed ordering" in {
    YAML.list(YAML.string("1") :: YAML.string("3") :: YAML.string("5") :: Nil) shouldEqual
      YAML.list(YAML.string("3") :: YAML.string("5") :: YAML.string("1") :: Nil)
  }
}
