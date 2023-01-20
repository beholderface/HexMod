package at.petrak.hexcasting.common.casting.operators.math.trig

import at.petrak.hexcasting.api.casting.ConstMediaAction
import at.petrak.hexcasting.api.casting.asActionResult
import at.petrak.hexcasting.api.casting.eval.CastingContext
import at.petrak.hexcasting.api.casting.getDoubleBetween
import at.petrak.hexcasting.api.casting.iota.Iota
import kotlin.math.acos

object OpArcCos : ConstMediaAction {
    override val argc: Int
        get() = 1

    override fun execute(args: List<Iota>, ctx: CastingContext): List<Iota> {
        val value = args.getDoubleBetween(0, -1.0, 1.0, argc)
        return acos(value).asActionResult
    }
}
