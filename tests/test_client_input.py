"""Headless input regression tests for both independent ItemChat projects.

Compiles the real input handlers; only the Minecraft/loader runtime and optional
integrations are fixtures. No Gradle test dependency or installed game is needed.
Run: python -m unittest discover -s tests -v
Set ITEMCHAT_TEST_JDK to a JDK directory if javac is not on PATH.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def fixtures(loader):
    api = "net.minecraftforge" if loader == "forge" else "net.neoforged.neoforge"
    sources = {
        "org.lwjgl.glfw.GLFW": """public final class GLFW {
            public static final int GLFW_PRESS=1, GLFW_RELEASE=0,
                GLFW_MOUSE_BUTTON_MIDDLE=2;
        }""",
        "com.mojang.blaze3d.platform.InputConstants": """public final class InputConstants {
            public enum Type { MOUSE, KEYSYM, SCANCODE;
                public Key getOrCreate(int code) { return new Key(this, code); }
            }
            public record Key(Type type, int value) {}
            public static final Key UNKNOWN = Type.KEYSYM.getOrCreate(-1);
            public static Key getKey(int key, int scan) {
                return key == -1 ? Type.SCANCODE.getOrCreate(scan) : Type.KEYSYM.getOrCreate(key);
            }
        }""",
        "net.minecraft.ChatFormatting": "public enum ChatFormatting { YELLOW }",
        "net.minecraft.network.chat.Component": """public class Component {
            public Component copy() { return this; }
            public Component withStyle(net.minecraft.ChatFormatting color) { return this; }
        }""",
        "net.minecraft.network.protocol.common.custom.CustomPacketPayload": """
            public interface CustomPacketPayload { record Type<T>(String name) {} }
        """,
        "net.minecraft.client.gui.components.events.GuiEventListener": "public interface GuiEventListener {}",
        "net.minecraft.client.gui.components.EditBox": """public class EditBox implements
            net.minecraft.client.gui.components.events.GuiEventListener {
            public boolean isFocused() { return true; }
        }""",
        "net.minecraft.client.gui.screens.Screen": """public class Screen {
            public static boolean shift, control, alt;
            public net.minecraft.client.gui.components.events.GuiEventListener focused;
            public net.minecraft.client.gui.components.events.GuiEventListener getFocused() { return focused; }
        }""",
        "net.minecraft.client.gui.screens.inventory.AbstractContainerScreen": """
            public class AbstractContainerScreen<T> extends net.minecraft.client.gui.screens.Screen {
                public net.minecraft.world.inventory.Slot slot;
                public net.minecraft.world.inventory.Slot getSlotUnderMouse() { return slot; }
            }
        """,
        "net.minecraft.world.item.ItemStack": """public class ItemStack {
            public static final ItemStack EMPTY = new ItemStack("");
            public final String name;
            public ItemStack(String name) { this.name = name; }
            public boolean isEmpty() { return name.isEmpty(); }
        }""",
        "net.minecraft.world.inventory.Slot": """public class Slot {
            public net.minecraft.world.item.ItemStack stack;
            public Slot(net.minecraft.world.item.ItemStack stack) { this.stack = stack; }
            public boolean hasItem() { return !stack.isEmpty(); }
            public net.minecraft.world.item.ItemStack getItem() { return stack; }
        }""",
        "net.minecraft.client.player.LocalPlayer": """public class LocalPlayer {
            public void displayClientMessage(net.minecraft.network.chat.Component text, boolean overlay) {}
        }""",
        "net.minecraft.client.multiplayer.ClientPacketListener": """public class ClientPacketListener {
            public Object getConnection() { return this; }
            public boolean hasChannel(net.minecraft.network.protocol.common.custom.CustomPacketPayload.Type<?> type) {
                return true;
            }
        }""",
        "net.minecraft.client.Minecraft": """public class Minecraft {
            private static final Minecraft INSTANCE = new Minecraft();
            public net.minecraft.client.gui.screens.Screen screen;
            public net.minecraft.client.player.LocalPlayer player = new net.minecraft.client.player.LocalPlayer();
            public static Minecraft getInstance() { return INSTANCE; }
            public net.minecraft.client.multiplayer.ClientPacketListener getConnection() {
                return new net.minecraft.client.multiplayer.ClientPacketListener();
            }
        }""",
        "net.minecraft.client.KeyMapping": """public class KeyMapping {
            private com.mojang.blaze3d.platform.InputConstants.Key key;
            private API.client.settings.KeyModifier modifier = API.client.settings.KeyModifier.NONE;
            private final String name;
            private final API.client.settings.KeyConflictContext context;
            public KeyMapping(String name, API.client.settings.KeyConflictContext context,
                    com.mojang.blaze3d.platform.InputConstants.Type type, int code, String category) {
                this.name=name; this.context=context; this.key=type.getOrCreate(code);
            }
            public boolean isActiveAndMatches(com.mojang.blaze3d.platform.InputConstants.Key candidate) {
                return !key.equals(com.mojang.blaze3d.platform.InputConstants.UNKNOWN)
                    && key.equals(candidate) && context.isActive() && modifier.isActive();
            }
            public void setKeyModifierAndCode(API.client.settings.KeyModifier modifier,
                    com.mojang.blaze3d.platform.InputConstants.Key key) { this.modifier=modifier; this.key=key; }
            public String getName() { return name; }
        }""",
        "com.example.itemchat.ItemChat": """public class ItemChat {
            public static final String MOD_ID="itemchat";
            public static net.minecraft.network.chat.Component tr(String key, String fallback, Object... args) {
                return new net.minecraft.network.chat.Component();
            }
        }""",
        "com.example.itemchat.net.ItemChatNetwork": """public class ItemChatNetwork {
            public static final java.util.List<Object> sent = new java.util.ArrayList<>();
            public static final Channel CHANNEL = new Channel();
            public static class Channel { public boolean isRemotePresent(Object connection) { return true; } }
            public static void sendToServer(Object packet) { sent.add(packet); }
        }""",
        "com.example.itemchat.net.ShareItemPacket": """public class ShareItemPacket {
            public static final net.minecraft.network.protocol.common.custom.CustomPacketPayload.Type<Object>
                TYPE = new net.minecraft.network.protocol.common.custom.CustomPacketPayload.Type<>("item");
            public final net.minecraft.world.item.ItemStack stack;
            public ShareItemPacket(net.minecraft.world.item.ItemStack stack) { this.stack=stack; }
        }""",
        "com.example.itemchat.net.ShareQuestPacket": """public class ShareQuestPacket {
            public static final net.minecraft.network.protocol.common.custom.CustomPacketPayload.Type<Object>
                TYPE = new net.minecraft.network.protocol.common.custom.CustomPacketPayload.Type<>("quest");
            public final long id;
            public ShareQuestPacket(long id) { this.id=id; }
            public ShareQuestPacket(long id, net.minecraft.network.chat.Component title) { this.id=id; }
        }""",
        "com.example.itemchat.client.JeiIntegration": """public class JeiIntegration {
            public static boolean keyboardFocused;
            public static boolean hasKeyboardFocus() { return keyboardFocused; }
            public static net.minecraft.world.item.ItemStack hovered = net.minecraft.world.item.ItemStack.EMPTY;
            public static net.minecraft.world.item.ItemStack getItemStackUnderMouse() { return hovered; }
        }""",
        "com.example.itemchat.client.FtbQuestsIntegration": """public class FtbQuestsIntegration {
            public record QuestUnderMouse(long questId, net.minecraft.network.chat.Component title) {}
            public static long hovered;
            public static long getQuestIdUnderMouse(net.minecraft.client.gui.screens.Screen screen) { return hovered; }
            public static QuestUnderMouse getQuestUnderMouse(net.minecraft.client.gui.screens.Screen screen) {
                return hovered == 0 ? null : new QuestUnderMouse(hovered, new net.minecraft.network.chat.Component());
            }
        }""",
        "FML.ModList": """public class ModList {
            private static final ModList INSTANCE = new ModList();
            public static final java.util.Set<String> loaded = new java.util.HashSet<>();
            public static ModList get() { return INSTANCE; }
            public boolean isLoaded(String id) { return loaded.contains(id); }
        }""",
        "API.client.settings.KeyConflictContext": """public enum KeyConflictContext { GUI;
            public boolean isActive() { return net.minecraft.client.Minecraft.getInstance().screen != null; }
        }""",
        "API.client.settings.KeyModifier": """public enum KeyModifier { NONE, SHIFT, CONTROL, ALT;
            public boolean isActive() {
                var screen = net.minecraft.client.gui.screens.Screen.class;
                return switch(this) {
                    case SHIFT -> net.minecraft.client.gui.screens.Screen.shift;
                    case CONTROL -> net.minecraft.client.gui.screens.Screen.control;
                    case ALT -> net.minecraft.client.gui.screens.Screen.alt;
                    case NONE -> !net.minecraft.client.gui.screens.Screen.shift
                        && !net.minecraft.client.gui.screens.Screen.control && !net.minecraft.client.gui.screens.Screen.alt;
                };
            }
        }""",
        "API.client.event.InputEvent": """public class InputEvent {
            public static class MouseButton {
                public static class Pre {
                    private final int button, action; private boolean canceled;
                    public Pre(int button, int action, int modifiers) { this.button=button; this.action=action; }
                    public int getAction() { return action; }
                    public int getButton() { return button; }
                    public void setCanceled(boolean value) { canceled=value; }
                    public boolean isCanceled() { return canceled; }
                }
            }
        }""",
        "API.client.event.ScreenEvent": """public class ScreenEvent {
            public static class Init { public static class Pre {} }
            public static class KeyReleased {
                public static class Pre extends KeyPressed.Pre {
                    public Pre(net.minecraft.client.gui.screens.Screen screen, int key, int scan, int modifiers) {
                        super(screen,key,scan,modifiers);
                    }
                }
            }
            public static class KeyPressed {
                public static class Pre {
                    private final net.minecraft.client.gui.screens.Screen screen;
                    private final int key, scan; private boolean canceled;
                    public Pre(net.minecraft.client.gui.screens.Screen screen, int key, int scan, int modifiers) {
                        this.screen=screen; this.key=key; this.scan=scan;
                    }
                    public net.minecraft.client.gui.screens.Screen getScreen() { return screen; }
                    public int getKeyCode() { return key; }
                    public int getScanCode() { return scan; }
                    public void setCanceled(boolean value) { canceled=value; }
                    public boolean isCanceled() { return canceled; }
                }
            }
        }""",
        "API.client.event.RegisterKeyMappingsEvent": """public class RegisterKeyMappingsEvent {
            public final java.util.List<net.minecraft.client.KeyMapping> registered = new java.util.ArrayList<>();
            public void register(net.minecraft.client.KeyMapping mapping) { registered.add(mapping); }
        }""",
        "EVENT.EventPriority": "public enum EventPriority { HIGHEST, NORMAL }",
        "EVENT.SubscribeEvent": """public @interface SubscribeEvent {
            EventPriority priority() default EventPriority.NORMAL;
            boolean receiveCanceled() default false;
        }""",
        "DIST.Dist": "public enum Dist { CLIENT }",
    }
    if loader == "forge":
        sources["net.minecraftforge.fml.common.Mod"] = """public @interface Mod {
            public @interface EventBusSubscriber {
                String modid(); net.minecraftforge.api.distmarker.Dist[] value(); Bus bus() default Bus.FORGE;
                public enum Bus { FORGE, MOD }
            }
        }"""
    else:
        sources["net.neoforged.fml.common.EventBusSubscriber"] = """public @interface EventBusSubscriber {
            String modid(); net.neoforged.api.distmarker.Dist[] value();
        }"""
    replacements = {
        "API": api,
        "FML": "net.minecraftforge.fml" if loader == "forge" else "net.neoforged.fml",
        "EVENT": "net.minecraftforge.eventbus.api" if loader == "forge" else "net.neoforged.bus.api",
        "DIST": "net.minecraftforge.api.distmarker" if loader == "forge" else "net.neoforged.api.distmarker",
    }
    def expand(text):
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    return {expand(name): expand(body) for name, body in sources.items()}, expand


HARNESS = """
package com.example.itemchat.client;
import com.mojang.blaze3d.platform.InputConstants;
import com.example.itemchat.net.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.gui.screens.inventory.*;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import API.client.event.*;
import API.client.settings.KeyModifier;
public class InputRegression {
    static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
    static void bind(InputConstants.Type type, int key) {
        ClientKeyMappings.SHARE.setKeyModifierAndCode(KeyModifier.NONE, type.getOrCreate(key));
    }
    static InputEvent.MouseButton.Pre mouse(int button, int action) {
        var event = new InputEvent.MouseButton.Pre(button, action, 0);
        ClientEvents.onMouseButtonPre(event);
        return event;
    }
    static ScreenEvent.KeyPressed.Pre key(int code, int scan) throws Exception {
        var event = new ScreenEvent.KeyPressed.Pre(Minecraft.getInstance().screen, code, scan, 0);
        try {
            ClientEvents.class.getMethod("onKeyPressed", ScreenEvent.KeyPressed.Pre.class).invoke(null, event);
        } catch (NoSuchMethodException e) { throw new AssertionError("Configured keyboard input must share", e); }
        return event;
    }
    static void release(int code, int scan) throws Exception {
        var event = new ScreenEvent.KeyReleased.Pre(Minecraft.getInstance().screen,code,scan,0);
        try {
            ClientEvents.class.getMethod("onKeyReleased", ScreenEvent.KeyReleased.Pre.class).invoke(null,event);
        } catch (NoSuchMethodException e) { throw new AssertionError("Key release must reset held sharing input",e); }
        check(!event.isCanceled(), "Sharing must not consume key release");
    }
    public static void main(String[] args) throws Exception {
        var container = new AbstractContainerScreen<>();
        container.slot = new Slot(new ItemStack("container"));
        Minecraft.getInstance().screen = container;
        switch(args[0]) {
            case "default_middle" -> check(mouse(2,1).isCanceled(), "Default middle click should share");
            case "rebound_middle" -> {
                bind(InputConstants.Type.KEYSYM, 86);
                check(!mouse(2,1).isCanceled(), "After rebinding to V, AE must receive the middle click");
            }
            case "mapped_mouse" -> {
                bind(InputConstants.Type.MOUSE,4);
                check(mouse(4,1).isCanceled(), "New mouse binding must share");
            }
            case "unbound" -> {
                ClientKeyMappings.SHARE.setKeyModifierAndCode(KeyModifier.NONE,InputConstants.UNKNOWN);
                check(!mouse(2,1).isCanceled(), "Unbound sharing must not swallow middle clicks");
            }
            case "release" -> check(!mouse(2,0).isCanceled(), "Mouse release must reach UI");
            case "keyboard" -> {
                bind(InputConstants.Type.KEYSYM,86);
                check(key(86,0).isCanceled(), "Mapped keyboard input must share");
            }
            case "keyboard_repeat" -> {
                bind(InputConstants.Type.KEYSYM,86);
                check(key(86,0).isCanceled(), "Initial press must share");
                check(key(86,0).isCanceled(), "Held key repeat must remain handled");
                check(key(86,0).isCanceled(), "Further repeat must remain handled");
            }
            case "keyboard_release" -> {
                bind(InputConstants.Type.KEYSYM,86);
                key(86,0); release(86,0);
                check(key(86,0).isCanceled(), "A new press after release must share again");
            }
            case "keyboard_reopen" -> {
                bind(InputConstants.Type.KEYSYM,86);
                key(86,0);
                try {
                    ClientEvents.class.getMethod("onScreenInit",ScreenEvent.Init.Pre.class)
                        .invoke(null,new ScreenEvent.Init.Pre());
                } catch (NoSuchMethodException e) { throw new AssertionError("Opening a GUI must reset stale held input",e); }
                check(key(86,0).isCanceled(), "Reopening a GUI must allow another press");
            }
            case "scancode" -> {
                bind(InputConstants.Type.SCANCODE,42);
                check(key(-1,42).isCanceled(), "Scancode bindings must share");
            }
            case "old_keyboard" -> {
                bind(InputConstants.Type.KEYSYM,66);
                check(!key(86,0).isCanceled(), "Old keyboard binding must be released");
            }
            case "modifier_required" -> {
                ClientKeyMappings.SHARE.setKeyModifierAndCode(KeyModifier.SHIFT,InputConstants.Type.MOUSE.getOrCreate(2));
                check(!mouse(2,1).isCanceled(), "Without Shift, AE must receive the middle click");
            }
            case "modifier_matches" -> {
                ClientKeyMappings.SHARE.setKeyModifierAndCode(KeyModifier.SHIFT,InputConstants.Type.MOUSE.getOrCreate(2));
                Screen.shift=true;
                check(mouse(2,1).isCanceled(), "Shift+middle binding must share");
            }
            case "no_target" -> {
                container.slot=null;
                check(!mouse(2,1).isCanceled(), "Empty area must not swallow the input");
            }
            case "no_screen" -> {
                Minecraft.getInstance().screen=null;
                check(!mouse(2,1).isCanceled(), "Gameplay input must be released");
            }
            case "typing" -> {
                bind(InputConstants.Type.KEYSYM,86);
                container.focused=new net.minecraft.client.gui.components.EditBox();
                check(!key(86,0).isCanceled(), "Typing in a focused search field must not share");
            }
            case "jei_typing" -> {
                bind(InputConstants.Type.KEYSYM,86);
                FML.ModList.loaded.add("jei");
                JeiIntegration.keyboardFocused=true;
                JeiIntegration.hovered=new ItemStack("jei");
                check(!key(86,0).isCanceled(), "JEI overlay search focus must preserve typing even when screen focus is null");
            }
            case "jei" -> {
                FML.ModList.loaded.add("jei");
                JeiIntegration.hovered=new ItemStack("jei");
                check(mouse(2,1).isCanceled(), "JEI item must share");
                check(((ShareItemPacket)ItemChatNetwork.sent.get(0)).stack.name.equals("jei"), "JEI must take precedence over container");
            }
            case "ftb" -> {
                FML.ModList.loaded.add("ftbquests"); FtbQuestsIntegration.hovered=123;
                check(mouse(2,1).isCanceled(), "FTB task must share");
                check(((ShareQuestPacket)ItemChatNetwork.sent.get(0)).id==123, "Task id must be preserved");
            }
            case "registration" -> {
                var event=new RegisterKeyMappingsEvent(); ClientKeyMappings.register(event);
                check(event.registered.size()==1 && event.registered.get(0)==ClientKeyMappings.SHARE,
                    "Controls must register exactly the sharing binding");
            }
            default -> throw new AssertionError("Unknown scenario");
        }
        boolean shares=java.util.Set.of("default_middle","mapped_mouse","keyboard","keyboard_repeat","scancode",
            "modifier_matches","jei","ftb").contains(args[0]);
        int expected=java.util.Set.of("keyboard_release","keyboard_reopen").contains(args[0]) ? 2 : shares ? 1 : 0;
        check(ItemChatNetwork.sent.size()==expected, "Exactly one packet per press, none for repeat or pass-through input");
        System.out.println("PASS " + args[0]);
    }
}
"""

SCENARIOS = (
    "default_middle", "rebound_middle", "mapped_mouse", "unbound", "release",
    "keyboard", "keyboard_repeat", "keyboard_release", "keyboard_reopen", "scancode",
    "old_keyboard", "modifier_required", "modifier_matches",
    "no_target", "no_screen", "typing", "jei_typing", "jei", "ftb", "registration",
)


class ClientInputRegression(unittest.TestCase):
    def test_both_loaders(self):
        jdk = os.environ.get("ITEMCHAT_TEST_JDK")
        if not jdk:
            bundled = Path(os.environ.get("APPDATA", "")) / ".minecraft/runtime/java-runtime-delta"
            jdk = str(bundled) if (bundled / "bin/javac.exe").exists() else None
        suffix = ".exe" if os.name == "nt" else ""
        javac = str(Path(jdk) / f"bin/javac{suffix}") if jdk else shutil.which("javac")
        java = str(Path(jdk) / f"bin/java{suffix}") if jdk else shutil.which("java")
        self.assertTrue(javac and java, "Set ITEMCHAT_TEST_JDK to a Java 17+ JDK")
        for loader, project in (("forge", "itemchat-forge"), ("neoforge", "itemchat-neoforge")):
            with tempfile.TemporaryDirectory(prefix=f"itemchat-{loader}-input-") as temporary:
                directory = Path(temporary)
                sources, expand = fixtures(loader)
                production = ROOT / project / "src/main/java/com/example/itemchat/client"
                mapping = production / "ClientKeyMappings.java"
                if not mapping.exists():
                    # Baseline fixture lets the old handler run: it ignores this configured key.
                    sources["com.example.itemchat.client.ClientKeyMappings"] = expand("""
                        public class ClientKeyMappings {
                            public static final net.minecraft.client.KeyMapping SHARE = new net.minecraft.client.KeyMapping(
                                "key.itemchat.share", API.client.settings.KeyConflictContext.GUI,
                                com.mojang.blaze3d.platform.InputConstants.Type.MOUSE,2,"key.categories.itemchat");
                            public static void register(API.client.event.RegisterKeyMappingsEvent event) { event.register(SHARE); }
                        }
                    """)
                files = []
                for name, body in sources.items():
                    path = directory / (name.replace(".", "/") + ".java")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(f"package {name.rsplit('.', 1)[0]};\n{body}", encoding="utf-8")
                    files.append(str(path))
                harness = directory / "InputRegression.java"
                harness.write_text(expand(HARNESS), encoding="utf-8")
                files.extend((str(harness), str(production / "ClientEvents.java")))
                if mapping.exists():
                    files.append(str(mapping))
                compile_result = subprocess.run(
                    [javac, "-encoding", "UTF-8", "-d", str(directory), *files],
                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
                )
                self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
                for scenario in SCENARIOS:
                    with self.subTest(loader=loader, scenario=scenario):
                        result = subprocess.run(
                            [java, "-cp", str(directory), "com.example.itemchat.client.InputRegression", scenario],
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
                        )
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
