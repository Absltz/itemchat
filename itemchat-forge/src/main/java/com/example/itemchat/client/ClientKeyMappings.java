package com.example.itemchat.client;

import com.example.itemchat.ItemChat;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.settings.KeyConflictContext;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

/** 客户端按键注册；原生控制设置负责改键、组合键、解绑和持久化。 */
@Mod.EventBusSubscriber(modid = ItemChat.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class ClientKeyMappings {

    public static final KeyMapping SHARE = new KeyMapping(
            "key.itemchat.share",
            KeyConflictContext.GUI,
            InputConstants.Type.MOUSE,
            GLFW.GLFW_MOUSE_BUTTON_MIDDLE,
            "key.categories.itemchat");

    private ClientKeyMappings() {
    }

    @SubscribeEvent
    public static void register(RegisterKeyMappingsEvent event) {
        event.register(SHARE);
    }
}
