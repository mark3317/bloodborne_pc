// SPDX-FileCopyrightText: Copyright 2026 shadPS4 Emulator Project
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#include <memory>

#include <string_view>

#include "common/types.h"
#include "core/net/p2p_relay.h"

namespace Core::Net::P2P {
class Keyring;
}

namespace Libraries::Net {
void ConfigureP2P(u16 udp_port, u32 advertised_addr);
u16 StartP2P(u16 udp_port);
void StopP2P();
std::shared_ptr<Core::Net::P2P::Keyring> GetP2PKeyring();

// Used by NP signaling/matching.
bool EnsureP2PTransport();
bool P2PTransportIsReady();
u16 GetP2PConfiguredPort(); // host order
u16 GetP2PBoundPort();      // host order, 0 when not running
u32 GetP2PAdvertisedAddr(); // Network order, 0 if unknown.
u16 GetP2PAdvertisedPort();
int P2PSignalingSendTo(const void* data, u32 len, u32 dest_addr, u16 dest_port);
int P2PSignalingRecvFrom(void* buf, u32 len, u32* from_addr, u16* from_port);
int P2PControlSendTo(const void* data, u32 len, u32 dest_addr, u16 dest_port);
int P2PControlRecvFrom(void* buf, u32 len, u32* from_addr, u16* from_port);
int P2PMatching2SendTo(const void* data, u32 len, u32 dest_addr, u16 dest_port);
int P2PMatching2RecvFrom(void* buf, u32 len, u32* from_addr, u16* from_port);

// bbport: the BBSC emulator's names for the relay (its signaling and matching2 code calls these).
inline void P2PRelaySetServer(u32 addr_nbo) {
    Core::Net::P2P::Relay::SetServer(addr_nbo);
}
inline void P2PRelaySetSelfEndpoint(u32 addr_nbo, u16 port_nbo) {
    Core::Net::P2P::Relay::SetSelfEndpoint(addr_nbo, port_nbo);
}
inline void P2PRelaySetLocalId(std::string_view online_id) {
    Core::Net::P2P::Relay::SetLocalId(online_id);
}
inline void P2PRelayRememberPeer(std::string_view online_id, u32 addr_nbo, u16 port_nbo) {
    Core::Net::P2P::Relay::RememberPeer(online_id, addr_nbo, port_nbo);
}

} // namespace Libraries::Net
