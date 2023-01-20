package at.petrak.hexcasting.common.casting.operators.stack

import at.petrak.hexcasting.api.casting.Action
import at.petrak.hexcasting.api.casting.OperationResult
import at.petrak.hexcasting.api.casting.eval.CastingContext
import at.petrak.hexcasting.api.casting.eval.vm.SpellContinuation
import at.petrak.hexcasting.api.casting.iota.DoubleIota
import at.petrak.hexcasting.api.casting.iota.Iota

object OpStackSize : Action {
    override fun operate(
        continuation: SpellContinuation,
        stack: MutableList<Iota>,
        ravenmind: Iota?,
        ctx: CastingContext
    ): OperationResult {
        stack.add(DoubleIota(stack.size.toDouble()))
        return OperationResult(continuation, stack, ravenmind, listOf())
    }
}
