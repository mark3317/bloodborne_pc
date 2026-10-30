"""Bounded packet correlation and the actual Windows native log sink (no game required)."""
from pathlib import Path
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CPP = r'''
#include <cassert>
#include <filesystem>
#include <windows.h>
#include "common/logging/log.h"
#include "core/net/p2p_latency.h"
using Core::Net::P2P::LatencySamples;
int wmain(int argc, wchar_t** argv) {
    assert(argc==2);
    LatencySamples client, host;
    const std::array<std::uint8_t,4> packet{1,2,3,4};
    client.Record('T',10,20,packet,1000000);
    host.Record('R',20,10,packet,1030000);
    host.Record('D',20,10,packet,3030000,2000000);
    assert(client.samples[0].hash==host.samples[0].hash);
    assert(host.samples[1].queue_us==2000000);
    assert(host.samples[0].wall_us-client.samples[0].wall_us==30000);
    auto changed=packet; changed[3]=5;
    host.Record('R',20,10,changed,1040000);
    assert(host.samples[2].hash!=client.samples[0].hash);
    for (size_t i=host.count;i<host.samples.size();++i) host.Record('R',20,10,packet,1050000);
    host.Record('D',20,10,packet,4000000);
    assert(host.count==1024 && host.omitted==1);
    host.Clear(); assert(host.count==0 && host.omitted==0);
    assert(host.remaining==65536-1024); // draining a batch does not reset the capture budget
    host.remaining=0; host.Record('R',20,10,packet,1050000);
    assert(host.count==0 && host.omitted==1);

    // Seed CRT's wide environment first, then change the Win32 environment as launchers can.
    (void)_wgetenv(L"BB_USER_DIR");
    SetEnvironmentVariableW(L"BB_COOP", L"1");
    SetEnvironmentVariableW(L"BB_USER_DIR", nullptr);
    SetEnvironmentVariableW(L"BB_GPU_LOG_FILE", nullptr);
    SetEnvironmentVariableW(L"BB_GPU_USER_DIR", argv[1]);
    assert(Common::Log::CoopDiagnosticsEnabled());
    LOG_WARNING(Lib_Net, "P2P diagnostic sink regression marker");
    bool found=false;
    for (const auto& f:std::filesystem::directory_iterator(std::filesystem::path(argv[1])/L"log")) {
        assert(f.path().extension()==L".log"); found=true;
    }
    assert(found);
}
'''
with tempfile.TemporaryDirectory(prefix="bbnet-latency-") as tmp:
    folder = Path(tmp)
    source, binary = folder / "test.cpp", folder / "test.exe"
    source.write_text(CPP, encoding="utf-8")
    subprocess.run([r"C:\msys64\clang64\bin\clang++.exe", "-std=c++23", "-municode",
                    "-I" + str(ROOT / "gpu/shim"), "-I" + str(ROOT / "gpu/shadps4"),
                    "-I" + str(ROOT / "gpu/bbnet/vendor/shadps4"),
                    str(source), str(ROOT / "gpu/shim/common/logging/log.cpp"), "-lfmt",
                    "-o", str(binary)], check=True)
    env = dict(os.environ)
    env["PATH"] = r"C:\msys64\clang64\bin;" + env["PATH"]
    env.pop("BB_GPU_LOG_FILE", None)
    env["BB_GPU_LOG"] = "warning"
    subprocess.run([str(binary), str(folder / "журнал")], env=env, check=True, timeout=10)
    logs = list((folder / "журнал/log").glob("bbnet-*.log"))
    assert len(logs) == 1
    assert "sink regression marker" in logs[0].read_text(encoding="utf-8")
print("PASS: datagram correlation, 2s queue age, bounded overflow, reset, Win32 environment and Unicode GPU user-dir native log")
