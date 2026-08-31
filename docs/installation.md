# Installation

> [!CAUTION]
> Flashing a kernel can brick your device and will void your warranty. Make a full backup (boot partition at minimum) before proceeding.

Choose the method that fits your situation:

| Method | When to use | Requires root | Guide |
|--------|-------------|---------------|-------|
| **Kernel Flasher** | Upgrading with root already available, no PC needed | Yes | [kernelflasher.md](kernelflasher.md) |
| **magiskboot** | When you want to flash a pre-patched `boot.img` directly (no pre-rooted setup required) | No | [magiskboot.md](magiskboot.md) |
| **PixelFlasher** | If you have zero flashing experience, a PC and a Pixel - other devices can work but are not officially supported | No | [pixelflasher.md](pixelflasher.md) |

## After flashing (both methods)

- Install / update the matching KernelSU manager APK (`manager-apk-*`).
- If using SUSFS, install the SUSFS module.
- Verify root with `su` or manager app.

---

See also: [Kernel Features Documentation](features.md) · [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases)
