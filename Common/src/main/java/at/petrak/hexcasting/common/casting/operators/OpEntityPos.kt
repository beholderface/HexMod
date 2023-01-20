package at.petrak.hexcasting.common.casting.operators

import at.petrak.hexcasting.api.casting.ConstMediaAction
import at.petrak.hexcasting.api.casting.asActionResult
import at.petrak.hexcasting.api.casting.eval.CastingContext
import at.petrak.hexcasting.api.casting.getEntity
import at.petrak.hexcasting.api.casting.iota.Iota

class OpEntityPos(val feet: Boolean) : ConstMediaAction {
    override val argc = 1

    override fun execute(args: List<Iota>, ctx: CastingContext): List<Iota> {
        val e = args.getEntity(0, argc)
        ctx.assertEntityInRange(e)
        return (if (this.feet) e.position() else e.eyePosition).asActionResult
    }
}
