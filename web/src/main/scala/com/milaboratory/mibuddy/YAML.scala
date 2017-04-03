package com.milaboratory.mibuddy

import scala.collection.immutable.SortedMap
import scala.language.implicitConversions
import scala.math.{Ordered, Ordering}

object YAML {

  import Ordering.Implicits._

  def cmp[T](c1: T, c2: T)(implicit ord: Ordering[T]) = ord.compare(c1, c2)

  object Implicit {
    implicit def fromString(string: String): YString = YString(string)

    implicit def fromList(l: List[YAMLNode]): YList = list(l)

    implicit def fromMap(m: Map[String, YAMLNode]): YMap = map(m)
  }

  sealed trait YAMLNode extends Comparable[YAMLNode] {
    private[YAML] def typeOrder: Int
  }

  final case class YList private[YAML](v: List[YAMLNode]) extends YAMLNode {
    private implicit def toList = v

    override private[YAML] def typeOrder: Int = 1

    override def compareTo(that: YAMLNode): Int = that match {
      case t: YList => cmp(v, t.v)
      case t => typeOrder compare t.typeOrder
    }
  }

  def list(list: List[YAMLNode]) = YList(list.sorted)

  final case class YMap(v: SortedMap[String, YAMLNode]) extends YAMLNode {
    private implicit def toMap = v

    override private[YAML] def typeOrder: Int = 2

    override def compareTo(that: YAMLNode): Int = that match {
      case t: YMap => cmp(v.toList, t.v.toList)
      case t => t.typeOrder compare t.typeOrder
    }
  }

  def map(map: Map[String, YAMLNode]) = YMap(SortedMap.empty[String, YAMLNode] ++ map)

  final case class YString(v: String) extends YAMLNode {
    override private[YAML] def typeOrder: Int = 0

    override def compareTo(that: YAMLNode): Int = that match {
      case t: YString =>
        cmp(v, t.v)
      case t => typeOrder compare t.typeOrder
    }
  }

  def string(string: String) = YString(string)
}
