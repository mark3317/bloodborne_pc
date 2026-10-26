// SPDX-FileCopyrightText: Copyright 2026 bbport contributors
// SPDX-License-Identifier: GPL-2.0-or-later

#include "core/libraries/network/bbsc_fast_sign.h"

#ifdef _WIN32
#include <windows.h>
#endif

namespace Bbport {

bool BbscRewriteSummonBody(std::vector<u8>& body) {
#ifdef _WIN32
    using Fn = u64 (*)(const char*, u64, char*, u64);
    const HMODULE mod = GetModuleHandleA("bbsc.dll");
    if (mod == nullptr) {
        return false;
    }
    const auto fn = reinterpret_cast<Fn>(
        reinterpret_cast<void*>(GetProcAddress(mod, "BbscRewriteSummonBody")));
    if (fn == nullptr || body.empty()) {
        return false;
    }
    std::vector<u8> out(body.size() + 64);
    const u64 length = fn(reinterpret_cast<const char*>(body.data()), body.size(),
                          reinterpret_cast<char*>(out.data()), out.size());
    if (length == 0 || length > out.size()) {
        return false;
    }
    out.resize(static_cast<size_t>(length));
    body = std::move(out);
    return true;
#else
    (void)body;
    return false;
#endif
}

} // namespace Bbport
