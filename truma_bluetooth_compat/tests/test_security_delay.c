#define _GNU_SOURCE
#include <assert.h>
#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/l2cap.h>
static int real_calls, sleeps, other_peer, encrypted, peer_error;
static int real_setopt(int fd, int level, int option, const void *v, socklen_t n)
{ (void)fd; (void)level; (void)option; (void)v; (void)n; real_calls++; return 17; }
static void *fake_dlsym(void *h, const char *s)
{ (void)h; assert(!strcmp(s,"setsockopt")); return (void *)real_setopt; }
static int fake_peer(int fd, struct sockaddr *a, socklen_t *n)
{
    (void)fd;
    if (peer_error) return -1;
    struct sockaddr_l2 p = {.l2_family=AF_BLUETOOTH,.l2_cid=htobs(4)};
    const uint8_t mac[6]={0x55,0x44,0x33,0x22,0x11,0x02};
    memcpy(p.l2_bdaddr.b,mac,6); if (other_peer) p.l2_bdaddr.b[0]++;
    memcpy(a,&p,sizeof(p)); *n=sizeof(p); return 0;
}
static int fake_get(int fd,int l,int o,void *v,socklen_t *n)
{ (void)fd;(void)l;(void)o;(void)n; ((struct bt_security *)v)->level=encrypted?2:1; return 0; }
static int fake_sleep(const struct timespec *t,struct timespec *r)
{ (void)r; assert(t->tv_sec==0 && t->tv_nsec==800000000L); sleeps++;return 0; }
#define setsockopt shim_setsockopt
#define dlsym fake_dlsym
#define getpeername fake_peer
#define getsockopt fake_get
#define nanosleep fake_sleep
#include "../truma_security_delay.c"
#undef setsockopt
int main(void)
{
    setenv("TRUMA_INET_ADDRESS", "02:11:22:33:44:55", 1);
    load_target();
    struct bt_security sec={.level=BT_SECURITY_MEDIUM};
    assert(shim_setsockopt(1,SOL_BLUETOOTH,BT_SECURITY,&sec,sizeof(sec))==17);
    assert(sleeps==1 && real_calls==1);
    other_peer=1; shim_setsockopt(1,SOL_BLUETOOTH,BT_SECURITY,&sec,sizeof(sec));
    other_peer=0; encrypted=1; shim_setsockopt(1,SOL_BLUETOOTH,BT_SECURITY,&sec,sizeof(sec));
    encrypted=0; peer_error=1; shim_setsockopt(1,SOL_BLUETOOTH,BT_SECURITY,&sec,sizeof(sec));
    peer_error=0; shim_setsockopt(1,SOL_SOCKET,SO_KEEPALIVE,&sec,sizeof(sec));
    sec.level=BT_SECURITY_LOW; shim_setsockopt(1,SOL_BLUETOOTH,BT_SECURITY,&sec,sizeof(sec));
    assert(sleeps==1 && real_calls==6);
    sec.level=BT_SECURITY_MEDIUM;
    unsetenv("TRUMA_INET_ADDRESS"); load_target();
    shim_setsockopt(1,SOL_BLUETOOTH,BT_SECURITY,&sec,sizeof(sec));
    setenv("TRUMA_INET_ADDRESS", "bad", 1); load_target();
    shim_setsockopt(1,SOL_BLUETOOTH,BT_SECURITY,&sec,sizeof(sec));
    assert(sleeps==1 && real_calls==8);
    puts("8 cases passed: only the intended peer's encryption upgrade is delayed; original call preserved.");
    return 0;
}
