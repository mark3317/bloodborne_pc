// SPDX-FileCopyrightText: Copyright 2026 bbport contributors
// SPDX-License-Identifier: GPL-2.0-or-later

// BBSC relay fallback for the P2P transport (port of BBSC 0.0.2's shadp2p p2p_sockets.cpp relay,
// https://github.com/CLSAMG22/BBSC bbport/bbport-1.7.2-bbsc.patch).
//
// Direct P2P needs one side reachable: CGNAT, strict routers and two PCs behind one router (no
// hairpin NAT) leave both sides unreachable and the connection goes DEAD after 30 s. The BBSC
// game server relays such frames (server/gameserver/bbhost_service.py Relay._shad, UDP 3478 on
// the shadNet server's address):
//   "BBR1" 0x01 id[16]                       register, every 5 s (keeps our NAT mapping open)
//   "BBR1" 0x02                              register acknowledged
//   "BBR1" 0x03 dst[16] src[16] ep[6] frame  frame for dst
//   "BBR1" 0x04 src[16] ep[6] frame          frame from src
//   "BBR1" 0x05 dst[16]                      dst is not on the relay (direct only for 10 s)
// ep = the sender's own public address and port (its STUN echo), so the receiver files the frame
// under the endpoint its signaling code uses for that peer.
//
// As in BBSC 0.0.2, every known peer goes through the relay from its first frame, with direct
// copies until the peer answers (a peer whose emulator has no relay is answered directly).
// BB_P2P_RELAY / SHADPS4_P2P_RELAY: 0 or off = no relay; auto or direct = "direct first, relay
// after 2 s without a direct answer"; a.b.c.d:port = another relay. BB_P2P_RELAY_PORT /
// SHADPS4_P2P_RELAY_PORT changes the port (3478). Off unless the shadNet server has Matching2
// (BBSC servers) - plain shadNet servers have no relay.

#pragma once

#include <functional>
#include <span>
#include <string_view>

#include "common/types.h"

namespace Core::Net::P2P::Relay {

// --- configuration, from the NP layer (any thread) ---
void SetServer(u32 addr_nbo);                       // the shadNet server's address, 0 = off
void SetSelfEndpoint(u32 addr_nbo, u16 port_nbo);   // our public endpoint (STUN echo)
void SetLocalId(std::string_view online_id);        // our online id (registered with the relay)
void RememberPeer(std::string_view online_id, u32 addr_nbo, u16 port_nbo); // a peer's endpoint

// --- used by the transport (its socket) ---
using RawSend = std::function<void(std::span<const u8> packet, u32 addr_nbo, u16 port_nbo)>;

enum class Path { Direct, Relay, Both };

// Whether a packet for dest goes directly, through the relay only, or both. Relay/Both: already
// sent through the relay with send.
Path Route(u32 dest_addr_nbo, u16 dest_port_nbo, std::span<const u8> packet, const RawSend& send);

bool Enabled();
bool IsServer(u32 addr_nbo, u16 port_nbo);

// A packet from the relay server. True with *frame/*from_* set when it carries a frame for the
// transport (the frame points into data).
bool Receive(std::span<const u8> data, std::span<const u8>* frame, u32* from_addr_nbo,
             u16* from_port_nbo);

// A packet straight from a peer (not the relay).
void NoteDirectReceive(u32 addr_nbo, u16 port_nbo);

// Registers with the relay when due (every 5 s, 2 s until answered) and logs a status line.
void KeepAlive(const RawSend& send);

} // namespace Core::Net::P2P::Relay
