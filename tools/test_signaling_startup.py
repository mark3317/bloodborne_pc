"""Compile actual signaling startup functions against a threaded rollback fixture."""
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
base = root / "gpu/bbnet/vendor/shadps4/core/libraries/np/np_signaling"
def extract(path, signature):
    source = path.read_text(encoding="utf-8")
    start = source.index(signature)
    brace = source.index("{", start)
    depth, end = 1, brace + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]
code = r"""
#include <cassert>
#include <cstdint>
#include <mutex>
#include <optional>
#include <thread>
using s32=int32_t; using s64=int64_t; using u32=uint32_t; using u64=uint64_t;
#define PS4_SYSV_ABI
#define LOG_INFO(...)
#define LOG_DEBUG(...)
#define LOG_ERROR(...)
constexpr s32 ORBIS_OK=0, ORBIS_NP_SIGNALING_ERROR_ALREADY_INITIALIZED=-1;
constexpr s32 ORBIS_NP_SIGNALING_ERROR_PROHIBITED_TO_USE=-2;
bool g_initialized=false, g_callout_ctx_active=false;
int g_callout_ctx=0, fail=0;
u32 g_echo_probe_word2=99, g_echo_probe_word3=99;
u64 g_echo_thread_handle=0; s32 g_echo_thread_status=0;
std::mutex signaling;
std::thread worker;
struct SignalingMutexGuard { SignalingMutexGuard(){signaling.lock();} ~SignalingMutexGuard(){signaling.unlock();} };
void InitSignalingMutex(){} void RegisterRuntimeHooks(){}
namespace Helpers {
s32 CheckInitializeAppType(u32* p){*p=0;return 0;}
s32 InitSignalingHeap(s64){return 0;} s32 CheckAppType(){return 0;}
void ShutdownSignalingHeap(){}
s32 StartMainRuntime(s32,s32,s64){
 worker=std::thread([]{std::lock_guard lock(signaling);}); return 0;
}
void ShutdownRuntime(){if(worker.joinable())worker.join();}
"""
code += extract(base / "np_signaling_helpers.cpp", "s32 StartEchoRuntime(").replace("StartEchoRuntime(", "RealStartEchoRuntime(", 1)
code += r"""
s32 StartEchoRuntime(s32 a,s32 b){return fail==1?-5:RealStartEchoRuntime(a,b);}
}
namespace NpCommon { s32 sceNpCalloutInitCtx(int*,const char*,u64,s32,u64){return fail==2?-6:0;} }
"""
code += extract(base / "np_signaling.cpp", "s32 PS4_SYSV_ABI sceNpSignalingInitialize(")
code += r"""
int main(){
 for(int failure: {0,1,2}){
  fail=failure;g_initialized=false;g_callout_ctx_active=false;
  auto rc=sceNpSignalingInitialize(0,0,48,0);
  assert(rc==(fail==1?-5:fail==2?-6:0));
  assert(g_initialized==(fail==0));
  assert(g_callout_ctx_active==(fail==0));
  Helpers::ShutdownRuntime();
 }
 assert(Helpers::RealStartEchoRuntime(700,48)==0);
 assert(g_echo_probe_word2==0 && g_echo_probe_word3==0);
 assert(g_echo_thread_handle==u64(-1) && g_echo_thread_status==-1);
}
"""
with tempfile.TemporaryDirectory(prefix="bbnet-startup-") as tmp:
    source=Path(tmp)/"test.cpp"; exe=Path(tmp)/"test.exe"
    source.write_text(code,encoding="utf-8")
    subprocess.run(["g++","-std=c++20","-pthread",str(source),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True,timeout=5)
print("signaling startup: success, echo failure and callout failure rollback PASS")
