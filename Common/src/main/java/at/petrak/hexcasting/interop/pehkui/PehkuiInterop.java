package at.petrak.hexcasting.interop.pehkui;

import at.petrak.hexcasting.common.casting.PatternRegistryManifest;
import at.petrak.hexcasting.api.casting.math.HexDir;
import at.petrak.hexcasting.api.casting.math.HexPattern;
import net.minecraft.world.entity.Entity;

import static at.petrak.hexcasting.api.HexAPI.modLoc;

public class PehkuiInterop {
    public static void init() {
        try {
            PatternRegistryManifest.mapPattern(HexPattern.fromAngles("aawawwawwa", HexDir.NORTH_WEST),
                modLoc("interop/pehkui/get"), OpGetScale.INSTANCE);
            PatternRegistryManifest.mapPattern(HexPattern.fromAngles("ddwdwwdwwd", HexDir.NORTH_EAST),
                modLoc("interop/pehkui/set"), OpSetScale.INSTANCE);
        } catch (PatternRegistryManifest.RegisterPatternException e) {
            e.printStackTrace();
        }
    }

    /**
     * Pehkui doesn't publish an API jar so we do this BS
     */
    public interface ApiAbstraction {
        float getScale(Entity e);

        void setScale(Entity e, float scale);
    }
}
