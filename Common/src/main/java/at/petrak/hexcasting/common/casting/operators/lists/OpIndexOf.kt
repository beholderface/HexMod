package at.petrak.hexcasting.common.casting.operators.lists

import at.petrak.hexcasting.api.casting.ConstMediaAction
import at.petrak.hexcasting.api.casting.asActionResult
import at.petrak.hexcasting.api.casting.eval.CastingContext
import at.petrak.hexcasting.api.casting.getList
import at.petrak.hexcasting.api.casting.iota.Iota

object OpIndexOf : ConstMediaAction {
    override val argc: Int
        get() = 2

    override fun execute(args: List<Iota>, ctx: CastingContext): List<Iota> {
        val list = args.getList(0, argc).toMutableList()
        val value = args[1]
        return list.indexOfFirst { Iota.tolerates(value, it) }.asActionResult
    }
}
