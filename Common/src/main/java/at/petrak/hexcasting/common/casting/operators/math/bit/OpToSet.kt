package at.petrak.hexcasting.common.casting.operators.math.bit

import at.petrak.hexcasting.api.casting.ConstMediaAction
import at.petrak.hexcasting.api.casting.asActionResult
import at.petrak.hexcasting.api.casting.eval.CastingContext
import at.petrak.hexcasting.api.casting.getList
import at.petrak.hexcasting.api.casting.iota.Iota

object OpToSet : ConstMediaAction {
    override val argc = 1

    override fun execute(args: List<Iota>, ctx: CastingContext): List<Iota> {
        val list = args.getList(0, argc)
        val out = mutableListOf<Iota>()

        for (subiota in list) {
            if (out.none { Iota.tolerates(it, subiota) }) {
                out.add(subiota)
            }
        }

        return out.asActionResult
    }
}
