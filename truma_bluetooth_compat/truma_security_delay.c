/* Experimental, reversible BlueZ compatibility shim. No key access or writes.
 * The only behavior change is an 800 ms delay before requesting encryption
 * on an ATT socket whose peer is this user's classic Truma iNet Box.
 * Existing BlueZ/kernel encryption policy and return values are preserved.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <time.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/l2cap.h>

typedef int (*setsockopt_fn)(int, int, int, const void *, socklen_t);
static uint8_t target[6];
static int target_valid;

static int hex_digit(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

__attribute__((constructor)) static void load_target(void)
{
    const char *address = getenv("TRUMA_INET_ADDRESS");
    target_valid = 0;
    if (!address || strlen(address) != 17) return;
    for (int i = 0; i < 6; i++) {
        int a = hex_digit(address[i * 3]), b = hex_digit(address[i * 3 + 1]);
        if (a < 0 || b < 0 || (i < 5 && address[i * 3 + 2] != ':')) return;
        target[5 - i] = (uint8_t)((a << 4) | b);
    }
    target_valid = 1;
}

int setsockopt(int fd, int level, int option, const void *value, socklen_t len)
{
    setsockopt_fn original = (setsockopt_fn)dlsym(RTLD_NEXT, "setsockopt");
    if (!original) { errno = ENOSYS; return -1; }
    if (target_valid && level == SOL_BLUETOOTH && option == BT_SECURITY && value &&
        len >= sizeof(struct bt_security)) {
        const struct bt_security *requested = value;
        struct sockaddr_l2 peer = {0};
        socklen_t peer_len = sizeof(peer);
        struct bt_security current = {0};
        socklen_t current_len = sizeof(current);
        if (requested->level >= BT_SECURITY_MEDIUM &&
            getpeername(fd, (struct sockaddr *)&peer, &peer_len) == 0 &&
            peer_len >= sizeof(peer) && peer.l2_family == AF_BLUETOOTH &&
            btohs(peer.l2_cid) == 4 &&
            memcmp(peer.l2_bdaddr.b, target, sizeof(target)) == 0 &&
            getsockopt(fd, SOL_BLUETOOTH, BT_SECURITY, &current, &current_len) == 0 &&
            current.level < BT_SECURITY_MEDIUM) {
            struct timespec pause = {.tv_sec=0, .tv_nsec=800000000L};
            while (nanosleep(&pause, &pause) < 0 && errno == EINTR) {}
        }
    }
    return original(fd, level, option, value, len);
}
