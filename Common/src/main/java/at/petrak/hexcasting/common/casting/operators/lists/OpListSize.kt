package at.petrak.hexcasting.common.casting.operators.lists

import at.petrak.hexcasting.api.casting.ConstMediaAction
import at.petrak.hexcasting.api.casting.asActionResult
import at.petrak.hexcasting.api.casting.eval.CastingContext
import at.petrak.hexcasting.api.casting.getList
import at.petrak.hexcasting.api.casting.iota.Iota

// it's still called beancounter's distillation in my heart
object OpListSize : ConstMediaAction {
    override val argc = 1
    override fun execute(args: List<Iota>, ctx: CastingContext): List<Iota> {
        return args.getList(0, argc).toList().size.asActionResult // mmm one-liner
    }
}
