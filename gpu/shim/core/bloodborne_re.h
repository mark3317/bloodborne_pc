// bbport co-op: the Bloodborne summon helpers from shadp2p's bloodborne_re.h. Seamless
// co-op (host placement) is not ported yet; these keep the header value between requests.
#pragma once
#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

namespace Core::Bloodborne {
std::optional<std::string> GetSeamlessHostPlacementHeader();
bool SetSeamlessHostPlacementHeader(std::string_view value);
void ClearSeamlessHostPlacementHeader();
inline void TraceMatching2LeaveRoom(std::uintptr_t, std::uint64_t) {} // bbport: BBSC trace, unused here

// bbport: the BBSC emulator's game hooks that its signaling code (bbnet/vendor/.../np_signaling,
// from BBSC) calls. The game side of BBSC is the BBSC mod here (bbsc.dll, with its own P2P
// channel), so these do nothing.
inline void BbscTimelineEvent(std::string_view, std::string_view) {}
inline void OnBbscHostFollowPacket(std::uint32_t, float, float, float, float, std::uint32_t,
                                   std::int32_t) {}
inline void OnBbscWorldFlagsPacket(const void*, std::uint32_t) {}
inline void OnBbscPvpPacket(std::uint8_t, std::uint8_t) {}
inline void OnBbscProgressPacket(const std::uint32_t*, std::size_t) {}
inline void OnBbscHostBossPacket(std::int32_t) {}
} // namespace Core::Bloodborne
