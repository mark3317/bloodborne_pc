// SPDX-FileCopyrightText: Copyright 2026 bbport contributors
// SPDX-License-Identifier: GPL-2.0-or-later

// bbport: see bloodborne_re.h - the BBSC relay client is the mod's here.
#pragma once

#include <cstdint>

namespace Core::Bbsc {
inline std::uint32_t RelaySendPacket(const void*, std::uint32_t) {
    return 0;
}
inline void NoteSignalingBbscPacket() {}
} // namespace Core::Bbsc
