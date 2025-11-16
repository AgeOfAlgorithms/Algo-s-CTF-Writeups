#include <linux/module.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/slab.h>
#include <linux/device.h>
#include <linux/miscdevice.h>
#include <linux/mutex.h>
#include <linux/string.h>
#include <linux/kprobes.h>      /* kprobes */
#include <linux/ptrace.h>

#define DRV "ghostlight"

#define GHOST_IOC_MAGIC  'G'
#define GHOST_IOC_ARM     _IOW(GHOST_IOC_MAGIC, 0x01, unsigned long)
#define GHOST_IOC_FREE    _IO(GHOST_IOC_MAGIC,  0x02)
#define GHOST_IOC_SPRAY   _IOW(GHOST_IOC_MAGIC, 0x03, unsigned long)
#define GHOST_IOC_HOOKON  _IO(GHOST_IOC_MAGIC,  0x04)
#define GHOST_IOC_HOOKOFF _IO(GHOST_IOC_MAGIC,  0x05)
#define GHOST_IOC_READFLAG _IOW(GHOST_IOC_MAGIC, 0x06, unsigned long)

struct glow {
    char pad[0x20];                         /* kmalloc-64 */
    void (*fn)(unsigned long arg);          /* attacker-controlled if UAF */
    unsigned long arg;
};

static struct glow *gl_ctx;
static struct mutex gl_lock;

/* We'll hook an arbitrary common syscall via kprobe (syscall "shadow") */
static struct kprobe gp = {
    .symbol_name = "__x64_sys_getpid",      /* works on Debian 6.1 cloud kernels */
};
static bool hook_enabled;

/* Called pre-syscall when kprobe hits */
static int kp_pre(struct kprobe *p, struct pt_regs *regs)
{
    struct glow *ctx = READ_ONCE(gl_ctx);
    if (ctx && ctx->fn)
        ctx->fn(ctx->arg);
    return 0;
}

/* spray API */
struct spray_req {
    unsigned int count;                     /* up to 4096 */
    unsigned long fn;
    unsigned long arg;
};

/* user passes pointer to struct { unsigned long buf; unsigned int len; } */
struct flag_req {
    unsigned long user_buf;
    unsigned int len;
};

case GHOST_IOC_READFLAG: {
    struct flag_req req;
    char *kbuf = NULL;
    struct file *f = NULL;
    loff_t pos = 0;
    ssize_t nread;

    if (copy_from_user(&req, (void __user *)arg, sizeof(req)))
        return -EFAULT;
    if (req.user_buf == 0 || req.len == 0 || req.len > 4096)
        return -EINVAL;

    kbuf = kmalloc(req.len, GFP_KERNEL);
    if (!kbuf)
        return -ENOMEM;

    /* open the flag file from kernel space */
    f = filp_open("/root/flag", O_RDONLY, 0);
    if (IS_ERR(f)) {
        kfree(kbuf);
        return PTR_ERR(f);
    }

#ifdef HAVE_KERNEL_READ /* modern kernels */
    nread = kernel_read(f, kbuf, req.len, &pos);
#else
    /* Fallback for older kernels: use vfs_read (if needed) */
    nread = vfs_read(f, kbuf, req.len, &pos);
#endif

    filp_close(f, NULL);

    if (nread < 0) {
        kfree(kbuf);
        return (long)nread;
    }

    if (copy_to_user((void __user *)req.user_buf, kbuf, nread)) {
        kfree(kbuf);
        return -EFAULT;
    }

    kfree(kbuf);

    /* return number of bytes read to the ioctl caller */
    ret = (long)nread;
    break;
}

static long ghost_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
    switch (cmd) {
    case GHOST_IOC_ARM: {
        struct glow *g = kmalloc(sizeof(*g), GFP_KERNEL);
        if (!g) return -ENOMEM;
        memset(g, 0, sizeof(*g));
        g->fn  = NULL;
        g->arg = arg;
        mutex_lock(&gl_lock);
        gl_ctx = g;                         /* leak old; not the primary bug */
        mutex_unlock(&gl_lock);
        return 0;
    }
    case GHOST_IOC_FREE: {
        struct glow *old;
        mutex_lock(&gl_lock);
        old = gl_ctx;
        if (old) kfree(old);                /* BUG: leave dangling while hook active */
        mutex_unlock(&gl_lock);
        return 0;
    }
    case GHOST_IOC_SPRAY: {
        struct spray_req req;
        unsigned int i;
        if (copy_from_user(&req, (void __user *)arg, sizeof(req)))
            return -EFAULT;
        if (!req.count || req.count > 4096) return -EINVAL;
        for (i = 0; i < req.count; i++) {
            struct glow *g = kmalloc(sizeof(*g), GFP_KERNEL);
            if (!g) return -ENOMEM;
            memset(g, 0, sizeof(*g));
            g->fn  = (void (*)(unsigned long))req.fn;
            g->arg = req.arg;
            /* intentionally leaked */
        }
        return 0;
    }
    case GHOST_IOC_HOOKON:
        if (!hook_enabled) {
            gp.pre_handler = kp_pre;
            if (register_kprobe(&gp) == 0)
                hook_enabled = true;
        }
        return 0;

    case GHOST_IOC_HOOKOFF:
        if (hook_enabled) {
            unregister_kprobe(&gp);
            hook_enabled = false;
        }
        return 0;

    default:
        return -ENOTTY;
    }
}

static const struct file_operations ghost_fops = {
    .owner          = THIS_MODULE,
    .unlocked_ioctl = ghost_ioctl,
#ifdef CONFIG_COMPAT
    .compat_ioctl   = ghost_ioctl,
#endif
};

static struct miscdevice ghost_dev = {
    .minor = MISC_DYNAMIC_MINOR,
    .name  = "ghostlight",
    .fops  = &ghost_fops,
    .mode  = 0666,
};

static int __init ghost_init(void)
{
    int rc = misc_register(&ghost_dev);
    if (rc) {
        pr_err(DRV ": misc_register failed: %d\n", rc);
        return rc;
    }
    mutex_init(&gl_lock);
    pr_info(DRV ": loaded. device=/dev/ghostlight (kprobe on __x64_sys_getpid)\n");
    return 0;
}

static void __exit ghost_exit(void)
{
    if (hook_enabled) {
        unregister_kprobe(&gp);
        hook_enabled = false;
    }
    if (gl_ctx) { kfree(gl_ctx); gl_ctx = NULL; }
    misc_deregister(&ghost_dev);
    pr_info(DRV ": unloaded\n");
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("POCTF");
MODULE_DESCRIPTION("EXP 200-3 Ghostlight: kprobe syscall UAF");
module_init(ghost_init);
module_exit(ghost_exit);

