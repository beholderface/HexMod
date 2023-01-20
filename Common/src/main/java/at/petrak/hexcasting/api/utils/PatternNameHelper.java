package at.petrak.hexcasting.api.utils;

import at.petrak.hexcasting.common.casting.PatternRegistryManifest;
import at.petrak.hexcasting.api.casting.eval.SpecialPatterns;
import at.petrak.hexcasting.api.casting.iota.PatternIota;
import at.petrak.hexcasting.api.casting.math.HexPattern;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;

public class PatternNameHelper {

    public static Component representationForPattern(HexPattern pattern) {
        if (pattern.sigsEqual(SpecialPatterns.CONSIDERATION)) {
            return Component.translatable("hexcasting.spell.hexcasting:escape").withStyle(ChatFormatting.LIGHT_PURPLE);
        } else if (pattern.sigsEqual(SpecialPatterns.INTROSPECTION)) {
            return Component.translatable("hexcasting.spell.hexcasting:open_paren").withStyle(ChatFormatting.LIGHT_PURPLE);
        } else if (pattern.sigsEqual(SpecialPatterns.RETROSPECTION)) {
            return Component.translatable("hexcasting.spell.hexcasting:close_paren").withStyle(ChatFormatting.LIGHT_PURPLE);
        }

        var action = PatternRegistryManifest.lookupPatternByShape(pattern);
        if (action != null) {
            return action.getDisplayName();
        }

        return new PatternIota(pattern).display(); // TODO: this should be merged into iota.display once Great Spells
        // can be identified by name
    }
}
