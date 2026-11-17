package com.example.itemchat.client;

import com.example.itemchat.ItemChat;
import com.example.itemchat.net.ItemChatNetwork;
import com.example.itemchat.net.ShareItemPacket;
import com.example.itemchat.net.ShareQuestPacket;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.multiplayer.ClientPacketListener;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

/**
 * 客户端分享输入：默认中键，也支持控制设置中的鼠标、键盘和组合键绑定。
 *
 * <h3>为什么统一用 {@link InputEvent.MouseButton.Pre}，而不是 {@code ScreenEvent}</h3>
 *
 * <p>最早这里用的是 {@code ScreenEvent.MouseButtonPressed.Pre}。它能用，但有一个坑：
 * 这个事件是在 {@code Screen#mouseClicked} 那条链上发的，很多模组都会监听它，而且一旦
 * 有人先 {@code setCanceled(true)}，Forge 就不会再调用后面没声明 {@code receiveCanceled}
 * 的监听器。</p>
 *
 * <p>实测就撞上了这种情况：同一份 jar，在 JEI 15.20 的整合包里中键物品正常，在 JEI 15.49
 * 的整合包里就没反应（背包槽位、FTB 任务都正常）。所以这里改成用更底层的
 * {@link InputEvent.MouseButton.Pre} —— 它在 {@code MouseHandler#onPress} 里、
 * <b>把点击分发给屏幕之前</b>触发，取消后屏幕（包括 JEI 的浮层）根本收不到这次点击，
 * 从根上绕开了"谁先取消"的竞争。</p>
 *
 * <p>优先级仍然是 {@code HIGHEST}，保证我们排在其它模组前面。</p>
 *
 * <p>{@code InputEvent} 属于游戏事件，所以 {@code bus} 写 {@code Bus.FORGE}；
 * {@code value = Dist.CLIENT} 保证这些监听只在客户端注册。</p>
 */
@Mod.EventBusSubscriber(modid = ItemChat.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ClientEvents {

    private static final String JEI_MOD_ID = "jei";
    private static final String FTB_QUESTS_MOD_ID = "ftbquests";
    private static InputConstants.Key heldShareKey = InputConstants.UNKNOWN;

    private ClientEvents() {
    }

    /**
     * 保留早期鼠标入口，但只处理当前绑定；改键或解绑后，旧中键完整交给 AE 等界面。
     */
    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void onMouseButtonPre(InputEvent.MouseButton.Pre event) {
        if (event.getAction() != GLFW.GLFW_PRESS) {
            return;
        }
        if (!ClientKeyMappings.SHARE.isActiveAndMatches(
                InputConstants.Type.MOUSE.getOrCreate(event.getButton()))) {
            return;
        }

        if (tryShareUnderMouse(Minecraft.getInstance().screen)) {
            event.setCanceled(true);
        }
    }

    /** 键盘改键也在界面处理之前触发；输入框正在打字时保留原有输入。 */
    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void onKeyPressed(ScreenEvent.KeyPressed.Pre event) {
        InputConstants.Key key = InputConstants.getKey(event.getKeyCode(), event.getScanCode());
        if (!ClientKeyMappings.SHARE.isActiveAndMatches(key)) {
            return;
        }
        Screen screen = event.getScreen();
        if (screen.getFocused() instanceof EditBox editBox && editBox.isFocused()) {
            return;
        }
        if (ModList.get().isLoaded(JEI_MOD_ID) && JeiIntegration.hasKeyboardFocus()) {
            return;
        }
        // 界面按键事件也包含系统长按重复；一次按下只广播一次。
        if (key.equals(heldShareKey)) {
            event.setCanceled(true);
            return;
        }
        if (tryShareUnderMouse(screen)) {
            heldShareKey = key;
            event.setCanceled(true);
        }
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST, receiveCanceled = true)
    public static void onKeyReleased(ScreenEvent.KeyReleased.Pre event) {
        if (heldShareKey.equals(InputConstants.getKey(event.getKeyCode(), event.getScanCode()))) {
            heldShareKey = InputConstants.UNKNOWN;
        }
    }

    /** 关闭界面后可能在游戏中松键，重新打开界面时清除旧状态。 */
    @SubscribeEvent
    public static void onScreenInit(ScreenEvent.Init.Pre event) {
        heldShareKey = InputConstants.UNKNOWN;
    }

    /** 两种输入共用目标选择；只有确实命中物品或任务时才消费事件。 */
    private static boolean tryShareUnderMouse(Screen screen) {
        if (screen == null || Minecraft.getInstance().player == null) {
            return false;
        }

        // 1) JEI：物品管理器列表 / 配方界面 / 书签栏里鼠标悬停的物品。
        //    这一条要在容器槽位之前判，因为 JEI 的列表浮层会盖在容器界面之上。
        if (ModList.get().isLoaded(JEI_MOD_ID)) {
            ItemStack jeiStack = JeiIntegration.getItemStackUnderMouse();
            if (!jeiStack.isEmpty()) {
                shareItem(jeiStack);
                return true;
            }
        }

        // 2) FTB 任务界面里鼠标下的任务
        if (ModList.get().isLoaded(FTB_QUESTS_MOD_ID)) {
            long questId = FtbQuestsIntegration.getQuestIdUnderMouse(screen);
            if (questId != 0L) {
                shareQuest(questId);
                return true;
            }
        }

        // 3) 普通容器界面的槽位
        if (screen instanceof AbstractContainerScreen<?> containerScreen) {
            Slot slot = containerScreen.getSlotUnderMouse();
            if (slot == null || !slot.hasItem()) {
                return false;
            }
            ItemStack stack = slot.getItem();
            if (stack.isEmpty()) {
                return false;
            }
            shareItem(stack);
            return true;
        }
        return false;
    }

    /** 把物品发给服务端广播；服务端没装本模组时只在自己屏幕上提示一句。 */
    private static void shareItem(ItemStack stack) {
        if (!isServerChannelPresent()) {
            notifySelf(ItemChat.tr("itemchat.msg.no_itemchat_item",
                    "当前服务器没有安装 ItemChat，无法向其他玩家展示物品。"));
            return;
        }
        ItemChatNetwork.sendToServer(new ShareItemPacket(stack));
    }

    /** 把任务发给服务端广播。 */
    private static void shareQuest(long questId) {
        if (!isServerChannelPresent()) {
            notifySelf(ItemChat.tr("itemchat.msg.no_itemchat_quest",
                    "当前服务器没有安装 ItemChat，无法向其他玩家展示任务。"));
            return;
        }
        ItemChatNetwork.sendToServer(new ShareQuestPacket(questId));
    }

    /**
     * 服务端是否装了本模组（即通道是否可用）。
     * 用 {@code isRemotePresent} 探测，没装时不会报错，只是功能降级。
     */
    private static boolean isServerChannelPresent() {
        ClientPacketListener connection = Minecraft.getInstance().getConnection();
        return connection != null && ItemChatNetwork.CHANNEL.isRemotePresent(connection.getConnection());
    }

    /** 只给自己看的提示（走 action bar 上方那条聊天提示，不进聊天记录）。 */
    private static void notifySelf(Component text) {
        LocalPlayer player = Minecraft.getInstance().player;
        if (player != null) {
            player.displayClientMessage(text.copy().withStyle(ChatFormatting.YELLOW), true);
        }
    }
}
