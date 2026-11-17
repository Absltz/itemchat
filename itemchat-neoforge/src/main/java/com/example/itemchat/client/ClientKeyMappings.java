package com.example.itemchat.client;

import com.example.itemchat.ItemChat;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.client.settings.KeyConflictContext;
import org.lwjgl.glfw.GLFW;

/** 客户端按键注册；原生控制设置负责改键、组合键、解绑和持久化。 */
@EventBusSubscriber(modid = ItemChat.MOD_ID, value = Dist.CLIENT)
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
